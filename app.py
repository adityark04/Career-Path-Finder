import pandas as pd
from flask import Flask, render_template, request
from sentence_transformers import SentenceTransformer, util
import pickle
import torch
from concurrent.futures import ThreadPoolExecutor
from scrapers import youtube_scraper, coursera_scraper
import re

app = Flask(__name__)

def load_all_data():
    print("Loading AI model and all embedding data...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    try:
        with open('data/job_embeddings.pkl', 'rb') as f:
            job_data = pickle.load(f)
        jobs_df, job_embeddings = job_data['df'], job_data['embeddings']
    except FileNotFoundError:
        print("FATAL: Job embeddings not found. Run generate_embeddings.py")
        jobs_df, job_embeddings = None, None

    try:
        with open('data/course_embeddings.pkl', 'rb') as f:
            course_data = pickle.load(f)
        courses_df, course_embeddings = course_data['df'], course_data['embeddings']
    except FileNotFoundError:
        print("WARNING: Static course embeddings not found. Run generate_embeddings.py")
        courses_df, course_embeddings = None, None
        
    print("All models and data loaded.")
    return model, jobs_df, job_embeddings, courses_df, course_embeddings

model, jobs_df, job_embeddings, courses_df, course_embeddings = load_all_data()

# --- Recommendation Functions ---
def recommend_jobs(user_query, top_k=10):
    if jobs_df is None: return []
    query_embedding = model.encode(user_query, convert_to_tensor=True)
    cosine_scores = util.cos_sim(query_embedding, job_embeddings)
    top_results = torch.topk(cosine_scores, k=min(top_k, len(jobs_df)))
    
    recommendations = []
    user_query_lower = user_query.lower()
    user_skills_mentioned = {skill for skill in SKILL_SET if skill in user_query_lower}
    
    for score, idx_tensor in zip(top_results[0][0], top_results[1][0]):
        idx = idx_tensor.item()
        job_details = jobs_df.iloc[idx].to_dict()
        original_score = score.item()
        normalized_score = ((original_score + 1) / 2) * 100
        job_details['similarity_score'] = f"{normalized_score:.2f}"
        
        job_text = (str(job_details.get('title', '')) + " " + str(job_details.get('description', ''))).lower()
        required_skills = {skill for skill in SKILL_SET if skill in job_text}
        
        job_details['required_skills'] = sorted(list(required_skills))
        job_details['skills_gap'] = sorted(list(required_skills - user_skills_mentioned))

        recommendations.append(job_details)
    return recommendations

def get_static_roadmap(job_title, job_profile, top_k=5):
    if courses_df is None: return []
    query_embedding = model.encode(job_profile, convert_to_tensor=True)
    cosine_scores = util.cos_sim(query_embedding, course_embeddings)
    top_results = torch.topk(cosine_scores, k=min(top_k, len(courses_df)))
    
    ai_roadmap = []
    for score, idx in zip(top_results[0][0], top_results[1][0]):
        if score.item() > 0.3:
            ai_roadmap.append(courses_df.iloc[idx.item()].to_dict())
            
    print(f"  > [Static AI] Found {len(ai_roadmap)} strong semantic matches.")
    
    keyword_roadmap = []
    keywords = set(re.findall(r'\b\w+\b', job_title.lower()))
    
    for _, course in courses_df.iterrows():
        course_skills = course['skills_taught'].lower()
        if any(keyword in course_skills for keyword in keywords):
            keyword_roadmap.append(course.to_dict())

    print(f"  > [Static Keyword] Found {len(keyword_roadmap)} keyword matches.")
    
    final_static_roadmap, seen_links = [], set()
    for course in ai_roadmap + keyword_roadmap:
        if course['link'] not in seen_links:
            final_static_roadmap.append(course)
            seen_links.add(course['link'])
    return final_static_roadmap

def get_live_roadmap(query):
    all_resources = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_youtube = executor.submit(youtube_scraper.scrape, query)
        future_coursera = executor.submit(coursera_scraper.scrape, query)
        for future in [future_youtube, future_coursera]:
            all_resources.extend(future.result())
    return all_resources

SKILL_SET = {'python', 'java', 'c++', 'c#', 'javascript', 'typescript', 'html', 'css', 'sql', 'nosql', 'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'fastapi', 'spring boot', 'git', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'linux', 'unix', 'bash', 'powershell', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'seaborn', 'tableau', 'power bi', 'excel', 'figma', 'sketch', 'adobe xd', 'jira', 'agile', 'scrum', 'rest api', 'graphql', 'machine learning', 'data analysis', 'data visualization', 'devops', 'ci/cd', 'automation', 'testing', 'selenium'}

# --- Flask Routes ---
@app.route('/')
def home(): return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def get_recommendations():
    user_query = request.form['skills']
    recommended_jobs = recommend_jobs(user_query)
    
    final_roadmap, top_job_title = [], "your career goal"
    
    if recommended_jobs:
        top_job = recommended_jobs[0]
        top_job_title = top_job['title']
        top_job_profile = top_job['title'] + ". " + top_job['description']
        
        live_resources = get_live_roadmap(top_job_title)
        static_resources = get_static_roadmap(top_job_title, top_job_profile)
        
        combined_resources = live_resources + static_resources
        seen_links = set()
        for resource in combined_resources:
            if resource['link'] not in seen_links:
                final_roadmap.append(resource)
                seen_links.add(resource['link'])
    
    return render_template('results.html', 
                           user_query=user_query, 
                           jobs=recommended_jobs,
                           roadmap_courses=final_roadmap,
                           top_job_title=top_job_title)

# --- API Endpoint for Interactive Roadmap Generation ---
@app.route('/get_roadmap', methods=['POST'])
def get_interactive_roadmap():
    data = request.get_json()
    job_title = data.get('title')
    if not job_title: return {"error": "Job title is required"}, 400
    
    # For interactive roadmaps, we can rely on a hybrid of live + a static backup
    live_resources = get_live_roadmap(job_title)
    static_resources = get_static_roadmap(job_title, job_title) # Use title as profile for simplicity
    
    final_roadmap, seen_links = [], set()
    for resource in live_resources + static_resources:
        if resource['link'] not in seen_links:
            final_roadmap.append(resource)
            seen_links.add(resource['link'])

    return {"roadmap": final_roadmap}

if __name__ == '__main__':
    app.run(debug=True)
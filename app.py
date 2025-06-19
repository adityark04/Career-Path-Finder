import pandas as pd
from flask import Flask, render_template, request
from sentence_transformers import SentenceTransformer, util
import pickle
import torch
from concurrent.futures import ThreadPoolExecutor
from scrapers import youtube_scraper, coursera_scraper

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

def recommend_jobs(user_query, top_k=10):
    if jobs_df is None: return []
    query_embedding = model.encode(user_query, convert_to_tensor=True)
    cosine_scores = util.cos_sim(query_embedding, job_embeddings)
    top_results = torch.topk(cosine_scores, k=min(top_k, len(jobs_df)))
    
    recommendations = []
    for score, idx_tensor in zip(top_results[0][0], top_results[1][0]):
        idx = idx_tensor.item()
        job_details = jobs_df.iloc[idx].to_dict()
        original_score = score.item()
        normalized_score = ((original_score + 1) / 2) * 100
        job_details['similarity_score'] = f"{normalized_score:.2f}"
        recommendations.append(job_details)
    return recommendations

def get_static_roadmap(target_profile, top_k=4):
    if courses_df is None: return []
    query_embedding = model.encode(target_profile, convert_to_tensor=True)
    cosine_scores = util.cos_sim(query_embedding, course_embeddings)
    top_results = torch.topk(cosine_scores, k=min(top_k, len(courses_df)))
    roadmap = [courses_df.iloc[idx.item()].to_dict() for _, idx in zip(top_results[0][0], top_results[1][0])]
    print(f"  > [Static DB] Found {len(roadmap)} fallback resources.")
    return roadmap

def get_live_roadmap(query):
    all_resources = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_youtube = executor.submit(youtube_scraper.scrape, query)
        future_coursera = executor.submit(coursera_scraper.scrape, query)
        for future in [future_youtube, future_coursera]:
            all_resources.extend(future.result())
    return all_resources

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def get_recommendations():
    user_query = request.form['skills']
    recommended_jobs = recommend_jobs(user_query)
    
    final_roadmap = []
    seen_links = set()
    top_job_title = "your career goal"
    
    if recommended_jobs:
        top_job = recommended_jobs[0]
        top_job_title = top_job['title']
        top_job_profile = top_job['title'] + ". " + top_job['description']
        
        # --- HYBRID ROADMAP LOGIC ---
        # 1. Get reliable static results first
        static_resources = get_static_roadmap(top_job_profile)
        
        # 2. Get fresh live results
        live_resources = get_live_roadmap(top_job_title)
        
        # 3. Combine and de-duplicate
        combined_resources = static_resources + live_resources
        for resource in combined_resources:
            if resource['link'] not in seen_links:
                final_roadmap.append(resource)
                seen_links.add(resource['link'])
    
    return render_template('results.html', 
                           user_query=user_query, 
                           jobs=recommended_jobs,
                           roadmap_courses=final_roadmap,
                           top_job_title=top_job_title)

if __name__ == '__main__':
    app.run(debug=True)
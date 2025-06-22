# --- IMPORTS ---
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from sentence_transformers import SentenceTransformer, util
import pickle
import torch
from concurrent.futures import ThreadPoolExecutor
from scrapers import youtube_scraper, coursera_scraper
import re
from models import User, get_user_by_id, get_user_by_username
import os

# --- APP & LOGIN MANAGER SETUP ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-super-secret-key-that-you-should-change'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)

# --- AI DATA LOADING & SKILL SET ---
def load_ai_data():
    print("Loading AI model and all embedding data...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    try:
        with open('data/job_embeddings.pkl', 'rb') as f: job_data = pickle.load(f)
        jobs_df, job_embeddings = job_data['df'], job_data['embeddings']
    except FileNotFoundError:
        print("FATAL: Job embeddings not found. Run generate_embeddings.py"); jobs_df, job_embeddings = None, None
    try:
        with open('data/course_embeddings.pkl', 'rb') as f: course_data = pickle.load(f)
        courses_df, course_embeddings = course_data['df'], course_data['embeddings']
    except FileNotFoundError:
        print("WARNING: Static course embeddings not found. Run generate_embeddings.py"); courses_df, course_embeddings = None, None
    print("All AI models and data loaded.")
    return model, jobs_df, job_embeddings, courses_df, course_embeddings

model, jobs_df, job_embeddings, courses_df, course_embeddings = load_ai_data()
SKILL_SET = {'python', 'java', 'c++', 'c#', 'javascript', 'typescript', 'html', 'css', 'sql', 'nosql', 'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'fastapi', 'spring boot', 'git', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'linux', 'unix', 'bash', 'powershell', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'seaborn', 'tableau', 'power bi', 'excel', 'figma', 'sketch', 'adobe xd', 'jira', 'agile', 'scrum', 'rest api', 'graphql', 'machine learning', 'data analysis', 'data visualization', 'devops', 'ci/cd', 'automation', 'testing', 'selenium'}

# --- RECOMMENDATION LOGIC ---
def recommend_jobs(user_query, top_k=10):
    if jobs_df is None: return []
    query_embedding = model.encode(user_query, convert_to_tensor=True)
    cosine_scores = util.cos_sim(query_embedding, job_embeddings)
    top_results = torch.topk(cosine_scores, k=min(top_k, len(jobs_df)))
    recommendations, user_skills_mentioned = [], {skill for skill in SKILL_SET if skill in user_query.lower()}
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

def get_static_roadmap(job_title, job_profile):
    if courses_df is None: return []
    query_embedding = model.encode(job_profile, convert_to_tensor=True)
    cosine_scores = util.cos_sim(query_embedding, course_embeddings)
    top_results = torch.topk(cosine_scores, k=min(5, len(courses_df)))
    ai_roadmap = [courses_df.iloc[idx.item()].to_dict() for score, idx in zip(top_results[0][0], top_results[1][0]) if score.item() > 0.3]
    keywords = set(re.findall(r'\b\w+\b', job_title.lower()))
    keyword_roadmap = [course.to_dict() for _, course in courses_df.iterrows() if any(keyword in course['skills_taught'].lower() for keyword in keywords)]
    final_static_roadmap, seen_links = [], set()
    for course in ai_roadmap + keyword_roadmap:
        if course['link'] not in seen_links: final_static_roadmap.append(course); seen_links.add(course['link'])
    return final_static_roadmap

def get_live_roadmap(query):
    all_resources = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(scraper.scrape, query) for scraper in [youtube_scraper, coursera_scraper]]
        for future in futures: all_resources.extend(future.result())
    return all_resources

# --- MAIN ROUTES ---
@app.route('/')
def home():
    if not current_user.is_authenticated:
        return render_template('landing.html')
    
    user = current_user
    if not user.skills:
        flash('Welcome! Complete your profile to get personalized career recommendations.', 'info')
        return redirect(url_for('edit_profile'))

    profile_query = f"aspiring {user.degree or ''} developer with skills in {user.skills or ''} from {user.college or ''}"
    recommended_jobs = recommend_jobs(profile_query)
    
    final_roadmap, top_job_title = [], "your ideal career"
    if recommended_jobs:
        top_job = recommended_jobs[0]
        top_job_title = top_job['title']
        top_job_profile = top_job['title'] + ". " + top_job['description']
        live_resources = get_live_roadmap(top_job_title)
        static_resources = get_static_roadmap(top_job_title, top_job_profile)
        combined_resources, seen_links = live_resources + static_resources, set()
        for resource in combined_resources:
            if resource['link'] not in seen_links: final_roadmap.append(resource); seen_links.add(resource['link'])
            
    return render_template('results.html', is_dashboard=True, jobs=recommended_jobs, roadmap_courses=final_roadmap, top_job_title=top_job_title)

# --- AUTHENTICATION ROUTES ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('home'))
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        if get_user_by_username(username):
            flash('Username already exists.', 'warning'); return redirect(url_for('register'))
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        conn = sqlite3.connect('database.db')
        conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
        conn.commit(); conn.close()
        flash('Registration successful! Please log in.', 'success'); return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('home'))
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        user = get_user_by_username(username)
        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid username or password.', 'danger'); return redirect(url_for('login'))
        login_user(user); return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user(); return redirect(url_for('home'))

# --- USER & API ROUTES ---
@app.route('/profile')
@login_required
def profile():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    saved_jobs = conn.execute('SELECT * FROM user_saved_jobs WHERE user_id = ? ORDER BY id DESC', (current_user.id,)).fetchall()
    conn.close()
    return render_template('profile.html', user=current_user, saved_jobs=saved_jobs)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        form_data = {k: request.form.get(k) for k in ['full_name', 'age', 'city', 'college', 'degree', 'skills']}
        conn = sqlite3.connect('database.db')
        conn.execute('''UPDATE users SET full_name = ?, age = ?, city = ?, college = ?, degree = ?, skills = ?
                        WHERE id = ?''',
                     (form_data['full_name'], form_data['age'], form_data['city'], form_data['college'], form_data['degree'], form_data['skills'], current_user.id))
        conn.commit(); conn.close()
        flash('Profile updated successfully!', 'success'); return redirect(url_for('profile'))
    return render_template('edit_profile.html', user=current_user)

@app.route('/get_roadmap', methods=['POST'])
def get_interactive_roadmap():
    data = request.get_json()
    job_title = data.get('title')
    if not job_title: return {"error": "Job title is required"}, 400
    live_resources = get_live_roadmap(job_title)
    static_resources = get_static_roadmap(job_title, job_title)
    final_roadmap, seen_links = [], set()
    for resource in live_resources + static_resources:
        if resource['link'] not in seen_links: final_roadmap.append(resource); seen_links.add(resource['link'])
    return {"roadmap": final_roadmap}

@app.route('/save_job', methods=['POST'])
@login_required
def save_job():
    data = request.get_json()
    job_data = {key: data.get(key) for key in ['title', 'company', 'location', 'description', 'link', 'source']}
    if not all([job_data['title'], job_data['link']]): return {"status": "error", "message": "Missing data"}, 400
    conn = sqlite3.connect('database.db')
    try:
        conn.execute('INSERT INTO user_saved_jobs (user_id, job_title, job_company, job_location, job_description, job_link, job_source) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (current_user.id, job_data['title'], job_data['company'], job_data['location'], job_data['description'], job_data['link'], job_data['source']))
        conn.commit(); status, message = "success", "Job Saved!"
    except sqlite3.IntegrityError: status, message = "info", "Already Saved"
    finally: conn.close()
    return {"status": status, "message": message}

if __name__ == '__main__':
    app.run(debug=True)
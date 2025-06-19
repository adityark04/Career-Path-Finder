import pandas as pd
from flask import Flask, render_template, request
from sentence_transformers import SentenceTransformer, util
import pickle
import torch

# Initialize the Flask App
app = Flask(__name__)

# --- Load AI Model and Pre-computed Embeddings ---
print("Loading AI model and pre-computed embeddings...")
model = SentenceTransformer('all-MiniLM-L6-v2')
with open('data/job_embeddings.pkl', 'rb') as f:
    embedding_data = pickle.load(f)
job_embeddings = embedding_data['embeddings']
jobs_df = embedding_data['jobs_df']
print("AI Model and embeddings loaded successfully.")

# --- AI-Powered Recommendation Function ---
def recommend_jobs_ai(user_skills):
    """Recommends jobs based on semantic similarity using embeddings."""
    user_embedding = model.encode(user_skills, convert_to_tensor=True)
    cosine_scores = util.cos_sim(user_embedding, job_embeddings)
    top_results = torch.topk(cosine_scores, k=min(5, len(jobs_df)))
    
    recommendations = []
    user_skills_set = set([skill.strip().lower() for skill in user_skills.split(',')])

    for score, idx_tensor in zip(top_results[0][0], top_results[1][0]):
        # Convert the PyTorch tensor 'idx_tensor' to a standard Python integer
        idx = idx_tensor.item()
        
        # Now, use the integer 'idx' to index the DataFrame
        job_details = jobs_df.iloc[idx].to_dict()
        
        # The score is also a tensor, so we use .item() on it as well
        job_details['similarity_score'] = f"{score.item()*100:.2f}%"
        
        # --- SKILLS GAP ANALYSIS (Corrected Logic) ---
        job_skills_set = set([s.strip().lower() for s in job_details['skills'].split(';')])
        skills_to_learn = job_skills_set - user_skills_set
        job_details['skills_to_learn'] = sorted(list(skills_to_learn))
        
        recommendations.append(job_details)
        
    return recommendations

# --- Flask Routes ---
@app.route('/')
def home():
    """Renders the home page."""
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    """Handles the form submission and displays AI recommendations."""
    user_skills = request.form['skills']
    recommended_jobs = recommend_jobs_ai(user_skills)
    return render_template('results.html', 
                           user_skills=user_skills, 
                           jobs=recommended_jobs)

# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=True)
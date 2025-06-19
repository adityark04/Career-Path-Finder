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
# --- AI-Powered Recommendation Function (More Robust) ---
# --- AI-Powered Recommendation Function (with Normalized Score) ---
def recommend_jobs_ai(user_skills):
    """Recommends jobs based on semantic similarity using embeddings."""
    if model is None:
        return []

    user_embedding = model.encode(user_skills, convert_to_tensor=True)
    cosine_scores = util.cos_sim(user_embedding, job_embeddings)
    top_results = torch.topk(cosine_scores, k=min(10, len(jobs_df)))
    
    recommendations = []
    
    for score, idx_tensor in zip(top_results[0][0], top_results[1][0]):
        idx = idx_tensor.item()
        job_details = jobs_df.iloc[idx].to_dict()
        
        # --- THIS IS THE FIX ---
        # Get the raw cosine similarity score (-1 to 1)
        original_score = score.item()
        # Normalize it to a 0-100 scale to be more user-friendly
        normalized_score = ((original_score + 1) / 2) * 100
        job_details['similarity_score'] = f"{normalized_score:.2f}"
        # --------------------
        
        # This structure is kept for if you ever add an explicit skills column back
        job_details['skills_to_learn'] = []

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
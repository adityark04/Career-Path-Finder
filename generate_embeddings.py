import pandas as pd
from sentence_transformers import SentenceTransformer
import pickle

print("Loading pre-trained sentence-transformer model...")
# Load a powerful, lightweight model
model = SentenceTransformer('all-MiniLM-L6-v2')

print("Loading data from CSV...")
df = pd.read_csv('data/mock_data.csv')
jobs_df = df[df['type'] == 'Job'].copy()

# Create a 'profile' for each job by combining its important text fields
jobs_df['profile'] = jobs_df['title'] + ". " + jobs_df['description'] + ". Skills: " + jobs_df['skills'].str.replace(';', ', ')
job_profiles = jobs_df['profile'].tolist()

print("Generating embeddings for all job profiles... (This may take a moment)")
# Generate the embeddings
job_embeddings = model.encode(job_profiles, show_progress_bar=True)

print("Embeddings generated successfully.")

# Save the embeddings and the corresponding job data for later use
embedding_data = {
    'embeddings': job_embeddings,
    'jobs_df': jobs_df
}

with open('data/job_embeddings.pkl', 'wb') as f:
    pickle.dump(embedding_data, f)

print("Embeddings and job data saved to data/job_embeddings.pkl")
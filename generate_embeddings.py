import pandas as pd
from sentence_transformers import SentenceTransformer
import pickle

# --- Configuration ---
SOURCE_DATA_FILE = "data/scraped_jobs_aggregated.csv"
OUTPUT_EMBEDDING_FILE = "data/job_embeddings.pkl"

print("Loading pre-trained sentence-transformer model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

print(f"Loading data from {SOURCE_DATA_FILE}...")
try:
    df = pd.read_csv(SOURCE_DATA_FILE)
except FileNotFoundError:
    print(f"Error: The source data file was not found: {SOURCE_DATA_FILE}")
    print("Please run the scraper script first (`python simple_scraper.py`)")
    exit()

# --- THIS IS THE FIX ---
# Ensure the 'skills' column contains strings, replacing empty (NaN) values with an empty string.
df['skills'] = df['skills'].fillna('')
# --------------------

# The AI will infer skills from the job title, company, and description
df['profile'] = df['title'].fillna('') + ". " + df['company'].fillna('') + ". " + df['description'].fillna('')
job_profiles = df['profile'].tolist()

print(f"Found {len(job_profiles)} job profiles to process.")
print("Generating AI embeddings... (This may take a moment)")
job_embeddings = model.encode(job_profiles, show_progress_bar=True)

print("Embeddings generated successfully.")

embedding_data = {
    'embeddings': job_embeddings,
    'jobs_df': df
}

with open(OUTPUT_EMBEDDING_FILE, 'wb') as f:
    pickle.dump(embedding_data, f)

print(f"Success! Embeddings and job data have been saved to {OUTPUT_EMBEDDING_FILE}")
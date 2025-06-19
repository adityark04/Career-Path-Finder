import pandas as pd
from sentence_transformers import SentenceTransformer
import pickle

JOBS_SOURCE_FILE = "data/scraped_jobs_aggregated.csv"
COURSES_SOURCE_FILE = "data/mock_courses.csv"
JOBS_OUTPUT_FILE = "data/job_embeddings.pkl"
COURSES_OUTPUT_FILE = "data/course_embeddings.pkl"

def generate_embeddings(model, source_file, output_file, profile_type):
    print(f"\n--- Generating Embeddings for: {profile_type} ---")
    try:
        df = pd.read_csv(source_file)
    except FileNotFoundError:
        print(f"Error: Source file not found at {source_file}. Skipping.")
        return

    if profile_type == 'Jobs':
        df['profile'] = df['title'].fillna('') + ". " + df['company'].fillna('') + ". " + df['description'].fillna('')
    elif profile_type == 'Courses':
        df['skills_taught'] = df['skills_taught'].fillna('')
        df['profile'] = df['title'].fillna('') + ". Skills taught: " + df['skills_taught']
    
    profiles = df['profile'].tolist()
    print(f"Found {len(profiles)} {profile_type.lower()} to process.")
    embeddings = model.encode(profiles, show_progress_bar=True)

    embedding_data = {'embeddings': embeddings, 'df': df}
    with open(output_file, 'wb') as f: pickle.dump(embedding_data, f)
    print(f"Success! {profile_type} embeddings saved to {output_file}")

def main():
    print("Loading pre-trained sentence-transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    generate_embeddings(model, JOBS_SOURCE_FILE, JOBS_OUTPUT_FILE, 'Jobs')
    generate_embeddings(model, COURSES_SOURCE_FILE, COURSES_OUTPUT_FILE, 'Courses')

if __name__ == "__main__":
    main()
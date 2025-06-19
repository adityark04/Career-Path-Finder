# scrapers/main_scraper.py

import csv
import time
import os # <-- IMPORT THE 'os' MODULE FOR HANDLING FILE PATHS

# Import the individual scraper modules
from . import linkedin_scraper
# from . import indeed_scraper # <-- Temporarily disabled because it's being blocked

# --- DEFINE ALL YOUR SEARCHES IN THIS SINGLE LIST ---
SEARCH_QUERIES = [
    {"keywords": "junior python developer", "location": "Remote"},
    {"keywords": "entry level data analyst", "location": "New York, NY"},
    {"keywords": "ux ui designer intern", "location": "Remote"},
    {"keywords": "junior full stack developer", "location": "Denver, CO"},
    {"keywords": "machine learning intern", "location": "United States"},
]

# --- DEFINE WHICH SCRAPERS TO RUN ---
# We have commented out the Indeed scraper for now
ACTIVE_SCRAPERS = [
    linkedin_scraper,
    # indeed_scraper, 
]

# --- ROBUST FILE PATH DEFINITION ---
# This builds an absolute path to the output file, which is much more reliable
# __file__ is the path to the current script (main_scraper.py)
# os.path.dirname(__file__) gets the directory of the script (scrapers/)
# os.path.join(...) intelligently combines path components
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE_NAME = os.path.join(PROJECT_ROOT, "data", "scraped_jobs_aggregated.csv")
# -----------------------------------

def main():
    print("Starting AGGREGATED job scraper...")
    
    all_scraped_data = []
    seen_links = set()

    for query in SEARCH_QUERIES:
        keywords = query["keywords"]
        location = query["location"]
        print(f"\n--- Running all scrapers for: '{keywords}' in '{location}' ---")

        for scraper_module in ACTIVE_SCRAPERS:
            results = scraper_module.scrape(keywords, location)
            
            for job in results:
                if job['link'] not in seen_links:
                    all_scraped_data.append(job)
                    seen_links.add(job['link'])
            
            time.sleep(1)

    if all_scraped_data:
        print(f"\nTotal unique jobs scraped from all sources: {len(all_scraped_data)}")
        print(f"Saving all jobs to {OUTPUT_FILE_NAME}...")
        
        # --- ENSURE THE 'data' DIRECTORY EXISTS ---
        os.makedirs(os.path.dirname(OUTPUT_FILE_NAME), exist_ok=True)
        # ------------------------------------------
        
        fieldnames = ['title', 'company', 'location', 'description', 'link', 'source', 'skills']
        # Use the absolute path variable to open the file
        with open(OUTPUT_FILE_NAME, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(all_scraped_data)
        print("Scraping complete!")
    else:
        print("No data was successfully scraped across all queries and sources.")

if __name__ == "__main__":
    main()
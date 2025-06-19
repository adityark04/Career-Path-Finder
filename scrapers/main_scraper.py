import csv
import time
import os
from . import linkedin_scraper
# from . import indeed_scraper # Temporarily disabled as it gets blocked

SEARCH_QUERIES = [
    {"keywords": "junior python developer", "location": "Remote"},
    {"keywords": "entry level data analyst", "location": "New York, NY"},
    {"keywords": "ux ui designer intern", "location": "Remote"},
    {"keywords": "junior full stack developer", "location": "Denver, CO"},
    {"keywords": "machine learning intern", "location": "United States"},
]

ACTIVE_SCRAPERS = [
    linkedin_scraper,
    # indeed_scraper, 
]

# Robustly define the output file path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE_NAME = os.path.join(PROJECT_ROOT, "data", "scraped_jobs_aggregated.csv")

def main():
    print("Starting AGGREGATED job scraper...")
    all_scraped_data = []
    seen_links = set()

    for query in SEARCH_QUERIES:
        keywords = query["keywords"]
        location = query["location"]
        print(f"\n--- Running scrapers for: '{keywords}' in '{location}' ---")

        for scraper_module in ACTIVE_SCRAPERS:
            results = scraper_module.scrape(keywords, location)
            for job in results:
                if job['link'] not in seen_links:
                    all_scraped_data.append(job)
                    seen_links.add(job['link'])
            time.sleep(1)

    if all_scraped_data:
        print(f"\nTotal unique jobs scraped: {len(all_scraped_data)}")
        print(f"Saving all jobs to {OUTPUT_FILE_NAME}...")
        
        os.makedirs(os.path.dirname(OUTPUT_FILE_NAME), exist_ok=True)
        
        fieldnames = ['title', 'company', 'location', 'description', 'link', 'source', 'skills']
        with open(OUTPUT_FILE_NAME, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(all_scraped_data)
        print("Scraping complete!")
    else:
        print("No data was scraped.")

if __name__ == "__main__":
    main()
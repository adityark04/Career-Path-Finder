import csv
import requests
from bs4 import BeautifulSoup
import time

# --- DEFINE ALL YOUR SEARCHES IN THIS SINGLE LIST ---
# This is the complete, combined list of different job streams.
SEARCH_QUERIES = [
    # --- Python Development ---
    {
        "keywords": "junior python developer",
        "location": "Remote"
    },
    {
        "keywords": "entry level python programmer",
        "location": "New York, NY"
    },
    {
        "keywords": "associate software engineer python",
        "location": "Austin, TX"
    },

    # --- Frontend Development ---
    {
        "keywords": "entry level front end developer",
        "location": "San Francisco, CA"
    },
    {
        "keywords": "junior ui developer react",
        "location": "Remote"
    },
    {
        "keywords": "associate frontend engineer",
        "location": "Seattle, WA"
    },

    # --- Backend Development ---
    {
        "keywords": "junior backend developer",
        "location": "Chicago, IL"
    },
    {
        "keywords": "entry level backend engineer java",
        "location": "Boston, MA"
    },
    {
        "keywords": "associate backend developer nodejs",
        "location": "Remote"
    },

    # --- Full Stack Development ---
    {
        "keywords": "junior full stack developer",
        "location": "New York, NY"
    },
    {
        "keywords": "entry level fullstack engineer",
        "location": "Remote"
    },
    {
        "keywords": "associate full stack developer",
        "location": "Denver, CO"
    },
    
    # --- Machine Learning & Data Science ---
    {
        "keywords": "machine learning intern",
        "location": "United States"
    },
    {
        "keywords": "entry level data scientist",
        "location": "San Francisco, CA"
    },
    {
        "keywords": "junior ai engineer",
        "location": "Remote"
    },
    {
        "keywords": "data science graduate program",
        "location": "New York, NY"
    },

    # --- Data Analysis ---
    {
        "keywords": "entry level data analyst",
        "location": "New York, NY"
    },
    {
        "keywords": "junior business intelligence analyst",
        "location": "Chicago, IL"
    },

    # --- Cloud & DevOps ---
    {
        "keywords": "cloud support associate",
        "location": "Herndon, VA" # Major AWS data center hub
    },
    {
        "keywords": "junior devops engineer",
        "location": "Remote"
    },
    {
        "keywords": "entry level site reliability engineer",
        "location": "Seattle, WA"
    },

    # --- UX/UI Design ---
    {
        "keywords": "ux ui designer intern",
        "location": "Remote"
    },
    {
        "keywords": "junior product designer",
        "location": "New York, NY"
    },

    # --- Product Management ---
    {
        "keywords": "associate product manager",
        "location": "San Francisco, CA"
    },
    {
        "keywords": "entry level product manager",
        "location": "United States"
    }
]
# ---------------------------------------------------

OUTPUT_FILE_NAME = "data/scraped_linkedin_jobs.csv"

def main():
    print("Starting MULTI-STREAM job scraper...")
    
    all_scraped_data = [] # A list to hold results from ALL searches
    seen_links = set() # A set to track job links and avoid duplicates

    # Loop through each defined query
    for query in SEARCH_QUERIES:
        keywords = query["keywords"]
        location = query["location"]
        
        print(f"\n--- Scraping for: '{keywords}' in '{location}' ---")

        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keywords.replace(' ', '%20')}&location={location.replace(' ', '%20')}&start=0"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"  - Error: Failed to fetch this query. Status code: {response.status_code}")
            continue # Skip to the next query

        soup = BeautifulSoup(response.content, 'html.parser')
        job_cards = soup.find_all('div', class_='base-search-card')
        print(f"  - Found {len(job_cards)} job cards for this query.")

        for card in job_cards:
            try:
                link_element = card.find('a', class_='base-card__full-link')
                link = link_element['href'] if link_element else ''

                # Duplicate check
                if not link or link in seen_links:
                    continue
                seen_links.add(link)
                
                title_element = card.find('h3', class_='base-search-card__title')
                title = title_element.text.strip() if title_element else 'N/A'

                company_element = card.find('h4', class_='base-search-card__subtitle')
                company = company_element.text.strip() if company_element else 'N/A'

                location_element = card.find('span', class_='job-search-card__location')
                location = location_element.text.strip() if location_element else 'N/A'
                
                description = f"Job at {company} in {location}."

                job_data = {
                    'title': title, 'company': company, 'location': location, 
                    'description': description, 'link': link
                }
                all_scraped_data.append(job_data)
                
            except Exception as e:
                continue
        
        # Wait a moment between requests
        time.sleep(1)

    # Save all collected data at the end
    if all_scraped_data:
        print(f"\nTotal unique jobs scraped: {len(all_scraped_data)}")
        print(f"Saving all jobs to {OUTPUT_FILE_NAME}...")
        
        fieldnames = ['title', 'company', 'location', 'description', 'link', 'skills']
        with open(OUTPUT_FILE_NAME, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(all_scraped_data)
        print("Scraping complete!")
    else:
        print("No data was successfully scraped across all queries.")

if __name__ == "__main__":
    main()
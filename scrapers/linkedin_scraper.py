# scrapers/linkedin_scraper.py

import requests
from bs4 import BeautifulSoup
import time

def scrape(keywords, location):
    """
    Scrapes LinkedIn for a given set of keywords and location.
    Returns a list of job dictionaries.
    """
    print(f"  > [LinkedIn] Scraping for: '{keywords}' in '{location}'")
    
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keywords.replace(' ', '%20')}&location={location.replace(' ', '%20')}&start=0"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes
    except requests.exceptions.RequestException as e:
        print(f"  - [LinkedIn] Error fetching page: {e}")
        return [] # Return an empty list on failure

    soup = BeautifulSoup(response.content, 'html.parser')
    job_cards = soup.find_all('div', class_='base-search-card')
    
    jobs_found = []
    for card in job_cards:
        try:
            link_element = card.find('a', class_='base-card__full-link')
            link = link_element['href'] if link_element else ''
            
            title_element = card.find('h3', class_='base-search-card__title')
            title = title_element.text.strip() if title_element else 'N/A'

            company_element = card.find('h4', class_='base-search-card__subtitle')
            company = company_element.text.strip() if company_element else 'N/A'

            location_element = card.find('span', class_='job-search-card__location')
            location_text = location_element.text.strip() if location_element else 'N/A'

            # Standardized data format
            job_data = {
                'title': title,
                'company': company,
                'location': location_text,
                'description': f"Job at {company} in {location_text}.",
                'link': link,
                'source': 'LinkedIn' # IMPORTANT: Add a source field!
            }
            jobs_found.append(job_data)
        except Exception:
            continue
            
    print(f"  - [LinkedIn] Found {len(jobs_found)} jobs.")
    return jobs_found
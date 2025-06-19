# scrapers/indeed_scraper.py

import requests
from bs4 import BeautifulSoup
import time

def scrape(keywords, location):
    """
    Scrapes Indeed.com for a given set of keywords and location.
    Returns a list of job dictionaries in the standardized format.
    """
    print(f"  > [Indeed] Scraping for: '{keywords}' in '{location}'")

    url = f"https://www.indeed.com/jobs?q={keywords.replace(' ', '+')}&l={location.replace(' ', '+')}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"  - [Indeed] Error fetching page: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    # Indeed uses a different class name for its job cards
    job_cards = soup.find_all('div', class_='job_seen_beacon')

    jobs_found = []
    base_url = "https://www.indeed.com"

    for card in job_cards:
        try:
            title_element = card.find('h2', class_='jobTitle').find('a')
            title = title_element.text.strip()

            company_element = card.find('span', class_='companyName')
            company = company_element.text.strip()

            location_element = card.find('div', class_='companyLocation')
            location_text = location_element.text.strip()

            # The link on Indeed is often relative, so we must build the full URL
            relative_link = title_element['href']
            link = base_url + relative_link

            # Standardized data format
            job_data = {
                'title': title,
                'company': company,
                'location': location_text,
                'description': f"Job at {company} in {location_text}.",
                'link': link,
                'source': 'Indeed' # Add the source!
            }
            jobs_found.append(job_data)
        except Exception:
            continue
            
    print(f"  - [Indeed] Found {len(jobs_found)} jobs.")
    return jobs_found
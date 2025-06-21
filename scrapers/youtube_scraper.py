import requests
from bs4 import BeautifulSoup

def scrape(query, limit=4):
    """
    A robust function to scrape YouTube that will not crash the main app.
    """
    print(f"  > [YouTube] Live scraping for: '{query} tutorial'")
    
    # --- The main try...except block ---
    try:
        search_query = (query + " tutorial for beginners").replace(' ', '+')
        url = f"https://www.youtube.com/results?search_query={search_query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Will raise an exception for 4xx/5xx errors

        soup = BeautifulSoup(response.text, 'html.parser')
        video_results = soup.find_all('ytd-video-renderer', class_='style-scope ytd-item-section-renderer', limit=limit)
        
        resources_found = []
        for video in video_results:
            try:
                title_element = video.find('a', {'id': 'video-title'})
                channel_element = video.find('a', {'class': 'yt-simple-endpoint style-scope yt-formatted-string'})
                if title_element and channel_element:
                    title = title_element.get('title')
                    link = "https://www.youtube.com" + title_element.get('href')
                    channel = channel_element.text
                    resources_found.append({
                        'title': title, 'source': channel, 'type': 'YouTube Video',
                        'link': link, 'skills_taught': f"Video tutorial on '{query}'"
                    })
            except Exception:
                continue
        
        print(f"  - [YouTube] Found {len(resources_found)} videos.")
        return resources_found
        
    except Exception as e:
        # If the request fails for any reason, print the error and return an empty list
        print(f"  - [YouTube] CRITICAL ERROR: The scraper failed. Reason: {e}")
        return []
import requests
from bs4 import BeautifulSoup

def scrape(query, limit=4):
    print(f"  > [YouTube] Live scraping for: '{query} tutorial'")
    search_query = (query + " tutorial for beginners").replace(' ', '+')
    url = f"https://www.youtube.com/results?search_query={search_query}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException: return []

    soup = BeautifulSoup(response.text, 'html.parser')
    # Modern YouTube selector for video containers
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
        except Exception: continue
    
    print(f"  - [YouTube] Found {len(resources_found)} videos.")
    return resources_found
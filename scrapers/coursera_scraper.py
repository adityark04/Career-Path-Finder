from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def scrape(query, limit=4):
    print(f"  > [Coursera] Live scraping for: '{query}'")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--log-level=3")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 10)
    
    search_query = query.replace(' ', '%20')
    url = f"https://www.coursera.org/search?query={search_query}"
    
    resources_found = []
    try:
        driver.get(url)
        # More robust selector using data attributes
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-e2e="product-card"]')))
        course_cards = driver.find_elements(By.CSS_SELECTOR, 'div[data-e2e="product-card"]')
        
        for card in course_cards[:limit]:
            try:
                title_element = card.find_element(By.CSS_SELECTOR, 'h3')
                link_element = card.find_element(By.TAG_NAME, 'a')
                partner_element = card.find_element(By.CSS_SELECTOR, 'span[data-e2e="sdp-partner-name"]')
                type_element = card.find_element(By.CSS_SELECTOR, 'div[data-e2e="product-card-type-text"]')
                
                resources_found.append({
                    'title': title_element.text, 'source': partner_element.text,
                    'type': type_element.text, 'link': link_element.get_attribute('href'),
                    'skills_taught': f"Covers topics related to '{query}'"
                })
            except Exception: continue
    except Exception: pass
    finally: driver.quit()
    
    print(f"  - [Coursera] Found {len(resources_found)} courses.")
    return resources_found
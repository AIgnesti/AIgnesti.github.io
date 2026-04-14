import json
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def fetch_ads_metrics():
    url = 'https://ui.adsabs.harvard.edu/search/p_=0&q=pubdate%3A%5B2017-01%20TO%209999-12%5D%20author%3A(%22ignesti%2Ca.%22)&sort=date%20desc%2C%20bibcode%20desc'
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    # Set a common User-Agent to avoid bot detection
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        print("Navigating to ADS...")
        driver.get(url)
        
        # Wait for the main content to load
        print("Waiting for page content...")
        time_to_wait = 30
        
        # We search for the text directly in the body if the specific class is missing
        wait = WebDriverWait(driver, time_to_wait)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Give JS an extra moment to populate the numbers
        import time
        time.sleep(10)
        
        page_text = driver.find_element(By.TAG_NAME, "body").text
        lines = page_text.split('\n')
        
        data = {"hIndex": "0", "totalCitations": "0", "citedRecords": "0"}
        
        # Search for keywords and take the preceding or following line
        for i, line in enumerate(lines):
            l = line.strip().lower()
            if "h-index" == l and i > 0:
                data["hIndex"] = lines[i-1].strip()
            if "total citations" == l and i > 0:
                data["totalCitations"] = lines[i-1].strip()
            if "number of cited papers" == l and i > 0:
                data["citedRecords"] = lines[i-1].strip()

        # If data is still 0, try a different parsing logic (sometimes numbers follow labels)
        if data["hIndex"] == "0":
            for i, line in enumerate(lines):
                if "h-index" in line.lower() and ":" in line:
                    data["hIndex"] = line.split(":")[-1].strip()

        # CRITICAL: Always write the file, even if empty, to prevent Git error 128
        with open('metrics.json', 'w') as f:
            json.dump(data, f)
            
        print(f"Scrape attempt finished. Data: {data}")

    except Exception as e:
        print(f"Scraper Error: {e}")
        # Ensure file exists even on crash
        if not os.path.exists('metrics.json'):
            with open('metrics.json', 'w') as f:
                json.dump({"error": str(e)}, f)
        sys.exit(1)
    finally:
        driver.quit()

if __name__ == "__main__":
    fetch_ads_metrics()

import json
import os
import sys
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By  # <--- Added this missing import
from webdriver_manager.chrome import ChromeDriverManager

def fetch_ads_metrics():
    url = 'https://ui.adsabs.harvard.edu/search/p_=0&q=pubdate%3A%5B2017-01%20TO%209999-12%5D%20author%3A(%22ignesti%2Ca.%22)&sort=date%20desc%2C%20bibcode%20desc'
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        print("Navigating to ADS...")
        driver.get(url)
        
        print("Waiting 25 seconds for ADS JavaScript and Metrics to settle...")
        time.sleep(25)
        
        # Get the body text - this is usually where the rendered metrics end up
        body_element = driver.find_element(By.TAG_NAME, "body")
        page_text = body_element.text
        
        data = {"hIndex": "0", "totalCitations": "0", "citedRecords": "0"}
        
        # Split by lines and look for the labels
        lines = [l.strip() for l in page_text.split('\n') if l.strip()]
        
        for i, line in enumerate(lines):
            low = line.lower()
            # ADS structure: The number is often the line IMMEDIATELY PRECEDING the label
            if low == "h-index" and i > 0:
                data["hIndex"] = lines[i-1]
            if low == "total citations" and i > 0:
                data["totalCitations"] = lines[i-1]
            if low == "number of cited papers" and i > 0:
                data["citedRecords"] = lines[i-1]

        # Debug print so you can see what it found in the GitHub logs
        print(f"Extraction result: {data}")

        # Always save the file
        with open('metrics.json', 'w') as f:
            json.dump(data, f)
            
    except Exception as e:
        print(f"Scraper encountered an error: {e}")
        # Save a dummy file so Git doesn't crash
        if not os.path.exists('metrics.json'):
            with open('metrics.json', 'w') as f:
                json.dump({"hIndex": "Error", "totalCitations": "Error", "citedRecords": "Error"}, f)
        sys.exit(1)
    finally:
        driver.quit()

if __name__ == "__main__":
    fetch_ads_metrics()

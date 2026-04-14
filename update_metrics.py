import json
import os
import sys
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def fetch_ads_metrics():
    url = 'https://ui.adsabs.harvard.edu/search/p_=0&q=pubdate%3A%5B2017-01%20TO%209999-12%5D%20author%3A(%22ignesti%2Ca.%22)&sort=date%20desc%2C%20bibcode%20desc'
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        print("Navigating to ADS...")
        driver.get(url)
        
        # Wait for the JavaScript to execute
        import time
        print("Waiting 20 seconds for ADS to calculate metrics...")
        time.sleep(20)
        
        # Strategy: Get the whole page source and find the metrics block
        html_source = driver.page_source
        
        data = {"hIndex": "0", "totalCitations": "0", "citedRecords": "0"}

        # Use Regex to find numbers in the metrics summary container
        # These patterns match the typical structure of the ADS metrics sidebar
        h_match = re.search(r'h-index.*?(\d+)', html_source, re.IGNORECASE | re.DOTALL)
        tc_match = re.search(r'Total citations.*?(\d+)', html_source, re.IGNORECASE | re.DOTALL)
        cr_match = re.search(r'Number of cited papers.*?(\d+)', html_source, re.IGNORECASE | re.DOTALL)

        if h_match: data["hIndex"] = h_match.group(1)
        if tc_match: data["totalCitations"] = tc_match.group(1)
        if cr_match: data["citedRecords"] = cr_match.group(1)

        # Fallback: Check if we can find the data in the raw text if regex fails
        if data["hIndex"] == "0":
            body_text = driver.find_element(By.TAG_NAME, "body").text
            print("Regex failed, trying text-split fallback...")
            # (Insert previous text-parsing logic here if needed)

        with open('metrics.json', 'w') as f:
            json.dump(data, f)
            
        print(f"Update complete. Found: {data}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        driver.quit()

if __name__ == "__main__":
    fetch_ads_metrics()

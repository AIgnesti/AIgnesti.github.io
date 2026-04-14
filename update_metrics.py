import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def fetch_ads_metrics():
    url = 'https://ui.adsabs.harvard.edu/search/p_=0&q=pubdate%3A%5B2017-01%20TO%209999-12%5D%20author%3A(%22ignesti%2Ca.%22)&sort=date%20desc%2C%20bibcode%20desc'
    
    # Configure Chrome options for a headless environment
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        print("Opening ADS...")
        driver.get(url)
        
        # Wait up to 30 seconds for the metrics summary to actually appear in the DOM
        print("Waiting for metrics to load...")
        wait = WebDriverWait(driver, 30)
        # ADS uses 'metrics-summary' class for the results sidebar
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "metrics-summary")))
        
        # Extract the text
        metrics_text = driver.find_element(By.CLASS_NAME, "metrics-summary").text
        lines = metrics_text.split('\n')
        
        data = {"hIndex": "0", "totalCitations": "0", "citedRecords": "0"}
        
        for i, line in enumerate(lines):
            l = line.strip().lower()
            if l == "h-index": data["hIndex"] = lines[i-1].strip()
            if l == "total citations": data["totalCitations"] = lines[i-1].strip()
            if l == "number of cited papers": data["citedRecords"] = lines[i-1].strip()

        with open('metrics.json', 'w') as f:
            json.dump(data, f)
            
        print(f"Successfully captured: {data}")

    except Exception as e:
        print(f"Error: {e}")
        # Take a screenshot for debugging if it fails (visible in GitHub Action artifacts)
        driver.save_screenshot("error_screenshot.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    fetch_ads_metrics()

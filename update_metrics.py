import json
import os
import sys
from requests_html import HTMLSession

def fetch_ads_metrics():
    # Create session
    session = HTMLSession()
    url = 'https://ui.adsabs.harvard.edu/search/p_=0&q=pubdate%3A%5B2017-01%20TO%209999-12%5D%20author%3A(%22ignesti%2Ca.%22)&sort=date%20desc%2C%20bibcode%20desc'
    
    try:
        print("Starting request...")
        r = session.get(url)
        
        # CRITICAL: Added browser arguments for GitHub Actions environment
        print("Rendering JavaScript (this may take a moment)...")
       r.html.render(
                sleep=15, 
                keep_page=True, 
                args=['--no-sandbox', '--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-gpu'])
        
        # Find the metrics summary block
        # ADS usually renders this in a div with class 'metrics-summary'
        summary = r.html.find('.metrics-summary', first=True)
        
        if not summary:
            print("Page loaded but metrics summary not found. Check URL or Selectors.")
            # Let's save the HTML to the log to see what ADS is showing us
            # print(r.html.html[:500]) 
            sys.exit(1)

        lines = summary.text.split('\n')
        data = {"hIndex": "0", "totalCitations": "0", "citedRecords": "0"}

        for i, line in enumerate(lines):
            l = line.strip().lower()
            if "h-index" == l: data["hIndex"] = lines[i-1].strip()
            if "total citations" == l: data["totalCitations"] = lines[i-1].strip()
            if "number of cited papers" == l: data["citedRecords"] = lines[i-1].strip()

        with open('metrics.json', 'w') as f:
            json.dump(data, f)
            
        print(f"Success! Data saved: {data}")

    except Exception as e:
        print(f"Scraper crashed with error: {e}")
        sys.exit(1) # Tell GitHub the action failed

if __name__ == "__main__":
    fetch_ads_metrics()

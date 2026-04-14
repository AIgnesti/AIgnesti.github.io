import json
import sys
import asyncio
from requests_html import HTMLSession

def fetch_ads_metrics():
    session = HTMLSession()
    url = 'https://ui.adsabs.harvard.edu/search/p_=0&q=pubdate%3A%5B2017-01%20TO%209999-12%5D%20author%3A(%22ignesti%2Ca.%22)&sort=date%20desc%2C%20bibcode%20desc'
    
    try:
        print("Fetching ADS Page...")
        r = session.get(url)
        
        print("Rendering JavaScript (15s sleep)...")
        # Added extra arguments to ensure it runs in the GitHub environment
        r.html.render(
            sleep=15, 
            keep_page=True, 
            args=[
                '--no-sandbox', 
                '--disable-setuid-sandbox', 
                '--disable-dev-shm-usage',
                '--disable-gpu'
            ]
        )
        
        # ADS is dynamic; we'll look for text indicators in the whole page
        page_text = r.html.full_text
        lines = page_text.split('\n')
        
        data = {"hIndex": "0", "totalCitations": "0", "citedRecords": "0"}
        
        for i, line in enumerate(lines):
            clean = line.strip().lower()
            if clean == "h-index":
                data["hIndex"] = lines[i-1].strip()
            elif clean == "total citations":
                data["totalCitations"] = lines[i-1].strip()
            elif clean == "number of cited papers":
                data["citedRecords"] = lines[i-1].strip()

        # Final check: if we got all zeros, something went wrong with the render
        if data["hIndex"] == "0" and data["totalCitations"] == "0":
            print("Warning: Data parsed as zeros. ADS might have blocked the render.")

        with open('metrics.json', 'w') as f:
            json.dump(data, f)
        print(f"File saved successfully: {data}")

    except Exception as e:
        print(f"Script Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_ads_metrics()

import json
import os
from requests_html import HTMLSession

def fetch_ads_metrics():
    session = HTMLSession()
    url = 'https://ui.adsabs.harvard.edu/search/p_=0&q=pubdate%3A%5B2017-01%20TO%209999-12%5D%20author%3A(%22ignesti%2Ca.%22)&sort=date%20desc%2C%20bibcode%20desc'
    
    try:
        print("Opening ADS...")
        r = session.get(url)
        
        # Give ADS plenty of time to render the JavaScript (15 seconds)
        r.html.render(sleep=15, keep_page=True)
        
        # ADS often stores the 'Metrics' in a specific summary block
        # We search for the text directly if the CSS classes are dynamic
        page_text = r.html.full_text
        
        data = {
            "hIndex": "0",
            "totalCitations": "0",
            "citedRecords": "0",
            "status": "updated"
        }

        # Simple text parsing logic
        lines = page_text.split('\n')
        for i, line in enumerate(lines):
            clean_line = line.strip().lower()
            if "h-index" == clean_line:
                data["hIndex"] = lines[i-1].strip()
            elif "total citations" == clean_line:
                data["totalCitations"] = lines[i-1].strip()
            elif "number of cited papers" == clean_line:
                data["citedRecords"] = lines[i-1].strip()

        with open('metrics.json', 'w') as f:
            json.dump(data, f)
        print("Successfully wrote metrics.json")
            
    except Exception as e:
        print(f"Scraper Error: {e}")

if __name__ == "__main__":
    fetch_ads_metrics()

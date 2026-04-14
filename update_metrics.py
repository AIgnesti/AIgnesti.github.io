import json
import sys
from requests_html import HTMLSession

def fetch_ads_metrics():
    session = HTMLSession()
    url = 'https://ui.adsabs.harvard.edu/search/p_=0&q=pubdate%3A%5B2017-01%20TO%209999-12%5D%20author%3A(%22ignesti%2Ca.%22)&sort=date%20desc%2C%20bibcode%20desc'
    
    try:
        print("Fetching page...")
        r = session.get(url)
        
        print("Rendering (15s)...")
        r.html.render(
            sleep=15, 
            keep_page=True, 
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        
        # ADS often uses the class 'metrics-summary' for the data block
        metrics_block = r.html.find('.metrics-summary', first=True)
        
        if not metrics_block:
            # Fallback: if class is missing, look for text in the whole page
            full_text = r.html.full_text
            print("Full page text captured. Parsing...")
        else:
            full_text = metrics_block.text

        data = {"hIndex": "0", "totalCitations": "0", "citedRecords": "0"}
        lines = full_text.split('\n')
        
        for i, line in enumerate(lines):
            l = line.strip().lower()
            if l == "h-index": data["hIndex"] = lines[i-1].strip()
            if l == "total citations": data["totalCitations"] = lines[i-1].strip()
            if l == "number of cited papers": data["citedRecords"] = lines[i-1].strip()

        with open('metrics.json', 'w') as f:
            json.dump(data, f)
            
        print(f"Update complete: {data}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_ads_metrics()

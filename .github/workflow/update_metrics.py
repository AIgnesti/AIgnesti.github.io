import json
from requests_html import HTMLSession

def fetch_ads_metrics():
    session = HTMLSession()
    url = 'https://ui.adsabs.harvard.edu/search/p_=0&q=pubdate%3A%5B2017-01%20TO%209999-12%5D%20author%3A(%22ignesti%2Ca.%22)&sort=date%20desc%2C%20bibcode%20desc'
    
    # Open the page and render the JavaScript
    r = session.get(url)
    r.html.render(sleep=5) # Wait 5 seconds for numbers to appear
    
    # Selectors based on ADS layout (these are the 'Metrics' summary items)
    try:
        # Note: These selectors may need adjustment if ADS updates their UI
        h_index = r.html.find('.h-index-value', first=True).text
        total_citations = r.html.find('.total-citations-value', first=True).text
        cited_records = r.html.find('.cited-records-value', first=True).text
        
        data = {
            "hIndex": h_index,
            "totalCitations": total_citations,
            "citedRecords": cited_records,
            "lastUpdated": r.html.find('.date-now', first=True).text # optional timestamp
        }
        
        with open('metrics.json', 'w') as f:
            json.dump(data, f)
            
    except Exception as e:
        print(f"Error scraping: {e}")

if __name__ == "__main__":
    fetch_ads_metrics()

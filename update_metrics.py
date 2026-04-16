import json
import requests
import os
import sys

def fetch_ads_metrics():
    token = os.getenv('ADS_TOKEN')
    if not token:
        print("Error: ADS_TOKEN not found in environment.")
        sys.exit(1)

    query = 'pubdate:[2017-01 TO 9999-12] author:("ignesti,a.")property:"refereed"'
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        # 1. Get the bibcodes
        search_url = f'https://api.adsabs.harvard.edu/v1/search/query?q={requests.utils.quote(query)}&fl=bibcode&rows=2000'
        print("Fetching bibcodes...")
        r = requests.get(search_url, headers=headers)
        r.raise_for_status()
        
        docs = r.json().get('response', {}).get('docs', [])
        bibcodes = [doc['bibcode'] for doc in docs]

        if not bibcodes:
            print("No papers found for this query.")
            return

        # 2. Get the metrics
        print(f"Fetching metrics for {len(bibcodes)} papers...")
        metrics_url = 'https://api.adsabs.harvard.edu/v1/metrics'
        payload = {"bibcodes": bibcodes}
        
        m_res = requests.post(metrics_url, headers=headers, json=payload)
        m_res.raise_for_status()
        m_data = m_res.json()

        # Extract stats blocks
        cit_stats = m_data.get('citation stats', {})
        indicators = m_data.get('indicators', {})

        # --- REFINED EXTRACTION LOGIC ---
        
        # 1. Total Citations (Checking two possible keys)
        total_citations = cit_stats.get('total_number_of_citations')
        if total_citations is None:
            #total_citations = cit_stats.get('number_of_citations', 0)
            total_citations = cit_stats.get('total number of citations', 0)

        # 2. Cited Records (Checking two possible keys)
        cited_records = cit_stats.get('refereed publications')
        if cited_records is None:
            # Fallback to 'number_of_papers' in citation stats if specific 'cited' key is missing
            cited_records = cit_stats.get('refereed publications', 0)

        # 3. h-index
        h_index = indicators.get('h', 0)

        output = {
            "hIndex": h_index,
            "totalCitations": total_citations,
            "citedRecords": cited_records,
            "last_updated_count": len(bibcodes)
        }

        # Write to file
        with open('metrics.json', 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"Success! Data found: {output}")

    except Exception as e:
        print(f"API Error: {e}")
        # This will print the full JSON if it fails, so you can see the keys in GitHub logs
        if 'm_res' in locals():
            print("Full API Response for debugging:")
            print(json.dumps(m_res.json(), indent=2))
        sys.exit(1)

if __name__ == "__main__":
    fetch_ads_metrics()

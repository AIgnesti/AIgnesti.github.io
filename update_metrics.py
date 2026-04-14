import json
import requests
import os
import sys

def fetch_ads_metrics():
    token = os.getenv('ADS_TOKEN')
    if not token:
        print("Error: ADS_TOKEN not found in environment.")
        sys.exit(1)

    query = 'pubdate:[2017-01 TO 9999-12] author:("ignesti,a.")'
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

        # The Metrics API returns several blocks: 'basic stats', 'citation stats', etc.
        # We extract from 'indicators' and 'citation stats'
        basic = m_data.get('basic stats', {})
        citations = m_data.get('citation stats', {})
        indicators = m_data.get('indicators', {})

        # Use .get() to avoid KeyErrors if ADS changes a field name
        output = {
            "hIndex": indicators.get('h', 0),
            "totalCitations": citations.get('total_number_of_citations', 0),
            "citedRecords": citations.get('number_of_cited_papers', 0),
            "paperCount": len(bibcodes)
        }

        # Write to file
        with open('metrics.json', 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"Success! metrics.json updated: {output}")

    except Exception as e:
        print(f"API Error: {e}")
        # Log the response body for debugging if it's a JSON error
        if 'm_res' in locals():
            print("Response Keys found:", m_res.json().keys())
        sys.exit(1)

if __name__ == "__main__":
    fetch_ads_metrics()

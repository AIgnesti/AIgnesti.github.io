import json
import requests
import os
import sys

def fetch_ads_metrics():
    # Get the token from GitHub Secrets
    token = os.getenv('ADS_TOKEN')
    if not token:
        print("Error: ADS_TOKEN not found in environment.")
        sys.exit(1)

    query = 'pubdate:[2017-01 TO 9999-12] author:("ignesti,a.")'
    
    # 1. Get the bibcodes for the query
    search_url = f'https://api.adsabs.harvard.edu/v1/search/query?q={query}&fl=bibcode&rows=2000'
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        print("Fetching bibcodes...")
        r = requests.get(search_url, headers=headers)
        r.raise_for_status()
        bibcodes = [doc['bibcode'] for doc in r.json()['response']['docs']]

        if not bibcodes:
            print("No papers found.")
            return

        # 2. Get the metrics for those bibcodes
        print(f"Fetching metrics for {len(bibcodes)} papers...")
        metrics_url = 'https://api.adsabs.harvard.edu/v1/metrics'
        payload = {"bibcodes": bibcodes}
        
        m_res = requests.post(metrics_url, headers=headers, json=payload)
        m_res.raise_for_status()
        m_data = m_res.json()

        # Extract the specific fields
        output = {
            "hIndex": m_data['indicators']['h'],
            "totalCitations": m_data['citation stats']['total_number_of_citations'],
            "citedRecords": m_data['citation stats']['number_of_cited_papers']
        }

        with open('metrics.json', 'w') as f:
            json.dump(output, f)
        
        print(f"Success! Data: {output}")

    except Exception as e:
        print(f"API Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_ads_metrics()

#!/usr/bin/env python3
"""Update the existing indexer with AI enrichment"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

SEARCH_SERVICE = os.getenv('AZURE_SEARCH_SERVICE_NAME')
ADMIN_KEY = os.getenv('AZURE_SEARCH_ADMIN_KEY')
INDEX_NAME = "training-data-index"
INDEXER_NAME = "training-data-index-indexer"  # Correct name
SKILLSET_NAME = "training-data-skillset"
API_VERSION = "2023-11-01"

BASE_URL = f"https://{SEARCH_SERVICE}.search.windows.net"
HEADERS = {
    'Content-Type': 'application/json',
    'api-key': ADMIN_KEY
}

print("🔧 UPDATING INDEXER WITH AI ENRICHMENT")
print("=" * 50)
print()

# Get current indexer
print(f"Getting indexer: {INDEXER_NAME}")
indexer_response = requests.get(
    f"{BASE_URL}/indexers/{INDEXER_NAME}?api-version={API_VERSION}",
    headers=HEADERS
)

if indexer_response.status_code == 200:
    indexer_def = indexer_response.json()
    print(f"✅ Found indexer: {indexer_def['name']}")
    print()
    
    # Update indexer configuration
    print("Updating indexer configuration...")
    indexer_def['skillsetName'] = SKILLSET_NAME
    
    # Enable image extraction for OCR
    if 'parameters' not in indexer_def:
        indexer_def['parameters'] = {}
    if 'configuration' not in indexer_def['parameters']:
        indexer_def['parameters']['configuration'] = {}
    
    indexer_def['parameters']['configuration'].update({
        'dataToExtract': 'contentAndMetadata',
        'imageAction': 'generateNormalizedImages',
        'parsingMode': 'default'
    })
    
    # Add output field mappings
    indexer_def['outputFieldMappings'] = [
        {"sourceFieldName": "/document/people", "targetFieldName": "people"},
        {"sourceFieldName": "/document/organizations", "targetFieldName": "organizations"},
        {"sourceFieldName": "/document/locations", "targetFieldName": "locations"},
        {"sourceFieldName": "/document/keyPhrases", "targetFieldName": "keyPhrases"},
        {"sourceFieldName": "/document/languageCode", "targetFieldName": "languageCode"},
        {"sourceFieldName": "/document/sentimentScore", "targetFieldName": "sentimentScore"},
        {"sourceFieldName": "/document/mergedText", "targetFieldName": "mergedText"},
        {"sourceFieldName": "/document/emails", "targetFieldName": "emails"},
        {"sourceFieldName": "/document/urls", "targetFieldName": "urls"},
        {"sourceFieldName": "/document/dateTimes", "targetFieldName": "dateTimes"}
    ]
    
    # Update indexer
    update_response = requests.put(
        f"{BASE_URL}/indexers/{INDEXER_NAME}?api-version={API_VERSION}",
        headers=HEADERS,
        json=indexer_def
    )
    
    if update_response.status_code in [200, 201, 204]:
        print("✅ Indexer updated successfully!")
        print()
        print("Enabled features:")
        print("  ✅ OCR (image text extraction)")
        print("  ✅ Entity extraction (people, orgs, locations)")
        print("  ✅ Key phrase extraction")
        print("  ✅ Language detection")
        print("  ✅ Sentiment analysis")
        print()
        
        # Run indexer
        print("Starting indexer to process documents...")
        run_response = requests.post(
            f"{BASE_URL}/indexers/{INDEXER_NAME}/run?api-version={API_VERSION}",
            headers=HEADERS
        )
        
        if run_response.status_code == 202:
            print("✅ Indexer started!")
            print("   Processing 2,266+ documents with AI enrichment...")
            print("   This may take 1-2 hours to complete")
        else:
            print(f"⚠️  Indexer run status: {run_response.status_code}")
            if run_response.text:
                print(f"   Response: {run_response.text[:200]}")
    else:
        print(f"❌ Indexer update failed: {update_response.status_code}")
        print(f"   Response: {update_response.text[:500]}")
else:
    print(f"❌ Failed to get indexer: {indexer_response.status_code}")
    print(f"   Response: {indexer_response.text[:200]}")


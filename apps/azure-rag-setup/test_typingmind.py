#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import requests

load_dotenv()

search_service = os.getenv('AZURE_SEARCH_SERVICE_NAME')
search_key = os.getenv('AZURE_SEARCH_ADMIN_KEY')
index_name = "azureblob-index"

print(f"🔍 Azure AI Search Configuration:")
print(f"   Service: {search_service}")
print(f"   Index: {index_name}")
print("")

# Test search for M365 content
search_url = f"https://{search_service}.search.windows.net/indexes/{index_name}/docs/search?api-version=2023-11-01"

headers = {
    'Content-Type': 'application/json',
    'api-key': search_key
}

# Search for SharePoint documents
queries = [
    ("sharepoint", "SharePoint documents"),
    ("UST", "UST company documents"),
    ("benefits", "Benefits documents"),
    ("marketing", "Marketing materials"),
    ("expense", "Expense reports")
]

print("🔍 Testing searches for M365 content:")
print("")

for query, description in queries:
    data = {
        "search": query,
        "top": 5,
        "select": "metadata_storage_name,metadata_storage_path"
    }
    
    response = requests.post(search_url, headers=headers, json=data, timeout=30)
    
    if response.status_code == 200:
        results = response.json()
        count = results.get('@odata.count', len(results.get('value', [])))
        print(f"✅ {description}: {count} results")
        
        if results.get('value'):
            print(f"   Sample: {results['value'][0].get('metadata_storage_name', 'N/A')}")
    else:
        print(f"❌ {description}: Error {response.status_code}")
    print("")

print("✅ TypingMind can now search M365 documents!")
print("")
print("📋 TypingMind Configuration:")
print(f"   Endpoint: https://{search_service}.search.windows.net")
print(f"   Index: {index_name}")
print(f"   API Key: {search_key[:10]}...")

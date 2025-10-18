#!/usr/bin/env python3
"""
Update Azure AI Search Index Schema for Enhanced Features
Adds fields for:
- Multimodal content flags (tables, equations, images)
- Graph relationships
- Enhanced metadata
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

SEARCH_SERVICE = os.getenv('AZURE_SEARCH_SERVICE_NAME')
ADMIN_KEY = os.getenv('AZURE_SEARCH_ADMIN_KEY')
ENDPOINT = os.getenv('AZURE_SEARCH_ENDPOINT')
INDEX_NAME = os.getenv('AZURE_SEARCH_INDEX_NAME', 'azureblob-index')
API_VERSION = "2023-11-01"

BASE_URL = f"{ENDPOINT}"
HEADERS = {
    'Content-Type': 'application/json',
    'api-key': ADMIN_KEY
}

print("🔄 UPDATING AZURE AI SEARCH INDEX SCHEMA")
print("=" * 60)
print(f"Index: {INDEX_NAME}")
print()

# Step 1: Get current index definition
print("📖 Step 1: Fetching current index schema...")
response = requests.get(
    f"{BASE_URL}/indexes/{INDEX_NAME}?api-version={API_VERSION}",
    headers=HEADERS
)

if response.status_code != 200:
    print(f"❌ Failed to get index: {response.status_code}")
    print(response.text)
    exit(1)

index_def = response.json()
print(f"✅ Current index has {len(index_def['fields'])} fields")

# Step 2: Define new fields for enhanced features
print("\n📝 Step 2: Preparing enhanced fields...")

new_fields = [
    # Multimodal content flags
    {
        "name": "has_tables",
        "type": "Edm.Boolean",
        "filterable": True,
        "facetable": True,
        "retrievable": True
    },
    {
        "name": "has_equations",
        "type": "Edm.Boolean",
        "filterable": True,
        "facetable": True,
        "retrievable": True
    },
    {
        "name": "has_images",
        "type": "Edm.Boolean",
        "filterable": True,
        "facetable": True,
        "retrievable": True
    },
    {
        "name": "tables_count",
        "type": "Edm.Int32",
        "filterable": True,
        "sortable": True,
        "retrievable": True
    },

    # Graph relationship fields
    {
        "name": "relationship_score",
        "type": "Edm.Double",
        "filterable": True,
        "sortable": True,
        "retrievable": True
    },
    {
        "name": "cites_count",
        "type": "Edm.Int32",
        "filterable": True,
        "sortable": True,
        "retrievable": True
    },
    {
        "name": "related_docs_count",
        "type": "Edm.Int32",
        "filterable": True,
        "sortable": True,
        "retrievable": True
    },
    {
        "name": "has_relationships",
        "type": "Edm.Boolean",
        "filterable": True,
        "facetable": True,
        "retrievable": True
    },
    {
        "name": "relationship_data",
        "type": "Edm.String",
        "searchable": False,
        "retrievable": True
    },

    # Enhanced multimodal content fields (searchable)
    {
        "name": "tables_content",
        "type": "Edm.String",
        "searchable": True,
        "analyzer": "en.microsoft",
        "retrievable": True
    },
    {
        "name": "equations_content",
        "type": "Edm.String",
        "searchable": True,
        "analyzer": "en.microsoft",
        "retrievable": True
    },
    {
        "name": "images_descriptions",
        "type": "Edm.String",
        "searchable": True,
        "analyzer": "en.microsoft",
        "retrievable": True
    },
    {
        "name": "enhanced_text",
        "type": "Edm.String",
        "searchable": True,
        "analyzer": "en.microsoft",
        "retrievable": True
    },

    # Graph relationship arrays
    {
        "name": "graph_relationships",
        "type": "Collection(Edm.String)",
        "searchable": True,
        "filterable": True,
        "retrievable": True
    },
    {
        "name": "related_documents",
        "type": "Collection(Edm.String)",
        "searchable": False,
        "filterable": True,
        "retrievable": True
    }
]

print(f"   Adding {len(new_fields)} new fields:")
for field in new_fields:
    print(f"   - {field['name']} ({field['type']})")

# Step 3: Check which fields already exist
existing_field_names = {field['name'] for field in index_def['fields']}
fields_to_add = [field for field in new_fields if field['name'] not in existing_field_names]

if not fields_to_add:
    print("\n✅ All enhanced fields already exist in the index!")
    print("   No updates needed.")
    exit(0)

print(f"\n📊 Fields to add: {len(fields_to_add)}")
for field in fields_to_add:
    print(f"   + {field['name']}")

# Step 4: Add new fields to index definition
print("\n🔧 Step 3: Updating index definition...")
index_def['fields'].extend(fields_to_add)

# Step 5: Update the index
print("\n📤 Step 4: Applying changes to Azure AI Search...")
response = requests.put(
    f"{BASE_URL}/indexes/{INDEX_NAME}?api-version={API_VERSION}&allowIndexDowntime=false",
    headers=HEADERS,
    json=index_def
)

if response.status_code in [200, 201, 204]:
    print("✅ Index schema updated successfully!")
    print(f"\n📊 Final index has {len(index_def['fields'])} fields")

    print("\n🎯 New Capabilities Enabled:")
    print("   ✅ Multimodal content detection (tables, equations, images)")
    print("   ✅ Document relationship tracking")
    print("   ✅ Graph-based search and filtering")
    print("   ✅ Enhanced metadata for RAG")

    print("\n💡 Example Queries:")
    print("   # Find documents with tables")
    print('   filter: "has_tables eq true"')
    print("\n   # Find highly connected documents")
    print('   filter: "relationship_score gt 5.0"')
    print('   orderby: "relationship_score desc"')
    print("\n   # Find related documents")
    print('   filter: "has_relationships eq true"')
    print('   select: "metadata_storage_name,relationship_score,related_documents"')

    print("\n📋 Next Steps:")
    print("   1. Run enhanced indexer: python3 m365_sharepoint_indexer_enhanced.py --limit 5")
    print("   2. Check relationship graph: cat sharepoint_graph.json")
    print("   3. Test TypingMind with new filters")

else:
    print(f"❌ Failed to update index: {response.status_code}")
    print(response.text)

    # Try to get more details
    try:
        error_details = response.json()
        print("\nError details:")
        print(json.dumps(error_details, indent=2))
    except:
        pass

    exit(1)

print("\n" + "=" * 60)
print("✅ SCHEMA UPDATE COMPLETE")
print("=" * 60)


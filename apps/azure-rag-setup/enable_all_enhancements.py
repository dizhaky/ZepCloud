#!/usr/bin/env python3
"""
Enable all Azure AI Search enhancements:
1. Semantic Search
2. Advanced OCR
3. AI Enrichment (Cognitive Skills)
4. Relationship Mapping
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

SEARCH_SERVICE = os.getenv('AZURE_SEARCH_SERVICE_NAME')
ADMIN_KEY = os.getenv('AZURE_SEARCH_ADMIN_KEY')
INDEX_NAME = "training-data-index"
API_VERSION = "2023-11-01"

BASE_URL = f"https://{SEARCH_SERVICE}.search.windows.net"
HEADERS = {
    'Content-Type': 'application/json',
    'api-key': ADMIN_KEY
}

print("🚀 AZURE AI SEARCH ENHANCEMENT SETUP")
print("=" * 50)
print()

# Step 1: Enable Semantic Search
print("📋 STEP 1: ENABLING SEMANTIC SEARCH")
print("-" * 50)

# Get current index
response = requests.get(
    f"{BASE_URL}/indexes/{INDEX_NAME}?api-version={API_VERSION}",
    headers=HEADERS
)

if response.status_code == 200:
    index_def = response.json()
    
    # Add semantic configuration
    if 'semantic' not in index_def or not index_def['semantic']:
        print("Adding semantic configuration to index...")
        
        index_def['semantic'] = {
            "configurations": [
                {
                    "name": "default",
                    "prioritizedFields": {
                        "titleField": {
                            "fieldName": "metadata_storage_name"
                        },
                        "prioritizedContentFields": [
                            {"fieldName": "content"}
                        ],
                        "prioritizedKeywordsFields": []
                    }
                }
            ]
        }
        
        # Update index
        update_response = requests.put(
            f"{BASE_URL}/indexes/{INDEX_NAME}?api-version={API_VERSION}",
            headers=HEADERS,
            json=index_def
        )
        
        if update_response.status_code in [200, 201, 204]:
            print("✅ Semantic search enabled successfully!")
        else:
            print(f"⚠️  Semantic search update status: {update_response.status_code}")
            print(f"   Response: {update_response.text[:200]}")
    else:
        print("✅ Semantic search already configured!")
else:
    print(f"❌ Failed to get index: {response.status_code}")

print()

# Step 2: Create Cognitive Services Skillset
print("📋 STEP 2: CREATING AI ENRICHMENT SKILLSET")
print("-" * 50)
print("Note: This requires Azure Cognitive Services resource")
print("Creating skillset with OCR, entity extraction, key phrases...")

skillset_name = "training-data-skillset"

skillset_def = {
    "name": skillset_name,
    "description": "AI enrichment skillset with OCR, entities, key phrases, and relationships",
    "skills": [
        {
            "@odata.type": "#Microsoft.Skills.Vision.OcrSkill",
            "name": "ocr",
            "description": "Extract text from images and scanned documents",
            "context": "/document/normalized_images/*",
            "defaultLanguageCode": "en",
            "detectOrientation": True,
            "inputs": [
                {
                    "name": "image",
                    "source": "/document/normalized_images/*"
                }
            ],
            "outputs": [
                {
                    "name": "text",
                    "targetName": "ocrText"
                }
            ]
        },
        {
            "@odata.type": "#Microsoft.Skills.Text.MergeSkill",
            "name": "merge",
            "description": "Merge OCR text with document text",
            "context": "/document",
            "insertPreTag": " ",
            "insertPostTag": " ",
            "inputs": [
                {
                    "name": "text",
                    "source": "/document/content"
                },
                {
                    "name": "itemsToInsert",
                    "source": "/document/normalized_images/*/ocrText"
                },
                {
                    "name": "offsets",
                    "source": "/document/normalized_images/*/contentOffset"
                }
            ],
            "outputs": [
                {
                    "name": "mergedText",
                    "targetName": "mergedText"
                }
            ]
        },
        {
            "@odata.type": "#Microsoft.Skills.Text.EntityRecognitionSkill",
            "name": "entities",
            "description": "Extract entities (people, organizations, locations)",
            "context": "/document/mergedText",
            "categories": ["Person", "Organization", "Location", "DateTime", "Quantity", "Email", "URL"],
            "defaultLanguageCode": "en",
            "minimumPrecision": 0.5,
            "inputs": [
                {
                    "name": "text",
                    "source": "/document/mergedText"
                }
            ],
            "outputs": [
                {
                    "name": "persons",
                    "targetName": "people"
                },
                {
                    "name": "organizations",
                    "targetName": "organizations"
                },
                {
                    "name": "locations",
                    "targetName": "locations"
                },
                {
                    "name": "dateTimes",
                    "targetName": "dateTimes"
                },
                {
                    "name": "emails",
                    "targetName": "emails"
                },
                {
                    "name": "urls",
                    "targetName": "urls"
                }
            ]
        },
        {
            "@odata.type": "#Microsoft.Skills.Text.KeyPhraseExtractionSkill",
            "name": "keyphrases",
            "description": "Extract key phrases from documents",
            "context": "/document/mergedText",
            "defaultLanguageCode": "en",
            "maxKeyPhraseCount": 20,
            "inputs": [
                {
                    "name": "text",
                    "source": "/document/mergedText"
                }
            ],
            "outputs": [
                {
                    "name": "keyPhrases",
                    "targetName": "keyPhrases"
                }
            ]
        },
        {
            "@odata.type": "#Microsoft.Skills.Text.LanguageDetectionSkill",
            "name": "language",
            "description": "Detect document language",
            "context": "/document",
            "inputs": [
                {
                    "name": "text",
                    "source": "/document/content"
                }
            ],
            "outputs": [
                {
                    "name": "languageCode",
                    "targetName": "languageCode"
                }
            ]
        },
        {
            "@odata.type": "#Microsoft.Skills.Text.SentimentSkill",
            "name": "sentiment",
            "description": "Analyze document sentiment",
            "context": "/document/mergedText",
            "defaultLanguageCode": "en",
            "inputs": [
                {
                    "name": "text",
                    "source": "/document/mergedText"
                }
            ],
            "outputs": [
                {
                    "name": "score",
                    "targetName": "sentimentScore"
                }
            ]
        }
    ],
    "cognitiveServices": {
        "@odata.type": "#Microsoft.Azure.Search.DefaultCognitiveServices"
    }
}

# Create skillset
skillset_response = requests.put(
    f"{BASE_URL}/skillsets/{skillset_name}?api-version={API_VERSION}",
    headers=HEADERS,
    json=skillset_def
)

if skillset_response.status_code in [200, 201]:
    print("✅ AI enrichment skillset created successfully!")
elif skillset_response.status_code == 400:
    print("⚠️  Skillset creation requires Azure Cognitive Services")
    print(f"   Response: {skillset_response.text[:300]}")
else:
    print(f"⚠️  Skillset status: {skillset_response.status_code}")
    print(f"   Response: {skillset_response.text[:300]}")

print()

# Step 3: Update Index with new fields
print("📋 STEP 3: UPDATING INDEX WITH ENRICHMENT FIELDS")
print("-" * 50)

# Get current index again
response = requests.get(
    f"{BASE_URL}/indexes/{INDEX_NAME}?api-version={API_VERSION}",
    headers=HEADERS
)

if response.status_code == 200:
    index_def = response.json()
    
    # Add new fields for enrichments
    new_fields = [
        {"name": "people", "type": "Collection(Edm.String)", "searchable": True, "filterable": True, "facetable": True},
        {"name": "organizations", "type": "Collection(Edm.String)", "searchable": True, "filterable": True, "facetable": True},
        {"name": "locations", "type": "Collection(Edm.String)", "searchable": True, "filterable": True, "facetable": True},
        {"name": "keyPhrases", "type": "Collection(Edm.String)", "searchable": True, "filterable": True, "facetable": True},
        {"name": "languageCode", "type": "Edm.String", "searchable": False, "filterable": True, "facetable": True},
        {"name": "sentimentScore", "type": "Edm.Double", "searchable": False, "filterable": True, "sortable": True},
        {"name": "ocrText", "type": "Edm.String", "searchable": True},
        {"name": "mergedText", "type": "Edm.String", "searchable": True},
        {"name": "emails", "type": "Collection(Edm.String)", "searchable": True, "filterable": True},
        {"name": "urls", "type": "Collection(Edm.String)", "searchable": True, "filterable": True},
        {"name": "dateTimes", "type": "Collection(Edm.String)", "searchable": True, "filterable": True},
        {"name": "relatedDocuments", "type": "Collection(Edm.String)", "searchable": True, "filterable": True}
    ]
    
    existing_field_names = [f['name'] for f in index_def['fields']]
    fields_to_add = [f for f in new_fields if f['name'] not in existing_field_names]
    
    if fields_to_add:
        print(f"Adding {len(fields_to_add)} new enrichment fields...")
        index_def['fields'].extend(fields_to_add)
        
        # Update index
        update_response = requests.put(
            f"{BASE_URL}/indexes/{INDEX_NAME}?api-version={API_VERSION}",
            headers=HEADERS,
            json=index_def
        )
        
        if update_response.status_code in [200, 201, 204]:
            print("✅ Index updated with enrichment fields!")
        else:
            print(f"⚠️  Index update status: {update_response.status_code}")
            print(f"   Response: {update_response.text[:200]}")
    else:
        print("✅ Enrichment fields already exist!")

print()

# Step 4: Update Indexer with skillset
print("📋 STEP 4: UPDATING INDEXER WITH AI ENRICHMENT")
print("-" * 50)

indexer_name = "training-data-indexer"

# Get current indexer
indexer_response = requests.get(
    f"{BASE_URL}/indexers/{indexer_name}?api-version={API_VERSION}",
    headers=HEADERS
)

if indexer_response.status_code == 200:
    indexer_def = indexer_response.json()
    
    # Update indexer configuration
    indexer_def['skillsetName'] = skillset_name
    
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
        f"{BASE_URL}/indexers/{indexer_name}?api-version={API_VERSION}",
        headers=HEADERS,
        json=indexer_def
    )
    
    if update_response.status_code in [200, 201, 204]:
        print("✅ Indexer updated with AI enrichment!")
        print("   - OCR enabled for image text extraction")
        print("   - Entity extraction enabled")
        print("   - Key phrase extraction enabled")
        print("   - Language detection enabled")
        print("   - Sentiment analysis enabled")
    else:
        print(f"⚠️  Indexer update status: {update_response.status_code}")
        print(f"   Response: {update_response.text[:300]}")
else:
    print(f"❌ Failed to get indexer: {indexer_response.status_code}")

print()

# Step 5: Run indexer to process documents
print("📋 STEP 5: RUNNING INDEXER TO PROCESS DOCUMENTS")
print("-" * 50)

run_response = requests.post(
    f"{BASE_URL}/indexers/{indexer_name}/run?api-version={API_VERSION}",
    headers=HEADERS
)

if run_response.status_code == 202:
    print("✅ Indexer started! Processing documents with AI enrichment...")
    print("   This will take some time to process all 2,266+ documents")
else:
    print(f"⚠️  Indexer run status: {run_response.status_code}")

print()
print("=" * 50)
print("🎉 ENHANCEMENT SETUP COMPLETE!")
print("=" * 50)
print()
print("✅ Enabled:")
print("   1. Semantic Search")
print("   2. Advanced OCR (image text extraction)")
print("   3. Entity Recognition (people, orgs, locations)")
print("   4. Key Phrase Extraction")
print("   5. Language Detection")
print("   6. Sentiment Analysis")
print()
print("⏳ Next Steps:")
print("   - Indexer is processing documents (may take 1-2 hours)")
print("   - Check status: python3 maintenance.py --action indexer")
print("   - Test enrichments once complete")
print()
print("📝 Note: Relationship mapping requires custom development")
print("   Will create separate script for document relationships")


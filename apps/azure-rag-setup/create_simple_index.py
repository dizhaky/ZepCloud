#!/usr/bin/env python3
"""
Simple Elasticsearch index creation for M365 data
"""
from elasticsearch import Elasticsearch
import json

def create_simple_index():
    """Create a simple Elasticsearch index for M365 documents"""

    # Connect to Elasticsearch
    es = Elasticsearch('http://localhost:9200')

    # Check connection
    if not es.ping():
        print("❌ Could not connect to Elasticsearch")
        return False

    print("✅ Connected to Elasticsearch")

    # Simple index mapping
    index_mapping = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "title": {"type": "text"},
                "content": {"type": "text"},
                "source_type": {"type": "keyword"},
                "created_at": {"type": "date"},
                "modified_at": {"type": "date"},
                "file_size": {"type": "long"},
                "file_type": {"type": "keyword"},
                "url": {"type": "keyword"},
                "author": {"type": "keyword"},
                "tags": {"type": "keyword"}
            }
        }
    }

    # Delete existing index if it exists
    if es.indices.exists(index="m365-documents"):
        print("Deleting existing index...")
        es.indices.delete(index="m365-documents")

    # Create index
    try:
        result = es.indices.create(
            index="m365-documents",
            body=index_mapping
        )
        print("✅ Index created successfully!")
        print(f"Index: {result['index']}")
        return True
    except Exception as e:
        print(f"❌ Failed to create index: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Creating Simple Elasticsearch Index")
    print("=" * 50)
    create_simple_index()

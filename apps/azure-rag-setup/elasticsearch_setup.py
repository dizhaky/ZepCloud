"""
Set up Elasticsearch indices and mappings for M365 data with RAG-Anything enhancements
"""
from elasticsearch import Elasticsearch
from config_elasticsearch import Config
import logging

logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)

def create_index():
    """Create Elasticsearch index with proper mappings including RAG-Anything fields"""

    # Connect to Elasticsearch Cloud Cluster
    es = Elasticsearch(
        Config.ELASTIC_HOST,
        basic_auth=(Config.ELASTIC_USERNAME, Config.ELASTIC_PASSWORD),
        verify_certs=True,
        ssl_show_warn=False
    )

    # Check connection
    if not es.ping():
        raise Exception("Could not connect to Elasticsearch")

    logger.info("Connected to Elasticsearch successfully")

    # Define index mapping with RAG-Anything enhancements
    index_mapping = {
        "settings": {
            "number_of_shards": 2,
            "number_of_replicas": 1,
            "analysis": {
                "analyzer": {
                    "default": {
                        "type": "standard"
                    },
                    "email_analyzer": {
                        "type": "custom",
                        "tokenizer": "uax_url_email",
                        "filter": ["lowercase"]
                    }
                }
            },
            "index": {
                "max_result_window": 50000
            }
        },
        "mappings": {
            "properties": {
                # Document identification
                "id": {"type": "keyword"},
                "source_type": {"type": "keyword"},
                "source_id": {"type": "keyword"},

                # Content fields
                "title": {
                    "type": "text",
                    "analyzer": "standard",
                    "fields": {
                        "keyword": {"type": "keyword", "ignore_above": 256}
                    }
                },
                "content": {
                    "type": "text",
                    "analyzer": "standard"
                },

                # RAG-Anything multimodal content
                "multimodal_content": {
                    "type": "object",
                    "properties": {
                        "tables": {
                            "type": "nested",
                            "properties": {
                                "table_id": {"type": "keyword"},
                                "content": {"type": "text"},
                                "rows": {"type": "integer"},
                                "columns": {"type": "integer"},
                                "position": {"type": "integer"}
                            }
                        },
                        "equations": {
                            "type": "nested",
                            "properties": {
                                "equation_id": {"type": "keyword"},
                                "latex": {"type": "text"},
                                "position": {"type": "integer"}
                            }
                        },
                        "images": {
                            "type": "nested",
                            "properties": {
                                "image_id": {"type": "keyword"},
                                "caption": {"type": "text"},
                                "alt_text": {"type": "text"},
                                "position": {"type": "integer"}
                            }
                        },
                        "charts": {
                            "type": "nested",
                            "properties": {
                                "chart_id": {"type": "keyword"},
                                "type": {"type": "keyword"},
                                "description": {"type": "text"},
                                "position": {"type": "integer"}
                            }
                        }
                    }
                },

                # RAG-Anything entities and relationships
                "entities": {
                    "type": "nested",
                    "properties": {
                        "type": {"type": "keyword"},
                        "value": {"type": "text"},
                        "confidence": {"type": "float"},
                        "position": {"type": "integer"},
                        "context": {"type": "text"}
                    }
                },
                "relationships": {
                    "type": "nested",
                    "properties": {
                        "source_entity": {"type": "keyword"},
                        "target_entity": {"type": "keyword"},
                        "relationship_type": {"type": "keyword"},
                        "confidence": {"type": "float"},
                        "context": {"type": "text"}
                    }
                },
                "document_relationships": {
                    "type": "nested",
                    "properties": {
                        "related_doc_id": {"type": "keyword"},
                        "relationship_type": {"type": "keyword"},
                        "strength": {"type": "float"},
                        "shared_entities": {"type": "keyword"},
                        "shared_topics": {"type": "keyword"}
                    }
                },

                # Enhanced metadata
                "key_phrases": {"type": "keyword"},
                "topics": {"type": "keyword"},
                "language": {"type": "keyword"},
                "sentiment": {"type": "keyword"},
                "complexity_score": {"type": "float"},

                # Metadata
                "file_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {"type": "keyword", "ignore_above": 512}
                    }
                },
                "file_type": {"type": "keyword"},
                "file_size": {"type": "long"},
                "file_extension": {"type": "keyword"},
                "url": {"type": "keyword"},
                "web_url": {"type": "keyword"},

                # Dates
                "created_date": {"type": "date"},
                "modified_date": {"type": "date"},
                "last_accessed": {"type": "date"},

                # People
                "created_by": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "modified_by": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "author": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword"}}
                },

                # SharePoint specific
                "site_name": {"type": "keyword"},
                "site_id": {"type": "keyword"},
                "library_name": {"type": "keyword"},
                "folder_path": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword"}}
                },

                # OneDrive specific
                "drive_name": {"type": "keyword"},
                "drive_owner": {"type": "keyword"},

                # Email specific
                "from_email": {"type": "keyword"},
                "to_emails": {"type": "keyword"},
                "cc_emails": {"type": "keyword"},
                "subject": {"type": "text"},
                "has_attachments": {"type": "boolean"},
                "importance": {"type": "keyword"},

                # Teams specific
                "team_name": {"type": "keyword"},
                "channel_name": {"type": "keyword"},
                "message_type": {"type": "keyword"},

                # Calendar specific
                "event_start": {"type": "date"},
                "event_end": {"type": "date"},
                "attendees": {"type": "keyword"},
                "location": {"type": "text"},

                # Processing metadata
                "indexed_date": {"type": "date"},
                "processing_status": {"type": "keyword"},
                "error_message": {"type": "text"},
                "processing_pipeline": {"type": "keyword"},
                "olmocr_processed": {"type": "boolean"},
                "raganything_processed": {"type": "boolean"}
            }
        }
    }

    # Check if index exists
    if es.indices.exists(index=Config.ELASTIC_INDEX):
        logger.warning(f"Index '{Config.ELASTIC_INDEX}' already exists")
        response = input("Do you want to delete and recreate it? (yes/no): ")
        if response.lower() == 'yes':
            es.indices.delete(index=Config.ELASTIC_INDEX)
            logger.info(f"Deleted existing index '{Config.ELASTIC_INDEX}'")
        else:
            logger.info("Keeping existing index")
            return

    # Create the index
    logger.info(f"Creating index '{Config.ELASTIC_INDEX}'...")
    es.indices.create(index=Config.ELASTIC_INDEX, body=index_mapping)
    logger.info(f"Index '{Config.ELASTIC_INDEX}' created successfully!")

    # Create index template for future indices
    template_body = {
        "index_patterns": ["m365-*"],
        "template": index_mapping
    }

    es.indices.put_index_template(
        name="m365-template",
        body=template_body
    )
    logger.info("Index template 'm365-template' created successfully!")

    # Get index info
    index_info = es.indices.get(index=Config.ELASTIC_INDEX)
    logger.info(f"Index configuration: {index_info}")

if __name__ == "__main__":
    print("="*60)
    print("Elasticsearch Index Setup for M365 Data with RAG-Anything")
    print("="*60)
    print(f"Elasticsearch Host: {Config.ELASTIC_HOST}")
    print(f"Index Name: {Config.ELASTIC_INDEX}")
    print("="*60)

    try:
        create_index()
        print("\n✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Verify Elasticsearch is running: curl -u elastic:password http://localhost:9200")
        print("2. Check Kibana: http://localhost:5601")
        print("3. Start syncing data: python m365_sync.py")
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        print(f"\n❌ Setup failed: {e}")

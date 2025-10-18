"""
Configuration management for M365 to Elasticsearch migration
"""
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv('env.elasticsearch')

class Config:
    # Elasticsearch Configuration - Cloud Cluster
    ELASTIC_HOST = os.getenv('ELASTIC_HOST', 'https://3b826c108baf419fab59f56c6715a731.us-central1.gcp.cloud.es.io:443')
    ELASTIC_USERNAME = os.getenv('ELASTIC_USERNAME', 'elastic')
    ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD', 'your_cloud_password_here')
    ELASTIC_INDEX = os.getenv('ELASTIC_INDEX', 'm365-documents')

    # Apache Tika Configuration
    TIKA_HOST = os.getenv('TIKA_HOST', 'http://localhost:9998')

    # OlmoCR Configuration
    OLMOCR_ENABLED = os.getenv('OLMOCR_ENABLED', 'true').lower() == 'true'
    OLMOCR_TARGET_DIM = int(os.getenv('OLMOCR_TARGET_DIM', 2048))

    # RAG-Anything Configuration
    RAG_ANYTHING_ENABLED = os.getenv('RAG_ANYTHING_ENABLED', 'true').lower() == 'true'
    RAG_ANYTHING_GRAPH_ENABLED = os.getenv('RAG_ANYTHING_GRAPH_ENABLED', 'true').lower() == 'true'

    # Azure AD Configuration
    AZURE_TENANT_ID = os.getenv('AZURE_TENANT_ID')
    AZURE_CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
    AZURE_CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')

    # Microsoft Graph API Scopes
    GRAPH_SCOPES = os.getenv('GRAPH_SCOPES',
                             'Sites.Read.All,Files.Read.All,Mail.Read,Calendars.Read,Contacts.Read,User.Read.All').split(',')

    # Processing Configuration
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', 100))
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', 50))
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    ENABLE_OCR = os.getenv('ENABLE_OCR', 'true').lower() == 'true'
    ENABLE_AI_ENRICHMENT = os.getenv('ENABLE_AI_ENRICHMENT', 'false').lower() == 'true'

    # Date Filtering
    DATE_FILTER_ENABLED = os.getenv('DATE_FILTER_ENABLED', 'false').lower() == 'true'
    DATE_FILTER_FROM = os.getenv('DATE_FILTER_FROM', '2020-01-01')

    # File Type Filtering
    FILE_TYPE_FILTER_ENABLED = os.getenv('FILE_TYPE_FILTER_ENABLED', 'false').lower() == 'true'
    EXCLUDED_FILE_EXTENSIONS = os.getenv('EXCLUDED_FILE_EXTENSIONS', '').split(',')

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'm365_sync.log')

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = ['AZURE_TENANT_ID', 'AZURE_CLIENT_ID']
        missing = [key for key in required if not getattr(cls, key)]

        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")

        return True

    @classmethod
    def get_date_filter(cls):
        """Get date filter for queries"""
        if cls.DATE_FILTER_ENABLED:
            try:
                return datetime.fromisoformat(cls.DATE_FILTER_FROM)
            except:
                return None
        return None

# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    print(f"Configuration Error: {e}")
    print("Please set the required environment variables in env.elasticsearch file")

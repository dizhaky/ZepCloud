#!/usr/bin/env python3
"""
Azure AI Search Indexer Configuration Script
Sets up data source, index, and indexer for RAG functionality
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any

# Azure imports
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    ComplexField,
    CorsOptions,
    SearchIndexer,
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection
)
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class IndexerConfigurator:
    """Configures Azure AI Search indexer for RAG functionality"""

    def __init__(self):
        self.search_service_name = os.getenv('AZURE_SEARCH_SERVICE_NAME')
        self.admin_key = os.getenv('AZURE_SEARCH_ADMIN_KEY')
        self.endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
        self.index_name = os.getenv('AZURE_SEARCH_INDEX_NAME', 'training-data-index')

        self.storage_account_name = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
        self.storage_key = os.getenv('AZURE_STORAGE_ACCOUNT_KEY')
        self.container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME', 'training-data')

        if not all([self.search_service_name, self.admin_key, self.endpoint]):
            raise ValueError("Azure Search credentials not found in .env file")

        # Initialize search client
        self.search_index_client = SearchIndexClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.admin_key)
        )

        self.data_source_name = f"{self.index_name}-datasource"
        self.indexer_name = f"{self.index_name}-indexer"

    def create_data_source(self) -> None:
        """Create data source connection to Azure Blob Storage"""
        print("🔗 Creating data source connection...")

        # Connection string for blob storage
        connection_string = f"DefaultEndpointsProtocol=https;AccountName={self.storage_account_name};AccountKey={self.storage_key};EndpointSuffix=core.windows.net"

        # Use REST API to create data source
        import requests

        data_source_config = {
            "name": self.data_source_name,
            "type": "azureblob",
            "credentials": {
                "connectionString": connection_string
            },
            "container": {
                "name": self.container_name
            }
        }

        try:
            url = f"{self.endpoint}/datasources/{self.data_source_name}?api-version=2023-11-01"
            headers = {
                "Content-Type": "application/json",
                "api-key": self.admin_key
            }

            response = requests.put(url, json=data_source_config, headers=headers)
            if response.status_code in [200, 201, 204]:
                print("✅ Data source created successfully")
            elif response.status_code == 409:
                print("ℹ️  Data source already exists")
            else:
                print(f"❌ Error creating data source: {response.status_code} - {response.text}")
                raise Exception(f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Error creating data source: {e}")
            raise

    def create_index(self) -> None:
        """Create search index with optimized fields for RAG"""
        print("📋 Creating search index...")

        # Define index fields
        fields = [
            # Primary key
            SimpleField(
                name="id",
                type=SearchFieldDataType.String,
                key=True,
                filterable=True,
                sortable=True
            ),

            # Content fields
            SearchableField(
                name="content",
                type=SearchFieldDataType.String,
                analyzer_name="en.microsoft",
                searchable=True,
                retrievable=True
            ),

            # Metadata fields
            SimpleField(
                name="metadata_storage_name",
                type=SearchFieldDataType.String,
                filterable=True,
                sortable=True,
                facetable=True,
                retrievable=True
            ),

            SimpleField(
                name="metadata_storage_path",
                type=SearchFieldDataType.String,
                filterable=True,
                retrievable=True
            ),

            SimpleField(
                name="metadata_storage_size",
                type=SearchFieldDataType.Int64,
                filterable=True,
                sortable=True,
                retrievable=True
            ),

            SimpleField(
                name="metadata_storage_last_modified",
                type=SearchFieldDataType.DateTimeOffset,
                filterable=True,
                sortable=True,
                retrievable=True
            ),

            SimpleField(
                name="metadata_content_type",
                type=SearchFieldDataType.String,
                filterable=True,
                facetable=True,
                retrievable=True
            ),

            # Custom metadata fields
            SimpleField(
                name="source",
                type=SearchFieldDataType.String,
                filterable=True,
                facetable=True,
                retrievable=True
            ),

            SimpleField(
                name="filename",
                type=SearchFieldDataType.String,
                filterable=True,
                sortable=True,
                retrievable=True
            ),

            SimpleField(
                name="filepath",
                type=SearchFieldDataType.String,
                filterable=True,
                retrievable=True
            ),

            SimpleField(
                name="size",
                type=SearchFieldDataType.String,
                filterable=True,
                retrievable=True
            ),

            SimpleField(
                name="modified",
                type=SearchFieldDataType.String,
                filterable=True,
                sortable=True,
                retrievable=True
            ),

            SimpleField(
                name="created",
                type=SearchFieldDataType.String,
                filterable=True,
                sortable=True,
                retrievable=True
            )
        ]

        # Create index
        index = SearchIndex(
            name=self.index_name,
            fields=fields,
            cors_options=CorsOptions(allowed_origins=["*"], max_age_in_seconds=300)
        )

        try:
            self.search_index_client.create_index(index)
            print("✅ Search index created successfully")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("ℹ️  Search index already exists")
            else:
                print(f"❌ Error creating index: {e}")
                raise

    def create_indexer(self) -> None:
        """Create and configure the indexer"""
        print("⚙️  Creating indexer...")

        # Use REST API to create indexer
        import requests

        indexer_config = {
            "name": self.indexer_name,
            "dataSourceName": self.data_source_name,
            "targetIndexName": self.index_name,
            "parameters": {
                "batchSize": 25,  # Reduced from 100 for better error handling
                "maxFailedItems": 100,  # Increased to tolerate more failures
                "maxFailedItemsPerBatch": 20,  # Increased from 5
                "configuration": {
                    "failOnUnsupportedContentType": False,
                    "failOnUnprocessableDocument": False,
                    "indexedFileNameExtensions": ".pdf,.docx,.doc,.xlsx,.xls,.txt,.md,.json,.csv,.msg,.eml,.html,.htm,.rtf,.xml",
                    "dataToExtract": "contentAndMetadata",
                    "imageAction": "none"
                }
            },
            "schedule": {
                "interval": "PT1H"  # Run every hour
            }
        }

        try:
            url = f"{self.endpoint}/indexers/{self.indexer_name}?api-version=2023-11-01"
            headers = {
                "Content-Type": "application/json",
                "api-key": self.admin_key
            }

            response = requests.put(url, json=indexer_config, headers=headers)
            if response.status_code in [200, 201, 204]:
                print("✅ Indexer created successfully")
            elif response.status_code == 409:
                print("ℹ️  Indexer already exists")
            else:
                print(f"❌ Error creating indexer: {response.status_code} - {response.text}")
                raise Exception(f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Error creating indexer: {e}")
            raise

    def run_indexer(self) -> None:
        """Run the indexer to process documents"""
        print("🚀 Running indexer...")

        try:
            import requests
            url = f"{self.endpoint}/indexers/{self.indexer_name}/run?api-version=2023-11-01"
            headers = {
                "api-key": self.admin_key
            }

            response = requests.post(url, headers=headers)
            if response.status_code == 202:
                print("✅ Indexer started successfully")
            else:
                print(f"❌ Error running indexer: {response.status_code} - {response.text}")
                raise Exception(f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Error running indexer: {e}")
            raise

    def check_indexer_status(self) -> Dict[str, Any]:
        """Check indexer status and statistics"""
        print("📊 Checking indexer status...")

        try:
            import requests
            url = f"{self.endpoint}/indexers/{self.indexer_name}/status?api-version=2023-11-01"
            headers = {
                "api-key": self.admin_key
            }

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                indexer_status = response.json()

                status_info = {
                    'status': indexer_status.get('status', 'Unknown'),
                    'last_result': indexer_status.get('lastResult', {}),
                    'execution_history': indexer_status.get('executionHistory', [])
                }

                print(f"📈 Indexer Status: {status_info['status']}")

                last_result = status_info['last_result']
                if last_result:
                    print(f"📄 Documents processed: {last_result.get('itemsProcessed', 0)}")
                    print(f"✅ Successful items: {last_result.get('itemsSucceeded', 0)}")
                    print(f"❌ Failed items: {last_result.get('itemsFailed', 0)}")

                    errors = last_result.get('errors', [])
                    if errors:
                        print("⚠️  Errors encountered:")
                        for error in errors[:5]:  # Show first 5 errors
                            print(f"   - {error}")

                return status_info
            else:
                print(f"❌ Error checking indexer status: {response.status_code} - {response.text}")
                return {}

        except Exception as e:
            print(f"❌ Error checking indexer status: {e}")
            return {}

    def wait_for_completion(self, timeout_minutes: int = 30) -> bool:
        """Wait for indexer to complete processing"""
        print(f"⏳ Waiting for indexer completion (timeout: {timeout_minutes} minutes)...")

        start_time = time.time()
        timeout_seconds = timeout_minutes * 60

        while time.time() - start_time < timeout_seconds:
            try:
                indexer_status = self.search_index_client.get_indexer_status(self.indexer_name)

                if indexer_status.status == "Running":
                    print("🔄 Indexer is running...")
                    time.sleep(30)  # Check every 30 seconds
                elif indexer_status.status == "Success":
                    print("✅ Indexer completed successfully!")
                    return True
                elif indexer_status.status == "Failed":
                    print("❌ Indexer failed!")
                    return False
                else:
                    print(f"ℹ️  Indexer status: {indexer_status.status}")
                    time.sleep(10)

            except Exception as e:
                print(f"❌ Error checking status: {e}")
                time.sleep(10)

        print("⏰ Timeout reached")
        return False

    def get_index_statistics(self) -> Dict[str, Any]:
        """Get index statistics"""
        try:
            index_stats = self.search_index_client.get_search_index_statistics(self.index_name)

            stats = {
                'document_count': index_stats.document_count,
                'storage_size': index_stats.storage_size,
                'vector_index_size': getattr(index_stats, 'vector_index_size', 0)
            }

            print(f"📊 Index Statistics:")
            print(f"   Documents: {stats['document_count']}")
            print(f"   Storage Size: {stats['storage_size']} bytes")

            return stats

        except Exception as e:
            print(f"❌ Error getting index statistics: {e}")
            return {}

def main():
    """Main configuration process"""
    print("🔧 Azure AI Search Indexer Configuration")
    print("=" * 50)

    try:
        # Initialize configurator
        configurator = IndexerConfigurator()

        # Create components
        configurator.create_data_source()
        configurator.create_index()
        configurator.create_indexer()

        # Run indexer
        configurator.run_indexer()

        # Check status
        status = configurator.check_indexer_status()

        # Wait for completion (optional)
        print("\n❓ Do you want to wait for indexer completion? (y/n): ", end="")
        if input().lower().startswith('y'):
            success = configurator.wait_for_completion()
            if success:
                stats = configurator.get_index_statistics()
                print(f"\n🎉 Indexing completed! {stats.get('document_count', 0)} documents indexed")
            else:
                print("\n⚠️  Indexing may not have completed successfully")

        print("\n✅ Configuration completed!")
        print("🔧 Next step: Run generate-typingmind-config.py to get TypingMind settings")

    except Exception as e:
        print(f"❌ Error during configuration: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())

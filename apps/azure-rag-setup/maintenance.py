#!/usr/bin/env python3
"""
Azure RAG Maintenance Script
Monitors and maintains Azure AI Search RAG system
"""

import os
import json
import sys
import argparse
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError
from dotenv import load_dotenv

# Import M365 modules
try:
    from m365_sharepoint_indexer import SharePointIndexer
    from m365_onedrive_indexer import OneDriveIndexer
    from m365_exchange_indexer import ExchangeIndexer
    M365_AVAILABLE = True
except ImportError:
    M365_AVAILABLE = False

# Load environment variables
load_dotenv()

class RAGMaintenance:
    """Maintenance utilities for Azure RAG system"""

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

        # Initialize clients
        self.search_index_client = SearchIndexClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.admin_key)
        )

        self.search_client = SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=AzureKeyCredential(self.admin_key)
        )

        # Storage client
        if self.storage_account_name and self.storage_key:
            connection_string = f"DefaultEndpointsProtocol=https;AccountName={self.storage_account_name};AccountKey={self.storage_key};EndpointSuffix=core.windows.net"
            self.blob_client = BlobServiceClient.from_connection_string(connection_string)
        else:
            self.blob_client = None

    def check_indexer_status(self) -> Dict[str, Any]:
        """Check indexer status and health"""
        print("🔍 Checking indexer status...")

        try:
            import requests
            indexer_name = f"{self.index_name}-indexer"
            url = f"{self.endpoint}/indexers/{indexer_name}/status?api-version=2023-11-01"
            headers = {
                "api-key": self.admin_key
            }

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                status = response.json()

                status_info = {
                    'status': status.get('status', 'Unknown'),
                    'last_result': status.get('lastResult', {}),
                    'execution_history': status.get('executionHistory', [])
                }

                print(f"📊 Indexer Status: {status_info['status']}")

                last_result = status_info['last_result']
                if last_result:
                    print(f"📄 Last run: {last_result.get('startTime', 'Unknown')}")
                    print(f"📄 Documents processed: {last_result.get('itemsProcessed', 0)}")
                    print(f"✅ Successful: {last_result.get('itemsSucceeded', 0)}")
                    print(f"❌ Failed: {last_result.get('itemsFailed', 0)}")

                    errors = last_result.get('errors', [])
                    if errors:
                        print("⚠️  Recent errors:")
                        for error in errors[:3]:
                            print(f"   - {error}")

                return status_info
            else:
                print(f"❌ Error checking indexer status: {response.status_code} - {response.text}")
                return {}

        except Exception as e:
            print(f"❌ Error checking indexer status: {e}")
            return {}

    def get_index_statistics(self) -> Dict[str, Any]:
        """Get comprehensive index statistics"""
        print("📊 Gathering index statistics...")

        try:
            import requests
            url = f"{self.endpoint}/indexes/{self.index_name}/stats?api-version=2023-11-01"
            headers = {
                "api-key": self.admin_key
            }

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                stats = response.json()

                # Get document count with search
                search_results = self.search_client.search("*", top=0, include_total_count=True)
                total_docs = search_results.get_count()

                statistics = {
                    'document_count': stats.get('documentCount', 0),
                    'storage_size_bytes': stats.get('storageSize', 0),
                    'vector_index_size': stats.get('vectorIndexSize', 0),
                    'search_verified_count': total_docs,
                    'last_updated': datetime.now().isoformat()
                }

                print(f"📈 Index Statistics:")
                print(f"   Documents: {statistics['document_count']}")
                print(f"   Storage: {statistics['storage_size_bytes'] / 1024 / 1024:.2f} MB")
                print(f"   Search verified: {statistics['search_verified_count']}")

                return statistics
            else:
                print(f"❌ Error getting index statistics: {response.status_code} - {response.text}")
                return {}

        except Exception as e:
            print(f"❌ Error getting index statistics: {e}")
            return {}

    def check_storage_usage(self) -> Dict[str, Any]:
        """Check Azure Storage usage and costs"""
        print("💾 Checking storage usage...")

        if not self.blob_client:
            print("⚠️  Storage client not available")
            return {}

        try:
            container_client = self.blob_client.get_container_client(self.container_name)
            blobs = container_client.list_blobs()

            total_size = 0
            blob_count = 0
            file_types = {}

            for blob in blobs:
                total_size += blob.size
                blob_count += 1

                # Count file types
                file_ext = os.path.splitext(blob.name)[1].lower()
                file_types[file_ext] = file_types.get(file_ext, 0) + 1

            storage_info = {
                'total_size_bytes': total_size,
                'total_size_mb': total_size / 1024 / 1024,
                'blob_count': blob_count,
                'file_types': file_types,
                'container_name': self.container_name
            }

            print(f"📦 Storage Usage:")
            print(f"   Total size: {storage_info['total_size_mb']:.2f} MB")
            print(f"   Blob count: {storage_info['blob_count']}")
            print(f"   File types: {file_types}")

            return storage_info

        except Exception as e:
            print(f"❌ Error checking storage usage: {e}")
            return {}

    def test_search_functionality(self) -> bool:
        """Test search functionality with sample queries"""
        print("🔍 Testing search functionality...")

        test_queries = [
            "*",  # Get all documents
            "document",  # Search for documents
            "email",  # Search for emails
            "pdf"  # Search for PDFs
        ]

        results = {}

        for query in test_queries:
            try:
                search_results = self.search_client.search(
                    search_text=query,
                    top=5,
                    include_total_count=True
                )

                result_list = list(search_results)
                total_count = search_results.get_count()

                results[query] = {
                    'total_count': total_count,
                    'returned_docs': len(result_list)
                }

                print(f"   Query '{query}': {total_count} results")

            except Exception as e:
                print(f"   Query '{query}': Error - {e}")
                results[query] = {'error': str(e)}

        # Overall assessment
        successful_queries = sum(1 for r in results.values() if 'error' not in r)
        if successful_queries == len(test_queries):
            print("✅ All search tests passed")
            return True
        else:
            print(f"⚠️  {len(test_queries) - successful_queries} search tests failed")
            return False

    def run_indexer(self) -> bool:
        """Manually run the indexer"""
        print("🚀 Running indexer manually...")

        try:
            import requests
            indexer_name = f"{self.index_name}-indexer"
            url = f"{self.endpoint}/indexers/{indexer_name}/run?api-version=2023-11-01"
            headers = {
                "api-key": self.admin_key
            }

            response = requests.post(url, headers=headers)
            if response.status_code == 202:
                print("✅ Indexer started successfully")
                return True
            else:
                print(f"❌ Error running indexer: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error running indexer: {e}")
            return False

    def clean_old_documents(self, days_old: int = 30) -> int:
        """Clean up old documents from storage"""
        print(f"🧹 Cleaning documents older than {days_old} days...")

        if not self.blob_client:
            print("⚠️  Storage client not available")
            return 0

        try:
            container_client = self.blob_client.get_container_client(self.container_name)
            cutoff_date = datetime.now() - timedelta(days=days_old)

            deleted_count = 0
            blobs = container_client.list_blobs()

            for blob in blobs:
                if blob.last_modified < cutoff_date:
                    try:
                        container_client.delete_blob(blob.name)
                        deleted_count += 1
                        print(f"   Deleted: {blob.name}")
                    except Exception as e:
                        print(f"   Error deleting {blob.name}: {e}")

            print(f"✅ Deleted {deleted_count} old documents")
            return deleted_count

        except Exception as e:
            print(f"❌ Error cleaning old documents: {e}")
            return 0

    def generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        print("📋 Generating health report...")

        report = {
            'timestamp': datetime.now().isoformat(),
            'indexer_status': self.check_indexer_status(),
            'index_statistics': self.get_index_statistics(),
            'storage_usage': self.check_storage_usage(),
            'search_functionality': self.test_search_functionality(),
            'm365_status': self._get_m365_status() if M365_AVAILABLE else {'status': 'M365 modules not available'}
        }

        # Overall health assessment
        health_score = 0
        if report['indexer_status'].get('status') == 'Success':
            health_score += 25
        if report['index_statistics'].get('document_count', 0) > 0:
            health_score += 25
        if report['storage_usage'].get('blob_count', 0) > 0:
            health_score += 25
        if report['search_functionality']:
            health_score += 25

        report['health_score'] = health_score
        report['health_status'] = 'Healthy' if health_score >= 75 else 'Warning' if health_score >= 50 else 'Critical'

        return report

    def save_health_report(self, report: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Save health report to file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"health_report_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"📊 Health report saved to: {filename}")
        return filename

    def _get_m365_status(self) -> Dict[str, Any]:
        """Get M365 sync status for all services"""
        if not M365_AVAILABLE:
            return {'status': 'M365 modules not available'}

        try:
            status = {
                'sharepoint': {},
                'onedrive': {},
                'exchange': {},
                'overall_status': 'Unknown'
            }

            # SharePoint status
            try:
                sharepoint_indexer = SharePointIndexer()
                sharepoint_status = sharepoint_indexer.get_status()
                status['sharepoint'] = {
                    'last_sync': sharepoint_status.get('last_sync'),
                    'sites_processed': sharepoint_status.get('sites_processed', 0),
                    'total_documents': sharepoint_status.get('total_documents', 0),
                    'processed_documents': sharepoint_status.get('processed_documents', 0)
                }
            except Exception as e:
                status['sharepoint'] = {'error': str(e)}

            # OneDrive status
            try:
                onedrive_indexer = OneDriveIndexer()
                onedrive_status = onedrive_indexer.get_status()
                status['onedrive'] = {
                    'last_sync': onedrive_status.get('last_sync'),
                    'users_processed': onedrive_status.get('users_processed', 0),
                    'total_documents': onedrive_status.get('total_documents', 0),
                    'processed_documents': onedrive_status.get('processed_documents', 0)
                }
            except Exception as e:
                status['onedrive'] = {'error': str(e)}

            # Exchange status
            try:
                exchange_indexer = ExchangeIndexer()
                exchange_status = exchange_indexer.get_status()
                status['exchange'] = {
                    'last_sync': exchange_status.get('last_sync'),
                    'users_processed': exchange_status.get('users_processed', 0),
                    'total_emails': exchange_status.get('total_emails', 0),
                    'total_attachments': exchange_status.get('total_attachments', 0),
                    'processed_attachments': exchange_status.get('processed_attachments', 0)
                }
            except Exception as e:
                status['exchange'] = {'error': str(e)}

            # Determine overall status
            services_with_sync = 0
            for service in ['sharepoint', 'onedrive', 'exchange']:
                if service in status and 'last_sync' in status[service] and status[service]['last_sync']:
                    services_with_sync += 1

            if services_with_sync == 3:
                status['overall_status'] = 'All services synced'
            elif services_with_sync > 0:
                status['overall_status'] = f'{services_with_sync}/3 services synced'
            else:
                status['overall_status'] = 'No services synced'

            return status

        except Exception as e:
            return {'status': 'Error', 'error': str(e)}


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Azure RAG Maintenance - Monitor and maintain your RAG system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run health check in non-interactive mode
  python3 maintenance.py --non-interactive --action health

  # Run indexer manually
  python3 maintenance.py --non-interactive --action run-indexer

  # Generate health report with JSON output
  python3 maintenance.py --non-interactive --action health --output json

  # Clean old documents
  python3 maintenance.py --non-interactive --action clean --days 30
        """
    )

    parser.add_argument(
        '--non-interactive',
        action='store_true',
        help='Run in non-interactive mode (no prompts)'
    )

    parser.add_argument(
        '--action',
        choices=['health', 'run-indexer', 'clean', 'status'],
        help='Action to perform: health (generate report), run-indexer (manually run), clean (remove old docs), status (indexer status)'
    )

    parser.add_argument(
        '--output',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )

    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Days old for cleanup (default: 30)'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress progress messages'
    )

    return parser.parse_args()


def main_interactive(maintenance: 'RAGMaintenance'):
    """Original interactive mode"""
    # Generate health report
    report = maintenance.generate_health_report()

    # Display summary
    print(f"\n📊 HEALTH SUMMARY")
    print(f"Status: {report['health_status']} ({report['health_score']}/100)")
    print(f"Documents: {report['index_statistics'].get('document_count', 0)}")
    print(f"Storage: {report['storage_usage'].get('total_size_mb', 0):.2f} MB")
    print(f"Search: {'✅ Working' if report['search_functionality'] else '❌ Issues'}")

    # Save report
    maintenance.save_health_report(report)

    # Interactive options
    print(f"\n🔧 MAINTENANCE OPTIONS")
    print("1. Run indexer manually")
    print("2. Clean old documents")
    print("3. Exit")

    choice = input("\nSelect option (1-3): ").strip()

    if choice == '1':
        maintenance.run_indexer()
    elif choice == '2':
        days = input("Enter days old for cleanup (default 30): ").strip()
        days = int(days) if days.isdigit() else 30
        maintenance.clean_old_documents(days)
    else:
        print("👋 Goodbye!")


def main_non_interactive(maintenance: 'RAGMaintenance', args):
    """Non-interactive mode with specific actions"""
    result = {'success': True, 'message': ''}

    if args.action == 'health':
        report = maintenance.generate_health_report()

        if args.output == 'json':
            print(json.dumps(report, indent=2))
        else:
            print(f"\n📊 HEALTH SUMMARY")
            print(f"Status: {report['health_status']} ({report['health_score']}/100)")
            print(f"Documents: {report['index_statistics'].get('document_count', 0)}")
            print(f"Storage: {report['storage_usage'].get('total_size_mb', 0):.2f} MB")
            print(f"Search: {'✅ Working' if report['search_functionality'] else '❌ Issues'}")

        filename = maintenance.save_health_report(report)
        result['message'] = f"Health report saved to {filename}"
        result['health_score'] = report['health_score']

    elif args.action == 'run-indexer':
        success = maintenance.run_indexer()
        result['success'] = success
        result['message'] = "Indexer started successfully" if success else "Failed to start indexer"

        if args.output == 'json':
            print(json.dumps(result, indent=2))

    elif args.action == 'clean':
        deleted = maintenance.clean_old_documents(args.days)
        result['deleted_count'] = deleted
        result['message'] = f"Deleted {deleted} old documents"

        if args.output == 'json':
            print(json.dumps(result, indent=2))

    elif args.action == 'status':
        status = maintenance.check_indexer_status()

        if args.output == 'json':
            print(json.dumps(status, indent=2))
        else:
            print(f"\n📊 Indexer Status: {status.get('status', 'Unknown')}")
            last_result = status.get('last_result', {})
            if last_result:
                print(f"   Documents processed: {last_result.get('itemsProcessed', 0)}")
                print(f"   Successful: {last_result.get('itemsSucceeded', 0)}")
                print(f"   Failed: {last_result.get('itemsFailed', 0)}")

        result['status'] = status

    return 0 if result['success'] else 1

def main():
    """Main maintenance process"""
    # Parse arguments
    args = parse_arguments()

    print("🔧 Azure RAG Maintenance")
    print("=" * 40)

    try:
        # Initialize maintenance
        maintenance = RAGMaintenance()

        # Choose mode
        if args.non_interactive:
            if not args.action:
                print("❌ Error: --action is required in non-interactive mode")
                print("Use --help for usage information")
                return 1
            return main_non_interactive(maintenance, args)
        else:
            main_interactive(maintenance)
            return 0

    except Exception as e:
        print(f"❌ Error during maintenance: {e}")
        return 1

if __name__ == "__main__":
    exit(main())

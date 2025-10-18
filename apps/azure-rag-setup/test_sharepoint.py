#!/usr/bin/env python3
"""
Comprehensive SharePoint Directory Test Script
Tests authentication, site access, document retrieval, and Azure Storage upload
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from m365_sharepoint_indexer import SharePointIndexer
from m365_auth import M365Auth
from azure.storage.blob import BlobServiceClient
import requests

class SharePointTest:
    """Comprehensive SharePoint testing suite"""

    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'passed': 0,
            'failed': 0,
            'warnings': 0
        }

    def add_test(self, name: str, status: str, message: str, details: Dict = None):
        """Add test result"""
        test_result = {
            'name': name,
            'status': status,  # 'pass', 'fail', 'warning'
            'message': message,
            'details': details or {}
        }
        self.results['tests'].append(test_result)

        if status == 'pass':
            self.results['passed'] += 1
        elif status == 'fail':
            self.results['failed'] += 1
        else:
            self.results['warnings'] += 1

    def print_result(self, status: str, name: str, message: str):
        """Print formatted test result"""
        icons = {'pass': '✅', 'fail': '❌', 'warning': '⚠️'}
        icon = icons.get(status, '❓')
        print(f"{icon} {name}: {message}")

    def test_environment_variables(self) -> bool:
        """Test 1: Verify all required environment variables"""
        print("\n" + "="*60)
        print("TEST 1: Environment Variables")
        print("="*60)

        required_vars = {
            'M365': ['M365_CLIENT_ID', 'M365_CLIENT_SECRET', 'M365_TENANT_ID'],
            'Azure Storage': ['AZURE_STORAGE_ACCOUNT_NAME', 'AZURE_STORAGE_ACCOUNT_KEY']
        }

        all_present = True
        for category, vars in required_vars.items():
            print(f"\n{category}:")
            for var in vars:
                value = os.getenv(var)
                if value:
                    masked = value[:8] + "..." if len(value) > 8 else "***"
                    self.print_result('pass', var, f"Set ({masked})")
                else:
                    self.print_result('fail', var, "Not set")
                    all_present = False

        if all_present:
            self.add_test('Environment Variables', 'pass', 'All required variables set')
        else:
            self.add_test('Environment Variables', 'fail', 'Missing required variables')

        return all_present

    def test_authentication(self) -> bool:
        """Test 2: Verify M365 authentication"""
        print("\n" + "="*60)
        print("TEST 2: M365 Authentication")
        print("="*60)

        try:
            auth = M365Auth()

            # Test credential validation
            if not auth.validate_credentials():
                self.print_result('fail', 'Credentials', 'Validation failed')
                self.add_test('M365 Authentication', 'fail', 'Credential validation failed')
                return False

            self.print_result('pass', 'Credentials', 'Valid')

            # Test token acquisition
            token = auth.get_access_token()
            if not token:
                self.print_result('fail', 'Token', 'Failed to acquire')
                self.add_test('M365 Authentication', 'fail', 'Token acquisition failed')
                return False

            self.print_result('pass', 'Token', f'Acquired ({token[:20]}...)')

            # Test Graph API headers
            headers = auth.get_graph_headers()
            if not headers or 'Authorization' not in headers:
                self.print_result('fail', 'Headers', 'Invalid format')
                self.add_test('M365 Authentication', 'fail', 'Invalid headers')
                return False

            self.print_result('pass', 'Headers', 'Valid format')

            self.add_test('M365 Authentication', 'pass', 'All authentication checks passed')
            return True

        except Exception as e:
            self.print_result('fail', 'Authentication', str(e))
            self.add_test('M365 Authentication', 'fail', f'Exception: {e}')
            return False

    def test_sharepoint_access(self, auth: M365Auth) -> Dict[str, Any]:
        """Test 3: Verify SharePoint site access"""
        print("\n" + "="*60)
        print("TEST 3: SharePoint Site Access")
        print("="*60)

        try:
            headers = auth.get_graph_headers()

            # Get list of SharePoint sites
            response = requests.get(
                'https://graph.microsoft.com/v1.0/sites?search=*',
                headers=headers,
                timeout=30
            )

            if response.status_code != 200:
                self.print_result('fail', 'Site List', f'HTTP {response.status_code}')
                self.add_test('SharePoint Access', 'fail', f'Failed to list sites: {response.status_code}')
                return {}

            sites_data = response.json()
            sites = sites_data.get('value', [])

            if not sites:
                self.print_result('warning', 'Site List', 'No sites found')
                self.add_test('SharePoint Access', 'warning', 'No SharePoint sites accessible')
                return {}

            self.print_result('pass', 'Site List', f'{len(sites)} sites found')

            # Display site information
            site_info = {}
            for i, site in enumerate(sites, 1):
                site_name = site.get('displayName', 'Unknown')
                site_id = site.get('id', '')
                web_url = site.get('webUrl', '')

                print(f"\n   Site {i}: {site_name}")
                print(f"      ID: {site_id[:50]}...")
                print(f"      URL: {web_url}")

                site_info[site_id] = {
                    'name': site_name,
                    'url': web_url,
                    'id': site_id
                }

            self.add_test('SharePoint Access', 'pass', f'{len(sites)} sites accessible',
                         {'site_count': len(sites), 'sites': list(site_info.keys())})

            return site_info

        except Exception as e:
            self.print_result('fail', 'SharePoint Access', str(e))
            self.add_test('SharePoint Access', 'fail', f'Exception: {e}')
            return {}

    def test_azure_storage(self) -> bool:
        """Test 4: Verify Azure Storage connectivity"""
        print("\n" + "="*60)
        print("TEST 4: Azure Storage Connection")
        print("="*60)

        try:
            account_name = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
            account_key = os.getenv('AZURE_STORAGE_ACCOUNT_KEY')

            if not account_name or not account_key:
                self.print_result('fail', 'Credentials', 'Missing storage credentials')
                self.add_test('Azure Storage', 'fail', 'Missing credentials')
                return False

            connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"

            blob_service = BlobServiceClient.from_connection_string(connection_string)

            # Test container access
            container_client = blob_service.get_container_client("training-data")

            # List some blobs to verify access
            blob_list = list(container_client.list_blobs(name_starts_with="sharepoint/", max_results=10))

            self.print_result('pass', 'Connection', f'Connected to {account_name}')
            self.print_result('pass', 'Container', f'training-data accessible')
            self.print_result('pass', 'Blobs', f'{len(blob_list)} SharePoint blobs found')

            self.add_test('Azure Storage', 'pass', 'Storage accessible',
                         {'account': account_name, 'blobs_found': len(blob_list)})
            return True

        except Exception as e:
            self.print_result('fail', 'Azure Storage', str(e))
            self.add_test('Azure Storage', 'fail', f'Exception: {e}')
            return False

    def test_progress_file(self) -> Dict[str, Any]:
        """Test 5: Check SharePoint progress file"""
        print("\n" + "="*60)
        print("TEST 5: Progress Tracking")
        print("="*60)

        progress_file = Path("sharepoint_progress.json")

        if not progress_file.exists():
            self.print_result('warning', 'Progress File', 'Not found (no previous runs)')
            self.add_test('Progress Tracking', 'warning', 'No progress file found')
            return {}

        try:
            with open(progress_file, 'r') as f:
                progress = json.load(f)

            last_sync = progress.get('last_sync', 'Never')
            sites = progress.get('sites', {})
            total_docs = progress.get('total_documents', 0)

            self.print_result('pass', 'Progress File', f'Found at {progress_file}')
            print(f"\n   Last Sync: {last_sync}")
            print(f"   Sites Indexed: {len(sites)}")
            print(f"   Total Documents: {total_docs}")

            for site_id, site_data in sites.items():
                site_name = site_data.get('name', 'Unknown')
                docs_found = site_data.get('documents_found', 0)
                docs_processed = site_data.get('documents_processed', 0)
                site_last_sync = site_data.get('last_sync', 'Unknown')

                print(f"\n   📊 {site_name}")
                print(f"      Found: {docs_found} documents")
                print(f"      Processed: {docs_processed} documents")
                print(f"      Last Sync: {site_last_sync}")

            self.add_test('Progress Tracking', 'pass', f'{len(sites)} sites tracked',
                         {'sites': len(sites), 'total_documents': total_docs})

            return progress

        except Exception as e:
            self.print_result('fail', 'Progress File', f'Error reading: {e}')
            self.add_test('Progress Tracking', 'fail', f'Exception: {e}')
            return {}

    def test_document_retrieval(self, site_info: Dict[str, Any]) -> bool:
        """Test 6: Test document retrieval from a site"""
        print("\n" + "="*60)
        print("TEST 6: Document Retrieval")
        print("="*60)

        if not site_info:
            self.print_result('warning', 'Document Retrieval', 'No sites available to test')
            self.add_test('Document Retrieval', 'warning', 'No sites available')
            return False

        try:
            indexer = SharePointIndexer()

            # Test with first available site
            site_id = list(site_info.keys())[0]
            site_name = site_info[site_id]['name']

            print(f"\n   Testing with site: {site_name}")

            # Get documents (without processing)
            auth = M365Auth()
            headers = auth.get_graph_headers()

            # Get drives for the site
            drives_response = requests.get(
                f'https://graph.microsoft.com/v1.0/sites/{site_id}/drives',
                headers=headers,
                timeout=30
            )

            if drives_response.status_code != 200:
                self.print_result('fail', 'Drives', f'HTTP {drives_response.status_code}')
                self.add_test('Document Retrieval', 'fail', f'Failed to get drives: {drives_response.status_code}')
                return False

            drives = drives_response.json().get('value', [])
            self.print_result('pass', 'Drives', f'{len(drives)} found')

            total_files = 0
            for drive in drives[:3]:  # Test first 3 drives
                drive_name = drive.get('name', 'Unknown')
                drive_id = drive.get('id')

                # Get root items
                items_response = requests.get(
                    f'https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children',
                    headers=headers,
                    timeout=30
                )

                if items_response.status_code == 200:
                    items = items_response.json().get('value', [])
                    files = [item for item in items if 'file' in item]
                    total_files += len(files)
                    print(f"   📁 {drive_name}: {len(files)} files")

            self.print_result('pass', 'Files', f'{total_files} files found')
            self.add_test('Document Retrieval', 'pass', f'{total_files} files accessible',
                         {'files_found': total_files, 'drives_checked': len(drives[:3])})

            return True

        except Exception as e:
            self.print_result('fail', 'Document Retrieval', str(e))
            self.add_test('Document Retrieval', 'fail', f'Exception: {e}')
            return False

    def test_indexer_initialization(self) -> bool:
        """Test 7: Verify SharePoint indexer initialization"""
        print("\n" + "="*60)
        print("TEST 7: Indexer Initialization")
        print("="*60)

        try:
            indexer = SharePointIndexer()

            # Check attributes
            if not hasattr(indexer, 'auth'):
                self.print_result('fail', 'Auth', 'Missing auth attribute')
                self.add_test('Indexer Initialization', 'fail', 'Missing auth attribute')
                return False

            self.print_result('pass', 'Auth', 'Initialized')

            if not hasattr(indexer, 'blob_service'):
                self.print_result('fail', 'Blob Service', 'Missing blob service')
                self.add_test('Indexer Initialization', 'fail', 'Missing blob service')
                return False

            self.print_result('pass', 'Blob Service', 'Connected')

            # Check supported extensions
            extensions = indexer.supported_extensions
            self.print_result('pass', 'File Types', f'{len(extensions)} types supported')
            print(f"      Supported: {', '.join(sorted(extensions))}")

            # Check container
            container = indexer.container_client
            self.print_result('pass', 'Container', f'Connected to {container.container_name}')

            self.add_test('Indexer Initialization', 'pass', 'Indexer fully initialized',
                         {'supported_types': len(extensions)})

            return True

        except Exception as e:
            self.print_result('fail', 'Indexer', str(e))
            self.add_test('Indexer Initialization', 'fail', f'Exception: {e}')
            return False

    def generate_report(self):
        """Generate and display final test report"""
        print("\n" + "="*60)
        print("FINAL TEST REPORT")
        print("="*60)

        print(f"\nTest Run: {self.results['timestamp']}")
        print(f"\nResults:")
        print(f"  ✅ Passed:  {self.results['passed']}")
        print(f"  ❌ Failed:  {self.results['failed']}")
        print(f"  ⚠️  Warnings: {self.results['warnings']}")

        total = self.results['passed'] + self.results['failed'] + self.results['warnings']
        if total > 0:
            pass_rate = (self.results['passed'] / total) * 100
            print(f"\n  Pass Rate: {pass_rate:.1f}%")

        print("\n" + "-"*60)
        print("Test Details:")
        print("-"*60)

        for test in self.results['tests']:
            icon = {'pass': '✅', 'fail': '❌', 'warning': '⚠️'}.get(test['status'], '❓')
            print(f"\n{icon} {test['name']}")
            print(f"   Status: {test['status'].upper()}")
            print(f"   Message: {test['message']}")
            if test['details']:
                print(f"   Details: {json.dumps(test['details'], indent=6)}")

        # Save report to file
        report_file = f"sharepoint_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        print(f"\n📄 Full report saved to: {report_file}")

        return self.results['failed'] == 0

def main():
    """Run all SharePoint tests"""
    print("="*60)
    print("SharePoint Directory Testing Suite")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tester = SharePointTest()

    # Run tests in sequence
    env_ok = tester.test_environment_variables()
    if not env_ok:
        print("\n❌ Environment check failed. Cannot proceed.")
        tester.generate_report()
        return 1

    auth_ok = tester.test_authentication()
    if not auth_ok:
        print("\n❌ Authentication failed. Cannot proceed.")
        tester.generate_report()
        return 1

    # Continue with remaining tests
    auth = M365Auth()
    site_info = tester.test_sharepoint_access(auth)
    tester.test_azure_storage()
    tester.test_progress_file()

    if site_info:
        tester.test_document_retrieval(site_info)

    tester.test_indexer_initialization()

    # Generate final report
    success = tester.generate_report()

    if success:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ {tester.results['failed']} test(s) failed")
        return 1

if __name__ == "__main__":
    exit(main())


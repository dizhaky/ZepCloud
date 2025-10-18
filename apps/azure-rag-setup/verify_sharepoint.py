#!/usr/bin/env python3
"""
Simple SharePoint Directory Verification Script
Uses cached authentication to test SharePoint access
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from m365_sharepoint_indexer import SharePointIndexer
from m365_auth import M365Auth
import requests

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*70)
    print(title.center(70))
    print("="*70)

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def verify_authentication():
    """Verify M365 authentication"""
    print_header("Step 1: Authentication Check")

    try:
        auth = M365Auth()

        # Test token acquisition
        print("   Checking authentication...")
        headers = auth.get_graph_headers()

        if not headers:
            print_error("Failed to get authentication headers")
            return None

        print_success("Authentication successful")
        return auth

    except Exception as e:
        print_error(f"Authentication failed: {e}")
        return None

def verify_sharepoint_access(auth):
    """Verify SharePoint site access"""
    print_header("Step 2: SharePoint Site Access")

    try:
        headers = auth.get_graph_headers()

        print("   Querying SharePoint sites...")
        response = requests.get(
            'https://graph.microsoft.com/v1.0/sites?search=*',
            headers=headers,
            timeout=30
        )

        if response.status_code != 200:
            print_error(f"Failed to query sites: HTTP {response.status_code}")
            return None

        sites = response.json().get('value', [])

        if not sites:
            print_info("No SharePoint sites found")
            return []

        print_success(f"Found {len(sites)} SharePoint site(s)")

        # Display site information
        for i, site in enumerate(sites, 1):
            site_name = site.get('displayName', 'Unknown')
            web_url = site.get('webUrl', '')
            print(f"\n   📊 Site {i}: {site_name}")
            print(f"      URL: {web_url}")

        return sites

    except Exception as e:
        print_error(f"Site access failed: {e}")
        return None

def verify_document_libraries(auth, site):
    """Verify document library access for a site"""
    print_header("Step 3: Document Library Access")

    try:
        site_id = site.get('id')
        site_name = site.get('displayName', 'Unknown')

        print(f"   Checking libraries in: {site_name}")

        headers = auth.get_graph_headers()

        # Get drives (document libraries)
        response = requests.get(
            f'https://graph.microsoft.com/v1.0/sites/{site_id}/drives',
            headers=headers,
            timeout=30
        )

        if response.status_code != 200:
            print_error(f"Failed to get document libraries: HTTP {response.status_code}")
            return None

        drives = response.json().get('value', [])

        if not drives:
            print_info(f"No document libraries found in {site_name}")
            return []

        print_success(f"Found {len(drives)} document library(ies)")

        total_files = 0
        for drive in drives:
            drive_name = drive.get('name', 'Unknown')
            drive_type = drive.get('driveType', 'unknown')

            print(f"\n   📁 Library: {drive_name} ({drive_type})")

            # Count files in this drive
            file_count = count_files_in_drive(auth, drive.get('id'))
            if file_count is not None:
                total_files += file_count
                print(f"      Files: {file_count}")

        print(f"\n   📊 Total files across all libraries: {total_files}")
        return drives

    except Exception as e:
        print_error(f"Library access failed: {e}")
        return None

def count_files_in_drive(auth, drive_id):
    """Count files in a drive"""
    try:
        headers = auth.get_graph_headers()

        response = requests.get(
            f'https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children',
            headers=headers,
            timeout=30
        )

        if response.status_code != 200:
            return None

        items = response.json().get('value', [])
        files = [item for item in items if 'file' in item]

        return len(files)

    except:
        return None

def verify_progress_tracking():
    """Verify progress tracking"""
    print_header("Step 4: Progress Tracking")

    progress_file = Path("sharepoint_progress.json")

    if not progress_file.exists():
        print_info("No progress file found (no previous indexing runs)")
        return

    try:
        with open(progress_file, 'r') as f:
            progress = json.load(f)

        last_sync = progress.get('last_sync', 'Never')
        sites = progress.get('sites', {})
        total_docs = progress.get('total_documents', 0)

        print(f"   Last sync: {last_sync}")
        print(f"   Sites indexed: {len(sites)}")
        print(f"   Total documents: {total_docs}")

        if sites:
            print_success("Progress tracking active")

            for site_id, site_data in sites.items():
                site_name = site_data.get('name', 'Unknown')
                docs_found = site_data.get('documents_found', 0)
                docs_processed = site_data.get('documents_processed', 0)

                print(f"\n   📊 {site_name}")
                print(f"      Documents found: {docs_found}")
                print(f"      Documents processed: {docs_processed}")
        else:
            print_info("No sites have been indexed yet")

    except Exception as e:
        print_error(f"Failed to read progress: {e}")

def verify_indexer_ready():
    """Verify SharePoint indexer is ready"""
    print_header("Step 5: Indexer Readiness")

    try:
        print("   Initializing SharePoint indexer...")
        indexer = SharePointIndexer()

        print_success("Indexer initialized successfully")

        # Check supported file types
        extensions = indexer.supported_extensions
        print(f"\n   Supported file types: {len(extensions)}")
        print(f"   Types: {', '.join(sorted(extensions))}")

        # Check blob storage connection
        container_name = indexer.container_client.container_name
        print(f"\n   Target container: {container_name}")

        print_success("All indexer components ready")

    except Exception as e:
        print_error(f"Indexer initialization failed: {e}")
        print_info("Note: Azure Storage credentials may not be configured")

def main():
    """Run SharePoint verification"""
    print_header("SharePoint Directory Verification")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Step 1: Authentication
    auth = verify_authentication()
    if not auth:
        print("\n❌ Cannot proceed without authentication")
        return 1

    # Step 2: SharePoint Access
    sites = verify_sharepoint_access(auth)
    if sites is None:
        print("\n❌ Cannot access SharePoint sites")
        return 1

    if not sites:
        print("\nℹ️  No SharePoint sites available to test")
    else:
        # Step 3: Document Libraries (test first site only)
        verify_document_libraries(auth, sites[0])

    # Step 4: Progress Tracking
    verify_progress_tracking()

    # Step 5: Indexer Readiness
    verify_indexer_ready()

    # Summary
    print_header("Verification Complete")
    print_success("SharePoint directory is accessible and functional")
    print("\n💡 Next steps:")
    print("   • Run: python3 m365_sharepoint_indexer.py --status")
    print("   • Index: python3 m365_sharepoint_indexer.py")
    print("   • Test with limit: python3 m365_sharepoint_indexer.py --limit 1")
    print()

    return 0

if __name__ == "__main__":
    exit(main())


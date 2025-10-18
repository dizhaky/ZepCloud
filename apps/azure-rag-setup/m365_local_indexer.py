#!/usr/bin/env python3
"""
M365 Local Indexer - Uses local storage instead of Azure
"""

import os
import sys
from pathlib import Path
from local_storage_manager import LocalStorageManager
from m365_auth import M365Auth
import requests
import json
from datetime import datetime

class M365LocalIndexer:
    """M365 indexer using local storage"""

    def __init__(self):
        self.auth = M365Auth()
        self.storage = LocalStorageManager()
        self.headers = self.auth.get_graph_headers()

        if not self.headers:
            raise ValueError("Failed to get authentication headers")

    def index_sharepoint_sites(self):
        """Index SharePoint sites"""
        print("🔍 Starting SharePoint indexing...")

        try:
            # Get all sites
            sites_url = 'https://graph.microsoft.com/v1.0/sites?search=*'
            response = requests.get(sites_url, headers=self.headers)

            if response.status_code == 200:
                sites = response.json().get('value', [])
                print(f"📁 Found {len(sites)} SharePoint sites")

                for site in sites[:5]:  # Limit to first 5 sites for testing
                    site_id = site['id']
                    site_name = site['displayName']
                    print(f"📂 Processing site: {site_name}")

                    # Get site drives
                    drives_url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drives'
                    drives_response = requests.get(drives_url, headers=self.headers)

                    if drives_response.status_code == 200:
                        drives = drives_response.json().get('value', [])
                        print(f"💾 Found {len(drives)} drives in {site_name}")

                        for drive in drives:
                            self._index_drive(drive, site_name)
                    else:
                        print(f"❌ Failed to get drives for {site_name}")
            else:
                print(f"❌ Failed to get SharePoint sites: {response.status_code}")

        except Exception as e:
            print(f"❌ Error indexing SharePoint: {e}")

    def _index_drive(self, drive, site_name):
        """Index a drive (document library)"""
        drive_id = drive['id']
        drive_name = drive['name']

        print(f"📄 Indexing drive: {drive_name}")

        try:
            # Get drive items
            items_url = f'https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children'
            response = requests.get(items_url, headers=self.headers)

            if response.status_code == 200:
                items = response.json().get('value', [])
                print(f"📋 Found {len(items)} items in {drive_name}")

                for item in items:
                    if 'file' in item:  # It's a file
                        self._index_file(item, site_name, drive_name)
                    elif 'folder' in item:  # It's a folder
                        self._index_folder(item, site_name, drive_name)
            else:
                print(f"❌ Failed to get items for {drive_name}")

        except Exception as e:
            print(f"❌ Error indexing drive {drive_name}: {e}")

    def _index_file(self, file_item, site_name, drive_name):
        """Index a file"""
        file_id = file_item['id']
        file_name = file_item['name']
        file_size = file_item.get('size', 0)

        # Skip large files (>10MB)
        if file_size > 10 * 1024 * 1024:
            print(f"⏭️  Skipping large file: {file_name} ({file_size} bytes)")
            return

        print(f"📄 Processing file: {file_name}")

        try:
            # Get file content
            content_url = f'https://graph.microsoft.com/v1.0/drives/{file_item["parentReference"]["driveId"]}/items/{file_id}/content'
            content_response = requests.get(content_url, headers=self.headers)

            if content_response.status_code == 200:
                content = content_response.text

                # Create document metadata
                metadata = {
                    'source': 'sharepoint',
                    'site_name': site_name,
                    'drive_name': drive_name,
                    'file_name': file_name,
                    'file_size': file_size,
                    'created_at': file_item.get('createdDateTime'),
                    'modified_at': file_item.get('lastModifiedDateTime'),
                    'web_url': file_item.get('webUrl'),
                    'file_type': file_item.get('file', {}).get('mimeType', 'unknown')
                }

                # Store in local storage
                document_id = f"sp_{file_id}"
                success = self.storage.store_document(
                    document_id=document_id,
                    source='sharepoint',
                    title=file_name,
                    content=content,
                    metadata=metadata,
                    file_path=f"sharepoint/{site_name}/{file_name}"
                )

                if success:
                    print(f"✅ Stored: {file_name}")
                else:
                    print(f"❌ Failed to store: {file_name}")
            else:
                print(f"❌ Failed to get content for {file_name}")

        except Exception as e:
            print(f"❌ Error processing file {file_name}: {e}")

    def _index_folder(self, folder_item, site_name, drive_name):
        """Index a folder (recursive)"""
        folder_id = folder_item['id']
        folder_name = folder_item['name']

        print(f"📁 Processing folder: {folder_name}")

        try:
            # Get folder items
            items_url = f'https://graph.microsoft.com/v1.0/drives/{folder_item["parentReference"]["driveId"]}/items/{folder_id}/children'
            response = requests.get(items_url, headers=self.headers)

            if response.status_code == 200:
                items = response.json().get('value', [])
                print(f"📋 Found {len(items)} items in folder {folder_name}")

                for item in items:
                    if 'file' in item:
                        self._index_file(item, site_name, drive_name)
                    elif 'folder' in item:
                        self._index_folder(item, site_name, drive_name)
            else:
                print(f"❌ Failed to get items for folder {folder_name}")

        except Exception as e:
            print(f"❌ Error processing folder {folder_name}: {e}")

    def get_stats(self):
        """Get indexing statistics"""
        stats = self.storage.get_storage_stats()
        print(f"\n📊 Indexing Statistics:")
        print(f"   Total documents: {stats.get('total_documents', 0)}")
        print(f"   SharePoint documents: {stats.get('sharepoint_documents', 0)}")
        print(f"   Storage size: {stats.get('storage_size_mb', 0)} MB")
        print(f"   Storage path: {stats.get('storage_path', 'unknown')}")

def main():
    """Main function"""
    print("🚀 M365 Local Indexer Starting...")
    print("=" * 50)

    try:
        # Test authentication
        if not M365Auth().test_connection():
            print("❌ Authentication failed")
            return 1

        print("✅ Authentication successful")

        # Create indexer
        indexer = M365LocalIndexer()

        # Start indexing
        indexer.index_sharepoint_sites()

        # Show stats
        indexer.get_stats()

        print("\n✅ M365 Local Indexing Complete!")
        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())

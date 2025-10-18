#!/usr/bin/env python3
"""
Microsoft 365 SharePoint Indexer
Downloads and indexes SharePoint documents to Azure Blob Storage
"""

# Standard library imports
import os
import json
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# Third-party imports
import requests
from azure.storage.blob import BlobServiceClient
from tenacity import retry, stop_after_attempt, wait_exponential
from tqdm import tqdm

# Local application imports
from config_manager import get_config_manager
from logger import setup_logging
from m365_auth import M365Auth

class SharePointIndexer:
    """Index SharePoint documents to Azure Blob Storage"""

    def __init__(self, progress_file: str = None):
        self.config = get_config_manager()
        self.logger = setup_logging('sharepoint-indexer', level='INFO')
        self.auth = M365Auth()

        # Use config manager for progress file
        self.progress_file = Path(progress_file or self.config.get_progress_file('sharepoint'))
        self.progress = self._load_progress()

        # Azure Blob Storage setup
        self.connection_string = self.config.get_connection_string()
        self.blob_service = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.blob_service.get_container_client(
            self.config.get_azure_storage_config().get('container_name', 'training-data')
        )

        # Supported file types from config
        self.supported_extensions = set(self.config.get_supported_file_extensions('sharepoint'))

        # Statistics
        self.stats = {
            'sites_processed': 0,
            'documents_found': 0,
            'documents_uploaded': 0,
            'documents_skipped': 0,
            'errors': 0,
            'start_time': datetime.now()
        }

    def _load_progress(self) -> Dict[str, Any]:
        """Load progress tracking data"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                    # Convert processed_documents list back to set
                    if 'processed_documents' in data and isinstance(data['processed_documents'], list):
                        data['processed_documents'] = set(data['processed_documents'])
                    return data
            except Exception as e:
                self.logger.warning(f"Error loading progress: {e}")

        return {
            'last_sync': None,
            'sites': {},
            'total_documents': 0,
            'total_size_bytes': 0,
            'processed_documents': set()
        }

    def _save_progress(self):
        """Save progress tracking data"""
        try:
            # Convert set to list for JSON serialization
            progress_copy = self.progress.copy()
            if 'processed_documents' in progress_copy and isinstance(progress_copy['processed_documents'], set):
                progress_copy['processed_documents'] = list(progress_copy['processed_documents'])

            with open(self.progress_file, 'w') as f:
                json.dump(progress_copy, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Error saving progress: {e}")


    def _get_file_extension(self, filename: str) -> str:
        """Get file extension in lowercase"""
        return Path(filename).suffix.lower()

    def _is_supported_file(self, filename: str) -> bool:
        """Check if file type is supported for indexing"""
        return self._get_file_extension(filename) in self.supported_extensions

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True
    )
    def _download_file(self, download_url: str, timeout: int = 300) -> bytes:
        """Download file content with retry logic"""
        headers = self.auth.get_graph_headers()
        if not headers:
            raise Exception("Authentication failed")

        response = requests.get(download_url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.content

    def _upload_to_blob(self, content: bytes, blob_name: str, metadata: Dict[str, str] = None) -> bool:
        """Upload content to Azure Blob Storage"""
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_client.upload_blob(
                content,
                overwrite=True,
                metadata=metadata or {},
                timeout=300
            )
            return True
        except Exception as e:
            self.logger.error(f"Upload failed for {blob_name}: {e}")
            return False

    def _get_site_documents(self, site_id: str, site_name: str) -> List[Dict[str, Any]]:
        """Get all documents from a SharePoint site"""
        headers = self.auth.get_graph_headers()
        if not headers:
            return []

        documents = []

        try:
            # Get all drives (document libraries) in the site
            drives_response = requests.get(
                f'https://graph.microsoft.com/v1.0/sites/{site_id}/drives',
                headers=headers,
                timeout=30
            )

            if drives_response.status_code != 200:
                self.logger.warning(f"Failed to get drives for site {site_name}: {drives_response.status_code}")
                return []

            drives_data = drives_response.json()
            drives = drives_data.get('value', [])

            for drive in drives:
                drive_id = drive.get('id')
                drive_name = drive.get('name', 'Unknown')

                self.logger.info(f"Processing drive: {drive_name}")

                # Get all files in this drive
                files = self._get_drive_files(drive_id, drive_name, site_name)
                documents.extend(files)

        except Exception as e:
            self.logger.error(f"Error processing site {site_name}: {e}")
            self.stats['errors'] += 1

        return documents

    def _get_drive_files(self, drive_id: str, drive_name: str, site_name: str) -> List[Dict[str, Any]]:
        """Get all files from a drive (document library)"""
        headers = self.auth.get_graph_headers()
        if not headers:
            return []

        files = []

        try:
            # Get root folder and all subfolders recursively
            files.extend(self._get_folder_files(drive_id, "root", f"{site_name}/{drive_name}"))

        except Exception as e:
            self.logger.error(f"Error processing drive {drive_name}: {e}")
            self.stats['errors'] += 1

        return files

    def _get_folder_files(self, drive_id: str, folder_id: str, folder_path: str, retry_count: int = 0, max_retries: int = 5) -> List[Dict[str, Any]]:
        """Recursively get all files from a folder with retry logic for rate limiting"""
        headers = self.auth.get_graph_headers()
        if not headers:
            return []

        files = []

        try:
            # Get folder contents
            if folder_id == "root":
                url = f'https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children'
            else:
                url = f'https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{folder_id}/children'

            response = requests.get(url, headers=headers, timeout=30)

            # Handle rate limiting (429) with exponential backoff
            if response.status_code == 429:
                if retry_count < max_retries:
                    # Get retry-after header or use exponential backoff
                    retry_after = int(response.headers.get('Retry-After', 2 ** retry_count))
                    self.logger.warning(f"Rate limited on {folder_path}. Waiting {retry_after}s before retry {retry_count + 1}/{max_retries}")
                    time.sleep(retry_after)
                    # Retry with incremented count
                    return self._get_folder_files(drive_id, folder_id, folder_path, retry_count + 1, max_retries)
                else:
                    self.logger.warning(f"Max retries reached for folder {folder_path}. Skipping.")
                    return []

            if response.status_code != 200:
                return []

            data = response.json()
            items = data.get('value', [])

            for item in items:
                if 'file' in item:
                    # It's a file
                    filename = item.get('name', '')

                    if self._is_supported_file(filename):
                        file_info = {
                            'id': item.get('id'),
                            'name': filename,
                            'size': item.get('size', 0),
                            'modified': item.get('lastModifiedDateTime'),
                            'created': item.get('createdDateTime'),
                            'web_url': item.get('webUrl'),
                            'download_url': item.get('@microsoft.graph.downloadUrl'),
                            'folder_path': folder_path,
                            'site_name': folder_path.split('/')[0] if '/' in folder_path else 'Unknown'
                        }
                        files.append(file_info)

                elif 'folder' in item:
                    # It's a folder, recurse
                    subfolder_id = item.get('id')
                    subfolder_name = item.get('name', '')
                    subfolder_path = f"{folder_path}/{subfolder_name}"

                    subfolder_files = self._get_folder_files(drive_id, subfolder_id, subfolder_path)
                    files.extend(subfolder_files)

        except Exception as e:
            self.logger.warning(f"Error processing folder {folder_path}: {e}")

        return files

    def _process_document(self, doc: Dict[str, Any]) -> bool:
        """Process a single document (download and upload)"""
        try:
            # Generate blob name
            site_name = doc['site_name']
            folder_path = doc['folder_path']
            filename = doc['name']

            # Clean up path for blob storage
            clean_site = site_name.replace(' ', '_').replace('/', '_')
            clean_folder = folder_path.replace(' ', '_').replace('/', '_')
            blob_name = f"sharepoint/{clean_site}/{clean_folder}/{filename}"

            # Check if already processed
            if self._is_document_processed(doc['id']):
                self.stats['documents_skipped'] += 1
                return True

            # Download file
            if not doc.get('download_url'):
                self.logger.warning(f"No download URL for {filename}")
                return False

            self.logger.info(f"Downloading: {filename}")
            content = self._download_file(doc['download_url'])

            # Prepare metadata
            metadata = {
                'source': 'sharepoint',
                'site_name': site_name,
                'folder_path': folder_path,
                'original_name': filename,
                'file_size': str(doc['size']),
                'modified_date': doc.get('modified', ''),
                'created_date': doc.get('created', ''),
                'web_url': doc.get('web_url', ''),
                'indexed_at': datetime.now().isoformat()
            }

            # Upload to blob storage
            if self._upload_to_blob(content, blob_name, metadata):
                self._mark_document_processed(doc['id'])
                self.stats['documents_uploaded'] += 1
                return True
            else:
                self.stats['errors'] += 1
                return False

        except Exception as e:
            self.logger.error(f"Error processing {doc.get('name', 'unknown')}: {e}")
            self.stats['errors'] += 1
            return False

    def _is_document_processed(self, doc_id: str) -> bool:
        """Check if document has already been processed"""
        return doc_id in self.progress.get('processed_documents', set())

    def _mark_document_processed(self, doc_id: str):
        """Mark document as processed"""
        if 'processed_documents' not in self.progress:
            self.progress['processed_documents'] = set()
        self.progress['processed_documents'].add(doc_id)

    def index_site(self, site_id: str, site_name: str) -> Dict[str, Any]:
        """Index all documents from a specific SharePoint site"""
        self.logger.info(f"Indexing site: {site_name}")

        start_time = datetime.now()
        documents = self._get_site_documents(site_id, site_name)

        if not documents:
            self.logger.info(f"No documents found in {site_name}")
            return {'success': True, 'documents': 0}

        self.logger.info(f"Found {len(documents)} documents")

        # Process documents with progress bar
        processed = 0
        for doc in tqdm(documents, desc=f"Processing {site_name}"):
            if self._process_document(doc):
                processed += 1

        # Update progress
        self.progress['sites'][site_id] = {
            'name': site_name,
            'last_sync': datetime.now().isoformat(),
            'documents_found': len(documents),
            'documents_processed': processed
        }

        self._save_progress()

        duration = datetime.now() - start_time
        self.logger.info(f"Completed {site_name}: {processed}/{len(documents)} documents in {duration}")

        return {
            'success': True,
            'documents': len(documents),
            'processed': processed,
            'duration': str(duration)
        }

    def index_all_sites(self, limit: int = None) -> Dict[str, Any]:
        """Index documents from all SharePoint sites"""
        self.logger.info("Starting SharePoint indexing...")

        headers = self.auth.get_graph_headers()
        if not headers:
            return {'error': 'Authentication failed'}

        try:
            # Get all SharePoint sites
            sites_response = requests.get(
                'https://graph.microsoft.com/v1.0/sites?search=*',
                headers=headers,
                timeout=30
            )

            if sites_response.status_code != 200:
                return {'error': f'Failed to get sites: {sites_response.status_code}'}

            sites_data = sites_response.json()
            sites = sites_data.get('value', [])

            if limit:
                sites = sites[:limit]

            self.logger.info(f"Found {len(sites)} SharePoint sites")

            results = []
            for site in sites:
                site_id = site.get('id')
                site_name = site.get('displayName', 'Unknown')

                result = self.index_site(site_id, site_name)
                results.append({
                    'site_name': site_name,
                    'site_id': site_id,
                    **result
                })

                self.stats['sites_processed'] += 1
                self.stats['documents_found'] += result.get('documents', 0)

            # Update overall progress
            self.progress['last_sync'] = datetime.now().isoformat()
            self.progress['total_documents'] = self.stats['documents_found']
            self._save_progress()

            return {
                'success': True,
                'sites_processed': self.stats['sites_processed'],
                'total_documents': self.stats['documents_found'],
                'documents_uploaded': self.stats['documents_uploaded'],
                'documents_skipped': self.stats['documents_skipped'],
                'errors': self.stats['errors'],
                'duration': str(datetime.now() - self.stats['start_time']),
                'site_results': results
            }

        except Exception as e:
            return {'error': f'Indexing failed: {e}'}

    def get_status(self) -> Dict[str, Any]:
        """Get current indexing status"""
        return {
            'last_sync': self.progress.get('last_sync'),
            'sites_processed': len(self.progress.get('sites', {})),
            'total_documents': self.progress.get('total_documents', 0),
            'processed_documents': len(self.progress.get('processed_documents', set())),
            'current_stats': self.stats
        }

def main():
    """CLI interface for SharePoint indexer"""
    import argparse

    parser = argparse.ArgumentParser(description='SharePoint Document Indexer')
    parser.add_argument('--site', help='Index specific site by ID')
    parser.add_argument('--limit', type=int, help='Limit number of sites to process')
    parser.add_argument('--status', action='store_true', help='Show indexing status')

    args = parser.parse_args()

    indexer = SharePointIndexer()

    if args.status:
        status = indexer.get_status()
        print("📊 SharePoint Indexing Status:")
        print(f"   Last Sync: {status.get('last_sync', 'Never')}")
        print(f"   Sites Processed: {status.get('sites_processed', 0)}")
        print(f"   Total Documents: {status.get('total_documents', 0)}")
        print(f"   Processed Documents: {status.get('processed_documents', 0)}")
        return 0

    if args.site:
        # Index specific site
        result = indexer.index_site(args.site, f"Site-{args.site}")
        print(f"Result: {result}")
    else:
        # Index all sites
        result = indexer.index_all_sites(args.limit)

        if result.get('success'):
            print(f"\n✅ SharePoint indexing completed!")
            print(f"   Sites: {result['sites_processed']}")
            print(f"   Documents: {result['total_documents']}")
            print(f"   Uploaded: {result['documents_uploaded']}")
            print(f"   Skipped: {result['documents_skipped']}")
            print(f"   Errors: {result['errors']}")
            print(f"   Duration: {result['duration']}")
        else:
            print(f"❌ Indexing failed: {result.get('error')}")
            return 1

    return 0

if __name__ == "__main__":
    exit(main())

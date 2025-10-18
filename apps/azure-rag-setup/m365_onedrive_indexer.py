#!/usr/bin/env python3
"""
Microsoft 365 OneDrive Indexer
Downloads and indexes OneDrive documents for all users to Azure Blob Storage
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

class OneDriveIndexer:
    """Index OneDrive documents for all users to Azure Blob Storage"""

    def __init__(self, progress_file: str = None):
        self.config = get_config_manager()
        self.logger = setup_logging('onedrive-indexer', level='INFO')
        self.auth = M365Auth()

        # Use config manager for progress file
        self.progress_file = Path(progress_file or self.config.get_progress_file('onedrive'))
        self.progress = self._load_progress()

        # Azure Blob Storage setup
        self.connection_string = self.config.get_connection_string()
        self.blob_service = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.blob_service.get_container_client(
            self.config.get_azure_storage_config().get('container_name', 'training-data')
        )

        # Supported file types from config
        self.supported_extensions = set(self.config.get_supported_file_extensions('onedrive'))

        # Statistics
        self.stats = {
            'users_processed': 0,
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
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Error loading progress: {e}")

        return {
            'last_sync': None,
            'users': {},
            'total_documents': 0,
            'total_size_bytes': 0
        }

    def _save_progress(self):
        """Save progress tracking data"""
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress, f, indent=2)
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

    def _get_user_documents(self, user_id: str, user_name: str) -> List[Dict[str, Any]]:
        """Get all documents from a user's OneDrive"""
        headers = self.auth.get_graph_headers()
        if not headers:
            return []

        documents = []

        try:
            # Get user's OneDrive
            onedrive_response = requests.get(
                f'https://graph.microsoft.com/v1.0/users/{user_id}/drive',
                headers=headers,
                timeout=30
            )

            if onedrive_response.status_code != 200:
                self.logger.warning(f"Failed to get OneDrive for user {user_name}: {onedrive_response.status_code}")
                return []

            drive_data = onedrive_response.json()
            drive_id = drive_data.get('id')

            self.logger.info(f"Processing OneDrive for: {user_name}")

            # Get all files in OneDrive root and subfolders
            files = self._get_drive_files(drive_id, user_name)
            documents.extend(files)

        except Exception as e:
            self.logger.error(f"Error processing user {user_name}: {e}")
            self.stats['errors'] += 1

        return documents

    def _get_drive_files(self, drive_id: str, user_name: str) -> List[Dict[str, Any]]:
        """Get all files from a OneDrive"""
        headers = self.auth.get_graph_headers()
        if not headers:
            return []

        files = []

        try:
            # Get root folder and all subfolders recursively
            files.extend(self._get_folder_files(drive_id, "root", user_name, ""))

        except Exception as e:
            self.logger.error(f"Error processing OneDrive for {user_name}: {e}")
            self.stats['errors'] += 1

        return files

    def _get_folder_files(self, drive_id: str, folder_id: str, user_name: str, folder_path: str) -> List[Dict[str, Any]]:
        """Recursively get all files from a folder"""
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
                            'user_name': user_name
                        }
                        files.append(file_info)

                elif 'folder' in item:
                    # It's a folder, recurse
                    subfolder_id = item.get('id')
                    subfolder_name = item.get('name', '')
                    subfolder_path = f"{folder_path}/{subfolder_name}" if folder_path else subfolder_name

                    subfolder_files = self._get_folder_files(drive_id, subfolder_id, user_name, subfolder_path)
                    files.extend(subfolder_files)

        except Exception as e:
            self.logger.warning(f"Error processing folder {folder_path} for {user_name}: {e}")

        return files

    def _process_document(self, doc: Dict[str, Any]) -> bool:
        """Process a single document (download and upload)"""
        try:
            # Generate blob name
            user_name = doc['user_name']
            folder_path = doc['folder_path']
            filename = doc['name']

            # Clean up path for blob storage
            clean_user = user_name.replace(' ', '_').replace('/', '_')
            clean_folder = folder_path.replace(' ', '_').replace('/', '_') if folder_path else 'root'
            blob_name = f"onedrive/{clean_user}/{clean_folder}/{filename}"

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
                'source': 'onedrive',
                'user_name': user_name,
                'folder_path': folder_path,
                'original_name': filename,
                'file_size': str(doc['size']),
                'modified_date': doc.get('modified', ''),
                'created_date': doc.get('created', ''),
                'web_url': doc.get('webUrl', ''),
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

    def index_user(self, user_id: str, user_name: str) -> Dict[str, Any]:
        """Index all documents from a specific user's OneDrive"""
        self.logger.info(f"Indexing OneDrive for: {user_name}")

        start_time = datetime.now()
        documents = self._get_user_documents(user_id, user_name)

        if not documents:
            self.logger.info(f"No documents found for {user_name}")
            return {'success': True, 'documents': 0}

        self.logger.info(f"Found {len(documents)} documents")

        # Process documents with progress bar
        processed = 0
        for doc in tqdm(documents, desc=f"Processing {user_name}"):
            if self._process_document(doc):
                processed += 1

        # Update progress
        self.progress['users'][user_id] = {
            'name': user_name,
            'last_sync': datetime.now().isoformat(),
            'documents_found': len(documents),
            'documents_processed': processed
        }

        self._save_progress()

        duration = datetime.now() - start_time
        self.logger.info(f"Completed {user_name}: {processed}/{len(documents)} documents in {duration}")

        return {
            'success': True,
            'documents': len(documents),
            'processed': processed,
            'duration': str(duration)
        }

    def index_all_users(self, limit: int = None) -> Dict[str, Any]:
        """Index documents from all users' OneDrive"""
        self.logger.info("Starting OneDrive indexing for all users...")

        headers = self.auth.get_graph_headers()
        if not headers:
            return {'error': 'Authentication failed'}

        try:
            # Get all users in the organization
            users_response = requests.get(
                'https://graph.microsoft.com/v1.0/users?$select=id,displayName,userPrincipalName',
                headers=headers,
                timeout=30
            )

            if users_response.status_code != 200:
                return {'error': f'Failed to get users: {users_response.status_code}'}

            users_data = users_response.json()
            users = users_data.get('value', [])

            if limit:
                users = users[:limit]

            self.logger.info(f"Found {len(users)} users")

            results = []
            for user in users:
                user_id = user.get('id')
                user_name = user.get('displayName', user.get('userPrincipalName', 'Unknown'))

                result = self.index_user(user_id, user_name)
                results.append({
                    'user_name': user_name,
                    'user_id': user_id,
                    **result
                })

                self.stats['users_processed'] += 1
                self.stats['documents_found'] += result.get('documents', 0)

            # Update overall progress
            self.progress['last_sync'] = datetime.now().isoformat()
            self.progress['total_documents'] = self.stats['documents_found']
            self._save_progress()

            return {
                'success': True,
                'users_processed': self.stats['users_processed'],
                'total_documents': self.stats['documents_found'],
                'documents_uploaded': self.stats['documents_uploaded'],
                'documents_skipped': self.stats['documents_skipped'],
                'errors': self.stats['errors'],
                'duration': str(datetime.now() - self.stats['start_time']),
                'user_results': results
            }

        except Exception as e:
            return {'error': f'Indexing failed: {e}'}

    def get_status(self) -> Dict[str, Any]:
        """Get current indexing status"""
        return {
            'last_sync': self.progress.get('last_sync'),
            'users_processed': len(self.progress.get('users', {})),
            'total_documents': self.progress.get('total_documents', 0),
            'processed_documents': len(self.progress.get('processed_documents', set())),
            'current_stats': self.stats
        }

def main():
    """CLI interface for OneDrive indexer"""
    import argparse

    parser = argparse.ArgumentParser(description='OneDrive Document Indexer')
    parser.add_argument('--user', help='Index specific user by ID')
    parser.add_argument('--limit', type=int, help='Limit number of users to process')
    parser.add_argument('--status', action='store_true', help='Show indexing status')

    args = parser.parse_args()

    indexer = OneDriveIndexer()

    if args.status:
        status = indexer.get_status()
        print("📊 OneDrive Indexing Status:")
        print(f"   Last Sync: {status.get('last_sync', 'Never')}")
        print(f"   Users Processed: {status.get('users_processed', 0)}")
        print(f"   Total Documents: {status.get('total_documents', 0)}")
        print(f"   Processed Documents: {status.get('processed_documents', 0)}")
        return 0

    if args.user:
        # Index specific user
        result = indexer.index_user(args.user, f"User-{args.user}")
        print(f"Result: {result}")
    else:
        # Index all users
        result = indexer.index_all_users(args.limit)

        if result.get('success'):
            print(f"\n✅ OneDrive indexing completed!")
            print(f"   Users: {result['users_processed']}")
            print(f"   Documents: {result['total_documents']}")
            print(f"   Uploaded: {result['documents_uploaded']}")
            print(f"   Skipped: {result['documents_skipped']}")
            print(f"   Errors: {result['errors']}")
            print(f"   Duration: {result['duration']}")
        else:
            print(f"❌ OneDrive indexing failed: {result.get('error')}")
            return 1

    return 0

if __name__ == "__main__":
    exit(main())

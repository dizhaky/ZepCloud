#!/usr/bin/env python3
"""
Microsoft 365 OneDrive Indexer - Adapted for Hetzner
Downloads and indexes OneDrive files to MinIO + Elasticsearch
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import asyncio

import requests  # type: ignore
from tenacity import retry, stop_after_attempt, wait_exponential
from tqdm import tqdm  # type: ignore
from elasticsearch import AsyncElasticsearch  # type: ignore

from config_manager import get_config_manager
from logger import setup_logging
from m365_auth import M365Auth
from storage_adapter import MinIOAdapter, ElasticsearchAdapter


class OneDriveIndexer:
    """Index OneDrive documents to MinIO and Elasticsearch"""

    def __init__(self, progress_file: Optional[str] = None):
        self.config = get_config_manager()
        self.logger = setup_logging('onedrive-indexer', level='INFO')
        self.auth = M365Auth()

        # Progress tracking
        progress_path = (
            progress_file or self.config.get_progress_file('onedrive')
        )
        self.progress_file = Path(progress_path)
        self.progress = self._load_progress()

        # Storage
        self.storage = MinIOAdapter()
        self.es_client: Optional[AsyncElasticsearch] = None
        self.es_adapter: Optional[ElasticsearchAdapter] = None

        # Supported file types
        extensions = self.config.get_supported_file_extensions('onedrive')
        self.supported_extensions = set(extensions)

        # Statistics
        self.stats: Dict = {
            'users_processed': 0,
            'documents_found': 0,
            'documents_uploaded': 0,
            'documents_skipped': 0,
            'errors': 0
        }

    def _load_progress(self) -> Dict:
        """Load progress from file"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Could not load progress file: {e}")
        return {'indexed_documents': {}, 'last_sync': None}

    def _save_progress(self):
        """Save progress to file"""
        try:
            self.progress_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save progress: {e}")

    async def initialize_elasticsearch(self):
        """Initialize Elasticsearch client"""
        es_config = self.config.get_elasticsearch_config()
        self.es_client = AsyncElasticsearch(
            hosts=[f"http://{es_config['host']}:{es_config['port']}"],
            basic_auth=(es_config['user'], es_config['password']),
            verify_certs=False
        )
        self.es_adapter = ElasticsearchAdapter(self.es_client)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def _make_graph_request(
        self, url: str, params: Optional[Dict] = None
    ) -> Dict:
        """Make authenticated request to Microsoft Graph API"""
        headers = self.auth.get_graph_headers()
        if not headers:
            raise ValueError("Failed to get authentication headers")

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_all_users(self) -> List[Dict]:
        """Get all users in the organization"""
        self.logger.info("Fetching all users...")

        users = []
        url: Optional[str] = "https://graph.microsoft.com/v1.0/users"

        while url:
            try:
                data = self._make_graph_request(url)
                users.extend(data.get('value', []))
                next_link = data.get('@odata.nextLink')
                url = str(next_link) if next_link else None
            except Exception as e:
                self.logger.error(f"Error fetching users: {e}")
                break

        self.logger.info(f"Found {len(users)} users")
        return users

    def get_user_files(
        self, user_id: str, path: str = "root"
    ) -> List[Dict]:
        """Get all files from a user's OneDrive"""
        items = []

        base = "https://graph.microsoft.com/v1.0/users"
        url: Optional[str] = f"{base}/{user_id}/drive/{path}/children"

        while url:
            try:
                data = self._make_graph_request(url)

                for item in data.get('value', []):
                    # Check if it's a file
                    if 'file' in item:
                        name = str(item.get('name', ''))
                        ext = Path(name).suffix.lower()

                        if ext in self.supported_extensions:
                            items.append(item)

                    # If folder, recurse
                    elif 'folder' in item:
                        folder_id = item['id']
                        folder_path = f"items/{folder_id}"
                        folder_items = self.get_user_files(
                            user_id, folder_path
                        )
                        items.extend(folder_items)

                next_link = data.get('@odata.nextLink')
                url = str(next_link) if next_link else None

            except Exception as e:
                error_msg = f"Error getting files for user {user_id}: {e}"
                self.logger.error(error_msg)
                break

        return items

    async def process_file(self, file: Dict, user_email: str) -> bool:
        """Download and index a single file"""
        file_id = file['id']
        file_name = file.get('name', 'Unknown')

        # Check if already indexed
        if file_id in self.progress['indexed_documents']:
            last_modified = file.get('lastModifiedDateTime')
            indexed_file = self.progress['indexed_documents'][file_id]
            if last_modified and last_modified == indexed_file.get(
                'last_modified'
            ):
                self.logger.debug(f"Skipping unchanged file: {file_name}")
                self.stats['documents_skipped'] += 1
                return True

        try:
            # Download file
            download_url = file.get('@microsoft.graph.downloadUrl')
            if not download_url:
                self.logger.warning(f"No download URL for {file_name}")
                return False

            self.logger.info(f"Processing: {file_name}")

            temp_path = f"/tmp/{file_id}_{file_name}"
            response = requests.get(download_url)
            response.raise_for_status()

            with open(temp_path, 'wb') as f:
                f.write(response.content)

            # Upload to MinIO
            blob_name = f"onedrive/{user_email}/{file_name}"
            metadata = {
                'm365_id': file_id,
                'source': 'onedrive',
                'user_email': user_email,
                'file_name': file_name,
                'file_size': str(file.get('size', 0)),
                'created': file.get('createdDateTime'),
                'modified': file.get('lastModifiedDateTime')
            }

            if self.storage.upload_file(temp_path, blob_name, metadata):
                self.logger.info(f"✅ Uploaded to MinIO: {blob_name}")

                # Index to Elasticsearch
                es_doc = {
                    'doc_id': file_id,
                    'title': file_name,
                    'content': '',
                    'metadata': metadata,
                    'has_images': False,
                    'has_tables': False,
                    'indexed_at': datetime.utcnow().isoformat()
                }

                if self.es_adapter and await self.es_adapter.index_document(
                    file_id, es_doc
                ):
                    log_msg = f"✅ Indexed to Elasticsearch: {file_name}"
                    self.logger.info(log_msg)

                    self.progress['indexed_documents'][file_id] = {
                        'name': file_name,
                        'last_modified': file.get('lastModifiedDateTime'),
                        'indexed_at': datetime.utcnow().isoformat()
                    }
                    self._save_progress()

                    self.stats['documents_uploaded'] += 1
                    os.remove(temp_path)
                    return True

            return False

        except Exception as e:
            self.logger.error(f"Error processing {file_name}: {e}")
            self.stats['errors'] += 1
            return False

    async def index_user(self, user_id: str, user_email: str) -> Dict:
        """Index all files from a user's OneDrive"""
        self.logger.info(f"Indexing OneDrive for: {user_email}")

        # Get all files
        files = self.get_user_files(user_id)
        self.stats['documents_found'] += len(files)

        self.logger.info(f"Found {len(files)} files to process")

        # Process each file
        for file in tqdm(files, desc=f"Indexing {user_email}"):
            await self.process_file(file, user_email)

        self.stats['users_processed'] += 1

        return {
            'user_email': user_email,
            'files_found': len(files),
            'files_uploaded': self.stats['documents_uploaded'],
            'errors': self.stats['errors']
        }

    async def index_all_users(self, limit: Optional[int] = None) -> Dict:
        """Index OneDrive files for all users"""
        start_time = datetime.utcnow()

        # Initialize Elasticsearch
        await self.initialize_elasticsearch()

        # Get all users
        users = self.get_all_users()

        if limit:
            users = users[:limit]

        # Process each user
        for user in users:
            user_id = user['id']
            user_email = user.get('userPrincipalName', 'Unknown')

            try:
                await self.index_user(user_id, user_email)
            except Exception as e:
                self.logger.error(
                    f"Error indexing user {user_email}: {e}"
                )
                self.stats['errors'] += 1
                continue

        end_time = datetime.utcnow()
        duration = end_time - start_time

        # Close Elasticsearch
        if self.es_client:
            await self.es_client.close()

        return {
            'success': True,
            'users_processed': self.stats['users_processed'],
            'total_documents': self.stats['documents_found'],
            'documents_uploaded': self.stats['documents_uploaded'],
            'documents_skipped': self.stats['documents_skipped'],
            'errors': self.stats['errors'],
            'duration': str(duration)
        }


async def main():
    """Main entry point for testing"""
    indexer = OneDriveIndexer()

    # Test with first user only
    results = await indexer.index_all_users(limit=1)

    print("\n" + "="*50)
    print("OneDrive Indexing Results")
    print("="*50)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    asyncio.run(main())

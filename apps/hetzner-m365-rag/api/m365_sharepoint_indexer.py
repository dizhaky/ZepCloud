#!/usr/bin/env python3
"""
Microsoft 365 SharePoint Indexer - Adapted for Hetzner
Downloads and indexes SharePoint documents to MinIO + Elasticsearch
"""

import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

import requests  # type: ignore
from tenacity import retry, stop_after_attempt, wait_exponential
from tqdm import tqdm  # type: ignore
from elasticsearch import AsyncElasticsearch  # type: ignore

from config_manager import get_config_manager
from logger import setup_logging
from m365_auth import M365Auth
from storage_adapter import MinIOAdapter, ElasticsearchAdapter


class SharePointIndexer:
    """Index SharePoint documents to MinIO and Elasticsearch"""

    def __init__(self, progress_file: Optional[str] = None):
        self.config = get_config_manager()
        self.logger = setup_logging('sharepoint-indexer', level='INFO')
        self.auth = M365Auth()

        # Progress tracking
        progress_path = (
            progress_file or self.config.get_progress_file('sharepoint')
        )
        self.progress_file = Path(progress_path)
        self.progress = self._load_progress()

        # MinIO storage setup
        self.storage = MinIOAdapter()

        # Elasticsearch setup (will be initialized async)
        self.es_client: Optional[AsyncElasticsearch] = None
        self.es_adapter: Optional[ElasticsearchAdapter] = None

        # Supported file types
        extensions = self.config.get_supported_file_extensions('sharepoint')
        self.supported_extensions = set(extensions)

        # Statistics
        self.stats: Dict = {
            'sites_processed': 0,
            'documents_found': 0,
            'documents_uploaded': 0,
            'documents_skipped': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }

    async def initialize_elasticsearch(self):
        """Initialize Elasticsearch client and adapter"""
        es_config = self.config.get_elasticsearch_config()
        self.es_client = AsyncElasticsearch(
            hosts=[f"http://{es_config['host']}:{es_config['port']}"],
            basic_auth=(es_config['user'], es_config['password']),
            verify_certs=False
        )
        self.es_adapter = ElasticsearchAdapter(self.es_client)

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

    def get_all_sites(self) -> List[Dict]:
        """Get all SharePoint sites"""
        self.logger.info("Fetching all SharePoint sites...")

        sites = []
        url: Optional[str] = (
            "https://graph.microsoft.com/v1.0/sites?search=*"
        )

        while url:
            try:
                data = self._make_graph_request(url)
                sites.extend(data.get('value', []))
                url = str(data.get('@odata.nextLink')) if data.get(
                    '@odata.nextLink'
                ) else None
            except Exception as e:
                self.logger.error(f"Error fetching sites: {e}")
                break

        self.logger.info(f"Found {len(sites)} sites")
        return sites

    def get_site_documents(self, site_id: str) -> List[Dict]:
        """Get all documents from a site"""
        documents = []

        # Get all drives (document libraries) in the site
        try:
            base = "https://graph.microsoft.com/v1.0/sites"
            drives_url = f"{base}/{site_id}/drives"
            drives_data = self._make_graph_request(drives_url)
            drives = drives_data.get('value', [])

            drive_count = len(drives)
            self.logger.info(
                f"Found {drive_count} drives in site {site_id}"
            )

            # Get files from each drive
            for drive in drives:
                drive_id = drive['id']
                drive_name = drive.get('name', 'Unknown')

                try:
                    items = self._get_drive_items(drive_id, site_id)
                    item_count = len(items)
                    self.logger.info(
                        f"Found {item_count} items in drive '{drive_name}'"
                    )
                    documents.extend(items)
                except Exception as e:
                    error_msg = "Error getting items from drive"
                    self.logger.error(
                        f"{error_msg} {drive_name}: {e}"
                    )
                    continue

        except Exception as e:
            self.logger.error(f"Error getting drives for site {site_id}: {e}")

        return documents

    def _get_drive_items(
        self, drive_id: str, site_id: str, path: str = "root"
    ) -> List[Dict]:
        """Recursively get all items from a drive"""
        items = []

        base = "https://graph.microsoft.com/v1.0/sites"
        url: Optional[str] = (
            f"{base}/{site_id}/drives/{drive_id}/{path}/children"
        )

        while url:
            try:
                data = self._make_graph_request(url)

                for item in data.get('value', []):
                    # Check if it's a file
                    if 'file' in item:
                        # Check if supported extension
                        name = str(item.get('name', ''))
                        ext = Path(name).suffix.lower()

                        if ext in self.supported_extensions:
                            items.append(item)

                    # If it's a folder, recurse
                    elif 'folder' in item:
                        folder_id = item['id']
                        folder_path = f"items/{folder_id}"
                        folder_items = self._get_drive_items(
                            drive_id, site_id, folder_path
                        )
                        items.extend(folder_items)

                next_link = data.get('@odata.nextLink')
                url = str(next_link) if next_link else None

            except Exception as e:
                self.logger.error(f"Error getting drive items: {e}")
                break

        return items

    async def process_document(
        self, doc: Dict, site_name: str, site_url: str
    ) -> bool:
        """
        Download and index a single document

        Args:
            doc: Document metadata from Graph API
            site_name: Name of the SharePoint site
            site_url: URL of the SharePoint site

        Returns:
            bool: True if successful
        """
        doc_id = doc['id']
        doc_name = doc.get('name', 'Unknown')

        # Check if already indexed
        if doc_id in self.progress['indexed_documents']:
            last_modified = doc.get('lastModifiedDateTime')
            indexed_doc = self.progress['indexed_documents'][doc_id]
            if last_modified and last_modified == indexed_doc.get(
                'last_modified'
            ):
                self.logger.debug(f"Skipping unchanged document: {doc_name}")
                self.stats['documents_skipped'] += 1
                return True

        try:
            # Download document
            download_url = doc.get('@microsoft.graph.downloadUrl')
            if not download_url:
                self.logger.warning(f"No download URL for {doc_name}")
                return False

            self.logger.info(f"Processing: {doc_name}")

            # Download to temp location
            temp_path = f"/tmp/{doc_id}_{doc_name}"
            response = requests.get(download_url)
            response.raise_for_status()

            with open(temp_path, 'wb') as f:
                f.write(response.content)

            # Upload to MinIO
            blob_name = f"sharepoint/{site_name}/{doc_name}"
            created_by = doc.get('createdBy', {}).get('user', {})
            author_name = created_by.get('displayName', 'Unknown')
            metadata = {
                'm365_id': doc_id,
                'source': 'sharepoint',
                'site_name': site_name,
                'site_url': site_url,
                'file_name': doc_name,
                'file_size': str(doc.get('size', 0)),
                'created': doc.get('createdDateTime'),
                'modified': doc.get('lastModifiedDateTime'),
                'author': author_name
            }

            if self.storage.upload_file(temp_path, blob_name, metadata):
                self.logger.info(f"✅ Uploaded to MinIO: {blob_name}")

                # Index to Elasticsearch
                es_doc = {
                    'doc_id': doc_id,
                    'title': doc_name,
                    'content': '',  # Will be extracted by RAG-Anything
                    'metadata': metadata,
                    'has_images': False,
                    'has_tables': False,
                    'indexed_at': datetime.utcnow().isoformat()
                }

                if self.es_adapter and await self.es_adapter.index_document(
                    doc_id, es_doc
                ):
                    log_msg = f"✅ Indexed to Elasticsearch: {doc_name}"
                    self.logger.info(log_msg)

                    # Update progress
                    self.progress['indexed_documents'][doc_id] = {
                        'name': doc_name,
                        'last_modified': doc.get('lastModifiedDateTime'),
                        'indexed_at': datetime.utcnow().isoformat()
                    }
                    self._save_progress()

                    self.stats['documents_uploaded'] += 1

                    # Clean up temp file
                    os.remove(temp_path)
                    return True

            return False

        except Exception as e:
            self.logger.error(f"Error processing {doc_name}: {e}")
            self.stats['errors'] += 1
            return False

    async def index_site(self, site_id: str, site_name: str) -> Dict:
        """
        Index all documents from a SharePoint site

        Args:
            site_id: SharePoint site ID
            site_name: Site name for logging

        Returns:
            dict: Indexing statistics
        """
        self.logger.info(f"Starting indexing for site: {site_name}")

        # Get site details
        try:
            base = "https://graph.microsoft.com/v1.0/sites"
            site_url_endpoint = f"{base}/{site_id}"
            site_data = self._make_graph_request(site_url_endpoint)
            site_web_url = site_data.get('webUrl', '')
        except Exception as e:
            self.logger.error(f"Could not get site details: {e}")
            site_web_url = ''

        # Get all documents
        documents = self.get_site_documents(site_id)
        self.stats['documents_found'] += len(documents)

        self.logger.info(f"Found {len(documents)} documents to process")

        # Process each document
        for doc in tqdm(documents, desc=f"Indexing {site_name}"):
            await self.process_document(doc, site_name, site_web_url)

        self.stats['sites_processed'] += 1

        return {
            'site_name': site_name,
            'documents_found': len(documents),
            'documents_uploaded': self.stats['documents_uploaded'],
            'errors': self.stats['errors']
        }

    async def index_all_sites(self, limit: Optional[int] = None) -> Dict:
        """
        Index all SharePoint sites

        Args:
            limit: Optional limit on number of sites to process

        Returns:
            dict: Overall statistics
        """
        self.stats['start_time'] = datetime.utcnow().isoformat()

        # Initialize Elasticsearch
        await self.initialize_elasticsearch()

        # Get all sites
        sites = self.get_all_sites()

        if limit:
            sites = sites[:limit]

        # Process each site
        for site in sites:
            site_id = site['id']
            site_name = site.get('displayName', site.get('name', 'Unknown'))

            try:
                await self.index_site(site_id, site_name)
            except Exception as e:
                self.logger.error(f"Error indexing site {site_name}: {e}")
                self.stats['errors'] += 1
                continue

        self.stats['end_time'] = datetime.utcnow().isoformat()

        # Calculate duration
        start_time_str = self.stats.get('start_time')
        end_time_str = self.stats.get('end_time')
        if (
            start_time_str and end_time_str and
            isinstance(start_time_str, str) and
            isinstance(end_time_str, str)
        ):
            start = datetime.fromisoformat(start_time_str)
            end = datetime.fromisoformat(end_time_str)
            duration = end - start
        else:
            duration = None

        # Close Elasticsearch
        if self.es_client:
            await self.es_client.close()

        return {
            'success': True,
            'sites_processed': self.stats['sites_processed'],
            'total_documents': self.stats['documents_found'],
            'documents_uploaded': self.stats['documents_uploaded'],
            'documents_skipped': self.stats['documents_skipped'],
            'errors': self.stats['errors'],
            'duration': str(duration) if duration else 'N/A',
            'start_time': self.stats['start_time'],
            'end_time': self.stats['end_time']
        }


async def main():
    """Main entry point for testing"""
    indexer = SharePointIndexer()

    # Test with first site only
    results = await indexer.index_all_sites(limit=1)

    print("\n" + "="*50)
    print("SharePoint Indexing Results")
    print("="*50)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    asyncio.run(main())

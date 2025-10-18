#!/usr/bin/env python3
"""
Enhanced Microsoft 365 SharePoint Indexer with Graph Relationships
Integrates with graph_builder to create document relationships before Azure indexing
"""

import os
import json
import sys
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import requests
from azure.storage.blob import BlobServiceClient
from tenacity import retry, stop_after_attempt, wait_exponential
from tqdm import tqdm
from dotenv import load_dotenv

# Add raganything-processor to path
sys.path.insert(0, str(Path(__file__).parent / "raganything-processor"))
from graph_builder import GraphBuilder

# Import base SharePoint indexer
from m365_auth import M365Auth

load_dotenv()

class EnhancedSharePointIndexer:
    """
    Enhanced SharePoint indexer with:
    - Graph relationship extraction
    - Multimodal content enrichment
    - Better metadata for Azure AI Search
    """

    def __init__(self, progress_file: str = "sharepoint_progress_enhanced.json"):
        self.auth = M365Auth()
        self.progress_file = Path(progress_file)
        self.progress = self._load_progress()

        # Azure Blob Storage setup
        self.connection_string = self._get_connection_string()
        self.blob_service = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.blob_service.get_container_client("training-data")

        # Graph builder for relationships
        self.graph_builder = GraphBuilder()

        # Load existing graph if available
        graph_file = Path("sharepoint_graph.json")
        if graph_file.exists():
            print("📊 Loading existing document graph...")
            self._load_graph(graph_file)

        # Supported file types
        self.supported_extensions = {
            '.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt',
            '.txt', '.md', '.json', '.csv', '.html', '.htm', '.rtf',
            '.xml', '.msg', '.eml'
        }

        # Statistics
        self.stats = {
            'sites_processed': 0,
            'documents_found': 0,
            'documents_uploaded': 0,
            'documents_skipped': 0,
            'relationships_created': 0,
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
                print(f"⚠️  Error loading progress: {e}")

        return {
            'last_sync': None,
            'sites': {},
            'total_documents': 0,
            'total_relationships': 0,
            'processed_documents': []
        }

    def _save_progress(self):
        """Save progress tracking data"""
        try:
            self.progress['total_relationships'] = len(self.graph_builder.documents)
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving progress: {e}")

    def _load_graph(self, graph_file: Path):
        """Load existing graph data"""
        try:
            with open(graph_file, 'r') as f:
                graph_data = json.load(f)

            # Reconstruct graph from saved data
            for doc_id, doc_data in graph_data.get('documents', {}).items():
                content = doc_data.get('content', '')
                metadata = doc_data.get('metadata', {})
                self.graph_builder.add_document(doc_id, content, metadata)

            print(f"   Loaded {len(self.graph_builder.documents)} documents")
        except Exception as e:
            print(f"⚠️  Error loading graph: {e}")

    def _get_connection_string(self) -> str:
        """Get Azure Storage connection string"""
        account_name = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
        account_key = os.getenv('AZURE_STORAGE_ACCOUNT_KEY')

        if not account_name or not account_key:
            raise ValueError("Missing Azure Storage credentials in environment")

        return f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"

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

    def _extract_multimodal_content(
        self,
        content: bytes,
        filename: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract multimodal content from document
        Uses Azure Cognitive Services data (already extracted by indexer)
        """
        multimodal = {
            'tables_extracted': [],
            'equations_extracted': [],
            'images_described': [],
            'has_tables': False,
            'has_equations': False,
            'has_images': False
        }

        # Check if content has potential multimodal elements
        content_str = content.decode('utf-8', errors='ignore') if isinstance(content, bytes) else str(content)

        # Detect tables (basic heuristic - Azure OCR will do better)
        if '|' in content_str or '\t' in content_str:
            multimodal['has_tables'] = True

        # Detect equations (LaTeX patterns)
        equation_patterns = [
            r'\$.*?\$',  # Inline math
            r'\\\[.*?\\\]',  # Display math
            r'\\begin\{equation\}',
            r'\\frac\{',
            r'\\sum',
            r'\\int'
        ]
        import re
        for pattern in equation_patterns:
            if re.search(pattern, content_str):
                multimodal['has_equations'] = True
                break

        # Note: Azure OCR will extract actual image content
        # We just flag that it needs processing
        if filename.lower().endswith(('.pdf', '.docx', '.pptx')):
            multimodal['has_images'] = True  # Likely has images

        return multimodal

    def _build_document_relationships(
        self,
        doc_id: str,
        content: bytes,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build relationships for this document"""
        try:
            # Convert content to text for analysis
            content_str = content.decode('utf-8', errors='ignore') if isinstance(content, bytes) else str(content)

            # Add to graph builder
            relationships = self.graph_builder.add_document(
                doc_id=doc_id,
                content=content_str[:10000],  # Limit for performance
                metadata=metadata
            )

            self.stats['relationships_created'] += 1

            return relationships

        except Exception as e:
            print(f"⚠️  Error building relationships: {e}")
            return {}

    def _upload_to_blob(
        self,
        content: bytes,
        blob_name: str,
        metadata: Dict[str, str] = None,
        relationships: Dict[str, Any] = None,
        multimodal: Dict[str, Any] = None
    ) -> bool:
        """Upload content to Azure Blob Storage with enhanced metadata"""
        try:
            blob_client = self.container_client.get_blob_client(blob_name)

            # Prepare enhanced metadata
            enhanced_metadata = metadata or {}

            # Add multimodal flags
            if multimodal:
                enhanced_metadata['has_tables'] = str(multimodal.get('has_tables', False))
                enhanced_metadata['has_equations'] = str(multimodal.get('has_equations', False))
                enhanced_metadata['has_images'] = str(multimodal.get('has_images', False))
                enhanced_metadata['tables_count'] = str(len(multimodal.get('tables_extracted', [])))

            # Add relationship data (as JSON string, limited size)
            if relationships:
                rel_summary = {
                    'relationship_score': relationships.get('relationship_score', 0.0),
                    'cites_count': len(relationships.get('relationships', {}).get('cites', [])),
                    'related_docs_count': len(relationships.get('relationships', {}).get('similar_topics', [])),
                    'has_relationships': relationships.get('relationship_score', 0.0) > 0
                }
                enhanced_metadata['relationship_data'] = json.dumps(rel_summary)

                # Store detailed relationships separately if needed
                # (Azure blob metadata has size limits)

            blob_client.upload_blob(
                content,
                overwrite=True,
                metadata=enhanced_metadata,
                timeout=300
            )
            return True
        except Exception as e:
            print(f"❌ Upload failed for {blob_name}: {e}")
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
                print(f"⚠️  Failed to get drives for site {site_name}: {drives_response.status_code}")
                return []

            drives_data = drives_response.json()
            drives = drives_data.get('value', [])

            for drive in drives:
                drive_id = drive.get('id')
                drive_name = drive.get('name', 'Unknown')

                print(f"   📁 Processing drive: {drive_name}")

                # Get all files in this drive
                files = self._get_drive_files(drive_id, drive_name, site_name)
                documents.extend(files)

        except Exception as e:
            print(f"❌ Error processing site {site_name}: {e}")
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
            print(f"❌ Error processing drive {drive_name}: {e}")
            self.stats['errors'] += 1

        return files

    def _get_folder_files(self, drive_id: str, folder_id: str, folder_path: str) -> List[Dict[str, Any]]:
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
            print(f"⚠️  Error processing folder {folder_path}: {e}")

        return files

    def _process_document(self, doc: Dict[str, Any]) -> bool:
        """Process a single document with enhanced metadata"""
        try:
            # Generate blob name
            site_name = doc['site_name']
            folder_path = doc['folder_path']
            filename = doc['name']

            # Clean up path for blob storage
            clean_site = site_name.replace(' ', '_').replace('/', '_')
            clean_folder = folder_path.replace(' ', '_').replace('/', '_')
            blob_name = f"sharepoint/{clean_site}/{clean_folder}/{filename}"
            doc_id = blob_name

            # Check if already processed
            if doc_id in self.progress.get('processed_documents', []):
                self.stats['documents_skipped'] += 1
                return True

            # Download file
            if not doc.get('download_url'):
                print(f"⚠️  No download URL for {filename}")
                return False

            print(f"   📄 Processing: {filename}")
            content = self._download_file(doc['download_url'])

            # Prepare base metadata
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

            # Extract multimodal content flags
            multimodal = self._extract_multimodal_content(content, filename, metadata)

            # Build document relationships
            # Note: For now, using filename-based metadata
            # Azure AI Search enrichment will add entities later
            relationships = self._build_document_relationships(
                doc_id=doc_id,
                content=content,
                metadata=metadata
            )

            # Upload to blob storage with enhanced metadata
            if self._upload_to_blob(content, blob_name, metadata, relationships, multimodal):
                self.progress['processed_documents'].append(doc_id)
                self.stats['documents_uploaded'] += 1
                return True
            else:
                self.stats['errors'] += 1
                return False

        except Exception as e:
            print(f"❌ Error processing {doc.get('name', 'unknown')}: {e}")
            self.stats['errors'] += 1
            return False

    def index_site(self, site_id: str, site_name: str) -> Dict[str, Any]:
        """Index all documents from a specific SharePoint site"""
        print(f"🏢 Indexing site: {site_name}")

        start_time = datetime.now()
        documents = self._get_site_documents(site_id, site_name)

        if not documents:
            print(f"   ℹ️  No documents found in {site_name}")
            return {'success': True, 'documents': 0}

        print(f"   📊 Found {len(documents)} documents")

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

        # Export graph periodically
        self.graph_builder.export_graph("sharepoint_graph.json")

        duration = datetime.now() - start_time
        print(f"   ✅ Completed {site_name}: {processed}/{len(documents)} documents in {duration}")

        return {
            'success': True,
            'documents': len(documents),
            'processed': processed,
            'duration': str(duration)
        }

    def index_all_sites(self, limit: int = None) -> Dict[str, Any]:
        """Index documents from all SharePoint sites"""
        print("🚀 Starting Enhanced SharePoint indexing with graph relationships...")

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

            print(f"📊 Found {len(sites)} SharePoint sites")

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

            # Final graph export
            self.graph_builder.export_graph("sharepoint_graph.json")

            # Print graph statistics
            print("\n📊 Graph Statistics:")
            stats = self.graph_builder.get_statistics()
            print(f"   Total documents in graph: {stats['total_documents']}")
            print(f"   Total relationships: {stats['total_citations']}")
            print(f"   Average connections per document: {stats['avg_relationships_per_doc']:.2f}")

            return {
                'success': True,
                'sites_processed': self.stats['sites_processed'],
                'total_documents': self.stats['documents_found'],
                'documents_uploaded': self.stats['documents_uploaded'],
                'documents_skipped': self.stats['documents_skipped'],
                'relationships_created': self.stats['relationships_created'],
                'errors': self.stats['errors'],
                'duration': str(datetime.now() - self.stats['start_time']),
                'site_results': results
            }

        except Exception as e:
            return {'error': f'Indexing failed: {e}'}

    def get_status(self) -> Dict[str, Any]:
        """Get current indexing status"""
        graph_stats = self.graph_builder.get_statistics()

        return {
            'last_sync': self.progress.get('last_sync'),
            'sites_processed': len(self.progress.get('sites', {})),
            'total_documents': self.progress.get('total_documents', 0),
            'processed_documents': len(self.progress.get('processed_documents', [])),
            'total_relationships': graph_stats['total_documents'],
            'current_stats': self.stats,
            'graph_stats': graph_stats
        }


def main():
    """CLI interface for Enhanced SharePoint indexer"""
    import argparse

    parser = argparse.ArgumentParser(description='Enhanced SharePoint Document Indexer with Graph Relationships')
    parser.add_argument('--site', help='Index specific site by ID')
    parser.add_argument('--limit', type=int, help='Limit number of sites to process')
    parser.add_argument('--status', action='store_true', help='Show indexing status')

    args = parser.parse_args()

    indexer = EnhancedSharePointIndexer()

    if args.status:
        status = indexer.get_status()
        print("📊 Enhanced SharePoint Indexing Status:")
        print(f"   Last Sync: {status.get('last_sync', 'Never')}")
        print(f"   Sites Processed: {status.get('sites_processed', 0)}")
        print(f"   Total Documents: {status.get('total_documents', 0)}")
        print(f"   Documents in Graph: {status.get('total_relationships', 0)}")
        return 0

    if args.site:
        # Index specific site
        result = indexer.index_site(args.site, f"Site-{args.site}")
        print(f"Result: {result}")
    else:
        # Index all sites
        result = indexer.index_all_sites(args.limit)

        if result.get('success'):
            print(f"\n✅ Enhanced SharePoint indexing completed!")
            print(f"   Sites: {result['sites_processed']}")
            print(f"   Documents: {result['total_documents']}")
            print(f"   Uploaded: {result['documents_uploaded']}")
            print(f"   Relationships: {result['relationships_created']}")
            print(f"   Skipped: {result['documents_skipped']}")
            print(f"   Errors: {result['errors']}")
            print(f"   Duration: {result['duration']}")
        else:
            print(f"❌ Indexing failed: {result.get('error')}")
            return 1

    return 0

if __name__ == "__main__":
    exit(main())


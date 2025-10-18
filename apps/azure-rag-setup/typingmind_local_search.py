#!/usr/bin/env python3
"""
TypingMind Local Search Integration
Connects Microsoft Graph API data to TypingMind via local search
"""

import os
import json
import sqlite3
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from logger import setup_logging

class TypingMindLocalSearch:
    """
    Local search service that connects Microsoft Graph API data to TypingMind
    """

    def __init__(self, storage_path: str = "/Volumes/Express 1M2/m365_local_storage", log_level: str = "INFO"):
        self.logger = setup_logging('typingmind-local-search', level=log_level)
        self.storage_path = Path(storage_path)
        self.db_path = self.storage_path / "m365_data.db"
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for TypingMind

        # Setup routes
        self._setup_routes()

        self.logger.info(f"TypingMind Local Search initialized")
        self.logger.info(f"Storage path: {self.storage_path}")
        self.logger.info(f"Database: {self.db_path}")

    def _setup_routes(self):
        """Setup Flask routes for TypingMind integration"""

        @self.app.route('/search', methods=['POST'])
        def search_documents():
            """Search documents endpoint for TypingMind"""
            try:
                data = request.get_json()
                query = data.get('search', '')
                top = data.get('top', 10)
                skip = data.get('skip', 0)

                self.logger.info(f"Search request: '{query}' (top={top}, skip={skip})")

                # Search local database
                results = self._search_local_documents(query, top, skip)

                return jsonify({
                    'value': results,
                    '@odata.count': len(results),
                    'search_time': datetime.now().isoformat()
                })

            except Exception as e:
                self.logger.error(f"Search error: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'storage_path': str(self.storage_path),
                'database_exists': self.db_path.exists(),
                'timestamp': datetime.now().isoformat()
            })

        @self.app.route('/stats', methods=['GET'])
        def get_stats():
            """Get storage statistics"""
            stats = self._get_storage_stats()
            return jsonify(stats)

    def _search_local_documents(self, query: str, top: int = 10, skip: int = 0) -> List[Dict[str, Any]]:
        """Search documents in local SQLite database"""
        if not self.db_path.exists():
            self.logger.warning("Database not found")
            return []

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Search in document metadata
            search_query = """
                SELECT id, source, source_id, title, file_path, metadata_path, indexed_at, size_bytes
                FROM documents
                WHERE title LIKE ? OR source LIKE ? OR source_id LIKE ?
                ORDER BY indexed_at DESC
                LIMIT ? OFFSET ?
            """

            search_term = f"%{query}%"
            cursor.execute(search_query, (search_term, search_term, search_term, top, skip))
            rows = cursor.fetchall()

            results = []
            for row in rows:
                doc_id, source, source_id, title, file_path, metadata_path, indexed_at, size_bytes = row

                # Load metadata
                metadata = {}
                if metadata_path and Path(metadata_path).exists():
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                    except Exception as e:
                        self.logger.warning(f"Could not load metadata for {doc_id}: {e}")

                # Get document content for search
                content = self._get_document_content(doc_id)

                result = {
                    '@search.score': 1.0,  # Simple scoring for now
                    'id': doc_id,
                    'title': title,
                    'source': source,
                    'source_id': source_id,
                    'file_path': file_path,
                    'indexed_at': indexed_at,
                    'size_bytes': size_bytes,
                    'content': content[:1000] if content else '',  # First 1000 chars
                    'metadata': metadata,
                    'web_url': metadata.get('web_url', ''),
                    'created_date_time': metadata.get('created_date_time', ''),
                    'last_modified_date_time': metadata.get('last_modified_date_time', ''),
                    'file_extension': metadata.get('file_extension', ''),
                    'user_name': metadata.get('user_name', ''),
                    'parent_info': metadata.get('parent_info', {})
                }

                results.append(result)

            conn.close()
            self.logger.info(f"Found {len(results)} documents for query: '{query}'")
            return results

        except Exception as e:
            self.logger.error(f"Database search error: {e}")
            return []

    def _get_document_content(self, doc_id: str) -> Optional[str]:
        """Get document content for search"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT file_path FROM documents WHERE id = ?", (doc_id,))
            result = cursor.fetchone()
            conn.close()

            if result:
                file_path = Path(result[0])
                if file_path.exists():
                    # For text files, read content
                    if file_path.suffix.lower() in ['.txt', '.md', '.json', '.csv']:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            return f.read()
                    # For binary files, return placeholder
                    else:
                        return f"[Binary file: {file_path.name}]"
        except Exception as e:
            self.logger.warning(f"Could not read content for {doc_id}: {e}")

        return None

    def _get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM documents")
            total_documents = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM documents WHERE source = 'sharepoint'")
            sharepoint_documents = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM documents WHERE source = 'onedrive'")
            onedrive_documents = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM documents WHERE source = 'exchange'")
            exchange_documents = cursor.fetchone()[0]

            cursor.execute("SELECT SUM(size_bytes) FROM documents")
            total_size_bytes = cursor.fetchone()[0] or 0

            conn.close()

            return {
                'total_documents': total_documents,
                'sharepoint_documents': sharepoint_documents,
                'onedrive_documents': onedrive_documents,
                'exchange_documents': exchange_documents,
                'storage_size_bytes': total_size_bytes,
                'storage_size_mb': round(total_size_bytes / (1024 * 1024), 2),
                'storage_path': str(self.storage_path)
            }

        except Exception as e:
            self.logger.error(f"Could not get storage stats: {e}")
            return {}

    def start_server(self, host: str = 'localhost', port: int = 5000, debug: bool = False):
        """Start the TypingMind local search server"""
        self.logger.info(f"Starting TypingMind Local Search server on {host}:{port}")
        self.logger.info("TypingMind can now connect to this local search service!")

        self.app.run(host=host, port=port, debug=debug)

def main():
    """Main function to start the TypingMind local search service"""
    search_service = TypingMindLocalSearch()

    # Get stats
    stats = search_service._get_storage_stats()
    print(f"📊 Local Storage Stats:")
    print(f"   Total documents: {stats.get('total_documents', 0)}")
    print(f"   SharePoint: {stats.get('sharepoint_documents', 0)}")
    print(f"   OneDrive: {stats.get('onedrive_documents', 0)}")
    print(f"   Exchange: {stats.get('exchange_documents', 0)}")
    print(f"   Storage size: {stats.get('storage_size_mb', 0)} MB")
    print("")

    # Start server
    search_service.start_server(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    main()

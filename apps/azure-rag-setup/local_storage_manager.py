#!/usr/bin/env python3
"""
Local Storage Manager - Replaces Azure Storage with local file system
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

class LocalStorageManager:
    """Local storage manager for M365 data"""

    def __init__(self, storage_path: str = "./local_storage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)

        # Create subdirectories
        (self.storage_path / "documents").mkdir(exist_ok=True)
        (self.storage_path / "metadata").mkdir(exist_ok=True)
        (self.storage_path / "indexes").mkdir(exist_ok=True)

        # Initialize local database
        self.db_path = self.storage_path / "m365_data.db"
        self._init_database()

    def _init_database(self):
        """Initialize local SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                source TEXT,
                title TEXT,
                content TEXT,
                metadata TEXT,
                file_path TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')

        # Create indexes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS indexes (
                id TEXT PRIMARY KEY,
                document_id TEXT,
                index_type TEXT,
                index_data TEXT,
                created_at TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def store_document(self, document_id: str, source: str, title: str,
                      content: str, metadata: Dict, file_path: Optional[str] = None) -> bool:
        """Store a document in local storage"""
        try:
            # Save content to file if provided
            if file_path:
                full_path = self.storage_path / "documents" / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            # Store metadata
            metadata_path = self.storage_path / "metadata" / f"{document_id}.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)

            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO documents
                (id, source, title, content, metadata, file_path, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                document_id,
                source,
                title,
                content,
                json.dumps(metadata),
                file_path,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))

            conn.commit()
            conn.close()

            return True

        except Exception as e:
            print(f"Error storing document {document_id}: {e}")
            return False

    def get_document(self, document_id: str) -> Optional[Dict]:
        """Retrieve a document from local storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, source, title, content, metadata, file_path, created_at, updated_at
                FROM documents WHERE id = ?
            ''', (document_id,))

            row = cursor.fetchone()
            conn.close()

            if row:
                return {
                    'id': row[0],
                    'source': row[1],
                    'title': row[2],
                    'content': row[3],
                    'metadata': json.loads(row[4]) if row[4] else {},
                    'file_path': row[5],
                    'created_at': row[6],
                    'updated_at': row[7]
                }

            return None

        except Exception as e:
            print(f"Error retrieving document {document_id}: {e}")
            return None

    def search_documents(self, query: str, source: Optional[str] = None) -> List[Dict]:
        """Search documents in local storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if source:
                cursor.execute('''
                    SELECT id, source, title, content, metadata, file_path, created_at, updated_at
                    FROM documents
                    WHERE (title LIKE ? OR content LIKE ?) AND source = ?
                    ORDER BY updated_at DESC
                ''', (f'%{query}%', f'%{query}%', source))
            else:
                cursor.execute('''
                    SELECT id, source, title, content, metadata, file_path, created_at, updated_at
                    FROM documents
                    WHERE title LIKE ? OR content LIKE ?
                    ORDER BY updated_at DESC
                ''', (f'%{query}%', f'%{query}%'))

            rows = cursor.fetchall()
            conn.close()

            documents = []
            for row in rows:
                documents.append({
                    'id': row[0],
                    'source': row[1],
                    'title': row[2],
                    'content': row[3],
                    'metadata': json.loads(row[4]) if row[4] else {},
                    'file_path': row[5],
                    'created_at': row[6],
                    'updated_at': row[7]
                })

            return documents

        except Exception as e:
            print(f"Error searching documents: {e}")
            return []

    def get_document_count(self, source: Optional[str] = None) -> int:
        """Get total document count"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if source:
                cursor.execute('SELECT COUNT(*) FROM documents WHERE source = ?', (source,))
            else:
                cursor.execute('SELECT COUNT(*) FROM documents')

            count = cursor.fetchone()[0]
            conn.close()

            return count

        except Exception as e:
            print(f"Error getting document count: {e}")
            return 0

    def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        try:
            total_docs = self.get_document_count()
            sharepoint_docs = self.get_document_count('sharepoint')
            onedrive_docs = self.get_document_count('onedrive')
            exchange_docs = self.get_document_count('exchange')

            # Calculate storage size
            storage_size = 0
            for root, dirs, files in os.walk(self.storage_path):
                for file in files:
                    storage_size += os.path.getsize(os.path.join(root, file))

            return {
                'total_documents': total_docs,
                'sharepoint_documents': sharepoint_docs,
                'onedrive_documents': onedrive_docs,
                'exchange_documents': exchange_docs,
                'storage_size_bytes': storage_size,
                'storage_size_mb': round(storage_size / (1024 * 1024), 2),
                'storage_path': str(self.storage_path)
            }

        except Exception as e:
            print(f"Error getting storage stats: {e}")
            return {}

if __name__ == "__main__":
    # Test local storage
    storage = LocalStorageManager()

    # Test storing a document
    test_doc = storage.store_document(
        document_id="test-001",
        source="test",
        title="Test Document",
        content="This is a test document content.",
        metadata={"author": "test", "type": "test"}
    )

    print(f"Document stored: {test_doc}")

    # Test retrieving a document
    doc = storage.get_document("test-001")
    print(f"Document retrieved: {doc['title'] if doc else 'Not found'}")

    # Test search
    results = storage.search_documents("test")
    print(f"Search results: {len(results)} documents")

    # Test stats
    stats = storage.get_storage_stats()
    print(f"Storage stats: {stats}")

"""
Storage Adapter for MinIO (S3-compatible)
Replaces Azure Blob Storage in the original implementation
"""

from minio import Minio
from minio.error import S3Error
from typing import Optional, BinaryIO
import os
import logging
from pathlib import Path
from datetime import timedelta

logger = logging.getLogger(__name__)

class MinIOAdapter:
    """Adapter class to replace Azure Blob Storage with MinIO"""
    
    def __init__(self):
        self.endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
        self.access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        self.secret_key = os.getenv("MINIO_SECRET_KEY", "changeme123")
        
        # Initialize MinIO client
        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False  # Set to True if using HTTPS
        )
        
        # Default bucket
        self.bucket_name = "m365-documents"
        self._ensure_bucket_exists()
        
        logger.info(f"MinIO adapter initialized - endpoint: {self.endpoint}")
    
    def _ensure_bucket_exists(self):
        """Ensure the default bucket exists"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error ensuring bucket exists: {e}")
            raise
    
    def upload_file(
        self, 
        file_path: str, 
        blob_name: str, 
        metadata: Optional[dict] = None
    ) -> bool:
        """
        Upload a file to MinIO
        
        Args:
            file_path: Local file path
            blob_name: Object name in MinIO
            metadata: Optional metadata dict
            
        Returns:
            bool: True if successful
        """
        try:
            # Convert metadata to tags if provided
            tags = None
            if metadata:
                tags = {k: str(v) for k, v in metadata.items() if v is not None}
            
            # Upload file
            self.client.fput_object(
                self.bucket_name,
                blob_name,
                file_path,
                metadata=tags
            )
            
            logger.info(f"Uploaded {blob_name} to MinIO")
            return True
            
        except S3Error as e:
            logger.error(f"Error uploading {blob_name}: {e}")
            return False
    
    def download_file(
        self, 
        blob_name: str, 
        download_path: str
    ) -> bool:
        """
        Download a file from MinIO
        
        Args:
            blob_name: Object name in MinIO
            download_path: Local path to save file
            
        Returns:
            bool: True if successful
        """
        try:
            self.client.fget_object(
                self.bucket_name,
                blob_name,
                download_path
            )
            
            logger.info(f"Downloaded {blob_name} from MinIO")
            return True
            
        except S3Error as e:
            logger.error(f"Error downloading {blob_name}: {e}")
            return False
    
    def file_exists(self, blob_name: str) -> bool:
        """
        Check if a file exists in MinIO
        
        Args:
            blob_name: Object name to check
            
        Returns:
            bool: True if exists
        """
        try:
            self.client.stat_object(self.bucket_name, blob_name)
            return True
        except S3Error:
            return False
    
    def get_file_url(self, blob_name: str, expires: int = 3600) -> Optional[str]:
        """
        Get a presigned URL for a file
        
        Args:
            blob_name: Object name
            expires: URL expiration time in seconds (default 1 hour)
            
        Returns:
            str: Presigned URL
        """
        try:
            url = self.client.presigned_get_object(
                self.bucket_name,
                blob_name,
                expires=timedelta(seconds=expires)
            )
            return url
        except S3Error as e:
            logger.error(f"Error generating presigned URL: {e}")
            return None
    
    def delete_file(self, blob_name: str) -> bool:
        """
        Delete a file from MinIO
        
        Args:
            blob_name: Object name to delete
            
        Returns:
            bool: True if successful
        """
        try:
            self.client.remove_object(self.bucket_name, blob_name)
            logger.info(f"Deleted {blob_name} from MinIO")
            return True
        except S3Error as e:
            logger.error(f"Error deleting {blob_name}: {e}")
            return False
    
    def list_files(self, prefix: str = "") -> list:
        """
        List files in MinIO with optional prefix
        
        Args:
            prefix: Optional prefix to filter objects
            
        Returns:
            list: List of object names
        """
        try:
            objects = self.client.list_objects(
                self.bucket_name,
                prefix=prefix,
                recursive=True
            )
            return [obj.object_name for obj in objects]
        except S3Error as e:
            logger.error(f"Error listing files: {e}")
            return []


class ElasticsearchAdapter:
    """
    Adapter class to replace Azure AI Search with Elasticsearch
    
    Note: This class uses synchronous __init__ (no async/await needed for instantiation).
    The instance methods are async and should be awaited when called.
    
    Example:
        adapter = ElasticsearchAdapter(es_client)  # No await
        await adapter.index_document(doc_id, content)  # Await async methods
    """
    
    def __init__(self, es_client):
        """
        Initialize with an Elasticsearch client (synchronous initialization)
        
        Args:
            es_client: AsyncElasticsearch client instance
        
        Note: Do NOT await this __init__ - it's synchronous by design.
        """
        self.es_client = es_client
        self.index_name = "documents"
        logger.info("Elasticsearch adapter initialized")
    
    async def index_document(
        self, 
        doc_id: str, 
        content: dict
    ) -> bool:
        """
        Index a document to Elasticsearch
        
        Args:
            doc_id: Document ID
            content: Document content dict
            
        Returns:
            bool: True if successful
        """
        try:
            await self.es_client.index(
                index=self.index_name,
                id=doc_id,
                document=content
            )
            logger.info(f"Indexed document {doc_id} to Elasticsearch")
            return True
        except Exception as e:
            logger.error(f"Error indexing document {doc_id}: {e}")
            return False
    
    async def bulk_index_documents(self, documents: list) -> dict:
        """
        Bulk index multiple documents
        
        Args:
            documents: List of document dicts with _id and _source
            
        Returns:
            dict: Result statistics
        """
        from elasticsearch.helpers import async_bulk
        
        try:
            actions = [
                {
                    "_index": self.index_name,
                    "_id": doc["_id"],
                    "_source": doc["_source"]
                }
                for doc in documents
            ]
            
            success, failed = await async_bulk(
                self.es_client, 
                actions, 
                raise_on_error=False
            )
            
            logger.info(f"Bulk indexed {success} documents, {failed} failed")
            return {
                "success": success,
                "failed": failed,
                "total": len(documents)
            }
        except Exception as e:
            logger.error(f"Error in bulk indexing: {e}")
            return {"success": 0, "failed": len(documents), "total": len(documents)}
    
    async def document_exists(self, doc_id: str) -> bool:
        """
        Check if a document exists in Elasticsearch
        
        Args:
            doc_id: Document ID
            
        Returns:
            bool: True if exists
        """
        try:
            return await self.es_client.exists(
                index=self.index_name,
                id=doc_id
            )
        except Exception as e:
            logger.error(f"Error checking document existence: {e}")
            return False
    
    async def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document from Elasticsearch
        
        Args:
            doc_id: Document ID
            
        Returns:
            bool: True if successful
        """
        try:
            await self.es_client.delete(
                index=self.index_name,
                id=doc_id
            )
            logger.info(f"Deleted document {doc_id} from Elasticsearch")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return False


"""
Configuration Manager for M365 RAG System
Adapted for Hetzner deployment with MinIO/Elasticsearch
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manage configuration for M365 RAG system"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            config_path: Optional path to config file
        """
        # Load environment variables
        load_dotenv()
        
        # Load config file if provided
        self.config = {}
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f) or {}
        
        # Default configuration
        self.defaults = {
            'elasticsearch': {
                'host': os.getenv('ES_HOST', 'elasticsearch'),
                'port': int(os.getenv('ES_PORT', 9200)),
                'user': os.getenv('ES_USER', 'elastic'),
                'password': os.getenv('ES_PASSWORD', 'changeme'),
                'index_prefix': 'documents'
            },
            'minio': {
                'endpoint': os.getenv('MINIO_ENDPOINT', 'minio:9000'),
                'access_key': os.getenv('MINIO_ACCESS_KEY', 'minioadmin'),
                'secret_key': os.getenv('MINIO_SECRET_KEY', 'changeme123'),
                'bucket': 'm365-documents'
            },
            'postgres': {
                'url': os.getenv('DATABASE_URL'),
                'pool_size': 10,
                'max_overflow': 20
            },
            'redis': {
                'url': os.getenv('REDIS_URL', 'redis://redis:6379'),
                'cache_ttl': 300
            },
            'm365': {
                'client_id': os.getenv('AZURE_CLIENT_ID'),
                'client_secret': os.getenv('AZURE_CLIENT_SECRET'),
                'tenant_id': os.getenv('AZURE_TENANT_ID'),
                'use_delegated_auth': os.getenv('M365_USE_DELEGATED_AUTH', 'true').lower() == 'true'
            },
            'rag': {
                'embedding_model': 'text-embedding-3-large',
                'embedding_dimensions': 1536,
                'llm_model': 'gpt-4o-mini',
                'chunk_size': 512,
                'chunk_overlap': 50
            },
            'sync': {
                'batch_size': 100,
                'max_retries': 3,
                'retry_delay': 5,
                'supported_extensions': ['.pdf', '.docx', '.xlsx', '.pptx', '.txt', '.md', '.csv']
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Dot-notation key (e.g., 'elasticsearch.host')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        # Try user config first
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                # Fallback to defaults
                value = self.defaults
                for k in keys:
                    if isinstance(value, dict) and k in value:
                        value = value[k]
                    else:
                        return default
                return value
        
        return value if value is not None else default
    
    def get_elasticsearch_config(self) -> Dict:
        """Get Elasticsearch configuration"""
        return self.get('elasticsearch', {})
    
    def get_minio_config(self) -> Dict:
        """Get MinIO configuration"""
        return self.get('minio', {})
    
    def get_postgres_config(self) -> Dict:
        """Get PostgreSQL configuration"""
        return self.get('postgres', {})
    
    def get_redis_config(self) -> Dict:
        """Get Redis configuration"""
        return self.get('redis', {})
    
    def get_m365_config(self) -> Dict:
        """Get M365 configuration"""
        return self.get('m365', {})
    
    def get_rag_config(self) -> Dict:
        """Get RAG configuration"""
        return self.get('rag', {})
    
    def get_sync_config(self) -> Dict:
        """Get sync configuration"""
        return self.get('sync', {})
    
    def get_supported_file_extensions(self, source: str = 'all') -> List[str]:
        """
        Get supported file extensions
        
        Args:
            source: Source type (all, sharepoint, onedrive, etc.)
            
        Returns:
            List of supported extensions
        """
        return self.get('sync.supported_extensions', [])
    
    def get_progress_file(self, source: str) -> str:
        """
        Get progress file path for a source
        
        Args:
            source: Source type
            
        Returns:
            Path to progress file
        """
        base_dir = Path('/data/m365-rag/data')
        base_dir.mkdir(parents=True, exist_ok=True)
        return str(base_dir / f'{source}_progress.json')
    
    def get_openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key"""
        return os.getenv('OPENAI_API_KEY')


# Global instance
_config_manager = None

def get_config_manager(config_path: Optional[str] = None) -> ConfigManager:
    """
    Get global config manager instance
    
    Args:
        config_path: Optional config file path
        
    Returns:
        ConfigManager instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_path)
    return _config_manager


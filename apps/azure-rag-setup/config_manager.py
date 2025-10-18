#!/usr/bin/env python3
"""
Centralized Configuration Manager for Azure RAG Setup
Provides unified configuration loading and validation across all components
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from logger import setup_logging


class ConfigManager:
    """Centralized configuration management for Azure RAG setup"""

    def __init__(self, config_dir: str = ".", log_level: str = "INFO"):
        self.logger = setup_logging('config-manager', level=log_level)
        self.config_dir = Path(config_dir)
        self._config_cache = {}

        # Load environment variables
        load_dotenv()

        # Load configuration files
        self._load_configs()

    def _load_configs(self):
        """Load all configuration files"""
        try:
            # Load main environment configuration
            self._load_env_config()

            # Load M365 configuration
            self._load_m365_config()

            # Load RAG-Anything configuration
            self._load_rag_anything_config()

            self.logger.info("Configuration loaded successfully")

        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise

    def _load_env_config(self):
        """Load environment-based configuration"""
        self._config_cache['env'] = {
            # Azure AI Search
            'azure_search': {
                'service_name': os.getenv('AZURE_SEARCH_SERVICE_NAME'),
                'admin_key': os.getenv('AZURE_SEARCH_ADMIN_KEY'),
                'endpoint': os.getenv('AZURE_SEARCH_ENDPOINT'),
                'index_name': os.getenv('AZURE_SEARCH_INDEX_NAME', 'training-data-index')
            },

            # Azure Storage
            'azure_storage': {
                'account_name': os.getenv('AZURE_STORAGE_ACCOUNT_NAME'),
                'account_key': os.getenv('AZURE_STORAGE_ACCOUNT_KEY'),
                'container_name': os.getenv('AZURE_STORAGE_CONTAINER_NAME', 'training-data'),
                'connection_string': os.getenv('AZURE_STORAGE_CONNECTION_STRING')
            },

            # Microsoft 365
            'm365': {
                'client_id': os.getenv('M365_CLIENT_ID'),
                'client_secret': os.getenv('M365_CLIENT_SECRET'),
                'tenant_id': os.getenv('M365_TENANT_ID'),
                'use_delegated_auth': os.getenv('M365_USE_DELEGATED_AUTH', 'false').lower() == 'true'
            },

            # Azure Cognitive Services
            'cognitive_services': {
                'key': os.getenv('AZURE_COGNITIVE_SERVICES_KEY'),
                'endpoint': os.getenv('AZURE_COGNITIVE_SERVICES_ENDPOINT')
            },

            # OpenAI (for RAG-Anything)
            'openai': {
                'api_key': os.getenv('OPENAI_API_KEY'),
                'base_url': os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
            },

            # Logging
            'logging': {
                'level': os.getenv('LOG_LEVEL', 'INFO'),
                'file': os.getenv('LOG_FILE', 'azure-rag.log')
            },

            # Processing settings
            'processing': {
                'batch_size': int(os.getenv('UPLOAD_BATCH_SIZE', '25')),
                'max_retries': int(os.getenv('UPLOAD_MAX_RETRIES', '3')),
                'timeout': int(os.getenv('UPLOAD_TIMEOUT', '300'))
            }
        }

    def _load_m365_config(self):
        """Load M365-specific configuration from YAML"""
        config_file = self.config_dir / 'm365_config.yaml'

        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    self._config_cache['m365_yaml'] = yaml.safe_load(f)
                self.logger.debug(f"Loaded M365 config from {config_file}")
            except Exception as e:
                self.logger.warning(f"Failed to load M365 config: {e}")
                self._config_cache['m365_yaml'] = {}
        else:
            self.logger.warning(f"M365 config file not found: {config_file}")
            self._config_cache['m365_yaml'] = {}

    def _load_rag_anything_config(self):
        """Load RAG-Anything configuration"""
        self._config_cache['rag_anything'] = {
            'parser': os.getenv('RAG_ANYTHING_PARSER', 'auto'),
            'parse_method': os.getenv('RAG_ANYTHING_PARSE_METHOD', 'auto'),
            'output_dir': os.getenv('RAG_ANYTHING_OUTPUT_DIR', './enhanced_output'),
            'batch_size': int(os.getenv('RAG_ANYTHING_BATCH_SIZE', '25')),
            'enable_table_extraction': os.getenv('ENABLE_TABLE_EXTRACTION', 'true').lower() == 'true',
            'enable_equation_extraction': os.getenv('ENABLE_EQUATION_EXTRACTION', 'true').lower() == 'true',
            'enable_image_processing': os.getenv('ENABLE_IMAGE_PROCESSING', 'true').lower() == 'true',
            'enable_graph_relationships': os.getenv('ENABLE_GRAPH_RELATIONSHIPS', 'true').lower() == 'true'
        }

    def get(self, section: str, key: str = None, default: Any = None) -> Any:
        """Get configuration value by section and optional key"""
        try:
            if key is None:
                return self._config_cache.get(section, default)
            else:
                section_config = self._config_cache.get(section, {})
                return section_config.get(key, default)
        except Exception as e:
            self.logger.error(f"Failed to get config {section}.{key}: {e}")
            return default

    def get_azure_search_config(self) -> Dict[str, Any]:
        """Get Azure AI Search configuration"""
        return self.get('env', 'azure_search', {})

    def get_azure_storage_config(self) -> Dict[str, Any]:
        """Get Azure Storage configuration"""
        return self.get('env', 'azure_storage', {})

    def get_m365_config(self) -> Dict[str, Any]:
        """Get Microsoft 365 configuration"""
        return self.get('env', 'm365', {})

    def get_cognitive_services_config(self) -> Dict[str, Any]:
        """Get Azure Cognitive Services configuration"""
        return self.get('env', 'cognitive_services', {})

    def get_openai_config(self) -> Dict[str, Any]:
        """Get OpenAI configuration"""
        return self.get('env', 'openai', {})

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return self.get('env', 'logging', {})

    def get_processing_config(self) -> Dict[str, Any]:
        """Get processing configuration"""
        return self.get('env', 'processing', {})

    def get_m365_yaml_config(self) -> Dict[str, Any]:
        """Get M365 YAML configuration"""
        return self.get('m365_yaml', default={})

    def get_rag_anything_config(self) -> Dict[str, Any]:
        """Get RAG-Anything configuration"""
        return self.get('rag_anything', default={})

    def validate_required_config(self) -> List[str]:
        """Validate that all required configuration is present"""
        missing = []

        # Azure AI Search
        azure_search = self.get_azure_search_config()
        if not azure_search.get('service_name'):
            missing.append('AZURE_SEARCH_SERVICE_NAME')
        if not azure_search.get('admin_key'):
            missing.append('AZURE_SEARCH_ADMIN_KEY')

        # Azure Storage
        azure_storage = self.get_azure_storage_config()
        if not azure_storage.get('account_name'):
            missing.append('AZURE_STORAGE_ACCOUNT_NAME')
        if not azure_storage.get('account_key'):
            missing.append('AZURE_STORAGE_ACCOUNT_KEY')

        # Microsoft 365
        m365 = self.get_m365_config()
        if not m365.get('client_id'):
            missing.append('M365_CLIENT_ID')
        if not m365.get('client_secret'):
            missing.append('M365_CLIENT_SECRET')
        if not m365.get('tenant_id'):
            missing.append('M365_TENANT_ID')

        return missing

    def get_connection_string(self) -> str:
        """Get storage connection string (Azure or Local)"""
        # Check if local storage is enabled
        if os.getenv('LOCAL_STORAGE_ENABLED', 'false').lower() == 'true':
            return "local://" + os.getenv('LOCAL_STORAGE_PATH', './local_storage')

        # Check if Azure storage is disabled
        if os.getenv('AZURE_STORAGE_ENABLED', 'true').lower() == 'false':
            return "local://" + os.getenv('LOCAL_STORAGE_PATH', './local_storage')

        storage_config = self.get_azure_storage_config()

        # Use explicit connection string if provided
        if storage_config.get('connection_string'):
            return storage_config['connection_string']

        # Build from components
        account_name = storage_config.get('account_name')
        account_key = storage_config.get('account_key')

        if not account_name or not account_key:
            # Fall back to local storage if Azure credentials are missing
            self.logger.warning("Azure Storage credentials missing, falling back to local storage")
            return "local://" + os.getenv('LOCAL_STORAGE_PATH', './local_storage')

        return f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"

    def get_supported_file_extensions(self, source: str = 'sharepoint') -> List[str]:
        """Get supported file extensions for a source"""
        m365_config = self.get_m365_yaml_config()

        if source in m365_config:
            extensions = m365_config[source].get('supported_extensions', [])
            # Add dots to extensions
            return [f'.{ext}' if not ext.startswith('.') else ext for ext in extensions]

        # Default extensions
        return ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt',
                '.txt', '.md', '.json', '.csv', '.html', '.htm', '.rtf',
                '.xml', '.msg', '.eml']

    def get_batch_size(self, source: str = 'sharepoint') -> int:
        """Get batch size for a source"""
        m365_config = self.get_m365_yaml_config()

        if source in m365_config:
            return m365_config[source].get('batch_size', 25)

        return 25

    def get_max_file_size_mb(self, source: str = 'sharepoint') -> int:
        """Get maximum file size in MB for a source"""
        m365_config = self.get_m365_yaml_config()

        if source in m365_config:
            return m365_config[source].get('max_file_size_mb', 100)

        return 100

    def get_progress_file(self, source: str = 'sharepoint') -> str:
        """Get progress file name for a source"""
        m365_config = self.get_m365_yaml_config()

        if source in m365_config:
            return m365_config[source].get('progress_file', f'{source}_progress.json')

        return f'{source}_progress.json'

    def get_rate_limit(self, source: str = 'sharepoint') -> int:
        """Get rate limit for a source"""
        m365_config = self.get_m365_yaml_config()
        sync_config = m365_config.get('sync', {})
        rate_limit_config = sync_config.get('rate_limit', {})

        return rate_limit_config.get(source, 100)

    def get_retry_config(self) -> Dict[str, Any]:
        """Get retry configuration"""
        m365_config = self.get_m365_yaml_config()
        sync_config = m365_config.get('sync', {})
        retry_config = sync_config.get('retry', {})

        return {
            'max_attempts': retry_config.get('max_attempts', 3),
            'base_delay_seconds': retry_config.get('base_delay_seconds', 2),
            'max_delay_seconds': retry_config.get('max_delay_seconds', 30)
        }

    def get_exclusions(self) -> Dict[str, Any]:
        """Get exclusion rules"""
        m365_config = self.get_m365_yaml_config()
        return m365_config.get('exclusions', {})

    def is_incremental_sync_enabled(self) -> bool:
        """Check if incremental sync is enabled"""
        m365_config = self.get_m365_yaml_config()
        sync_config = m365_config.get('sync', {})
        incremental_config = sync_config.get('incremental', {})

        return incremental_config.get('enabled', True)

    def get_incremental_days_back(self) -> int:
        """Get incremental sync days back"""
        m365_config = self.get_m365_yaml_config()
        sync_config = m365_config.get('sync', {})
        incremental_config = sync_config.get('incremental', {})

        return incremental_config.get('days_back', 7)

    def save_config(self, section: str, config: Dict[str, Any]):
        """Save configuration to cache"""
        self._config_cache[section] = config
        self.logger.debug(f"Saved config for section: {section}")

    def reload_config(self):
        """Reload all configuration"""
        self._config_cache.clear()
        self._load_configs()
        self.logger.info("Configuration reloaded")


# Global configuration instance
_config_manager = None

def get_config_manager(config_dir: str = ".", log_level: str = "INFO") -> ConfigManager:
    """Get global configuration manager instance"""
    global _config_manager

    if _config_manager is None:
        _config_manager = ConfigManager(config_dir, log_level)

    return _config_manager


# Convenience functions
def get_config(section: str, key: str = None, default: Any = None) -> Any:
    """Get configuration value"""
    return get_config_manager().get(section, key, default)

def get_azure_search_config() -> Dict[str, Any]:
    """Get Azure AI Search configuration"""
    return get_config_manager().get_azure_search_config()

def get_azure_storage_config() -> Dict[str, Any]:
    """Get Azure Storage configuration"""
    return get_config_manager().get_azure_storage_config()

def get_m365_config() -> Dict[str, Any]:
    """Get Microsoft 365 configuration"""
    return get_config_manager().get_m365_config()

def get_connection_string() -> str:
    """Get Azure Storage connection string"""
    return get_config_manager().get_connection_string()

def validate_required_config() -> List[str]:
    """Validate required configuration"""
    return get_config_manager().validate_required_config()


# Example usage
if __name__ == "__main__":
    # Initialize configuration manager
    config = get_config_manager()

    # Validate configuration
    missing = config.validate_required_config()
    if missing:
        print(f"❌ Missing required configuration: {missing}")
    else:
        print("✅ All required configuration present")

    # Print configuration summary
    print("\n📋 Configuration Summary:")
    print(f"Azure Search: {config.get_azure_search_config().get('service_name', 'Not configured')}")
    print(f"Azure Storage: {config.get_azure_storage_config().get('account_name', 'Not configured')}")
    print(f"M365 Tenant: {config.get_m365_config().get('tenant_id', 'Not configured')}")
    print(f"Log Level: {config.get_logging_config().get('level', 'INFO')}")

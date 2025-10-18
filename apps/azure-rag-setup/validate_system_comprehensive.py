#!/usr/bin/env python3
"""
Comprehensive System Validation Script
Validates all components of the Azure RAG setup using shared utilities
"""

# Standard library imports
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Third-party imports
import requests
from azure.storage.blob import BlobServiceClient

# Local application imports
from config_manager import get_config_manager
from logger import setup_logging
from m365_auth import M365Auth


class SystemValidator:
    """Comprehensive system validation using shared utilities"""

    def __init__(self):
        self.config = get_config_manager()
        self.logger = setup_logging('system-validator', level='INFO')
        self.auth = M365Auth()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'overall_success': False,
            'success_rate': 0.0
        }

    def validate_configuration(self) -> bool:
        """Validate configuration management"""
        self.logger.info("Validating configuration management...")

        try:
            # Test config manager
            missing_vars = self.config.validate_required_config()
            if missing_vars:
                self.logger.error(f"Missing required configuration: {missing_vars}")
                return False

            # Test Azure Search config
            search_config = self.config.get_azure_search_config()
            if not search_config.get('service_name'):
                self.logger.error("Azure Search service name not configured")
                return False

            # Test Azure Storage config
            storage_config = self.config.get_azure_storage_config()
            if not storage_config.get('account_name'):
                self.logger.error("Azure Storage account name not configured")
                return False

            # Test M365 config
            m365_config = self.config.get_m365_config()
            if not m365_config.get('client_id'):
                self.logger.error("M365 client ID not configured")
                return False

            self.logger.info("Configuration validation passed")
            return True

        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False

    def validate_authentication(self) -> bool:
        """Validate M365 authentication"""
        self.logger.info("Validating M365 authentication...")

        try:
            if not self.auth.validate_credentials():
                self.logger.error("M365 credentials validation failed")
                return False

            # Test token retrieval
            token = self.auth.get_access_token()
            if not token:
                self.logger.error("Failed to retrieve access token")
                return False

            self.logger.info("M365 authentication validation passed")
            return True

        except Exception as e:
            self.logger.error(f"M365 authentication validation failed: {e}")
            return False

    def validate_azure_search(self) -> bool:
        """Validate Azure AI Search connectivity"""
        self.logger.info("Validating Azure AI Search connectivity...")

        try:
            search_config = self.config.get_azure_search_config()
            endpoint = search_config.get('endpoint')
            admin_key = search_config.get('admin_key')

            if not endpoint or not admin_key:
                self.logger.error("Azure Search configuration incomplete")
                return False

            # Test search service connectivity
            headers = {
                'api-key': admin_key,
                'Content-Type': 'application/json'
            }

            # Test service stats endpoint
            stats_url = f"{endpoint}/servicestats?api-version=2023-11-01"
            response = requests.get(stats_url, headers=headers, timeout=30)

            if response.status_code != 200:
                self.logger.error(f"Azure Search connectivity failed: {response.status_code}")
                return False

            self.logger.info("Azure AI Search connectivity validation passed")
            return True

        except Exception as e:
            self.logger.error(f"Azure AI Search validation failed: {e}")
            return False

    def validate_azure_storage(self) -> bool:
        """Validate Azure Storage connectivity"""
        self.logger.info("Validating Azure Storage connectivity...")

        try:
            # Test connection string
            connection_string = self.config.get_connection_string()
            blob_service = BlobServiceClient.from_connection_string(connection_string)

            # Test container access
            container_name = self.config.get_azure_storage_config().get('container_name', 'training-data')
            container_client = blob_service.get_container_client(container_name)

            # Test container properties
            properties = container_client.get_container_properties()
            if not properties:
                self.logger.error("Failed to access Azure Storage container")
                return False

            self.logger.info("Azure Storage connectivity validation passed")
            return True

        except Exception as e:
            self.logger.error(f"Azure Storage validation failed: {e}")
            return False

    def validate_m365_indexers(self) -> bool:
        """Validate M365 indexer modules"""
        self.logger.info("Validating M365 indexer modules...")

        try:
            # Test SharePoint indexer
            from m365_sharepoint_indexer import SharePointIndexer
            sharepoint_indexer = SharePointIndexer()
            if not sharepoint_indexer:
                self.logger.error("SharePoint indexer initialization failed")
                return False

            # Test OneDrive indexer
            from m365_onedrive_indexer import OneDriveIndexer
            onedrive_indexer = OneDriveIndexer()
            if not onedrive_indexer:
                self.logger.error("OneDrive indexer initialization failed")
                return False

            # Test Exchange indexer
            from m365_exchange_indexer import ExchangeIndexer
            exchange_indexer = ExchangeIndexer()
            if not exchange_indexer:
                self.logger.error("Exchange indexer initialization failed")
                return False

            self.logger.info("M365 indexer modules validation passed")
            return True

        except Exception as e:
            self.logger.error(f"M365 indexer validation failed: {e}")
            return False

    def validate_rag_anything(self) -> bool:
        """Validate RAG-Anything integration"""
        self.logger.info("Validating RAG-Anything integration...")

        try:
            # Test orchestrator
            from orchestrate_rag_anything import RAGAnythingOrchestrator
            orchestrator = RAGAnythingOrchestrator()
            if not orchestrator:
                self.logger.error("RAG-Anything orchestrator initialization failed")
                return False

            # Test enhanced SharePoint indexer
            from m365_sharepoint_indexer_enhanced import EnhancedSharePointIndexer
            enhanced_indexer = EnhancedSharePointIndexer()
            if not enhanced_indexer:
                self.logger.error("Enhanced SharePoint indexer initialization failed")
                return False

            self.logger.info("RAG-Anything integration validation passed")
            return True

        except Exception as e:
            self.logger.error(f"RAG-Anything validation failed: {e}")
            return False

    def validate_typingmind_config(self) -> bool:
        """Validate TypingMind configuration"""
        self.logger.info("Validating TypingMind configuration...")

        try:
            # Test TypingMind config file
            config_file = Path('typingmind-azure-config.json')
            if not config_file.exists():
                self.logger.error("TypingMind configuration file not found")
                return False

            # Test config generation script
            from generate_typingmind_config import generate_typingmind_config
            if not generate_typingmind_config:
                self.logger.error("TypingMind config generation script not found")
                return False

            self.logger.info("TypingMind configuration validation passed")
            return True

        except Exception as e:
            self.logger.error(f"TypingMind configuration validation failed: {e}")
            return False

    def validate_upload_utilities(self) -> bool:
        """Validate upload utilities"""
        self.logger.info("Validating upload utilities...")

        try:
            # Test upload with retry script
            from upload_with_retry import UploadWithRetry
            uploader = UploadWithRetry()
            if not uploader:
                self.logger.error("Upload with retry utility initialization failed")
                return False

            self.logger.info("Upload utilities validation passed")
            return True

        except Exception as e:
            self.logger.error(f"Upload utilities validation failed: {e}")
            return False

    def validate_maintenance_utilities(self) -> bool:
        """Validate maintenance utilities"""
        self.logger.info("Validating maintenance utilities...")

        try:
            # Test maintenance script
            from maintenance import RAGMaintenance
            maintenance = RAGMaintenance()
            if not maintenance:
                self.logger.error("Maintenance utility initialization failed")
                return False

            self.logger.info("Maintenance utilities validation passed")
            return True

        except Exception as e:
            self.logger.error(f"Maintenance utilities validation failed: {e}")
            return False

    def run_all_validations(self) -> Dict[str, Any]:
        """Run all validation tests"""
        self.logger.info("Starting comprehensive system validation...")

        # Define validation tests
        tests = {
            'configuration': self.validate_configuration,
            'authentication': self.validate_authentication,
            'azure_search': self.validate_azure_search,
            'azure_storage': self.validate_azure_storage,
            'm365_indexers': self.validate_m365_indexers,
            'rag_anything': self.validate_rag_anything,
            'typingmind_config': self.validate_typingmind_config,
            'upload_utilities': self.validate_upload_utilities,
            'maintenance_utilities': self.validate_maintenance_utilities
        }

        # Run all tests
        for test_name, test_func in tests.items():
            try:
                result = test_func()
                self.results['tests'][test_name] = result
                self.logger.info(f"Test '{test_name}': {'PASSED' if result else 'FAILED'}")
            except Exception as e:
                self.logger.error(f"Test '{test_name}' failed with exception: {e}")
                self.results['tests'][test_name] = False

        # Calculate overall results
        test_results = list(self.results['tests'].values())
        self.results['overall_success'] = all(test_results)
        self.results['success_rate'] = sum(test_results) / len(test_results) * 100

        return self.results

    def generate_report(self) -> str:
        """Generate validation report"""
        report = f"""
🧪 Comprehensive System Validation Report
==========================================

Timestamp: {self.results['timestamp']}
Overall Success: {'✅ PASSED' if self.results['overall_success'] else '❌ FAILED'}
Success Rate: {self.results['success_rate']:.1f}%

Test Results:
"""

        for test_name, result in self.results['tests'].items():
            status = "✅ PASSED" if result else "❌ FAILED"
            report += f"  {test_name}: {status}\n"

        report += f"""
Summary:
- Total Tests: {len(self.results['tests'])}
- Passed: {sum(self.results['tests'].values())}
- Failed: {len(self.results['tests']) - sum(self.results['tests'].values())}
- Success Rate: {self.results['success_rate']:.1f}%

Recommendations:
"""

        if not self.results['overall_success']:
            failed_tests = [name for name, result in self.results['tests'].items() if not result]
            report += f"- Fix failed tests: {', '.join(failed_tests)}\n"
        else:
            report += "- All systems are operational and ready for use!\n"

        return report


def main():
    """Main validation function"""
    print("🧪 Azure RAG Setup - Comprehensive System Validation")
    print("=" * 60)

    # Initialize validator
    validator = SystemValidator()

    # Run all validations
    results = validator.run_all_validations()

    # Generate and display report
    report = validator.generate_report()
    print(report)

    # Save results to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f"validation_results_{timestamp}.json"

    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n📄 Detailed results saved to: {results_file}")

    # Exit with appropriate code
    sys.exit(0 if results['overall_success'] else 1)


if __name__ == "__main__":
    main()

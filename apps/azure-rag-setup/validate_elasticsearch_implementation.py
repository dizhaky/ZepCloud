#!/usr/bin/env python3
"""
Comprehensive validation script for Elasticsearch + RAG-Anything + OlmoCR implementation
Validates all components are ready for testing and deployment
"""
import os
import sys
import json
import subprocess
import requests
from pathlib import Path
from datetime import datetime

class ElasticsearchImplementationValidator:
    """Validate complete Elasticsearch implementation"""

    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'UNKNOWN',
            'components': {},
            'issues': [],
            'recommendations': []
        }
        self.base_dir = Path.cwd()

    def validate_file_structure(self):
        """Validate all required files are present"""
        print("🔍 Validating file structure...")

        required_files = {
            'Infrastructure': [
                'docker-compose.yml',
                'env.elasticsearch',
                'config_elasticsearch.py',
                'elasticsearch_setup.py'
            ],
            'API Layer': [
                'api_server.py',
                'query_interface.py',
                'm365_sync_elasticsearch.py'
            ],
            'Testing': [
                'test_elasticsearch_integration.py',
                'requirements-elasticsearch.txt'
            ],
            'Configuration': [
                'typingmind-elasticsearch-config.json'
            ],
            'Documentation': [
                'ELASTICSEARCH_SETUP_GUIDE.md',
                'ELASTICSEARCH_IMPLEMENTATION_COMPLETE.md',
                'ELASTICSEARCH_READY_FOR_TESTING.md',
                'ELASTICSEARCH_TESTING_GUIDE.md',
                'ELASTICSEARCH_DEPLOYMENT_CHECKLIST.md',
                'AGENT_HANDOFF_SUMMARY.md'
            ]
        }

        missing_files = []
        present_files = []

        for category, files in required_files.items():
            category_status = []
            for file in files:
                file_path = self.base_dir / file
                if file_path.exists():
                    present_files.append(file)
                    category_status.append(f"✅ {file}")
                else:
                    missing_files.append(file)
                    category_status.append(f"❌ {file}")

            self.results['components'][category] = {
                'status': 'COMPLETE' if not any(f in missing_files for f in files) else 'INCOMPLETE',
                'files': category_status
            }

        if missing_files:
            self.results['issues'].append(f"Missing files: {', '.join(missing_files)}")

        print(f"✅ Found {len(present_files)} files")
        if missing_files:
            print(f"❌ Missing {len(missing_files)} files: {', '.join(missing_files)}")

        return len(missing_files) == 0

    def validate_utils_directory(self):
        """Validate utils directory structure"""
        print("🔍 Validating utils directory...")

        utils_dir = self.base_dir / 'utils'
        if not utils_dir.exists():
            self.results['issues'].append("utils/ directory missing")
            return False

        required_utils = [
            'bulk_indexer.py',
            'graph_client.py',
            'document_processor.py',
            'olmocr_processor.py',
            'raganything_processor.py',
            'elasticsearch_graph_builder.py'
        ]

        missing_utils = []
        for util in required_utils:
            if not (utils_dir / util).exists():
                missing_utils.append(util)

        if missing_utils:
            self.results['issues'].append(f"Missing utils: {', '.join(missing_utils)}")
            return False

        print(f"✅ All {len(required_utils)} utils files present")
        return True

    def validate_docker_compose(self):
        """Validate docker-compose.yml configuration"""
        print("🔍 Validating docker-compose.yml...")

        compose_file = self.base_dir / 'docker-compose.yml'
        if not compose_file.exists():
            self.results['issues'].append("docker-compose.yml missing")
            return False

        try:
            with open(compose_file, 'r') as f:
                content = f.read()

            # Check for required services
            required_services = ['elasticsearch', 'kibana', 'tika']
            missing_services = []

            for service in required_services:
                if f"  {service}:" not in content:
                    missing_services.append(service)

            if missing_services:
                self.results['issues'].append(f"Missing services in docker-compose.yml: {', '.join(missing_services)}")
                return False

            print("✅ Docker Compose configuration valid")
            return True

        except Exception as e:
            self.results['issues'].append(f"Error reading docker-compose.yml: {e}")
            return False

    def validate_environment_config(self):
        """Validate environment configuration"""
        print("🔍 Validating environment configuration...")

        env_file = self.base_dir / 'env.elasticsearch'
        if not env_file.exists():
            self.results['issues'].append("env.elasticsearch missing")
            return False

        try:
            with open(env_file, 'r') as f:
                content = f.read()

            # Check for required variables
            required_vars = [
                'ELASTIC_HOST',
                'ELASTIC_USERNAME',
                'ELASTIC_PASSWORD',
                'ELASTIC_INDEX',
                'TIKA_HOST',
                'AZURE_TENANT_ID',
                'AZURE_CLIENT_ID',
                'AZURE_CLIENT_SECRET'
            ]

            missing_vars = []
            for var in required_vars:
                if f"{var}=" not in content:
                    missing_vars.append(var)

            if missing_vars:
                self.results['issues'].append(f"Missing environment variables: {', '.join(missing_vars)}")
                return False

            # Check for placeholder values
            if 'your-tenant-id-here' in content or 'your-client-id-here' in content:
                self.results['recommendations'].append("Update Azure credentials in env.elasticsearch")

            print("✅ Environment configuration valid")
            return True

        except Exception as e:
            self.results['issues'].append(f"Error reading env.elasticsearch: {e}")
            return False

    def validate_requirements(self):
        """Validate Python requirements"""
        print("🔍 Validating Python requirements...")

        req_file = self.base_dir / 'requirements-elasticsearch.txt'
        if not req_file.exists():
            self.results['issues'].append("requirements-elasticsearch.txt missing")
            return False

        try:
            with open(req_file, 'r') as f:
                requirements = f.read().strip().split('\n')

            # Check for key dependencies
            key_deps = [
                'elasticsearch',
                'requests',
                'python-dotenv',
                'tqdm',
                'flask'
            ]

            missing_deps = []
            for dep in key_deps:
                if not any(dep in req for req in requirements):
                    missing_deps.append(dep)

            if missing_deps:
                self.results['issues'].append(f"Missing key dependencies: {', '.join(missing_deps)}")
                return False

            print(f"✅ Found {len(requirements)} dependencies")
            return True

        except Exception as e:
            self.results['issues'].append(f"Error reading requirements: {e}")
            return False

    def validate_test_suite(self):
        """Validate test suite configuration"""
        print("🔍 Validating test suite...")

        test_file = self.base_dir / 'test_elasticsearch_integration.py'
        if not test_file.exists():
            self.results['issues'].append("test_elasticsearch_integration.py missing")
            return False

        try:
            with open(test_file, 'r') as f:
                content = f.read()

            # Check for required test functions
            required_tests = [
                'test_elasticsearch_connection',
                'test_tika_connection',
                'test_api_server',
                'test_search_functionality',
                'test_enhanced_features',
                'test_multimodal_search',
                'test_entity_search',
                'test_stats_endpoint'
            ]

            missing_tests = []
            for test in required_tests:
                if f"def {test}(" not in content:
                    missing_tests.append(test)

            if missing_tests:
                self.results['issues'].append(f"Missing test functions: {', '.join(missing_tests)}")
                return False

            print(f"✅ Found {len(required_tests)} test functions")
            return True

        except Exception as e:
            self.results['issues'].append(f"Error reading test file: {e}")
            return False

    def validate_typingmind_config(self):
        """Validate TypingMind configuration"""
        print("🔍 Validating TypingMind configuration...")

        config_file = self.base_dir / 'typingmind-elasticsearch-config.json'
        if not config_file.exists():
            self.results['issues'].append("typingmind-elasticsearch-config.json missing")
            return False

        try:
            with open(config_file, 'r') as f:
                config = json.load(f)

            # Check for required fields
            required_fields = ['name', 'endpoints']
            missing_fields = []

            for field in required_fields:
                if field not in config:
                    missing_fields.append(field)

            if missing_fields:
                self.results['issues'].append(f"Missing TypingMind config fields: {', '.join(missing_fields)}")
                return False

            # Check endpoints
            endpoints = config.get('endpoints', {})
            required_endpoints = ['base_url', 'search', 'health']
            missing_endpoints = []

            for endpoint in required_endpoints:
                if endpoint not in endpoints:
                    missing_endpoints.append(endpoint)

            if missing_endpoints:
                self.results['issues'].append(f"Missing TypingMind endpoints: {', '.join(missing_endpoints)}")
                return False

            print("✅ TypingMind configuration valid")
            return True

        except Exception as e:
            self.results['issues'].append(f"Error reading TypingMind config: {e}")
            return False

    def validate_documentation(self):
        """Validate documentation completeness"""
        print("🔍 Validating documentation...")

        doc_files = [
            'ELASTICSEARCH_SETUP_GUIDE.md',
            'ELASTICSEARCH_IMPLEMENTATION_COMPLETE.md',
            'ELASTICSEARCH_READY_FOR_TESTING.md',
            'ELASTICSEARCH_TESTING_GUIDE.md',
            'ELASTICSEARCH_DEPLOYMENT_CHECKLIST.md',
            'AGENT_HANDOFF_SUMMARY.md'
        ]

        missing_docs = []
        for doc in doc_files:
            if not (self.base_dir / doc).exists():
                missing_docs.append(doc)

        if missing_docs:
            self.results['issues'].append(f"Missing documentation: {', '.join(missing_docs)}")
            return False

        print(f"✅ All {len(doc_files)} documentation files present")
        return True

    def check_docker_availability(self):
        """Check if Docker is available"""
        print("🔍 Checking Docker availability...")

        try:
            result = subprocess.run(['docker', '--version'],
                                 capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Docker available")
                return True
            else:
                self.results['issues'].append("Docker not available")
                return False
        except Exception as e:
            self.results['issues'].append(f"Docker check failed: {e}")
            return False

    def check_python_environment(self):
        """Check Python environment"""
        print("🔍 Checking Python environment...")

        try:
            # Check Python version
            if sys.version_info < (3, 8):
                self.results['issues'].append(f"Python 3.8+ required, found {sys.version}")
                return False

            # Check if we can import key modules
            import requests
            import json
            from datetime import datetime

            print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} available")
            return True

        except ImportError as e:
            self.results['issues'].append(f"Missing Python module: {e}")
            return False

    def generate_summary(self):
        """Generate validation summary"""
        print("\n" + "="*60)
        print("📊 ELASTICSEARCH IMPLEMENTATION VALIDATION SUMMARY")
        print("="*60)

        total_checks = 8
        passed_checks = 0

        checks = [
            ("File Structure", self.validate_file_structure()),
            ("Utils Directory", self.validate_utils_directory()),
            ("Docker Compose", self.validate_docker_compose()),
            ("Environment Config", self.validate_environment_config()),
            ("Python Requirements", self.validate_requirements()),
            ("Test Suite", self.validate_test_suite()),
            ("TypingMind Config", self.validate_typingmind_config()),
            ("Documentation", self.validate_documentation())
        ]

        for check_name, result in checks:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{check_name}: {status}")
            if result:
                passed_checks += 1

        # Additional system checks
        print("\n🔧 System Environment Checks:")
        docker_ok = self.check_docker_availability()
        python_ok = self.check_python_environment()

        docker_status = "✅ AVAILABLE" if docker_ok else "❌ NOT AVAILABLE"
        python_status = "✅ AVAILABLE" if python_ok else "❌ NOT AVAILABLE"

        print(f"Docker: {docker_status}")
        print(f"Python: {python_status}")

        # Overall status
        total_system_checks = 2
        system_passed = sum([docker_ok, python_ok])

        overall_passed = passed_checks + system_passed
        overall_total = total_checks + total_system_checks

        print(f"\n📈 Overall Status: {overall_passed}/{overall_total} checks passed ({overall_passed/overall_total*100:.1f}%)")

        if overall_passed == overall_total:
            self.results['overall_status'] = 'READY_FOR_TESTING'
            print("\n🎉 IMPLEMENTATION READY FOR TESTING!")
            print("\nNext Steps:")
            print("1. Start infrastructure: docker-compose up -d")
            print("2. Run tests: python test_elasticsearch_integration.py")
            print("3. Start API: python api_server.py")
            print("4. Sync data: python m365_sync_elasticsearch.py")
        else:
            self.results['overall_status'] = 'ISSUES_FOUND'
            print(f"\n⚠️ {overall_total - overall_passed} issues found. Please address before testing.")

        # Issues and recommendations
        if self.results['issues']:
            print(f"\n🚨 Issues Found ({len(self.results['issues'])}):")
            for i, issue in enumerate(self.results['issues'], 1):
                print(f"  {i}. {issue}")

        if self.results['recommendations']:
            print(f"\n💡 Recommendations ({len(self.results['recommendations'])}):")
            for i, rec in enumerate(self.results['recommendations'], 1):
                print(f"  {i}. {rec}")

        return overall_passed == overall_total

    def save_results(self):
        """Save validation results to file"""
        results_file = self.base_dir / 'elasticsearch_validation_results.json'
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📄 Results saved to: {results_file}")

def main():
    """Main validation function"""
    print("🔍 Elasticsearch + RAG-Anything + OlmoCR Implementation Validation")
    print("="*70)

    validator = ElasticsearchImplementationValidator()
    success = validator.generate_summary()
    validator.save_results()

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

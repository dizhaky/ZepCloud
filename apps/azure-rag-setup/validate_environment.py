#!/usr/bin/env python3
"""
Environment validation script for Azure RAG setup
Validates all required environment variables and dependencies
"""

# Standard library imports
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Third-party imports
from dotenv import load_dotenv

# Local application imports
from config_manager import get_config_manager
from logger import setup_logging


# Required environment variables
REQUIRED_VARS = {
    'AZURE_SEARCH_SERVICE_NAME': 'Azure AI Search service name',
    'AZURE_SEARCH_ADMIN_KEY': 'Azure AI Search admin key',
    'AZURE_SEARCH_ENDPOINT': 'Azure AI Search endpoint URL',
    'AZURE_STORAGE_ACCOUNT_NAME': 'Azure Storage account name',
    'AZURE_STORAGE_ACCOUNT_KEY': 'Azure Storage account key',
}

# Optional environment variables
OPTIONAL_VARS = {
    'AZURE_SEARCH_INDEX_NAME': 'Azure AI Search index name (default: training-data-index)',
    'AZURE_STORAGE_CONTAINER_NAME': 'Azure Storage container name (default: training-data)',
}

# Required Python packages
REQUIRED_PACKAGES = [
    'azure.storage.blob',
    'azure.search.documents',
    'azure.identity',
    'azure.core',
    'dotenv',
    'requests',
    'tenacity',
    'tqdm',
]


def check_env_file() -> bool:
    """Check if .env file exists"""
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found")
        print("   Create .env file from env.example:")
        print("   cp env.example .env")
        return False
    print("✅ .env file exists")
    return True


def check_environment_variables() -> Tuple[bool, List[str]]:
    """Check required environment variables"""
    load_dotenv()

    missing = []
    found = []

    print("\n📋 Checking required environment variables...")

    for var, desc in REQUIRED_VARS.items():
        value = os.getenv(var)
        if not value:
            missing.append(f"  ❌ {var}: {desc}")
        else:
            # Show partial value for security
            masked_value = value[:8] + '...' if len(value) > 8 else '***'
            found.append(f"  ✅ {var}: {masked_value}")

    # Display results
    for msg in found:
        print(msg)

    if missing:
        print("\n❌ Missing required variables:")
        for msg in missing:
            print(msg)
        return False, missing

    print("✅ All required environment variables are set")

    # Check optional variables
    print("\n📋 Checking optional environment variables...")
    for var, desc in OPTIONAL_VARS.items():
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {value}")
        else:
            print(f"  ℹ️  {var}: Not set (will use default)")

    return True, []


def check_python_packages() -> Tuple[bool, List[str]]:
    """Check required Python packages"""
    print("\n📦 Checking required Python packages...")

    missing = []
    found = []

    for package in REQUIRED_PACKAGES:
        try:
            __import__(package.replace('.', '/').split('/')[0])
            found.append(f"  ✅ {package}")
        except ImportError:
            missing.append(package)

    # Display results
    for msg in found:
        print(msg)

    if missing:
        print("\n❌ Missing required packages:")
        for package in missing:
            print(f"  ❌ {package}")
        print("\n📥 Install missing packages:")
        print("  pip install -r requirements.txt")
        return False, missing

    print("✅ All required packages are installed")
    return True, []


def check_azure_connectivity() -> bool:
    """Check Azure service connectivity"""
    print("\n🌐 Checking Azure connectivity...")

    try:
        from azure.search.documents.indexes import SearchIndexClient
        from azure.core.credentials import AzureKeyCredential

        endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
        admin_key = os.getenv('AZURE_SEARCH_ADMIN_KEY')

        if not endpoint or not admin_key:
            print("  ⚠️  Skipping connectivity check (credentials not available)")
            return True

        # Try to connect
        client = SearchIndexClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(admin_key)
        )

        # List indexes (lightweight operation)
        indexes = list(client.list_indexes())
        print(f"  ✅ Connected to Azure AI Search ({len(indexes)} indexes found)")
        return True

    except Exception as e:
        print(f"  ❌ Failed to connect to Azure: {e}")
        print("  ⚠️  Check your credentials and network connection")
        return False


def check_file_structure() -> bool:
    """Check required files exist"""
    print("\n📁 Checking file structure...")

    required_files = [
        'requirements.txt',
        'env.example',
        'configure-indexer.py',
        'maintenance.py',
        'upload_with_retry.py',
    ]

    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} (missing)")
            all_exist = False

    if all_exist:
        print("✅ All required files exist")
    else:
        print("⚠️  Some files are missing")

    return all_exist


def generate_report() -> Dict[str, bool]:
    """Generate validation report"""
    report = {
        'env_file': check_env_file(),
        'environment_variables': False,
        'python_packages': False,
        'azure_connectivity': False,
        'file_structure': False,
    }

    if report['env_file']:
        env_valid, _ = check_environment_variables()
        report['environment_variables'] = env_valid

        packages_valid, _ = check_python_packages()
        report['python_packages'] = packages_valid

        if env_valid and packages_valid:
            report['azure_connectivity'] = check_azure_connectivity()

    report['file_structure'] = check_file_structure()

    return report


def print_summary(report: Dict[str, bool]) -> None:
    """Print validation summary"""
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)

    checks = [
        ('Environment file (.env)', report['env_file']),
        ('Environment variables', report['environment_variables']),
        ('Python packages', report['python_packages']),
        ('Azure connectivity', report['azure_connectivity']),
        ('File structure', report['file_structure']),
    ]

    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check_name}")

    # Overall status
    all_passed = all(report.values())
    print("\n" + "=" * 50)

    if all_passed:
        print("✅ ENVIRONMENT VALIDATION PASSED")
        print("🚀 You're ready to run the Azure RAG setup!")
    else:
        print("❌ ENVIRONMENT VALIDATION FAILED")
        print("⚠️  Fix the issues above before proceeding")

    print("=" * 50)


def main() -> int:
    """Main validation process"""
    print("🔍 Azure RAG Environment Validation")
    print("=" * 50)

    # Generate report
    report = generate_report()

    # Print summary
    print_summary(report)

    # Return status
    return 0 if all(report.values()) else 1


if __name__ == "__main__":
    sys.exit(main())


#!/usr/bin/env python3
"""
Complete System Validation Script
Validates that all M365 integration components are working correctly
"""

# Standard library imports
import sys
import json
from pathlib import Path
from datetime import datetime

# Local application imports
from config_manager import get_config_manager
from logger import setup_logging

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing module imports...")

    try:
        from m365_auth import M365Auth
        print("✅ m365_auth imported")
    except Exception as e:
        print(f"❌ m365_auth failed: {e}")
        return False

    try:
        from estimate_m365_volume import M365VolumeEstimator
        print("✅ estimate_m365_volume imported")
    except Exception as e:
        print(f"❌ estimate_m365_volume failed: {e}")
        return False

    try:
        from m365_sharepoint_indexer import SharePointIndexer
        print("✅ m365_sharepoint_indexer imported")
    except Exception as e:
        print(f"❌ m365_sharepoint_indexer failed: {e}")
        return False

    try:
        from m365_onedrive_indexer import OneDriveIndexer
        print("✅ m365_onedrive_indexer imported")
    except Exception as e:
        print(f"❌ m365_onedrive_indexer failed: {e}")
        return False

    try:
        from m365_exchange_indexer import ExchangeIndexer
        print("✅ m365_exchange_indexer imported")
    except Exception as e:
        print(f"❌ m365_exchange_indexer failed: {e}")
        return False

    try:
        from m365_indexer import M365IndexerCLI
        print("✅ m365_indexer imported")
    except Exception as e:
        print(f"❌ m365_indexer failed: {e}")
        return False

    return True

def test_file_structure():
    """Test that all required files exist"""
    print("\n🧪 Testing file structure...")

    required_files = [
        'm365_auth.py',
        'estimate_m365_volume.py',
        'm365_sharepoint_indexer.py',
        'm365_onedrive_indexer.py',
        'm365_exchange_indexer.py',
        'm365_indexer.py',
        'm365_config.yaml',
        'setup_azure_ad_1password.sh',
        'get_m365_credentials.sh',
        'M365_INTEGRATION_GUIDE.md',
        '1PASSWORD_SETUP_GUIDE.md',
        'M365_COMPLETE_IMPLEMENTATION.md'
    ]

    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} missing")
            all_exist = False

    return all_exist

def test_cli_commands():
    """Test that CLI commands work"""
    print("\n🧪 Testing CLI commands...")

    import subprocess

    commands = [
        ['python3', 'm365_indexer.py', '--help'],
        ['python3', 'm365_indexer.py', 'test-auth', '--help'],
        ['python3', 'm365_indexer.py', 'estimate', '--help'],
        ['python3', 'm365_indexer.py', 'sync-sharepoint', '--help'],
        ['python3', 'm365_indexer.py', 'sync-onedrive', '--help'],
        ['python3', 'm365_indexer.py', 'sync-exchange', '--help'],
        ['python3', 'm365_indexer.py', 'sync', '--help'],
        ['python3', 'm365_indexer.py', 'status', '--help']
    ]

    all_work = True
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ {' '.join(cmd)}")
            else:
                print(f"❌ {' '.join(cmd)} - {result.stderr}")
                all_work = False
        except Exception as e:
            print(f"❌ {' '.join(cmd)} - {e}")
            all_work = False

    return all_work

def test_config_loading():
    """Test configuration loading"""
    print("\n🧪 Testing configuration loading...")

    try:
        import yaml
        with open('m365_config.yaml', 'r') as f:
            config = yaml.safe_load(f)

        required_sections = ['sharepoint', 'onedrive', 'exchange', 'azure_storage', 'sync']
        all_sections = True

        for section in required_sections:
            if section in config:
                print(f"✅ {section} configuration")
            else:
                print(f"❌ {section} configuration missing")
                all_sections = False

        return all_sections
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False

def test_setup_scripts():
    """Test setup scripts are executable"""
    print("\n🧪 Testing setup scripts...")

    scripts = [
        'setup_azure_ad_1password.sh',
        'get_m365_credentials.sh'
    ]

    all_executable = True
    for script in scripts:
        if Path(script).exists():
            if Path(script).stat().st_mode & 0o111:  # Check if executable
                print(f"✅ {script} is executable")
            else:
                print(f"❌ {script} is not executable")
                all_executable = False
        else:
            print(f"❌ {script} not found")
            all_executable = False

    return all_executable

def test_maintenance_integration():
    """Test maintenance.py integration"""
    print("\n🧪 Testing maintenance integration...")

    try:
        import subprocess
        result = subprocess.run([
            'python3', 'maintenance.py', '--non-interactive', '--action', 'health'
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("✅ maintenance.py health check works")
            return True
        else:
            print(f"❌ maintenance.py health check failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ maintenance.py test failed: {e}")
        return False

def generate_validation_report():
    """Generate comprehensive validation report"""
    print("\n📊 Generating validation report...")

    report = {
        'timestamp': datetime.now().isoformat(),
        'tests': {
            'imports': test_imports(),
            'file_structure': test_file_structure(),
            'cli_commands': test_cli_commands(),
            'config_loading': test_config_loading(),
            'setup_scripts': test_setup_scripts(),
            'maintenance_integration': test_maintenance_integration()
        }
    }

    # Calculate overall success
    all_tests = report['tests'].values()
    report['overall_success'] = all(all_tests)
    report['success_rate'] = sum(all_tests) / len(all_tests) * 100

    return report

def main():
    """Run complete system validation"""
    print("🚀 Microsoft 365 Integration - Complete System Validation")
    print("=" * 60)

    # Run all tests
    report = generate_validation_report()

    # Print results
    print("\n" + "=" * 60)
    print("📊 VALIDATION RESULTS")
    print("=" * 60)

    for test_name, result in report['tests'].items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")

    print(f"\nOverall Success Rate: {report['success_rate']:.1f}%")

    if report['overall_success']:
        print("\n🎉 ALL TESTS PASSED - SYSTEM IS READY!")
        print("\n📋 Next Steps:")
        print("1. Set up Azure AD app: ./setup_azure_ad_1password.sh")
        print("2. Test authentication: ./get_m365_credentials.sh")
        print("3. Estimate volume: python3 m365_indexer.py estimate")
        print("4. Start indexing: python3 m365_indexer.py sync-sharepoint")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED - CHECK ERRORS ABOVE")
        return 1

if __name__ == "__main__":
    exit(main())

#!/usr/bin/env python3
"""
Azure RAG Setup Test Script
Tests the installation and basic functionality of the Azure RAG setup
"""

import os
import sys
import subprocess
from pathlib import Path

def test_python_imports():
    """Test if required Python packages can be imported"""
    print("🐍 Testing Python imports...")

    required_packages = [
        'azure.storage.blob',
        'azure.search.documents',
        'azure.core.credentials',
        'dotenv'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n⚠️  Missing packages: {missing_packages}")
        print("💡 Run: pip install -r requirements.txt")
        return False

    print("✅ All Python packages available")
    return True

def test_azure_cli():
    """Test if Azure CLI is available"""
    print("🔧 Testing Azure CLI...")

    try:
        result = subprocess.run(['az', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Azure CLI is available")
            return True
        else:
            print("❌ Azure CLI not working")
            return False
    except FileNotFoundError:
        print("❌ Azure CLI not found")
        print("💡 Install with: brew install azure-cli")
        return False

def test_environment_file():
    """Test if environment file exists"""
    print("📄 Testing environment configuration...")

    env_file = Path('.env')
    env_example = Path('env.example')

    if env_file.exists():
        print("✅ .env file exists")
        return True
    elif env_example.exists():
        print("⚠️  .env file not found, but env.example exists")
        print("💡 Copy env.example to .env and fill in your Azure credentials")
        return False
    else:
        print("❌ No environment configuration found")
        return False

def test_script_permissions():
    """Test if scripts are executable"""
    print("🔐 Testing script permissions...")

    scripts = [
        'azure-setup.sh',
        'upload-training-data.py',
        'configure-indexer.py',
        'generate-typingmind-config.py',
        'maintenance.py'
    ]

    all_executable = True

    for script in scripts:
        script_path = Path(script)
        if script_path.exists():
            if os.access(script_path, os.X_OK):
                print(f"  ✅ {script}")
            else:
                print(f"  ❌ {script} (not executable)")
                all_executable = False
        else:
            print(f"  ❌ {script} (not found)")
            all_executable = False

    return all_executable

def test_onedrive_paths():
    """Test if OneDrive paths are accessible"""
    print("📁 Testing OneDrive paths...")

    home = Path.home()
    possible_paths = [
        home / "Library/CloudStorage/OneDrive-Personal",
        home / "Library/CloudStorage/OneDrive-UnitedSafetyTechnologyInc",
        home / "OneDrive - AES",
        home / "OneDrive"
    ]

    accessible_paths = []

    for path in possible_paths:
        if path.exists():
            accessible_paths.append(str(path))
            print(f"  ✅ {path}")
        else:
            print(f"  ❌ {path}")

    if accessible_paths:
        print(f"✅ Found {len(accessible_paths)} accessible OneDrive paths")
        return True
    else:
        print("⚠️  No OneDrive paths found")
        print("💡 Make sure OneDrive is synced to your Mac")
        return False

def main():
    """Run all tests"""
    print("🧪 Azure RAG Setup Test")
    print("=" * 40)

    tests = [
        ("Python Imports", test_python_imports),
        ("Azure CLI", test_azure_cli),
        ("Environment Config", test_environment_file),
        ("Script Permissions", test_script_permissions),
        ("OneDrive Paths", test_onedrive_paths)
    ]

    results = {}

    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}")
        print("-" * 20)
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Error in {test_name}: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 40)
    print("📊 TEST SUMMARY")
    print("=" * 40)

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Your setup is ready.")
        print("🚀 Next steps:")
        print("  1. Run: ./azure-setup.sh")
        print("  2. Run: python3 upload-training-data.py")
        print("  3. Run: python3 configure-indexer.py")
        print("  4. Run: python3 generate-typingmind-config.py")
    else:
        print("\n⚠️  Some tests failed. Please address the issues above.")
        print("💡 Check the troubleshooting section in README.md")

    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())

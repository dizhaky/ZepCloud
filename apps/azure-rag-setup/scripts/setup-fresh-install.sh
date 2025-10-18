#!/bin/bash
# Azure RAG Setup - Fresh Installation Script
# This script sets up the complete Azure RAG system from scratch

set -e  # Exit on any error

echo "🚀 Azure RAG Setup - Fresh Installation"
echo "========================================"
echo ""

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Error: Please run this script from the azure-rag-setup directory"
    exit 1
fi

echo "📋 Prerequisites Check"
echo "----------------------"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if [[ $(echo "$PYTHON_VERSION < 3.8" | bc -l) -eq 1 ]]; then
    echo "❌ Error: Python 3.8+ is required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python 3.8+ found: $PYTHON_VERSION"

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is not installed"
    exit 1
fi

echo "✅ pip3 found"

# Check 1Password CLI
if ! command -v op &> /dev/null; then
    echo "⚠️  Warning: 1Password CLI not found. Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install 1password-cli
    else
        echo "❌ Error: Please install 1Password CLI manually"
        exit 1
    fi
fi

echo "✅ 1Password CLI found"

echo ""
echo "📦 Installing Dependencies"
echo "--------------------------"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Dependencies installed"

echo ""
echo "🔧 Environment Setup"
echo "-------------------"

# Copy environment template
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp env.example .env
    echo "✅ .env file created"
    echo "⚠️  Please edit .env file with your Azure credentials"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🔐 Security Setup"
echo "-----------------"

# Check if 1Password is signed in
if ! op account list &> /dev/null; then
    echo "⚠️  1Password CLI not signed in. Please sign in:"
    op signin
fi

echo "✅ 1Password CLI ready"

echo ""
echo "🧪 System Validation"
echo "-------------------"

# Validate environment
echo "Validating environment..."
python3 validate_environment.py

echo "✅ Environment validation passed"

echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Azure credentials"
echo "2. Run: ./setup_azure_ad_1password.sh"
echo "3. Run: python3 m365_indexer.py test-auth"
echo "4. Run: python3 m365_indexer.py estimate"
echo "5. Run: python3 m365_indexer.py sync-sharepoint"
echo ""
echo "For detailed instructions, see:"
echo "- README.md - Quick start guide"
echo "- docs/DEPLOYMENT.md - Complete deployment guide"
echo "- docs/INDEX.md - Documentation index"
echo ""
echo "🚀 Ready to go!"


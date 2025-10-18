#!/bin/bash
# Azure RAG Setup - Quick Test Script
# This script runs a quick test of all system components

set -e  # Exit on any error

echo "🧪 Azure RAG Setup - Quick Test"
echo "==============================="
echo ""

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Error: Please run this script from the azure-rag-setup directory"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "🔍 Testing System Components"
echo "---------------------------"

# Test 1: Environment validation
echo "1. Testing environment validation..."
if python3 validate_environment.py; then
    echo "   ✅ Environment validation passed"
else
    echo "   ❌ Environment validation failed"
    exit 1
fi

# Test 2: System health
echo "2. Testing system health..."
if python3 maintenance.py --non-interactive --action health; then
    echo "   ✅ System health check passed"
else
    echo "   ❌ System health check failed"
    exit 1
fi

# Test 3: M365 authentication
echo "3. Testing M365 authentication..."
if python3 m365_indexer.py test-auth; then
    echo "   ✅ M365 authentication passed"
else
    echo "   ❌ M365 authentication failed"
    exit 1
fi

# Test 4: Azure connectivity
echo "4. Testing Azure connectivity..."
if python3 maintenance.py --non-interactive --action status; then
    echo "   ✅ Azure connectivity passed"
else
    echo "   ❌ Azure connectivity failed"
    exit 1
fi

# Test 5: RAG-Anything integration
echo "5. Testing RAG-Anything integration..."
if python3 -m pytest test_rag_anything_integration.py -v; then
    echo "   ✅ RAG-Anything integration passed"
else
    echo "   ❌ RAG-Anything integration failed"
    exit 1
fi

# Test 6: TypingMind configuration
echo "6. Testing TypingMind configuration..."
if python3 verify_typingmind_config.py; then
    echo "   ✅ TypingMind configuration passed"
else
    echo "   ❌ TypingMind configuration failed"
    exit 1
fi

echo ""
echo "🎉 All Tests Passed!"
echo "==================="
echo ""
echo "System Status:"
echo "✅ Environment: Valid"
echo "✅ System Health: Good"
echo "✅ M365 Authentication: Working"
echo "✅ Azure Connectivity: Working"
echo "✅ RAG-Anything: Working"
echo "✅ TypingMind: Configured"
echo ""
echo "🚀 System is ready for production use!"
echo ""
echo "Next steps:"
echo "1. Run: python3 m365_indexer.py estimate"
echo "2. Run: python3 m365_indexer.py sync-sharepoint"
echo "3. Run: python3 orchestrate_rag_anything.py --source sharepoint --limit 2"
echo "4. Test search in TypingMind"
echo ""
echo "For detailed instructions, see:"
echo "- README.md - Quick start guide"
echo "- docs/DEPLOYMENT.md - Complete deployment guide"
echo "- docs/TESTING.md - Testing guide"


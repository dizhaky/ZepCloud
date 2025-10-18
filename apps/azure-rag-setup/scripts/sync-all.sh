#!/bin/bash
# Azure RAG Setup - Sync All M365 Sources
# This script syncs all M365 data sources

set -e  # Exit on any error

echo "🔄 Azure RAG Setup - Sync All M365 Sources"
echo "=========================================="
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

echo "🔍 Pre-Sync Validation"
echo "---------------------"

# Test authentication
echo "Testing M365 authentication..."
if python3 m365_indexer.py test-auth; then
    echo "✅ M365 authentication successful"
else
    echo "❌ M365 authentication failed"
    exit 1
fi

# Check system health
echo "Checking system health..."
if python3 maintenance.py --non-interactive --action health; then
    echo "✅ System health check passed"
else
    echo "❌ System health check failed"
    exit 1
fi

echo ""
echo "📊 Volume Estimation"
echo "-------------------"

# Estimate data volume
echo "Estimating data volume..."
python3 m365_indexer.py estimate

echo ""
echo "🔄 Starting M365 Sync"
echo "--------------------"

# Sync all M365 sources
echo "Syncing all M365 sources..."
python3 m365_indexer.py sync

echo ""
echo "🧠 Enhanced Features Sync"
echo "------------------------"

# Sync enhanced features
echo "Syncing enhanced features..."
python3 orchestrate_rag_anything.py --source sharepoint

echo ""
echo "📊 Post-Sync Status"
echo "------------------"

# Check sync status
echo "Checking sync status..."
python3 m365_indexer.py status

# Check system health
echo "Checking system health..."
python3 maintenance.py --non-interactive --action health

echo ""
echo "🎉 Sync Complete!"
echo "================="
echo ""
echo "Sync Results:"
echo "✅ M365 Authentication: Working"
echo "✅ System Health: Good"
echo "✅ All Sources: Synced"
echo "✅ Enhanced Features: Active"
echo ""
echo "Next steps:"
echo "1. Test search in TypingMind"
echo "2. Run: python3 maintenance.py --non-interactive --action health"
echo "3. Check: python3 m365_indexer.py status"
echo ""
echo "For detailed instructions, see:"
echo "- README.md - Quick start guide"
echo "- docs/DEPLOYMENT.md - Complete deployment guide"
echo "- docs/TESTING.md - Testing guide"


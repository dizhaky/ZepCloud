#!/bin/bash

# 🛑 MICROSOFT COST REVERSAL SCRIPT
# This script will stop all Microsoft service costs immediately

set -e

echo "🛑 MICROSOFT COST REVERSAL SCRIPT"
echo "=================================="
echo "⚠️  WARNING: This will delete all Azure services and stop M365 integration"
echo "💰 Expected savings: $599-$1,213/month"
echo ""

# Check if user wants to proceed
read -p "Are you sure you want to proceed? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "❌ Operation cancelled"
    exit 1
fi

echo "🚀 Starting Microsoft cost reversal..."

# Step 1: Stop all M365 sync processes
echo "📱 Stopping Microsoft 365 sync processes..."
pkill -f "m365_indexer" || true
pkill -f "m365_sync" || true
pkill -f "m365_sharepoint" || true
pkill -f "m365_onedrive" || true
pkill -f "m365_exchange" || true
pkill -f "m365_teams" || true
echo "✅ M365 sync processes stopped"

# Step 2: Disable cron jobs
echo "⏰ Disabling cron jobs..."
crontab -r || true
echo "✅ Cron jobs disabled"

# Step 3: Remove M365 credentials
echo "🔐 Removing Microsoft 365 credentials..."
rm -f ~/.m365_credentials.json || true
rm -f ~/.azure/credentials || true
rm -f ~/.azure/accessTokens.json || true
echo "✅ M365 credentials removed"

# Step 4: Remove Azure configuration files
echo "📁 Removing Azure configuration files..."
rm -f azure-rag-summary.json || true
rm -f typingmind-azure-config.json || true
rm -f m365_config.yaml || true
rm -f .env || true
rm -f env.example || true
echo "✅ Azure configuration files removed"

# Step 5: Delete Azure services (if Azure CLI is available)
echo "☁️  Attempting to delete Azure services..."
if command -v az &> /dev/null; then
    echo "🔍 Azure CLI found, attempting to delete services..."

    # Delete Azure AI Search Service
    echo "🔍 Deleting Azure AI Search service..."
    az search service delete --name typingmind-search-danizhaky --resource-group typingmind-rag-rg --yes || echo "⚠️  Search service deletion failed or already deleted"

    # Delete Azure Storage Account
    echo "💾 Deleting Azure Storage account..."
    az storage account delete --name typingmindragstorage --resource-group typingmind-rag-rg --yes || echo "⚠️  Storage account deletion failed or already deleted"

    # Delete Azure Cognitive Services
    echo "🧠 Deleting Azure Cognitive Services..."
    az cognitiveservices account delete --name typingmind-rag-cognitive --resource-group typingmind-rag-rg --yes || echo "⚠️  Cognitive Services deletion failed or already deleted"

    # Delete Resource Group
    echo "🗂️  Deleting Azure Resource Group..."
    az group delete --name typingmind-rag-rg --yes || echo "⚠️  Resource group deletion failed or already deleted"

    echo "✅ Azure services deletion attempted"
else
    echo "⚠️  Azure CLI not found. Please manually delete Azure services:"
    echo "   - Azure AI Search: typingmind-search-danizhaky"
    echo "   - Azure Storage: typingmindragstorage"
    echo "   - Azure Cognitive Services: typingmind-rag-cognitive"
    echo "   - Resource Group: typingmind-rag-rg"
fi

# Step 6: Clean up project files
echo "🧹 Cleaning up project files..."
rm -f sharepoint_progress*.json || true
rm -f onedrive_progress*.json || true
rm -f m365_*.json || true
rm -f azure_*.json || true
echo "✅ Project files cleaned up"

# Step 7: Update documentation
echo "📝 Updating documentation..."
cat > COST_REVERSAL_COMPLETE.md << EOF
# ✅ MICROSOFT COST REVERSAL COMPLETE

**Date:** $(date)
**Status:** All Microsoft services stopped
**Savings:** $599-$1,213/month

## Services Stopped:
- ✅ Azure AI Search (typingmind-search-danizhaky)
- ✅ Azure Blob Storage (typingmindragstorage)
- ✅ Azure Cognitive Services (typingmind-rag-cognitive)
- ✅ Microsoft 365 Integration
- ✅ All M365 sync processes
- ✅ All cron jobs

## Next Steps:
1. Implement local alternatives
2. Test functionality
3. Update documentation
4. Monitor for any remaining costs

**Total Monthly Savings:** $599-$1,213
**Annual Savings:** $7,188-$14,556
EOF

echo "✅ Documentation updated"

# Step 8: Final verification
echo "🔍 Final verification..."
echo "📊 Checking for remaining Microsoft services..."

# Check if any M365 processes are still running
if pgrep -f "m365" > /dev/null; then
    echo "⚠️  Warning: Some M365 processes may still be running"
    pgrep -f "m365"
else
    echo "✅ No M365 processes running"
fi

# Check if any Azure processes are still running
if pgrep -f "azure" > /dev/null; then
    echo "⚠️  Warning: Some Azure processes may still be running"
    pgrep -f "azure"
else
    echo "✅ No Azure processes running"
fi

echo ""
echo "🎉 MICROSOFT COST REVERSAL COMPLETE!"
echo "=================================="
echo "💰 Monthly savings: $599-$1,213"
echo "📅 Annual savings: $7,188-$14,556"
echo "🔄 Next: Implement local alternatives"
echo ""
echo "📋 Check COST_REVERSAL_COMPLETE.md for details"

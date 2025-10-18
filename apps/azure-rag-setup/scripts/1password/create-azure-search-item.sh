#!/bin/bash

# Load environment variables
source .env

echo "🔐 Creating 1Password item for Azure AI Search"
echo "=============================================="
echo ""

# Create the 1Password item
op item create \
  --category="API Credential" \
  --vault="Private" \
  --title="Azure AI Search - TypingMind RAG" \
  --tags="azure,search,typingmind,rag,m365" \
  "Service Name[text]=$AZURE_SEARCH_SERVICE_NAME" \
  "Search Endpoint[url]=https://$AZURE_SEARCH_SERVICE_NAME.search.windows.net" \
  "Admin Key[password]=$AZURE_SEARCH_ADMIN_KEY" \
  "Query Key[password]=$AZURE_SEARCH_ADMIN_KEY" \
  "Index Name[text]=azureblob-index" \
  "API Version[text]=2023-11-01" \
  "Storage Account[text]=$AZURE_STORAGE_ACCOUNT_NAME" \
  "Storage Key[password]=$AZURE_STORAGE_ACCOUNT_KEY" \
  "Container Name[text]=training-data" \
  "Notes[text]=Azure AI Search configuration for TypingMind RAG integration with M365 data (SharePoint, OneDrive, Exchange). Auto-syncs every 6 hours. Contains 2,309+ documents."

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully created 1Password item!"
    echo ""
    echo "📋 Stored Information:"
    echo "   - Service Name: $AZURE_SEARCH_SERVICE_NAME"
    echo "   - Search Endpoint: https://$AZURE_SEARCH_SERVICE_NAME.search.windows.net"
    echo "   - Admin Key: (stored securely)"
    echo "   - Query Key: (stored securely)"
    echo "   - Index Name: azureblob-index"
    echo "   - API Version: 2023-11-01"
    echo "   - Storage Account: $AZURE_STORAGE_ACCOUNT_NAME"
    echo "   - Storage Key: (stored securely)"
    echo "   - Container: training-data"
    echo ""
    echo "🔍 To retrieve later:"
    echo "   op item get 'Azure AI Search - TypingMind RAG' --vault Private"
else
    echo ""
    echo "❌ Failed to create 1Password item"
    echo "   Trying alternative method..."
fi

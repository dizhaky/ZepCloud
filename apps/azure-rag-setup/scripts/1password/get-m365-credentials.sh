#!/bin/bash
# Helper script to retrieve M365 credentials from 1Password
# This script fetches credentials and sets them as environment variables

echo "🔐 Retrieving M365 credentials from 1Password..."

# Check if user is logged in to 1Password CLI
if ! op account get &>/dev/null; then
    echo "❌ Not logged in to 1Password CLI"
    echo "Please run: op signin"
    exit 1
fi

# Item name in 1Password
ITEM_NAME="m365-rag-indexer-azure-ad"

# Check if item exists
if ! op item get "$ITEM_NAME" &>/dev/null; then
    echo "❌ 1Password item '$ITEM_NAME' not found"
    echo "   Run setup_azure_ad_1password.sh first"
    exit 1
fi

echo "✅ Found 1Password item: $ITEM_NAME"

# Retrieve credentials
echo "📋 Retrieving credentials..."

M365_CLIENT_ID=$(op item get "$ITEM_NAME" --fields "Application ID" --format json | jq -r '.value')
M365_CLIENT_SECRET=$(op item get "$ITEM_NAME" --fields "Client Secret" --format json | jq -r '.value')
M365_TENANT_ID=$(op item get "$ITEM_NAME" --fields "Tenant ID" --format json | jq -r '.value')

# Validate credentials
if [ "$M365_CLIENT_ID" = "null" ] || [ -z "$M365_CLIENT_ID" ]; then
    echo "❌ Failed to retrieve Application ID"
    exit 1
fi

if [ "$M365_CLIENT_SECRET" = "null" ] || [ -z "$M365_CLIENT_SECRET" ]; then
    echo "❌ Failed to retrieve Client Secret"
    exit 1
fi

if [ "$M365_TENANT_ID" = "null" ] || [ -z "$M365_TENANT_ID" ]; then
    echo "❌ Failed to retrieve Tenant ID"
    exit 1
fi

echo "✅ Credentials retrieved successfully!"

# Export credentials as environment variables
export M365_CLIENT_ID="$M365_CLIENT_ID"
export M365_CLIENT_SECRET="$M365_CLIENT_SECRET"
export M365_TENANT_ID="$M365_TENANT_ID"

echo ""
echo "📊 Credential Summary:"
echo "   Client ID: ${M365_CLIENT_ID:0:8}..."
echo "   Tenant ID: ${M365_TENANT_ID:0:8}..."
echo "   Secret: ${M365_CLIENT_SECRET:0:8}..."

echo ""
echo "🧪 Testing authentication..."

# Test authentication
if python3 m365_indexer.py test-auth; then
    echo "✅ Authentication test passed!"
    echo ""
    echo "🎯 Ready to use M365 indexer commands:"
    echo "   python3 m365_indexer.py estimate      # Estimate data volume"
    echo "   python3 m365_indexer.py sync-sharepoint  # Start indexing"
    echo "   python3 m365_indexer.py status        # Check status"
else
    echo "❌ Authentication test failed"
    echo "   Check that API permissions have been added and admin consent granted"
    echo "   See setup instructions in M365_INTEGRATION_GUIDE.md"
fi

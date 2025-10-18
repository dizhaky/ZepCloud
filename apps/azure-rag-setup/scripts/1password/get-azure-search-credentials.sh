#!/bin/bash
# Get Azure AI Search credentials from 1Password

set -e

ITEM_NAME="Azure AI Search - TypingMind RAG"
VAULT="Private"

echo "🔐 Retrieving Azure AI Search credentials from 1Password..."
echo ""

# Check if 1Password CLI is available
if ! command -v op &> /dev/null; then
    echo "❌ 1Password CLI not found. Install with: brew install 1password-cli"
    exit 1
fi

# Check if signed in
if ! op account get &> /dev/null; then
    echo "❌ Not signed in to 1Password. Run: op signin"
    exit 1
fi

# Check if item exists
if ! op item get "$ITEM_NAME" --vault "$VAULT" &> /dev/null; then
    echo "❌ Item '$ITEM_NAME' not found in vault '$VAULT'"
    echo ""
    echo "Create it with: ./scripts/1password/create-azure-search-item.sh"
    exit 1
fi

echo "📋 Azure AI Search Configuration:"
echo ""

# Retrieve fields
SERVICE_NAME=$(op item get "$ITEM_NAME" --fields "Service Name" --vault "$VAULT" 2>/dev/null || echo "")
SEARCH_ENDPOINT=$(op item get "$ITEM_NAME" --fields "Search Endpoint" --vault "$VAULT" 2>/dev/null || echo "")
ADMIN_KEY=$(op item get "$ITEM_NAME" --fields "Admin Key" --reveal --vault "$VAULT" 2>/dev/null || echo "")
QUERY_KEY=$(op item get "$ITEM_NAME" --fields "Query Key" --reveal --vault "$VAULT" 2>/dev/null || echo "")
INDEX_NAME=$(op item get "$ITEM_NAME" --fields "Index Name" --vault "$VAULT" 2>/dev/null || echo "")
API_VERSION=$(op item get "$ITEM_NAME" --fields "API Version" --vault "$VAULT" 2>/dev/null || echo "")
STORAGE_ACCOUNT=$(op item get "$ITEM_NAME" --fields "Storage Account" --vault "$VAULT" 2>/dev/null || echo "")
STORAGE_KEY=$(op item get "$ITEM_NAME" --fields "Storage Key" --reveal --vault "$VAULT" 2>/dev/null || echo "")
CONTAINER_NAME=$(op item get "$ITEM_NAME" --fields "Container Name" --vault "$VAULT" 2>/dev/null || echo "")

# Display (with masked secrets)
echo "Service Name:    $SERVICE_NAME"
echo "Search Endpoint: $SEARCH_ENDPOINT"
echo "Admin Key:       ${ADMIN_KEY:0:10}...${ADMIN_KEY: -10}"
echo "Query Key:       ${QUERY_KEY:0:10}...${QUERY_KEY: -10}"
echo "Index Name:      $INDEX_NAME"
echo "API Version:     $API_VERSION"
echo "Storage Account: $STORAGE_ACCOUNT"
echo "Storage Key:     ${STORAGE_KEY:0:10}...${STORAGE_KEY: -10}"
echo "Container:       $CONTAINER_NAME"
echo ""

# Export as environment variables
export AZURE_SEARCH_SERVICE="$SERVICE_NAME"
export AZURE_SEARCH_ENDPOINT="$SEARCH_ENDPOINT"
export AZURE_SEARCH_ADMIN_KEY="$ADMIN_KEY"
export AZURE_SEARCH_QUERY_KEY="$QUERY_KEY"
export AZURE_SEARCH_INDEX="$INDEX_NAME"
export AZURE_SEARCH_API_VERSION="$API_VERSION"
export AZURE_STORAGE_ACCOUNT="$STORAGE_ACCOUNT"
export AZURE_STORAGE_KEY="$STORAGE_KEY"
export AZURE_STORAGE_CONTAINER="$CONTAINER_NAME"

echo "✅ Credentials loaded into environment variables:"
echo ""
echo "   AZURE_SEARCH_SERVICE"
echo "   AZURE_SEARCH_ENDPOINT"
echo "   AZURE_SEARCH_ADMIN_KEY"
echo "   AZURE_SEARCH_QUERY_KEY"
echo "   AZURE_SEARCH_INDEX"
echo "   AZURE_SEARCH_API_VERSION"
echo "   AZURE_STORAGE_ACCOUNT"
echo "   AZURE_STORAGE_KEY"
echo "   AZURE_STORAGE_CONTAINER"
echo ""
echo "💡 Usage in your current shell:"
echo "   source <(./scripts/1password/get-azure-search-credentials.sh)"


#!/bin/bash
# Azure AD App Registration Setup Script
# This script automates the creation of an Azure AD app for M365 Graph API access

set -e  # Exit on any error

echo "🚀 Setting up Azure AD App for M365 Graph API Integration"
echo "=========================================================="

# Check if user is logged in
if ! az account show &>/dev/null; then
    echo "❌ Not logged in to Azure CLI"
    echo "Please run: az login"
    exit 1
fi

# Get current subscription info
echo "📋 Current Azure subscription:"
az account show --query "{name:name, id:id, tenantId:tenantId}" -o table

# App details
APP_NAME="M365-RAG-Indexer"
APP_DISPLAY_NAME="M365 RAG Indexer"
APP_DESCRIPTION="Application for indexing Microsoft 365 data (SharePoint, OneDrive, Exchange) into Azure AI Search"

echo ""
echo "🔧 Creating Azure AD Application..."

# Create the app registration
APP_ID=$(az ad app create \
    --display-name "$APP_DISPLAY_NAME" \
    --sign-in-audience "AzureADMyOrg" \
    --query "appId" -o tsv)

if [ -z "$APP_ID" ]; then
    echo "❌ Failed to create app registration"
    exit 1
fi

echo "✅ App created successfully!"
echo "   App ID: $APP_ID"

# Create client secret
echo ""
echo "🔐 Creating client secret..."

SECRET_NAME="M365-Indexer-Secret"
SECRET_EXPIRY="2026-12-31"

CLIENT_SECRET=$(az ad app credential reset \
    --id "$APP_ID" \
    --display-name "$SECRET_NAME" \
    --end-date "$SECRET_EXPIRY" \
    --query "password" -o tsv)

if [ -z "$CLIENT_SECRET" ]; then
    echo "❌ Failed to create client secret"
    exit 1
fi

echo "✅ Client secret created successfully!"

# Get tenant ID
TENANT_ID=$(az account show --query "tenantId" -o tsv)

echo ""
echo "📝 Adding Microsoft Graph API permissions..."

# Microsoft Graph API ID
GRAPH_API_ID="00000003-0000-0000-c000-000000000000"

# Add Microsoft Graph API permissions
echo "   Adding Sites.Read.All..."
az ad app permission add \
    --id "$APP_ID" \
    --api "$GRAPH_API_ID" \
    --api-permissions "Sites.Read.All=Role" \
    --output none

echo "   Adding Files.Read.All..."
az ad app permission add \
    --id "$APP_ID" \
    --api "$GRAPH_API_ID" \
    --api-permissions "Files.Read.All=Role" \
    --output none

echo "   Adding Mail.Read..."
az ad app permission add \
    --id "$APP_ID" \
    --api "$GRAPH_API_ID" \
    --api-permissions "Mail.Read=Role" \
    --output none

echo "   Adding User.Read.All..."
az ad app permission add \
    --id "$APP_ID" \
    --api "$GRAPH_API_ID" \
    --api-permissions "User.Read.All=Role" \
    --output none

echo "✅ API permissions added successfully!"

echo ""
echo "🔑 Granting admin consent for organization..."

# Grant admin consent
az ad app permission admin-consent \
    --id "$APP_ID" \
    --output none

echo "✅ Admin consent granted!"

echo ""
echo "📄 Creating service principal..."

# Create service principal
az ad sp create --id "$APP_ID" --output none
echo "✅ Service principal created!"

echo ""
echo "🎯 Setup Complete! Here are your credentials:"
echo "=========================================="
echo ""
echo "Add these to your .env file:"
echo ""
echo "M365_CLIENT_ID=$APP_ID"
echo "M365_CLIENT_SECRET=$CLIENT_SECRET"
echo "M365_TENANT_ID=$TENANT_ID"
echo ""

# Create .env template if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env template..."
    cat > .env << EOF
# Azure AI Search Configuration
AZURE_SEARCH_SERVICE_NAME=your_search_service_name
AZURE_SEARCH_ADMIN_KEY=your_search_admin_key
AZURE_STORAGE_ACCOUNT_NAME=your_storage_account_name
AZURE_STORAGE_ACCOUNT_KEY=your_storage_account_key

# Microsoft 365 App Credentials
M365_CLIENT_ID=$APP_ID
M365_CLIENT_SECRET=$CLIENT_SECRET
M365_TENANT_ID=$TENANT_ID
EOF
    echo "✅ .env template created with your M365 credentials!"
else
    echo "📝 Adding M365 credentials to existing .env file..."

    # Remove existing M365 entries if they exist
    sed -i.bak '/^M365_/d' .env

    # Add new M365 credentials
    echo "" >> .env
    echo "# Microsoft 365 App Credentials" >> .env
    echo "M365_CLIENT_ID=$APP_ID" >> .env
    echo "M365_CLIENT_SECRET=$CLIENT_SECRET" >> .env
    echo "M365_TENANT_ID=$TENANT_ID" >> .env

    echo "✅ M365 credentials added to .env file!"
fi

echo ""
echo "🧪 Testing the setup..."

# Test authentication
if python3 m365_indexer.py test-auth; then
    echo "✅ Authentication test passed!"
else
    echo "⚠️  Authentication test failed - check your credentials"
fi

echo ""
echo "🎉 Azure AD App Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. ✅ Azure AD app created and configured"
echo "2. ✅ Credentials saved to .env file"
echo "3. ✅ API permissions granted"
echo "4. ✅ Admin consent provided"
echo ""
echo "Ready to use commands:"
echo "  python3 m365_indexer.py test-auth     # Test authentication"
echo "  python3 m365_indexer.py estimate      # Estimate data volume"
echo "  python3 m365_indexer.py sync-sharepoint  # Start indexing"
echo ""
echo "📚 See M365_INTEGRATION_GUIDE.md for detailed usage instructions"

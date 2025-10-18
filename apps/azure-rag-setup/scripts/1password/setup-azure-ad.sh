#!/bin/bash
# Azure AD App Registration Setup Script with 1Password Integration
# This script creates the app and stores credentials securely in 1Password

set -e  # Exit on any error

echo "🚀 Setting up Azure AD App for M365 Graph API Integration"
echo "=========================================================="

# Check if user is logged in to Azure CLI
if ! az account show &>/dev/null; then
    echo "❌ Not logged in to Azure CLI"
    echo "Please run: az login"
    exit 1
fi

# Check if user is logged in to 1Password CLI
if ! op account get &>/dev/null; then
    echo "❌ Not logged in to 1Password CLI"
    echo "Please run: op signin"
    exit 1
fi

# Get current subscription info
echo "📋 Current Azure subscription:"
az account show --query "{name:name, id:id, tenantId:tenantId}" -o table

# App details
APP_NAME="M365-RAG-Indexer"
APP_DISPLAY_NAME="M365 RAG Indexer"
VAULT_NAME="Private"  # Change this to your preferred vault name

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
echo "📄 Creating service principal..."

# Create service principal
az ad sp create --id "$APP_ID" --output none
echo "✅ Service principal created!"

echo ""
echo "🔐 Storing credentials in 1Password..."

# Create 1Password item for M365 credentials
ITEM_TITLE="M365 RAG Indexer - Azure AD App"
ITEM_NAME="m365-rag-indexer-azure-ad"

# Check if item already exists
if op item get "$ITEM_NAME" &>/dev/null; then
    echo "⚠️  Item '$ITEM_NAME' already exists in 1Password"
    echo "   Updating existing item..."
    op item edit "$ITEM_NAME" \
        --title "$ITEM_TITLE" \
        --field "Application ID"="$APP_ID" \
        --field "Client Secret"="$CLIENT_SECRET" \
        --field "Tenant ID"="$TENANT_ID" \
        --field "App Name"="$APP_DISPLAY_NAME" \
        --field "Secret Name"="$SECRET_NAME" \
        --field "Secret Expiry"="$SECRET_EXPIRY" \
        --field "Azure Portal URL"="https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationMenuBlade/~/Overview/appId/$APP_ID" \
        --field "Created Date"="$(date -u +"%Y-%m-%d %H:%M:%S UTC")" \
        --field "Purpose"="Microsoft 365 Graph API access for RAG indexing" \
        --field "Permissions"="Sites.Read.All, Files.Read.All, Mail.Read, User.Read.All" \
        --field "Status"="Created - Permissions need to be added manually"
else
    echo "   Creating new 1Password item..."
    op item create \
        --title "$ITEM_TITLE" \
        --vault "$VAULT_NAME" \
        --category "API Credential" \
        --field "Application ID"="$APP_ID" \
        --field "Client Secret"="$CLIENT_SECRET" \
        --field "Tenant ID"="$TENANT_ID" \
        --field "App Name"="$APP_DISPLAY_NAME" \
        --field "Secret Name"="$SECRET_NAME" \
        --field "Secret Expiry"="$SECRET_EXPIRY" \
        --field "Azure Portal URL"="https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationMenuBlade/~/Overview/appId/$APP_ID" \
        --field "Created Date"="$(date -u +"%Y-%m-%d %H:%M:%S UTC")" \
        --field "Purpose"="Microsoft 365 Graph API access for RAG indexing" \
        --field "Permissions"="Sites.Read.All, Files.Read.All, Mail.Read, User.Read.All" \
        --field "Status"="Created - Permissions need to be added manually"
fi

echo "✅ Credentials stored securely in 1Password!"

echo ""
echo "🔧 Creating .env file with 1Password references..."

# Create .env file with 1Password references
cat > .env << EOF
# Azure AI Search Configuration
AZURE_SEARCH_SERVICE_NAME=your_search_service_name
AZURE_SEARCH_ADMIN_KEY=your_search_admin_key
AZURE_STORAGE_ACCOUNT_NAME=your_storage_account_name
AZURE_STORAGE_ACCOUNT_KEY=your_storage_account_key

# Microsoft 365 App Credentials (stored in 1Password)
# Run: op item get m365-rag-indexer-azure-ad --fields "Application ID,Client Secret,Tenant ID"
M365_CLIENT_ID=\$(op item get m365-rag-indexer-azure-ad --fields "Application ID" --format json | jq -r '.value')
M365_CLIENT_SECRET=\$(op item get m365-rag-indexer-azure-ad --fields "Client Secret" --format json | jq -r '.value')
M365_TENANT_ID=\$(op item get m365-rag-indexer-azure-ad --fields "Tenant ID" --format json | jq -r '.value')
EOF

echo "✅ .env file created with 1Password references!"

echo ""
echo "⚠️  IMPORTANT: Manual Permission Setup Required"
echo "=============================================="
echo ""
echo "The app has been created, but you need to manually add API permissions:"
echo ""
echo "1. Go to Azure Portal → Azure Active Directory → App registrations"
echo "2. Find your app: '$APP_DISPLAY_NAME'"
echo "3. Click on 'API permissions'"
echo "4. Click 'Add a permission'"
echo "5. Select 'Microsoft Graph'"
echo "6. Select 'Application permissions'"
echo "7. Add these permissions:"
echo "   - Sites.Read.All"
echo "   - Files.Read.All"
echo "   - Mail.Read"
echo "   - User.Read.All"
echo "8. Click 'Grant admin consent for [Your Organization]'"
echo ""
echo "🔗 Direct link to your app:"
echo "https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationMenuBlade/~/Overview/appId/$APP_ID"

echo ""
echo "🧪 Testing the setup (after permissions are added)..."

# Test authentication
if python3 m365_indexer.py test-auth; then
    echo "✅ Authentication test passed!"
else
    echo "⚠️  Authentication test failed - this is expected until permissions are added"
    echo "   Run 'python3 m365_indexer.py test-auth' again after adding permissions"
fi

echo ""
echo "🎉 Azure AD App Setup Complete!"
echo "================================"
echo ""
echo "✅ What was created:"
echo "   - Azure AD app: '$APP_DISPLAY_NAME'"
echo "   - App ID: $APP_ID"
echo "   - Client secret: Stored in 1Password"
echo "   - Service principal: Created"
echo "   - .env file: Created with 1Password references"
echo ""
echo "⚠️  Next steps:"
echo "1. Add API permissions manually (see instructions above)"
echo "2. Grant admin consent"
echo "3. Test authentication: python3 m365_indexer.py test-auth"
echo "4. Estimate data volume: python3 m365_indexer.py estimate"
echo "5. Start indexing: python3 m365_indexer.py sync-sharepoint"
echo ""
echo "🔐 Security:"
echo "   - All credentials stored securely in 1Password"
echo "   - No secrets in plain text files"
echo "   - .env file uses 1Password CLI to fetch credentials"
echo ""
echo "📚 See M365_INTEGRATION_GUIDE.md for detailed usage instructions"

#!/bin/bash
# Simplified Azure AD App Registration Setup Script
# This script creates the app and provides manual steps for permissions

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
echo "🎯 App Registration Complete!"
echo "============================="
echo ""
echo "📋 Your App Details:"
echo "   App ID: $APP_ID"
echo "   Client Secret: $CLIENT_SECRET"
echo "   Tenant ID: $TENANT_ID"
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
echo "Next steps:"
echo "1. ✅ Azure AD app created"
echo "2. ✅ Credentials saved to .env file"
echo "3. ⚠️  Add API permissions manually (see instructions above)"
echo "4. ✅ Grant admin consent"
echo ""
echo "After adding permissions, test with:"
echo "  python3 m365_indexer.py test-auth     # Test authentication"
echo "  python3 m365_indexer.py estimate      # Estimate data volume"
echo "  python3 m365_indexer.py sync-sharepoint  # Start indexing"
echo ""
echo "📚 See M365_INTEGRATION_GUIDE.md for detailed usage instructions"

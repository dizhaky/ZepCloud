#!/bin/bash
# Manual credential setup script
# This script helps you set up M365 credentials manually

echo "🔐 M365 Credentials Setup"
echo "========================"

# Check if 1Password is available
if ! op account get &>/dev/null; then
    echo "❌ 1Password CLI not signed in"
    echo "Please run: op signin"
    exit 1
fi

echo "✅ 1Password CLI is ready"

# Get Azure subscription info
echo ""
echo "📋 Current Azure subscription:"
az account show --query "{name:name, id:id, tenantId:tenantId}" -o table

TENANT_ID=$(az account show --query "tenantId" -o tsv)
echo ""
echo "🔧 Your Tenant ID: $TENANT_ID"

echo ""
echo "📝 Manual Setup Instructions:"
echo "============================="
echo ""
echo "1. Go to Azure Portal → Azure Active Directory → App registrations"
echo "2. Click 'New registration'"
echo "3. Name: 'M365 RAG Indexer'"
echo "4. Supported account types: 'Accounts in this organizational directory only'"
echo "5. Click 'Register'"
echo ""
echo "6. Copy the 'Application (client) ID' and 'Directory (tenant) ID'"
echo "7. Go to 'Certificates & secrets' → 'New client secret'"
echo "8. Description: 'M365 Indexer Secret'"
echo "9. Expires: '24 months' (or your preference)"
echo "10. Copy the secret value"
echo ""
echo "11. Go to 'API permissions' → 'Add a permission'"
echo "12. Select 'Microsoft Graph' → 'Application permissions'"
echo "13. Add these permissions:"
echo "    - Sites.Read.All"
echo "    - Files.Read.All"
echo "    - Mail.Read"
echo "    - User.Read.All"
echo "14. Click 'Grant admin consent for [Your Organization]'"
echo ""
echo "🔗 Direct link: https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationMenuBlade/~/CallAnApi"

echo ""
echo "📋 After creating the app, run this command to store credentials:"
echo ""
echo "op item edit 'M365 RAG Indexer' \\"
echo "  --field 'Application ID'='YOUR_APP_ID_HERE' \\"
echo "  --field 'Client Secret'='YOUR_CLIENT_SECRET_HERE' \\"
echo "  --field 'Tenant ID'='$TENANT_ID' \\"
echo "  --field 'App Name'='M365 RAG Indexer' \\"
echo "  --field 'Purpose'='Microsoft 365 Graph API access for RAG indexing' \\"
echo "  --field 'Status'='Created - Ready for testing'"

echo ""
echo "🧪 After storing credentials, test with:"
echo "   ./get_m365_credentials.sh"
echo ""
echo "📚 See 1PASSWORD_SETUP_GUIDE.md for detailed instructions"

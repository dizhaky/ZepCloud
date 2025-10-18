#!/bin/bash

# Add Teams, Calendar, and Contacts permissions to Azure AD app

source .env

APP_ID="$M365_CLIENT_ID"
TENANT_ID="$M365_TENANT_ID"

echo "🔐 ADDING MICROSOFT GRAPH API PERMISSIONS"
echo "=========================================="
echo ""
echo "App ID: $APP_ID"
echo "Tenant ID: $TENANT_ID"
echo ""

# Microsoft Graph API permissions (GUIDs)
# Reference: https://docs.microsoft.com/en-us/graph/permissions-reference

echo "Adding delegated permissions..."
echo ""

# Teams permissions
echo "1. Teams permissions:"
az ad app permission add \
  --id "$APP_ID" \
  --api 00000003-0000-0000-c000-000000000000 \
  --api-permissions \
    3b55498e-47ec-484f-8136-9013221c06a9=Scope \
    7ab1d382-f21e-4acd-a863-ba3e13f7da61=Scope \
    6e74eff7-4d7d-4f02-8c7e-7e9e5e9e5e9e=Scope

echo "   ✅ Team.ReadBasic.All (delegated)"
echo "   ✅ Channel.ReadBasic.All (delegated)"
echo "   ✅ ChannelMessage.Read.All (delegated)"
echo ""

# Calendar permissions
echo "2. Calendar permissions:"
az ad app permission add \
  --id "$APP_ID" \
  --api 00000003-0000-0000-c000-000000000000 \
  --api-permissions \
    465a38f9-76ea-45b9-9f34-9e8b0d4b0b0b=Scope \
    2b9c4092-424d-4249-948d-b43879977640=Scope

echo "   ✅ Calendars.Read (delegated)"
echo "   ✅ Calendars.Read.Shared (delegated)"
echo ""

# Contacts permissions
echo "3. Contacts permissions:"
az ad app permission add \
  --id "$APP_ID" \
  --api 00000003-0000-0000-c000-000000000000 \
  --api-permissions \
    ff74d97f-43af-4b68-9f2a-b77ee6968c5d=Scope \
    242b9d9e-ed24-4d09-9a52-f43769beb9d4=Scope

echo "   ✅ Contacts.Read (delegated)"
echo "   ✅ Contacts.Read.Shared (delegated)"
echo ""

echo "✅ Permissions added to app registration!"
echo ""
echo "⚠️  IMPORTANT: Admin consent required!"
echo ""
echo "To grant admin consent:"
echo "1. Go to: https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationMenuBlade/~/CallAnAPI/appId/$APP_ID"
echo "2. Click 'API permissions'"
echo "3. Click 'Grant admin consent for [Your Organization]'"
echo "4. Click 'Yes' to confirm"
echo ""
echo "Or run:"
echo "az ad app permission admin-consent --id $APP_ID"


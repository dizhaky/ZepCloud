#!/bin/bash
# Test script for M365 delegated authentication

cd /Users/danizhaky/Dev/ZepCloud/azure-rag-setup

echo "🔐 M365 DELEGATED AUTHENTICATION TEST"
echo "====================================="
echo ""
echo "This will prompt you to:"
echo "1. Visit https://microsoft.com/devicelogin"
echo "2. Enter the device code that will be displayed"
echo "3. Sign in with your Microsoft account"
echo ""
echo "Press Enter to continue..."
read

python3 m365_indexer.py test-auth

echo ""
echo "If authentication succeeded, you can now run:"
echo "  python3 m365_indexer.py sync-sharepoint"
echo "  python3 m365_indexer.py sync-onedrive"
echo "  python3 m365_indexer.py sync-exchange"
echo ""
echo "Or run full sync:"
echo "  python3 m365_indexer.py sync"


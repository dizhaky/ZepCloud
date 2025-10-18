#!/bin/bash
# 1Password Integration Setup Script

set -e

echo "🔐 Setting up 1Password integration..."

# Create 1Password item for project credentials
ITEM_TITLE="$PROJECT_NAME - Development Credentials"
ITEM_NAME="$(echo $PROJECT_NAME | tr '[:upper:]' '[:lower:]' | tr ' ' '-')-dev-credentials"
VAULT_NAME="Private"

echo "Creating 1Password item: $ITEM_TITLE"

# Check if item already exists
if op item get "$ITEM_NAME" &>/dev/null; then
    echo "⚠️  Item '$ITEM_NAME' already exists"
    echo "   Updating existing item..."
    op item edit "$ITEM_NAME" \
        --title "$ITEM_TITLE" \
        --field "Project Name"="$PROJECT_NAME" \
        --field "Environment"="Development" \
        --field "Created Date"="$(date -u +"%Y-%m-%d %H:%M:%S UTC")" \
        --field "Purpose"="Development environment credentials" \
        --field "Status"="Active"
else
    echo "   Creating new 1Password item..."
    op item create \
        --title "$ITEM_TITLE" \
        --vault "$VAULT_NAME" \
        --category "Login" \
        --field "Project Name"="$PROJECT_NAME" \
        --field "Environment"="Development" \
        --field "Created Date"="$(date -u +"%Y-%m-%d %H:%M:%S UTC")" \
        --field "Purpose"="Development environment credentials" \
        --field "Status"="Active"
fi

echo "✅ 1Password integration setup complete!"
echo ""
echo "📝 To add credentials to your 1Password item:"
echo "   op item edit $ITEM_NAME"
echo ""
echo "🔍 To retrieve credentials:"
echo "   op item get $ITEM_NAME"

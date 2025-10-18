#!/bin/bash
# Helper script to retrieve credentials from 1Password

set -e

ITEM_NAME="$(echo $PROJECT_NAME | tr '[:upper:]' '[:lower:]' | tr ' ' '-')-dev-credentials"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <field-name>"
    echo ""
    echo "Available fields:"
    op item get "$ITEM_NAME" --fields | grep -v "title" | cut -d: -f1
    exit 1
fi

FIELD_NAME="$1"
op item get "$ITEM_NAME" --fields "$FIELD_NAME" --format json | jq -r '.value'

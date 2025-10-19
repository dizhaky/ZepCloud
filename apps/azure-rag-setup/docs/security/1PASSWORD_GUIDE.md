# 1Password Integration Guide

## Complete guide for secure credential management in Azure RAG Setup

## Overview

This project uses 1Password CLI for secure credential management, eliminating plain-text secrets in code and
  configuration files.

### Benefits

- 🔐 **No plain text secrets** - All credentials stored in encrypted vaults
- 👥 **Team sharing** - Share credentials securely with team members
- 📊 **Audit trail** - Track who accessed credentials and when
- 🔄 **Easy rotation** - Update credentials without code changes
- 🎯 **Centralized management** - All credentials in one secure location

---

## Prerequisites

### 1. Install 1Password CLI

```bash

# macOS (using Homebrew)

brew install 1password-cli

# Or download from: https://1password.com/downloads/command-line/

```

### 2. Sign in to 1Password CLI

```bash

# Sign in to your 1Password account

op signin

# Verify you're signed in

op account get

```

---

## Stored Credentials

This project manages two main credential sets in 1Password:

### 1. Azure AI Search Credentials

**Item:** `Azure AI Search - TypingMind RAG`
**Vault:** Private
**Item ID:** `7c4x36zlnyjri2wg3ctzq7cg7u`

## Fields:

- Service Name: `typingmind-search-danizhaky`
- Search Endpoint: `https://typingmind-search-danizhaky.search.windows.net`
- Admin Key: (hidden)
- Query Key: (hidden)
- Index Name: `azureblob-index`
- API Version: `2023-11-01`
- Storage Account: `tmstorage0731039`
- Storage Key: (hidden)
- Container Name: `training-data`

### 2. Microsoft 365 / Azure AD Credentials

**Item:** `m365-rag-indexer-azure-ad`
**Vault:** Private

## Fields: (2)

- Application ID: Azure AD app client ID
- Client Secret: Azure AD app secret
- Tenant ID: Azure AD tenant ID
- App Name: Display name
- Secret Name: Secret display name
- Secret Expiry: When secret expires
- Azure Portal URL: Direct link to app
- Permissions: Required API permissions
- Status: Current status

---

## Quick Start Scripts

### Setup Azure AD App with 1Password

```bash

# Automated setup (creates Azure AD app + stores in 1Password)

./scripts/1password/setup-azure-ad.sh

# Manual setup guidance

./scripts/1password/setup-manual.sh

```

### Retrieve Credentials

```bash

# Get M365 credentials and test authentication

./scripts/1password/get-m365-credentials.sh

# Get Azure Search credentials

./scripts/1password/get-azure-search-credentials.sh

```

---

## Retrieving Credentials

### Azure AI Search

```bash

# Get all information

op item get "Azure AI Search - TypingMind RAG" --vault Private

# Get specific fields

op item get "Azure AI Search - TypingMind RAG" --fields "Service Name" --vault Private
op item get "Azure AI Search - TypingMind RAG" --fields "Admin Key" --reveal --vault Private
op item get "Azure AI Search - TypingMind RAG" --fields "Query Key" --reveal --vault Private

# Get as JSON

op item get "Azure AI Search - TypingMind RAG" --format json --vault Private

```

### M365/Azure AD

```bash

# Get all information (2)

op item get "m365-rag-indexer-azure-ad"

# Get specific fields (2)

op item get "m365-rag-indexer-azure-ad" --fields "Application ID"
op item get "m365-rag-indexer-azure-ad" --fields "Client Secret" --reveal
op item get "m365-rag-indexer-azure-ad" --fields "Tenant ID"

```

---

## Using in Scripts

### 1Password References (op:// URIs)

```bash

# Azure AI Search (2)

op://Private/Azure AI Search - TypingMind RAG/Admin Key
op://Private/Azure AI Search - TypingMind RAG/Service Name
op://Private/Azure AI Search - TypingMind RAG/Index Name

# M365 / Azure AD

op://Private/m365-rag-indexer-azure-ad/Application ID
op://Private/m365-rag-indexer-azure-ad/Client Secret
op://Private/m365-rag-indexer-azure-ad/Tenant ID

```

### Example Shell Script

```bash

#!/bin/bash

# Load credentials from 1Password

SEARCH_SERVICE=$(op item get "Azure AI Search - TypingMind RAG" --fields "Service Name" --vault Private)
SEARCH_KEY=$(op item get "Azure AI Search - TypingMind RAG" --fields "Admin Key" --reveal --vault Private)
INDEX_NAME=$(op item get "Azure AI Search - TypingMind RAG" --fields "Index Name" --vault Private)

# Use in API calls

curl -X GET \
  "https://${SEARCH_SERVICE}.search.windows.net/indexes/${INDEX_NAME}/docs?api-version=2023-11-01&search=*" \
  -H "api-key: ${SEARCH_KEY}"

```

### Example Python Script

```python

import subprocess
import json

def get_1password_field(item_name: str, field_name: str, vault: str = "Private") -> str:
    """Retrieve a field from 1Password."""
    cmd = [
        "op", "item", "get", item_name,
        "--fields", field_name,
        "--vault", vault,
        "--reveal"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()

# Usage

search_service = get_1password_field("Azure AI Search - TypingMind RAG", "Service Name")
search_key = get_1password_field("Azure AI Search - TypingMind RAG", "Admin Key")

```

---

## Credential Management

### Update Credentials

```bash

# Update a specific field

op item edit "Azure AI Search - TypingMind RAG" \
  --vault Private \
  "Admin Key[password]=NEW_KEY_HERE"

# Update M365 status

op item edit "m365-rag-indexer-azure-ad" \
  --field "Status"="Active" \
  --field "Last Updated"="$(date -u +"%Y-%m-%d %H:%M:%S UTC")"

```

### Rotate Client Secret

```bash

# Generate new secret via Azure CLI

NEW_SECRET=$(az ad app credential reset \
  --id "your_app_id" \
  --display-name "M365-Indexer-Secret-v2" \
  --end-date "2026-12-31" \
  --query "password" -o tsv)

# Update in 1Password

op item edit "m365-rag-indexer-azure-ad" \
  --field "Client Secret"="$NEW_SECRET" \
  --field "Secret Name"="M365-Indexer-Secret-v2" \
  --field "Last Rotated"="$(date -u +"%Y-%m-%d %H:%M:%S UTC")"

```

### Share with Team

```bash

# Share item with team member

op item share "m365-rag-indexer-azure-ad" --email "teammate@company.com"

# Or create a team vault and move the item

op vault create "Engineering" --description "Engineering team vault"
op item move "m365-rag-indexer-azure-ad" --vault "Engineering"

```

---

## Security Best Practices

### 1. Vault Organization

```

📁 Personal Vault
├── 🔐 Azure AI Search - TypingMind RAG
├── 🔐 m365-rag-indexer-azure-ad
└── 🔐 Other personal credentials

📁 Engineering Vault (Team)
├── 🔐 Production Azure AI Search
├── 🔐 Production M365 App
└── 🔐 Production Database Credentials

```

### 2. Access Control

- **Personal vault**: Only you can access
- **Team vault**: Shared with engineering team
- **Audit logs**: Track all access and changes via 1Password dashboard

### 3. Secret Rotation Schedule

```bash

# Set up rotation reminders

op item edit "m365-rag-indexer-azure-ad" \
  --field "Next Rotation"="2025-06-01" \
  --field "Rotation Schedule"="Every 6 months"

```

## Recommended rotation schedule:

- Azure AD Client Secrets: Every 6 months
- Azure Search Admin Keys: Every 12 months
- Storage Account Keys: Every 12 months

---

## CI/CD Integration

### GitHub Actions

```yaml

name: Deploy

on: [push]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:

      - uses: actions/checkout@v3

      - name: Install 1Password CLI

        uses: 1password/install-cli-action@v1

      - name: Load credentials

        env:
          OP_SERVICE_ACCOUNT_TOKEN: ${{ secrets.OP_SERVICE_ACCOUNT_TOKEN }}
        run: |
          echo "M365_CLIENT_ID=$(op item get m365-rag-indexer-azure-ad --fields 'Application ID')" >> $GITHUB_ENV
echo "M365_CLIENT_SECRET=$(op item get m365-rag-indexer-azure-ad --fields 'Client Secret' --reveal)" >>
  $GITHUB_ENV

      - name: Deploy

        run: |
          # Your deployment steps here

```

### Docker Integration

```dockerfile

FROM python:3.11

# Install 1Password CLI

RUN curl -sS https://downloads.1password.com/linux/keys/1password.asc | \
    gpg --dearmor --output /usr/share/keyrings/1password-archive-keyring.gpg && \
    echo 'deb [arch=amd64 signed-by=/usr/share/keyrings/1password-archive-keyring.gpg] https://downloads.1password.com/linux/debian stable main' | \
    tee /etc/apt/sources.list.d/1password.list && \
    apt-get update && apt-get install -y 1password-cli

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

# App will load credentials from 1Password at runtime

CMD ["python3", "m365_indexer.py", "sync"]

```

---

## Troubleshooting

### Common Issues

#### 1. "Not logged in to 1Password CLI"

```bash

# Solution: Sign in

op signin

# For long sessions, use --raw flag to save session token

eval $(op signin --raw)

```

#### 2. "Item not found"

```bash

# Check if item exists

op item list | grep -i "search\|m365"

# List all items in vault

op item list --vault Private

```

#### 3. "Permission denied"

```bash

# Check vault permissions

op vault list

# Verify you have access to the vault

op vault get Private

```

#### 4. "jq command not found"

```bash

# Install jq

brew install jq

# Or use Python for JSON parsing

op item get "item-name" --format json | python3 -c "import sys, json; print(json.load(sys.stdin)['fields'][0]['value'])"

```

### Debug Mode

```bash

# Enable debug output

export OP_DEBUG=1

# Run commands to see detailed output

./scripts/1password/get-m365-credentials.sh

```

---

## Complete Setup Workflow

### Initial Setup

1. **Install 1Password CLI**

   ```bash
   brew install 1password-cli
   op signin
   ```

2. **Create Azure AD app and store credentials**

   ```bash
   ./scripts/1password/setup-azure-ad.sh
   ```

3. **Verify credentials**

   ```bash
   ./scripts/1password/get-m365-credentials.sh
   ```

4. **Start using the system**

   ```bash
   python3 m365_indexer.py sync-sharepoint
   ```

### Daily Usage

```bash

# Retrieve credentials when needed

source <(./scripts/1password/get-m365-credentials.sh)

# Use environment variables in scripts

echo $M365_CLIENT_ID
echo $M365_TENANT_ID

```

---

## Reference Documentation

- [1Password CLI Documentation](https://developer.1password.com/docs/cli/)
- [Azure AD App Registration](https://docs.microsoft.com/en-us/azure/active-directory/develop/)
- [Azure AI Search API](https://docs.microsoft.com/en-us/azure/search/)
- [Microsoft Graph API](https://docs.microsoft.com/en-us/graph/)

---

## Support

For issues with:

- **1Password CLI**: Check [1Password Support](https://support.1password.com/)
- **Azure credentials**: See [docs/AZURE_RAG_CORE.md](AZURE_RAG_CORE.md)
- **M365 integration**: See [docs/M365_INTEGRATION.md](M365_INTEGRATION.md)
- **Security concerns**: See [docs/SECURITY.md](SECURITY.md)

---

**Last Updated:** October 18, 2025
**Status:** ✅ Production Ready

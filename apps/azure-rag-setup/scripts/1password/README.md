# 1Password Scripts

**Helper scripts for managing credentials with 1Password CLI**

## Available Scripts

### Azure AD / M365 Setup

- **`setup-azure-ad.sh`** - Automated Azure AD app creation with 1Password storage
- **`setup-manual.sh`** - Manual setup guidance for Azure AD app
- **`get-m365-credentials.sh`** - Retrieve and test M365 credentials

### Azure AI Search Setup

- **`create-azure-search-item.sh`** - Create 1Password item for Azure Search credentials

### Generic Helper Scripts

- **`setup-1password.sh`** - Generic 1Password item creation (from template)
- **`get-credentials.sh`** - Generic credential retrieval helper

## Usage

All scripts should be run from the project root:

```bash
# Azure AD setup
./scripts/1password/setup-azure-ad.sh

# Get credentials
./scripts/1password/get-m365-credentials.sh

# Create Azure Search item
./scripts/1password/create-azure-search-item.sh
```

## Requirements

- 1Password CLI installed (`brew install 1password-cli`)
- Signed in to 1Password CLI (`op signin`)
- Azure CLI installed and logged in (for Azure AD setup)

## Documentation

See [docs/security/1PASSWORD_GUIDE.md](../../docs/security/1PASSWORD_GUIDE.md) for complete documentation.

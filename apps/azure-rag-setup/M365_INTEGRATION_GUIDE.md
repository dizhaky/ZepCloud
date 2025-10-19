# Microsoft 365 Integration Guide

This guide explains how to set up and use the Microsoft 365 Graph API integration for indexing SharePoint, OneDrive, and
  Exchange data into your Azure AI Search RAG system.

## Overview

The M365 integration allows you to index documents from:

- **SharePoint Sites** - All document libraries across your organization
- **OneDrive for Business** - All users' personal OneDrive files
- **Exchange Online** - All users' emails and attachments

## Prerequisites

### 1. Azure AD App Registration

You need to register an Azure AD application with the following permissions:

#### Required API Permissions

- `Sites.Read.All` - Read all SharePoint sites
- `Files.Read.All` - Read all files in OneDrive and SharePoint
- `Mail.Read` - Read all mailboxes
- `User.Read.All` - Read all users in the organization

#### Steps to Register

1. **Go to Azure Portal** → Azure Active Directory → App registrations
2. **Click "New registration"**
3. **Name**: "M365 RAG Indexer" (or your preferred name)
4. **Supported account types**: "Accounts in this organizational directory only"
5. **Redirect URI**: Leave blank for now
6. **Click "Register"**

#### Configure API Permissions

1. **Go to "API permissions"** in your app
2. **Click "Add a permission"**
3. **Select "Microsoft Graph"**
4. **Select "Application permissions"**
5. **Add these permissions:**
   - Sites.Read.All
   - Files.Read.All
   - Mail.Read
   - User.Read.All
6. **Click "Grant admin consent"** (requires Global Admin)

#### Generate Client Secret

1. **Go to "Certificates & secrets"**
2. **Click "New client secret"**
3. **Description**: "M365 Indexer Secret"
4. **Expires**: 24 months (or your preference)
5. **Click "Add"**
6. **Copy the secret value** (you won't see it again!)

#### Get Application ID and Tenant ID

1. **Application (client) ID**: Found on the "Overview" page
2. **Directory (tenant) ID**: Found on the "Overview" page

### 2. Environment Configuration

Add these variables to your `.env` file:

```bash

# Microsoft 365 App Credentials

M365_CLIENT_ID=your_application_client_id
M365_CLIENT_SECRET=your_client_secret_value
M365_TENANT_ID=your_tenant_id

```

### 3. Install Dependencies

```bash

pip install -r requirements.txt

```

## Usage

### Test Authentication

```bash

python3 m365_indexer.py test-auth

```

This will verify your credentials and test the Microsoft Graph API connection.

### Estimate Data Volume

Before indexing, estimate how much data you'll be processing:

```bash

python3 m365_indexer.py estimate

```

This will:

- Count SharePoint sites and documents
- Estimate OneDrive storage across all users
- Calculate Exchange mailbox sizes
- Recommend Azure AI Search tier based on volume

### Sync SharePoint (MVP)

Start with SharePoint documents:

```bash

# Sync all SharePoint sites

python3 m365_indexer.py sync-sharepoint

# Sync specific site

python3 m365_indexer.py sync-sharepoint --site "site-id-here"

# Limit number of sites (for testing)

python3 m365_indexer.py sync-sharepoint --limit 3

```

### Check Status

```bash

python3 m365_indexer.py status

```

Shows:

- Last sync time
- Number of sites processed
- Total documents found
- Documents successfully uploaded

### Full Sync (All Services)

```bash

python3 m365_indexer.py sync

```

Currently syncs SharePoint only. OneDrive and Exchange sync will be added in future phases.

## Configuration

Edit `m365_config.yaml` to customize:

### File Types

```yaml

sharepoint:
  supported_extensions:

    - pdf
    - docx
    - xlsx

    # ... add more as needed

```

### Size Limits

```yaml

sharepoint:
  max_file_size_mb: 100 # Skip files larger than 100MB

```

### Exclusions

```yaml

exclusions:
  file_patterns:

    - "*.tmp"
    - "~*"

  folder_patterns:

    - "*/_vti_*"
    - "*/Forms"

```

## File Organization

Documents are organized in Azure Blob Storage as:

```

training-data/
├── sharepoint/
│   ├── Site_Name/
│   │   ├── Document_Library/
│   │   │   ├── document1.pdf
│   │   │   └── document2.docx
│   └── Another_Site/
│       └── ...
├── onedrive/          # (future)
│   └── User_Name/
└── exchange/          # (future)
    └── User_Name/

```

## Progress Tracking

The system tracks progress in JSON files:

- `sharepoint_progress.json` - SharePoint sync status
- `onedrive_progress.json` - OneDrive sync status (future)
- `exchange_progress.json` - Exchange sync status (future)

## Monitoring

### Check Indexer Status

```bash

python3 maintenance.py --non-interactive --action health

```

### View Detailed Logs

```bash

tail -f m365_indexer.log

```

## Troubleshooting

### Authentication Issues

**Error**: "Authentication failed"

**Solutions**:

1. Verify credentials in `.env` file
2. Check that admin consent was granted
3. Ensure app has required permissions
4. Test with: `python3 m365_indexer.py test-auth`

### Permission Issues

**Error**: "Insufficient privileges"

**Solutions**:

1. Ensure Global Admin granted consent
2. Check API permissions are correct
3. Verify tenant ID is correct

### Rate Limiting

**Error**: "Too many requests"

**Solutions**:

1. The system includes automatic retry with exponential backoff
2. Reduce batch sizes in `m365_config.yaml`
3. Add delays between requests

### Large File Issues

**Error**: "File too large" or timeouts

**Solutions**:

1. Increase `max_file_size_mb` in config
2. Increase timeout values
3. Consider excluding very large files

## Security Considerations

### Data Privacy

- All data stays within your Azure tenant
- No data is sent to external services
- Documents are stored in your Azure Blob Storage

### Access Control

- App requires explicit permissions
- Admin consent required for organization-wide access
- Consider excluding sensitive sites/users

### Compliance

- Review what data is being indexed
- Consider legal requirements for email indexing
- Implement data retention policies

## Performance Tips

### For Large Organizations

1. **Start small**: Test with a few sites first
2. **Use limits**: `--limit 5` for initial testing
3. **Monitor costs**: Check Azure AI Search tier requirements
4. **Schedule syncs**: Run during off-peak hours

### Optimization

1. **Incremental sync**: Only processes changed files
2. **Batch processing**: Handles multiple files efficiently
3. **Resume capability**: Can restart from where it left off
4. **Progress tracking**: Avoids re-processing files

## Next Steps

### Phase 1 Complete ✅

- SharePoint indexing working
- Authentication and progress tracking implemented
- CLI interface functional

### Phase 2 (Coming Soon)

- OneDrive for all users
- Exchange email indexing
- Enhanced monitoring dashboard

### Phase 3 (Future)

- Teams files and chats
- Advanced filtering and exclusions
- Automated scheduling

## Support

### Common Commands Reference

```bash

# Test everything is working

python3 m365_indexer.py test-auth

# See what data you have

python3 m365_indexer.py estimate

# Start indexing

python3 m365_indexer.py sync-sharepoint

# Check progress

python3 m365_indexer.py status

# View system health

python3 maintenance.py --non-interactive --action health

```

### Getting Help

1. **Check logs**: Look for error messages in console output
2. **Verify setup**: Ensure all prerequisites are met
3. **Test authentication**: Run `test-auth` command
4. **Start small**: Use `--limit` parameter for testing

## Cost Estimation

The volume estimator will tell you which Azure AI Search tier you need:

- **Free Tier**: Up to 10,000 documents, 50MB storage
- **Basic Tier**: $75/month, up to 100,000 documents, 2GB storage
- **Standard S1**: $250/month, up to 1,000,000 documents, 25GB storage
- **Standard S2**: $500/month, up to 10,000,000 documents, 100GB storage

Run `python3 m365_indexer.py estimate` to see your specific requirements.

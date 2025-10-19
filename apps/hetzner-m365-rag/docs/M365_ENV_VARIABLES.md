# M365 Environment Variables - Configuration Guide

## Overview

This document explains the environment variable naming convention for Microsoft 365 authentication in the Hetzner M365 RAG system.

## Variable Naming Convention

### Primary Variables (Recommended)

Use `M365_*` prefix for all Microsoft 365 authentication variables:

```bash
M365_CLIENT_ID=your-m365-application-client-id
M365_CLIENT_SECRET=your-m365-application-client-secret
M365_TENANT_ID=your-m365-tenant-id
M365_USE_DELEGATED_AUTH=true
```

### Backward Compatibility

The system also supports `AZURE_*` prefix for backward compatibility:

```bash
AZURE_CLIENT_ID=your-azure-application-client-id
AZURE_CLIENT_SECRET=your-azure-application-client-secret
AZURE_TENANT_ID=your-azure-tenant-id
```

**Note:** If both `M365_*` and `AZURE_*` variables are present, `M365_*` takes precedence.

## Authentication Modes

### Delegated Authentication (User Context)

**Recommended for:** Interactive indexing, development, testing

```bash
M365_USE_DELEGATED_AUTH=true
M365_CLIENT_ID=<your-public-client-app-id>
M365_TENANT_ID=<your-tenant-id>
# No M365_CLIENT_SECRET needed for delegated auth
```

**Authentication Methods:**
1. **Interactive Browser** (Primary): Opens browser for Microsoft login
2. **Device Code Flow** (Fallback): Displays code for manual entry

### Application Authentication (App Context)

**Recommended for:** Automated syncing, production deployments

```bash
M365_USE_DELEGATED_AUTH=false
M365_CLIENT_ID=<your-app-registration-id>
M365_CLIENT_SECRET=<your-client-secret>
M365_TENANT_ID=<your-tenant-id>
```

## Configuration in Docker Compose

The `docker-compose.yml` file includes intelligent fallback logic:

```yaml
environment:
  - M365_CLIENT_ID=${M365_CLIENT_ID:-${AZURE_CLIENT_ID}}
  - M365_CLIENT_SECRET=${M365_CLIENT_SECRET:-${AZURE_CLIENT_SECRET}}
  - M365_TENANT_ID=${M365_TENANT_ID:-${AZURE_TENANT_ID}}
  - M365_USE_DELEGATED_AUTH=${M365_USE_DELEGATED_AUTH:-true}
```

**Behavior:**
- Tries `M365_*` variables first
- Falls back to `AZURE_*` if `M365_*` not found
- Defaults to `true` for delegated auth if not specified

## Configuration in Code

The `config_manager.py` module handles the variable resolution:

```python
'm365': {
    # Support both M365_* and AZURE_* for backward compatibility
    'client_id': os.getenv(
        'M365_CLIENT_ID',
        os.getenv('AZURE_CLIENT_ID')
    ),
    'client_secret': os.getenv(
        'M365_CLIENT_SECRET',
        os.getenv('AZURE_CLIENT_SECRET')
    ),
    'tenant_id': os.getenv(
        'M365_TENANT_ID',
        os.getenv('AZURE_TENANT_ID')
    ),
    'use_delegated_auth': use_delegated.lower() == 'true'
}
```

## Azure AD App Registration

### For Delegated Auth (User Context)

1. **Application Type:** Public client/native
2. **Redirect URI:** `http://localhost` (for interactive browser flow)
3. **API Permissions:**
   - `Sites.ReadWrite.All`
   - `Files.ReadWrite.All`
   - `Mail.Read`
   - `User.Read.All`
   - **Permission Type:** Delegated
4. **Admin Consent:** Required

### For Application Auth (App Context)

1. **Application Type:** Web application
2. **Client Secret:** Generate and store securely
3. **API Permissions:**
   - `Sites.ReadWrite.All`
   - `Files.ReadWrite.All`
   - `Mail.Read`
   - `User.Read.All`
   - **Permission Type:** Application
4. **Admin Consent:** Required

## Migration Guide

### From AZURE_* to M365_*

If you have existing `.env` files with `AZURE_*` variables:

**Option 1: Keep as-is (Backward Compatible)**
```bash
# Your existing configuration will continue to work
AZURE_CLIENT_ID=abc123
AZURE_CLIENT_SECRET=xyz789
AZURE_TENANT_ID=tenant-id
```

**Option 2: Migrate to M365_* (Recommended)**
```bash
# Rename variables for consistency
M365_CLIENT_ID=abc123
M365_CLIENT_SECRET=xyz789
M365_TENANT_ID=tenant-id
M365_USE_DELEGATED_AUTH=true
```

**Option 3: Both (Maximum Compatibility)**
```bash
# Set both for transition period
M365_CLIENT_ID=abc123
M365_CLIENT_SECRET=xyz789
M365_TENANT_ID=tenant-id
M365_USE_DELEGATED_AUTH=true

# Old variables as fallback
AZURE_CLIENT_ID=abc123
AZURE_CLIENT_SECRET=xyz789
AZURE_TENANT_ID=tenant-id
```

## Troubleshooting

### Authentication Fails

**Check Variable Names:**
```bash
# Verify variables are set correctly
echo $M365_CLIENT_ID
echo $M365_TENANT_ID
echo $M365_USE_DELEGATED_AUTH
```

**In Docker:**
```bash
docker compose exec api env | grep M365
```

### Variable Not Found

**Common Issues:**
1. Using `AZURE_*` in `.env` but code expects `M365_*`
   - **Solution:** Upgrade to latest code that supports both
2. Variable name typo
   - **Solution:** Double-check spelling (case-sensitive)
3. `.env` file not loaded
   - **Solution:** Ensure `.env` file is in project root

### Delegated vs Application Auth

**Error:** "Invalid client secret"
- **Cause:** Using `M365_CLIENT_SECRET` with delegated auth
- **Solution:** Set `M365_USE_DELEGATED_AUTH=true` and remove client secret

**Error:** "User interaction required"
- **Cause:** Using application auth without client secret
- **Solution:** Set `M365_USE_DELEGATED_AUTH=false` and provide client secret

## Security Best Practices

### Credential Storage

✅ **DO:**
- Use environment variables for credentials
- Store secrets in `.env` file (git-ignored)
- Use Azure Key Vault or 1Password in production
- Rotate secrets regularly
- Use different credentials for dev/staging/prod

❌ **DON'T:**
- Hard-code credentials in source code
- Commit `.env` files to version control
- Share credentials in plain text
- Use production credentials for development

### Secret Rotation

**Monthly Rotation Recommended:**
1. Generate new client secret in Azure AD
2. Update `M365_CLIENT_SECRET` in `.env`
3. Restart services: `docker compose restart api`
4. Verify authentication works
5. Delete old secret from Azure AD

## Examples

### Development Setup (Delegated Auth)

```bash
# .env file
M365_CLIENT_ID=12345678-1234-1234-1234-123456789012
M365_TENANT_ID=87654321-4321-4321-4321-210987654321
M365_USE_DELEGATED_AUTH=true

# No client secret needed - uses interactive browser login
```

### Production Setup (Application Auth)

```bash
# .env file
M365_CLIENT_ID=12345678-1234-1234-1234-123456789012
M365_CLIENT_SECRET=super-secret-value-from-azure-ad
M365_TENANT_ID=87654321-4321-4321-4321-210987654321
M365_USE_DELEGATED_AUTH=false
```

### Hybrid Setup (Development + Automation)

```bash
# .env file for local development with delegated auth
M365_CLIENT_ID=12345678-1234-1234-1234-123456789012
M365_TENANT_ID=87654321-4321-4321-4321-210987654321
M365_USE_DELEGATED_AUTH=true

# docker-compose.production.yml overrides for automation
environment:
  - M365_CLIENT_SECRET=${M365_CLIENT_SECRET}
  - M365_USE_DELEGATED_AUTH=false
```

## Additional Resources

- [Azure AD App Registration Guide](https://docs.microsoft.com/azure/active-directory/develop/quickstart-register-app)
- [Microsoft Graph API Permissions](https://docs.microsoft.com/graph/permissions-reference)
- [MSAL Python Documentation](https://msal-python.readthedocs.io/)

## Support

For issues related to M365 authentication:

1. Check this guide first
2. Verify Azure AD app configuration
3. Check logs: `docker compose logs api | grep -i m365`
4. Review authentication module logs in `/data/m365-rag/logs/`

---

**Last Updated:** October 19, 2025  
**Version:** 1.0  
**Status:** Production Ready


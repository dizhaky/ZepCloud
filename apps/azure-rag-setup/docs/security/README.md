# Security Documentation

**Comprehensive security guides for Azure RAG Setup**

## Available Guides

### 🔐 [1Password Integration Guide](1PASSWORD_GUIDE.md)

Complete guide for secure credential management using 1Password CLI.

**Contents:**

- Prerequisites and setup
- Stored credentials (Azure Search + M365)
- Quick start scripts
- Credential retrieval examples
- Security best practices
- CI/CD integration
- Troubleshooting

**Quick Links:**

- Setup: `./scripts/1password/setup-azure-ad.sh`
- Retrieve credentials: `./scripts/1password/get-m365-credentials.sh`
- Azure Search credentials: `./scripts/1password/get-azure-search-credentials.sh`

---

## Security Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    1Password Vault                       │
│  (Encrypted Credential Storage)                         │
│                                                          │
│  ├── Azure AI Search - TypingMind RAG                   │
│  │   ├── Service Name                                   │
│  │   ├── Admin Key (encrypted)                          │
│  │   ├── Query Key (encrypted)                          │
│  │   └── Index Configuration                            │
│  │                                                       │
│  └── m365-rag-indexer-azure-ad                          │
│      ├── Application ID                                 │
│      ├── Client Secret (encrypted)                      │
│      └── Tenant ID                                      │
└─────────────────────────────────────────────────────────┘
              │
              │ (1Password CLI with MFA)
              ▼
┌─────────────────────────────────────────────────────────┐
│                Application Runtime                       │
│                                                          │
│  ├── Scripts retrieve credentials on-demand             │
│  ├── No plain text secrets in code                      │
│  ├── Environment variables loaded at runtime            │
│  └── Audit trail of all credential access               │
└─────────────────────────────────────────────────────────┘
              │
              │ (Azure AD OAuth 2.0)
              ▼
┌─────────────────────────────────────────────────────────┐
│              Azure & Microsoft Services                  │
│                                                          │
│  ├── Azure AI Search                                    │
│  ├── Azure Blob Storage                                 │
│  ├── Microsoft 365 (SharePoint, OneDrive, etc.)         │
│  └── Azure AD (Authentication)                          │
└─────────────────────────────────────────────────────────┘
```

---

## Security Principles

### 1. Zero Plain-Text Secrets

✅ **All credentials stored in 1Password**

- No `.env` files with secrets
- No hardcoded credentials in code
- No secrets in version control

### 2. Principle of Least Privilege

✅ **Minimal permissions granted**

- Azure AD app permissions scoped to required APIs
- Read-only access where possible
- Service-specific accounts

### 3. Credential Rotation

✅ **Regular credential updates**

- Azure AD secrets: 6-month rotation
- Azure Search keys: 12-month rotation
- Automated rotation reminders

### 4. Audit & Monitoring

✅ **Complete audit trail**

- 1Password tracks all credential access
- Azure AD logs authentication attempts
- Application logs all API calls

### 5. Multi-Factor Authentication

✅ **MFA required**

- 1Password CLI requires MFA
- Azure AD enforces MFA
- No shared accounts

---

## Best Practices

### Development Environment

```bash
# Always retrieve credentials at runtime
source <(./scripts/1password/get-m365-credentials.sh)

# Never commit secrets
echo ".env" >> .gitignore
echo "*.key" >> .gitignore
echo "*secret*" >> .gitignore
```

### Production Environment

```bash
# Use 1Password service accounts in CI/CD
export OP_SERVICE_ACCOUNT_TOKEN="${OP_TOKEN}"

# Load credentials at container startup
./scripts/1password/get-m365-credentials.sh

# Implement secret scanning
git secrets --install
```

### Team Collaboration

```bash
# Share credentials via 1Password team vaults
op vault create "Engineering"
op item move "m365-rag-indexer-azure-ad" --vault "Engineering"

# Set up access controls
op vault group add "Engineering" "Developers" --permissions "read"
```

---

## Compliance

### Data Protection

- ✅ **GDPR compliant** - Data encrypted at rest and in transit
- ✅ **SOC 2 Type II** - 1Password is SOC 2 certified
- ✅ **Zero-knowledge encryption** - 1Password uses zero-knowledge architecture

### Access Control

- ✅ **Role-based access** - Team vaults with granular permissions
- ✅ **Audit logs** - Complete history of credential access
- ✅ **MFA enforcement** - Required for all accounts

### Incident Response

- ✅ **Immediate revocation** - Credentials can be rotated instantly
- ✅ **Notification system** - Alerts on suspicious access
- ✅ **Recovery procedures** - Documented recovery workflows

---

## Quick Reference

### Retrieve Credentials

```bash
# M365 / Azure AD
./scripts/1password/get-m365-credentials.sh

# Azure AI Search
./scripts/1password/get-azure-search-credentials.sh
```

### Update Credentials

```bash
# Update Azure AD secret
op item edit "m365-rag-indexer-azure-ad" \
  --field "Client Secret"="NEW_SECRET"

# Update Azure Search key
op item edit "Azure AI Search - TypingMind RAG" \
  --vault Private \
  "Admin Key[password]=NEW_KEY"
```

### Check Status

```bash
# Verify 1Password CLI
op account get

# List stored items
op item list | grep -i "azure\|m365"

# Check credential expiry
op item get "m365-rag-indexer-azure-ad" --fields "Secret Expiry"
```

---

## Related Documentation

- [1Password Guide](1PASSWORD_GUIDE.md) - Complete integration guide
- [Azure AD Setup](../M365_INTEGRATION.md) - M365 integration details
- [Azure Search Config](../AZURE_RAG_CORE.md) - Azure Search setup

---

**Last Updated:** October 18, 2025
**Status:** ✅ Production Ready

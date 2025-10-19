# 1Password Integration Guide - M365 RAG System

Secure credential management using 1Password CLI for all sensitive data.

---

## 🔐 Why 1Password

- **Never store credentials in plain text**
- **Centralized credential management**
- **Easy rotation and updates**
- **Audit trail for access**
- **Team sharing capabilities**

---

## Step 1: Install 1Password CLI

### Windows Installation

## Option A: Using Winget (Recommended)

```powershell

winget install --id AgileBits.1Password.CLI

```

## Option B: Using Scoop

```powershell

scoop install 1password-cli

```

## Option C: Manual Download

1. Visit [https://1password.com/downloads/command-line/](https://1password.com/downloads/command-line/)
2. Download the Windows installer
3. Run the installer
4. Restart your terminal

### Verify Installation

```powershell

op --version

```

---

## Step 2: Sign In to 1Password

```powershell

# First time sign in

op signin

# Or if already configured

op signin --account your-account.1password.com

```

## Save your session:

```powershell

# This creates a session token

$env:OP_SESSION_your_account = $(op signin --raw)

```

---

## Step 3: Create 1Password Items

### A. Create Vault for M365 RAG Project

```powershell

# Create a dedicated vault (optional but recommended)

op vault create "M365-RAG-Production"

```

### B. Store Credentials

#### Hetzner Server

```powershell

op item create `
  --category=server `
  --vault="M365-RAG-Production" `
  --title="Hetzner AX52 Server" `
  server_ip="YOUR_SERVER_IP" `
  ssh_user="root" `
  ssh_port="22" `
  --tags="hetzner,production"

```

#### Azure AD / M365

```powershell

op item create `
  --category="API Credential" `
  --vault="M365-RAG-Production" `
  --title="Azure AD M365 RAG App" `
  client_id="YOUR_CLIENT_ID" `
  client_secret="YOUR_CLIENT_SECRET" `
  tenant_id="YOUR_TENANT_ID" `
  --tags="azure,m365"

```

#### OpenAI API

```powershell

op item create `
  --category="API Credential" `
  --vault="M365-RAG-Production" `
  --title="OpenAI API Key" `
  api_key="sk-YOUR_KEY" `
  organization_id="org-YOUR_ORG" `
  --tags="openai,api"

```

#### Database Credentials

```powershell

op item create `
  --category="Database" `
  --vault="M365-RAG-Production" `
  --title="M365 RAG PostgreSQL" `
  database="m365_rag" `
  username="raguser" `
  password[password]="$(openssl rand -base64 32)" `
  hostname="postgres" `
  port="5432" `
  --tags="postgres,database"

```

#### Elasticsearch

```powershell

op item create `
  --category="Database" `
  --vault="M365-RAG-Production" `
  --title="M365 RAG Elasticsearch" `
  username="elastic" `
  password[password]="$(openssl rand -base64 32)" `
  hostname="elasticsearch" `
  port="9200" `
  --tags="elasticsearch"

```

#### Redis

```powershell

op item create `
  --category="Database" `
  --vault="M365-RAG-Production" `
  --title="M365 RAG Redis" `
  password[password]="$(openssl rand -base64 32)" `
  hostname="redis" `
  port="6379" `
  --tags="redis"

```

#### MinIO

```powershell

op item create `
  --category="API Credential" `
  --vault="M365-RAG-Production" `
  --title="M365 RAG MinIO" `
  access_key="$(openssl rand -hex 16)" `
  secret_key="$(openssl rand -base64 32)" `
  endpoint="minio:9000" `
  bucket="m365-documents" `
  --tags="minio,storage"

```

#### JWT Secret

```powershell

op item create `
  --category="Password" `
  --vault="M365-RAG-Production" `
  --title="M365 RAG JWT Secret" `
  password[password]="$(openssl rand -hex 32)" `
  --tags="jwt,api"

```

---

## Step 4: Create Environment File Generator Script

Create a PowerShell script to generate `.env` from 1Password:

```powershell

# Save as: scripts/generate-env-from-1password.ps1

<#
.SYNOPSIS
    Generate .env file from 1Password credentials
.DESCRIPTION
    Pulls all M365 RAG credentials from 1Password and generates .env file
.EXAMPLE
    .\generate-env-from-1password.ps1
#>

param(
    [string]$Vault = "M365-RAG-Production",
    [string]$OutputFile = ".env"
)

# Ensure 1Password CLI is available

if (-not (Get-Command op -ErrorAction SilentlyContinue)) {
    Write-Error "1Password CLI (op) not found. Please install it first."
    exit 1
}

Write-Host "🔐 Fetching credentials from 1Password..." -ForegroundColor Cyan

# Get credentials from 1Password

$azureClientId = op item get "Azure AD M365 RAG App" --vault $Vault --fields client_id
$azureClientSecret = op item get "Azure AD M365 RAG App" --vault $Vault --fields client_secret
$azureTenantId = op item get "Azure AD M365 RAG App" --vault $Vault --fields tenant_id

$openaiKey = op item get "OpenAI API Key" --vault $Vault --fields api_key
$openaiOrg = op item get "OpenAI API Key" --vault $Vault --fields organization_id

$postgresPassword = op item get "M365 RAG PostgreSQL" --vault $Vault --fields password
$esPassword = op item get "M365 RAG Elasticsearch" --vault $Vault --fields password
$redisPassword = op item get "M365 RAG Redis" --vault $Vault --fields password

$minioAccessKey = op item get "M365 RAG MinIO" --vault $Vault --fields access_key
$minioSecretKey = op item get "M365 RAG MinIO" --vault $Vault --fields secret_key

$jwtSecret = op item get "M365 RAG JWT Secret" --vault $Vault --fields password

$hetznerIp = op item get "Hetzner AX52 Server" --vault $Vault --fields server_ip

# Generate .env file

$envContent = @"

# ============================================

# M365 RAG System - Environment Configuration

# Generated from 1Password on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

# ============================================ (2)

# WARNING: This file is auto-generated. Do not edit manually

# Update credentials in 1Password and regenerate this file

# ============================================ (3)

# ============================================ (4)

# DATABASE & STORAGE

# ============================================ (5)

DATABASE_URL=postgresql://raguser:$postgresPassword@postgres:5432/m365_rag
POSTGRES_USER=raguser
POSTGRES_PASSWORD=$postgresPassword
POSTGRES_DB=m365_rag

# ============================================ (6)

# ELASTICSEARCH (2)

# ============================================ (7)

ES_HOST=elasticsearch
ES_PORT=9200
ES_USER=elastic
ES_PASSWORD=$esPassword
ES_USE_SSL=true
ES_VERIFY_CERTS=false

# ============================================ (8)

# REDIS (2)

# ============================================ (9)

REDIS_URL=redis://:$redisPassword@redis:6379
REDIS_PASSWORD=$redisPassword

# ============================================ (10)

# MINIO (S3-compatible storage)

# ============================================ (11)

MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=$minioAccessKey
MINIO_SECRET_KEY=$minioSecretKey
MINIO_BUCKET=m365-documents

# ============================================ (12)

# MICROSOFT 365 / AZURE AD

# ============================================ (13)

AZURE_CLIENT_ID=$azureClientId
AZURE_CLIENT_SECRET=$azureClientSecret
AZURE_TENANT_ID=$azureTenantId
M365_USE_DELEGATED_AUTH=false

# ============================================ (14)

# OPENAI

# ============================================ (15)

OPENAI_API_KEY=$openaiKey
OPENAI_ORG_ID=$openaiOrg

# ============================================ (16)

# SECURITY

# ============================================ (17)

JWT_SECRET=$jwtSecret
API_KEY=$(openssl rand -hex 32)

# ============================================ (18)

# HETZNER SERVER (2)

# ============================================ (19)

HETZNER_SERVER_IP=$hetznerIp

# ============================================ (20)

# OPTIONAL: EMAIL ALERTS

# ============================================ (21)

# SMTP_HOST=smtp.gmail.com

# SMTP_PORT=587

# SMTP_USER=your-email@gmail.com

# SMTP_PASSWORD=your-app-password

# ALERT_EMAIL=admin@yourdomain.com

"@

# Write to file

$envContent | Out-File -FilePath $OutputFile -Encoding UTF8 -NoNewline

# Set secure permissions (Windows)

$acl = Get-Acl $OutputFile
$acl.SetAccessRuleProtection($true, $false)
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    [System.Security.Principal.WindowsIdentity]::GetCurrent().Name,
    "FullControl",
    "Allow"
)
$acl.SetAccessRule($rule)
Set-Acl $OutputFile $acl

Write-Host "✅ .env file generated successfully!" -ForegroundColor Green
Write-Host "   Location: $OutputFile" -ForegroundColor Gray
Write-Host "   Permissions set to current user only" -ForegroundColor Gray
Write-Host ""
Write-Host "⚠️  Remember:" -ForegroundColor Yellow
Write-Host "   - Never commit .env to git" -ForegroundColor Yellow
Write-Host "   - Regenerate this file after updating 1Password" -ForegroundColor Yellow
Write-Host "   - Keep 1Password vault locked when not in use" -ForegroundColor Yellow

```

---

## Step 5: Generate .env File

```powershell

# Navigate to project root

cd apps/hetzner-m365-rag

# Generate .env from 1Password

.\scripts\generate-env-from-1password.ps1

```

---

## Step 6: Retrieve Individual Credentials

### Quick Reference Commands

```powershell

# Get Azure Client ID

op item get "Azure AD M365 RAG App" --vault M365-RAG-Production --fields client_id

# Get OpenAI API Key

op item get "OpenAI API Key" --vault M365-RAG-Production --fields api_key

# Get PostgreSQL Password

op item get "M365 RAG PostgreSQL" --vault M365-RAG-Production --fields password

# Get Hetzner Server IP

op item get "Hetzner AX52 Server" --vault M365-RAG-Production --fields server_ip

# SSH to Hetzner (using 1Password)

$HETZNER_IP = op item get "Hetzner AX52 Server" --vault M365-RAG-Production --fields server_ip
ssh root@$HETZNER_IP

```

---

## Step 7: Update Credentials

### When Rotating Credentials

```powershell

# Update Azure Client Secret

op item edit "Azure AD M365 RAG App" --vault M365-RAG-Production client_secret="NEW_SECRET"

# Update OpenAI API Key

op item edit "OpenAI API Key" --vault M365-RAG-Production api_key="NEW_KEY"

# Regenerate .env file

.\scripts\generate-env-from-1password.ps1

# Restart services to use new credentials

docker compose restart

```

---

## Step 8: Team Sharing (Optional)

### Share Vault with Team

```powershell

# Invite team member to vault

op vault user grant --vault M365-RAG-Production --user teammate@company.com

# Set permissions (view_items, create_items, edit_items, etc.)

op vault user set-role --vault M365-RAG-Production --user teammate@company.com --role manager

```

---

## Security Best Practices

### ✅ DO

- **Store ALL credentials in 1Password**
- **Use service accounts for API access**
- **Rotate credentials every 6-12 months**
- **Use separate vaults for dev/staging/production**
- **Enable 2FA on 1Password account**
- **Lock 1Password when not in use**
- **Use strong master password**

### ❌ DON'T

- **Never commit .env to git** (already in .gitignore)
- **Never share credentials via email/chat**
- **Never store credentials in code comments**
- **Never use production credentials in development**
- **Never share your 1Password master password**

---

## Automation & CI/CD Integration

### GitHub Actions with 1Password

```yaml

# .github/workflows/deploy.yml

name: Deploy to Hetzner

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:

      - uses: actions/checkout@v3

      - name: Install 1Password CLI

        uses: 1password/load-secrets-action@v1
        with:
          export-env: true
        env:
          OP_SERVICE_ACCOUNT_TOKEN: ${{ secrets.OP_SERVICE_ACCOUNT_TOKEN }}
          AZURE_CLIENT_ID: op://M365-RAG-Production/Azure AD M365 RAG App/client_id
          AZURE_CLIENT_SECRET: op://M365-RAG-Production/Azure AD M365 RAG App/client_secret
          OPENAI_API_KEY: op://M365-RAG-Production/OpenAI API Key/api_key

      - name: Deploy

        run: |
          # Your deployment commands here

```

---

## Troubleshooting

### Issue: "op not found"

```powershell

# Add to PATH (Windows)

$env:PATH += ";C:\Program Files\1Password CLI"

# Or reinstall

winget install --id AgileBits.1Password.CLI

```

### Issue: "Authentication required"

```powershell

# Sign in again

op signin

# Or check session

op whoami

```

### Issue: "Item not found"

```powershell

# List all items in vault

op item list --vault M365-RAG-Production

# Search for item

op item get "Azure AD" --vault M365-RAG-Production

```

---

## Quick Start Checklist

- [ ] Install 1Password CLI
- [ ] Sign in to 1Password
- [ ] Create M365-RAG-Production vault
- [ ] Add all credentials to 1Password
- [ ] Create generate-env script
- [ ] Run script to generate .env
- [ ] Verify .env file has correct values
- [ ] Delete any old plaintext credential files
- [ ] Add 1Password integration to deployment docs

---

## Resources

- **1Password CLI Docs**: [https://developer.1password.com/docs/cli](https://developer.1password.com/docs/cli)
- **1Password GitHub Actions**: [https://github.com/1password/load-secrets-action](https://github.com/1password/load-secrets-action)
- **Security Best Practices**: See `SECURITY.md`

---

## Next Steps:

1. Install 1Password CLI (see above)
2. Store your credentials in 1Password
3. Generate .env file from 1Password
4. Continue with deployment using secure credentials!

🔐 **Your credentials are now secure!**

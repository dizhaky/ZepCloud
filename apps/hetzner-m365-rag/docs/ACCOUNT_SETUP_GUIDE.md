# Account Setup Guide - M365 RAG System

Complete guide to setting up all required accounts and credentials.

---

## Required Accounts Checklist

### 1. Hetzner Cloud Account

**Purpose**: Host the M365 RAG infrastructure

**Steps**:

1. Go to [https://www.hetzner.com](https://www.hetzner.com)
2. Click "Sign Up" or "Register"
3. Complete registration with email verification
4. Add payment method (credit card or SEPA)
5. Enable 2FA for security

**What You'll Need**:

- Server: AX52 Dedicated Server (recommended)
  - 12-core CPU
  - 64GB RAM
  - 2x 512GB NVMe SSD (RAID 1)
  - ~€60/month

**Order Server**:

```bash

# After login, go to

# Console → Servers → Order → Dedicated Servers → AX Line → AX52

```

**Save These Details**:

- [ ] Server IP address: `________________`
- [ ] SSH root password (emailed to you)
- [ ] Server hostname: `________________`

---

### 2. Microsoft 365 / Azure AD Account

**Purpose**: Access M365 documents (SharePoint, OneDrive)

**Requirements**:

- **Option A**: M365 Admin Account (easiest)
  - Global Admin or SharePoint Admin role
  - Can access all sites/files

- **Option B**: Azure AD App Registration (recommended for production)
  - Requires tenant admin consent
  - More secure with limited permissions

#### Option A: Use Existing M365 Admin

**Steps**:

1. Verify you have M365 admin access
2. Go to [https://admin.microsoft.com](https://admin.microsoft.com)
3. Confirm you can access:
   - SharePoint Admin Center
   - OneDrive Admin

**Save These Details**:

- [ ] M365 Admin Email: `________________`
- [ ] Tenant ID: `________________` (from Azure Portal)
- [ ] Tenant Name: `________________`

#### Option B: Create Azure AD App Registration (Recommended)

**Steps**:

1. **Go to Azure Portal**:
   - Visit [https://portal.azure.com](https://portal.azure.com)
   - Sign in with M365 admin account

2. **Register Application**:

   ```
   Azure Active Directory → App registrations → New registration

   Name: M365 RAG Indexer
   Supported account types: Single tenant
   Redirect URI: (leave blank for now)
   ```

3. **Note Application Details**:
   - Copy **Application (client) ID**
   - Copy **Directory (tenant) ID**

4. **Create Client Secret**:

   ```
   Your App → Certificates & secrets → New client secret

   Description: M365 RAG API Key
   Expires: 24 months
   ```

   - **IMPORTANT**: Copy the secret value immediately (shown only once)

5. **Configure API Permissions**:

   ```
   Your App → API permissions → Add a permission → Microsoft Graph
   ```

   **Required Permissions** (Application permissions):

   - `Files.Read.All` - Read OneDrive files
   - `Sites.Read.All` - Read SharePoint sites
   - `User.Read.All` - Read user information
   - `Mail.Read` - Read emails (optional)

   **Click "Grant admin consent"** (requires Global Admin)

6. **Verify Permissions**:

   ```
   API permissions tab should show:
   ✅ Files.Read.All (Granted for [Your Org])
   ✅ Sites.Read.All (Granted for [Your Org])
   ✅ User.Read.All (Granted for [Your Org])
   ```

**Save These Details**:

- [ ] Client ID: `________________`
- [ ] Client Secret: `________________`
- [ ] Tenant ID: `________________`
- [ ] Redirect URI: `http://localhost:8000/auth/callback` (if using delegated)

---

### 3. OpenAI Account

**Purpose**: Embeddings and LLM for RAG functionality

**Steps**:

1. **Create OpenAI Account**:
   - Go to [https://platform.openai.com](https://platform.openai.com)
   - Sign up with email or Google/Microsoft account
   - Verify email

2. **Add Payment Method**:
   - Go to [https://platform.openai.com/account/billing](https://platform.openai.com/account/billing)
   - Click "Add payment method"
   - Add credit card
   - Set usage limits (recommended: $50/month to start)

3. **Create API Key**:
   - Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
   - Click "Create new secret key"
   - Name: `M365-RAG-Production`
   - Copy the key immediately (shown only once)

4. **Configure Usage Limits** (Optional but recommended):

   ```
   Billing → Usage limits

   Hard limit: $100/month
   Soft limit: $50/month (email alert)
   ```

**Models You'll Use**:

- `text-embedding-3-large` - For embeddings (~$0.13 per 1M tokens)
- `gpt-4o-mini` - For chat/QA (~$0.15/$0.60 per 1M tokens)

**Estimated Costs**:

- 10,000 documents: ~$5-10 for embeddings
- 1,000 queries/day: ~$5-10/day
- **Monthly estimate**: $100-200 for moderate usage

**Save These Details**:

- [ ] OpenAI API Key: `sk-...________________`
- [ ] Organization ID (optional): `________________`

---

### 4. Email Account for Alerts (Optional)

**Purpose**: Receive system alerts and notifications

**Options**:

- **Gmail** (easiest for testing)
- **SendGrid** (recommended for production)
- **AWS SES** (cost-effective)

#### Option: Gmail SMTP

**Steps**:

1. Go to [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Create app password:
   - Name: `M365 RAG Alerts`
   - Copy the 16-character password

**Save These Details**:

- [ ] SMTP Email: `________________@gmail.com`
- [ ] SMTP Password: `________________`

---

### 5. Domain Name (Optional but Recommended)

**Purpose**: Professional URL instead of IP address

**Providers**:

- **Namecheap**: $8-12/year
- **Google Domains**: $12/year
- **Cloudflare**: $8-10/year

**Steps**:

1. Register domain (e.g., `m365-rag.yourdomain.com`)
2. Configure DNS:

   ```
   A Record: @ → Your Hetzner Server IP
   A Record: www → Your Hetzner Server IP
   ```

**Save These Details**:

- [ ] Domain: `________________`
- [ ] Registrar: `________________`
- [ ] DNS Provider: `________________`

---

## Creating the .env File

Once you have all accounts set up, create your `.env` file:

```bash

# Navigate to project

cd apps/hetzner-m365-rag

# Create .env file

cat > .env << 'EOF'

# ============================================

# DATABASE & STORAGE

# ============================================ (2)

DATABASE_URL=postgresql://raguser:YOUR_SECURE_PASSWORD@postgres:5432/m365_rag
POSTGRES_USER=raguser
POSTGRES_PASSWORD=YOUR_SECURE_PASSWORD
POSTGRES_DB=m365_rag

# ============================================ (3)

# ELASTICSEARCH

# ============================================ (4)

ES_HOST=elasticsearch
ES_PORT=9200
ES_USER=elastic
ES_PASSWORD=YOUR_SECURE_ES_PASSWORD
ES_USE_SSL=true
ES_VERIFY_CERTS=false

# ============================================ (5)

# REDIS

# ============================================ (6)

REDIS_URL=redis://redis:6379
REDIS_PASSWORD=YOUR_SECURE_REDIS_PASSWORD

# ============================================ (7)

# MINIO (S3-compatible storage)

# ============================================ (8)

MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=YOUR_MINIO_ACCESS_KEY
MINIO_SECRET_KEY=YOUR_SECURE_MINIO_SECRET
MINIO_BUCKET=m365-documents

# ============================================ (9)

# MICROSOFT 365 / AZURE AD

# ============================================ (10)

AZURE_CLIENT_ID=YOUR_CLIENT_ID_HERE
AZURE_CLIENT_SECRET=YOUR_CLIENT_SECRET_HERE
AZURE_TENANT_ID=YOUR_TENANT_ID_HERE
M365_USE_DELEGATED_AUTH=false

# ============================================ (11)

# OPENAI

# ============================================ (12)

OPENAI_API_KEY=sk-YOUR_OPENAI_KEY_HERE
OPENAI_ORG_ID=org-YOUR_ORG_ID_HERE  # Optional

# ============================================ (13)

# SECURITY

# ============================================ (14)

JWT_SECRET=YOUR_RANDOM_JWT_SECRET_HERE
API_KEY=YOUR_API_KEY_HERE  # For securing endpoints

# ============================================ (15)

# OPTIONAL: EMAIL ALERTS

# ============================================ (16)

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_EMAIL=admin@yourdomain.com

EOF

# Set secure permissions

chmod 600 .env

```

**Generate Secure Passwords**:

```bash

# Generate random passwords

openssl rand -base64 32  # For DATABASE_PASSWORD
openssl rand -base64 32  # For ES_PASSWORD
openssl rand -base64 32  # For REDIS_PASSWORD
openssl rand -base64 32  # For MINIO_SECRET_KEY
openssl rand -hex 32     # For JWT_SECRET

```

---

## Verification Checklist

Before proceeding to deployment, verify:

### Hetzner

- [ ] Server ordered and IP received
- [ ] Can SSH into server: `ssh root@YOUR_SERVER_IP`
- [ ] Server has internet connectivity

### Microsoft 365

- [ ] Azure AD app created (or admin account ready)
- [ ] Client ID, Secret, and Tenant ID saved
- [ ] API permissions granted
- [ ] Can access Graph API: Test with Graph Explorer
  - [https://developer.microsoft.com/en-us/graph/graph-explorer](https://developer.microsoft.com/en-us/graph/graph-explorer)

### OpenAI (2)

- [ ] Account created and verified
- [ ] Payment method added
- [ ] API key generated and saved
- [ ] Usage limits configured
- [ ] Test API access:

  ```bash
  curl https://api.openai.com/v1/models \
    -H "Authorization: Bearer YOUR_API_KEY"
  ```

### Configuration

- [ ] `.env` file created
- [ ] All credentials filled in
- [ ] File permissions set to 600
- [ ] Backup copy saved securely

---

## Security Best Practices

1. **Never commit .env to Git**

   ```bash
   # Already in .gitignore, but double-check
   echo ".env" >> .gitignore
   ```

2. **Use strong passwords**
   - Minimum 32 characters for production
   - Use password manager (1Password, Bitwarden)

3. **Enable 2FA everywhere**
   - Hetzner console
   - Azure Portal
   - OpenAI account

4. **Rotate credentials regularly**
   - Azure secrets: Every 6-12 months
   - OpenAI keys: Every 12 months
   - Database passwords: Every 12 months

5. **Backup credentials securely**
   - Encrypted password manager
   - Secure note system
   - Never in plain text files

---

## Cost Summary

| Service | Monthly Cost | Notes |
|---------|-------------|-------|
| **Hetzner AX52** | €60 (~$65) | Dedicated server |
| **OpenAI API** | $100-200 | Usage-based, varies by traffic |
| **Domain** | $1 | (~$12/year) |
| **SSL Certificate** | $0 | Free with Let's Encrypt |
| **Backups** | $5-10 | Optional: Hetzner Storage Box |
| **Total** | **$170-280/month** | |

**Cost Optimization Tips**:

- Use `gpt-4o-mini` instead of `gpt-4` (10x cheaper)
- Implement aggressive caching
- Use embedding cache for duplicate content
- Set OpenAI usage limits

---

## Next Steps

Once all accounts are set up:

1. ✅ **Complete this account setup**
2. 📦 **Deploy to Hetzner** - Follow `DEPLOYMENT_CHECKLIST.md`
3. 🔐 **Configure SSL** - Follow `docs/SSL_SETUP.md`
4. 📊 **Set up monitoring** - Configure Grafana dashboards
5. 🔄 **Initial M365 sync** - Index first documents

---

## Support & Troubleshooting

## Having issues?

- **Azure AD permissions**: Ensure admin consent is granted
- **OpenAI rate limits**: Check usage dashboard
- **Hetzner access**: Check email for SSH credentials
- **Graph API errors**: Use Graph Explorer to test

## Need help?

- Check `README.md` for general documentation
- See `TROUBLESHOOTING.md` for common issues
- Open GitHub issue for bugs

---

**Ready to deploy?** 🚀

Once you've completed this setup, proceed to `DEPLOYMENT_CHECKLIST.md` to deploy the system to your Hetzner server!

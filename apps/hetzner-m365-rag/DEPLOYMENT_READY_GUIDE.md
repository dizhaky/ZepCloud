# 🚀 Hetzner M365 RAG - Deployment Ready Guide

**Generated:** 2025-10-19
**Status:** Ready for Deployment
**Credentials Source:** 1Password

---

## ✅ Pre-Deployment Checklist

### Credentials Retrieved from 1Password

1. **Hetzner Account** ✅
   - Email: `dizhaky@gmail.com`
   - Password: Retrieved from 1Password
   - URL: https://accounts.hetzner.com

2. **OpenAI API Key** ✅
   - Configured in `.env.deployment`
   - Valid and ready to use

3. **Azure AD App Registration** ⚠️ **ACTION REQUIRED**
   - Status: **Not yet created**
   - See instructions below

---

## 🔑 Step 1: Create Azure AD App Registration

**IMPORTANT:** Complete this before deploying to Hetzner!

### Quick Setup Instructions

1. **Go to Azure Portal**:

   ```
   https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade
   ```

2. **Click "New registration"**

3. **Configure Application**:
   - **Name**: `M365 RAG System`
   - **Supported account types**: `Accounts in this organizational directory only (Single tenant)`
   - **Redirect URI**:
     - Platform: `Web`
     - URL: `http://localhost:8000`

4. **Click "Register"**

5. **Copy These Values** (you'll need them):
   - **Application (client) ID** → This is `M365_CLIENT_ID`
   - **Directory (tenant) ID** → This is `M365_TENANT_ID`

6. **Create Client Secret**:
   - Go to "Certificates & secrets" tab
   - Click "New client secret"
   - Description: `M365 RAG System Secret`
   - Expires: `24 months` (recommended)
   - Click "Add"
   - **COPY THE SECRET VALUE IMMEDIATELY** → This is `M365_CLIENT_SECRET`
   - ⚠️ You cannot view it again after leaving the page!

7. **Add API Permissions**:
   - Go to "API permissions" tab
   - Click "Add a permission"
   - Select "Microsoft Graph"
   - Choose "Delegated permissions"
   - Add these permissions:
     - `Files.Read.All`
     - `Files.ReadWrite.All`
     - `Sites.Read.All`
     - `Sites.ReadWrite.All`
     - `Mail.Read`
     - `User.Read`
     - `User.Read.All`
   - Click "Add permissions"

8. **Grant Admin Consent**:
   - Click "Grant admin consent for [Your Organization]"
   - Confirm "Yes"
   - All permissions should now show "Granted" status

---

## 📝 Step 2: Update Environment Configuration

1. **Open the deployment environment file**:

   ```bash
   notepad c:\Dev\ZepCloud\apps\hetzner-m365-rag\.env.deployment
   ```

2. **Update these values** with your Azure AD app registration details:

   ```bash
   M365_CLIENT_ID=<your-application-client-id-from-step-5>
   M365_CLIENT_SECRET=<your-client-secret-from-step-6>
   M365_TENANT_ID=<your-directory-tenant-id-from-step-5>
   ```

3. **Generate secure passwords** for these fields (replace placeholders):

   ```powershell
   # Run in PowerShell to generate secure passwords
   -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
   ```

   Update:

   - `ELASTIC_PASSWORD`
   - `POSTGRES_PASSWORD`
   - `MINIO_ROOT_PASSWORD`
   - `REDIS_PASSWORD`
   - `GRAFANA_PASSWORD`
   - `JWT_SECRET`
   - `RAGFLOW_SECRET_KEY`

4. **Save the file**

---

## 🖥️ Step 3: Access Hetzner Console

### Login to Hetzner

**Note:** If you see a rate limit message, wait 10 minutes and retry.

1. **Open Hetzner Console**:

   ```
   https://accounts.hetzner.com/login
   ```

2. **Login with credentials from 1Password**:
   - Email: `dizhaky@gmail.com`
   - Password: (from 1Password)

3. **Navigate to Server Management**

### Options for Server Setup

**Option A: Use Existing Server** (if you have one)

- Note the server IP address
- Ensure SSH access is enabled
- Proceed to Step 4

## Option B: Create New AX52 Dedicated Server

1. Go to "Dedicated Servers" > "Order"
2. Select: **AX52**
   - CPU: AMD Ryzen 9 5950X (16 cores / 32 threads)
   - RAM: 128GB DDR4 ECC
   - Storage: 2x 3.84TB NVMe SSD
   - Network: 1 Gbit/s
   - Price: ~€108/month
3. Choose datacenter location (recommended: Falkenstein or Helsinki)
4. Operating System: **Ubuntu 24.04 LTS**
5. Add SSH key (recommended) or note root password
6. Complete order
7. Wait for provisioning (usually 2-4 hours)
8. Note the assigned IP address

---

## 📤 Step 4: Upload Files to Hetzner Server

### Prepare Deployment Package

1. **Create deployment archive**:

   ```powershell
   cd c:\Dev\ZepCloud\apps\hetzner-m365-rag

   # Create tar archive (requires WSL or Git Bash)
   wsl tar -czf ../m365-rag-deploy.tar.gz .
   ```

### Upload to Server

## Replace `SERVER_IP` with your actual Hetzner server IP

```powershell

# Using SCP (recommended)

scp c:\Dev\ZepCloud\apps\m365-rag-deploy.tar.gz root@SERVER_IP:/tmp/

# Or using SFTP

sftp root@SERVER_IP
put c:\Dev\ZepCloud\apps\m365-rag-deploy.tar.gz /tmp/
bye

```

---

## 🚀 Step 5: Deploy on Hetzner Server

### SSH into Server

```powershell

ssh root@SERVER_IP

```

### Extract and Deploy

```bash

# Extract deployment files

cd /tmp
tar -xzf m365-rag-deploy.tar.gz -C /opt/
mv /opt/hetzner-m365-rag /opt/m365-rag

# Copy your configured .env file

# (You'll need to transfer this separately or edit on server)

# Make scripts executable

cd /opt/m365-rag
chmod +x scripts/*.sh

# Run deployment script

./scripts/deploy.sh

```

### What the Deployment Script Does

The `deploy.sh` script will automatically:

1. ✅ Update system packages
2. ✅ Install Docker and Docker Compose
3. ✅ Configure firewall (UFW)
4. ✅ Install fail2ban for security
5. ✅ Generate Elasticsearch SSL certificates
6. ✅ Create data directories with correct permissions
7. ✅ Start all 11 Docker services
8. ✅ Run health checks
9. ✅ Display access URLs

**Estimated time:** 10-15 minutes

---

## ✅ Step 6: Verify Deployment

### Check Service Health

```bash

# Check all services are running

docker compose ps

# Should show all services as "healthy" or "Up"

```

### Test API Endpoint

```bash

# Health check

curl http://localhost:8000/health

# Expected response

# {

#   "status": "healthy",

#   "version": "1.0.0",

#   "services": {

#     "elasticsearch": "connected",

#     "postgres": "connected",

#     "redis": "connected"

#   }

# } (2)

```

### Test Elasticsearch

```bash

# Check cluster health (replace ELASTIC_PASSWORD)

curl -k -u elastic:YOUR_ELASTIC_PASSWORD https://localhost:9200/_cluster/health

# Expected: {"status":"green"}

```

### Check Logs

```bash

# View all service logs

docker compose logs -f

# View specific service

docker compose logs -f api
docker compose logs -f elasticsearch
docker compose logs -f ragflow

```

---

## 🌐 Access Points

After successful deployment, access these URLs:

- **RAGFlow UI**: `http://YOUR_SERVER_IP:9380`
- **FastAPI**: `http://YOUR_SERVER_IP:8000`
- **API Docs (Swagger)**: `http://YOUR_SERVER_IP:8000/docs`
- **Grafana**: `http://YOUR_SERVER_IP:3000`
  - Username: `admin`
  - Password: (from your `.env` file)
- **Prometheus**: `http://YOUR_SERVER_IP:9090`
- **MinIO Console**: `http://YOUR_SERVER_IP:9001`

---

## 🔐 Post-Deployment Security

### Enable HTTPS with Let's Encrypt (Recommended)

**Prerequisites:** Domain name pointing to your server

```bash

# Install Certbot

apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate

certbot --nginx -d rag.yourdomain.com

# Auto-renewal is configured automatically

```

### Configure Automated Backups

```bash

# Add to crontab

crontab -e

# Add this line for daily backups at 2 AM

0 2 * * * /opt/m365-rag/scripts/backup.sh >> /var/log/m365-rag-backup.log 2>&1

```

### Monitor System

- Check Grafana dashboards daily
- Review logs for errors
- Monitor disk space: `df -h`
- Monitor memory: `free -h`

---

## 🧪 Testing M365 Integration

### Authenticate with M365

```bash

# Interactive browser authentication

curl -X POST http://YOUR_SERVER_IP:8000/m365/auth \
  -H "Content-Type: application/json" \
  -d '{"auth_type":"interactive"}'

# Follow the URL in the response to complete authentication

```

### Sync SharePoint

```bash

# Sync SharePoint site

curl -X POST http://YOUR_SERVER_IP:8000/m365/sync/sharepoint \
  -H "Content-Type: application/json" \
  -d '{
    "site_url": "https://yourtenant.sharepoint.com/sites/yoursite"
  }'

```

### Test Search

```bash

# Search indexed documents

curl -X POST http://YOUR_SERVER_IP:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "quarterly report",
    "filters": {"source": "sharepoint"},
    "limit": 5
  }'

```

---

## 🐛 Troubleshooting

### Elasticsearch Won't Start

```bash

# Check logs (2)

docker compose logs elasticsearch

# Common fix: Increase vm.max_map_count

sudo sysctl -w vm.max_map_count=262144
echo "vm.max_map_count=262144" >> /etc/sysctl.conf

# Restart

docker compose restart elasticsearch

```

### Out of Memory

```bash

# Check memory usage

free -h
docker stats

# Adjust resource limits in docker-compose.yml

# Reduce Elasticsearch heap if needed

ES_JAVA_OPTS: "-Xms8g -Xmx8g"  # Reduce from 16g if needed

```

### M365 Authentication Fails

```bash

# Verify Azure app permissions

# Check .env file has correct values

cat /opt/m365-rag/.env | grep M365

# Test authentication manually

docker compose exec api python -c "from api.m365_auth import M365Auth; print(M365Auth().get_access_token())"

```

### Services Can't Connect

```bash

# Check Docker network

docker network inspect hetzner-m365-rag_m365-rag-network

# Restart all services

docker compose down
docker compose up -d

```

---

## 📚 Additional Resources

- **Deployment Script**: `scripts/deploy.sh`
- **Docker Compose**: `docker-compose.yml`
- **M365 Configuration**: `docs/M365_ENV_VARIABLES.md`
- **Security Hardening**: `docs/SECURITY_HARDENING_GUIDE.md`
- **Monitoring Setup**: `docs/MONITORING_AND_ALERTING_CONFIGURATION.md`
- **Disaster Recovery**: `docs/DISASTER_RECOVERY_AND_BACKUP_SECURITY_PLAN.md`
- **Backup Configuration**: `docs/BACKUP_CONFIGURATION.md`

---

## 📞 Support

### Documentation

- Implementation Guide: `docs/IMPLEMENTATION_GUIDE.md`
- Architecture: `docs/ARCHITECTURE.md`
- API Documentation: `http://YOUR_SERVER_IP:8000/docs` (Swagger UI)

### Common Issues

See `docs/BUG_FIXES.md` and `docs/BUG_FIXES_ROUND2.md` for resolved issues.

---

## ✨ Summary

## Current Status:

- ✅ Hetzner credentials retrieved
- ✅ OpenAI API key configured
- ✅ Deployment files prepared
- ⚠️ Azure AD app registration needed (see Step 1)

## Next Actions:

1. Create Azure AD app registration (Step 1)
2. Update `.env.deployment` with Azure values (Step 2)
3. Log into Hetzner console (Step 3)
4. Upload files to server (Step 4)
5. Run deployment script (Step 5)
6. Verify and test (Step 6)

**Estimated Total Time:** 30-45 minutes (excluding server provisioning)

---

**Last Updated:** 2025-10-19
**Version:** 1.0
**Prepared By:** Kilo Code AI Agent

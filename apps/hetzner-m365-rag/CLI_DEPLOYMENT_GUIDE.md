# 🚀 CLI-Based Deployment Guide - 100% Automated

**Last Updated:** 2025-10-19
**Status:** ✅ **100% CLI AUTOMATION READY**

---

## 🎯 COMPLETE CLI AUTOMATION

No browser automation needed! Everything is done via command-line tools.

---

## 📋 PREREQUISITES

### Install Required CLI Tools

#### 1. Azure CLI (for Azure AD app creation)

```powershell

winget install Microsoft.AzureCLI

# Or download: https://aka.ms/installazurecliwindows

```

#### 2. Hetzner Cloud CLI (for server creation)

Download from: https://github.com/hetznercloud/cli/releases/latest

- Download `hcloud-windows-amd64.zip`
- Extract `hcloud.exe`
- Move to: `$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps\`

#### 3. 1Password CLI (optional, for credential management)

```powershell

winget install 1Password.1Password-CLI

```

### Configure API Access

#### Azure CLI Login

```powershell

az login --use-device-code

```

#### Hetzner Cloud API Token

1. Go to: https://console.hetzner.cloud/
2. Select/create project
3. Go to: Security > API Tokens
4. Click "Generate API Token"
5. Name: "M365-RAG-Deployment"
6. Permissions: Read & Write
7. Copy token and set:

```powershell

$env:HCLOUD_TOKEN = "your_token_here"

```

---

## 🚀 DEPLOYMENT OPTIONS

### Option 1: 100% Automated (Recommended)

## Create Hetzner Cloud server AND deploy:

```powershell

cd C:\Dev\ZepCloud\apps\hetzner-m365-rag
.\DEPLOY_COMPLETE_CLI.ps1 -CreateServer

```

This will:

1. ✅ Generate all passwords
2. ✅ Create Azure AD app via CLI
3. ✅ Create deployment archive
4. ✅ Create Hetzner Cloud server (cx51)
5. ✅ Upload deployment package
6. ✅ Deploy all services

**Time:** ~30 minutes

### Option 2: Use Existing Server

```powershell

cd C:\Dev\ZepCloud\apps\hetzner-m365-rag
.\DEPLOY_COMPLETE_CLI.ps1 -ServerIP YOUR_SERVER_IP

```

### Option 3: Order Dedicated Server First

```powershell

# 1. Prepare deployment package

cd C:\Dev\ZepCloud\apps\hetzner-m365-rag
.\DEPLOY_COMPLETE_CLI.ps1

# 2. Order AX52 at: https://www.hetzner.com/dedicated-rootserver/matrix-ax

# Wait 2-4 hours for provisioning email

# 3. Deploy to dedicated server

.\scripts\deploy-to-server.ps1 -ServerIP YOUR_SERVER_IP

```

---

## 📊 SERVER OPTIONS

### Hetzner Cloud (cx51) - Instant Provisioning

## Specs:

- 8 vCPUs (AMD EPYC)
- 32GB RAM
- 360GB NVMe SSD
- 20TB traffic
- **€26.40/month ($29)**

## Best For:

- Testing and development
- MVP deployment
- Small teams
- Quick setup

## Created via:

```powershell

.\scripts\setup-hetzner-server.ps1

```

### Hetzner Dedicated (AX52) - Production

## Specs: (2)

- 16 cores (AMD Ryzen 9 5950X)
- 128GB DDR4 ECC RAM
- 2x 3.84TB NVMe SSD
- Unlimited traffic @ 1 Gbit/s
- **€108/month ($117)**

## Best For: (2)

- Production deployment
- Large teams
- Heavy workloads
- Maximum performance

## Order at:

https://www.hetzner.com/dedicated-rootserver/matrix-ax

---

## 🔧 INDIVIDUAL SCRIPT USAGE

### 1. Environment Setup

```powershell

.\scripts\prepare-env.ps1

```

- Generates secure passwords
- Retrieves OpenAI key from 1Password
- Creates .env file

### 2. Azure AD App Creation

```powershell

# Automated via Azure CLI

.\scripts\create-azure-ad-app.ps1

# Or manual input

.\scripts\azure-ad-setup-helper.ps1

```

### 3. Hetzner Cloud Server

```powershell

.\scripts\setup-hetzner-server.ps1

```

Creates Hetzner Cloud server instantly via CLI

### 4. Deployment Archive

```powershell

.\scripts\create-deployment-archive.ps1

```

Creates tar.gz package for server deployment

### 5. Server Deployment

```powershell

.\scripts\deploy-to-server.ps1 -ServerIP YOUR_IP

```

Uploads and deploys everything to server

---

## ✅ VERIFICATION

### Check Service Status

```bash

ssh root@YOUR_SERVER_IP
cd /opt/m365-rag
docker compose ps

```

All services should show "healthy"

### Test API

```bash

curl http://localhost:8000/health

```

Expected: `{"status":"healthy"}`

### Test Elasticsearch

```bash

curl -k https://localhost:9200/_cluster/health

```

Expected: `{"status":"green"}`

---

## 🌐 ACCESS YOUR SYSTEM

| Service | URL | Purpose |
|---------|-----|---------|
| **RAGFlow UI** | http://SERVER_IP:9380 | Main interface |
| **FastAPI** | http://SERVER_IP:8000 | API endpoint |
| **API Docs** | http://SERVER_IP:8000/docs | Interactive docs |
| **Grafana** | http://SERVER_IP:3000 | Monitoring |
| **Prometheus** | http://SERVER_IP:9090 | Metrics |
| **MinIO** | http://SERVER_IP:9001 | Object storage |

**Passwords:** Check `PASSWORDS_GENERATED.txt`

---

## 💰 COST COMPARISON

### Hetzner Cloud (cx51)

- **Monthly:** €26.40 ($29)
- **Annual:** €316.80 ($348)
- **vs Azure:** Save $771-1,471/month
- **Annual Savings:** $9,252-17,652

### Hetzner Dedicated (AX52)

- **Monthly:** €108 ($117)
- **Annual:** €1,296 ($1,404)
- **vs Azure:** Save $683-1,383/month
- **Annual Savings:** $8,196-16,596

### Azure Alternative

- **Monthly:** $800-1,500
- **Annual:** $9,600-18,000

**ROI:** 1-2 months on either Hetzner option!

---

## 🆘 TROUBLESHOOTING

### hcloud not found

```powershell

# Download from GitHub

https://github.com/hetznercloud/cli/releases/latest

# Extract and move hcloud.exe to WindowsApps folder

# Restart PowerShell

```

### Azure CLI login fails

```powershell

az login --use-device-code

# Follow browser instructions

```

### SSH connection timeout

```bash

# Wait 2-3 minutes after server creation

hcloud server list

# Check server status should be "running"

```

### Deployment fails

```bash

ssh root@SERVER_IP
cd /opt/m365-rag
docker compose logs

# Check for specific service errors

```

---

## 📖 ADDITIONAL DOCUMENTATION

## Quick Start:

- `START_HERE.md` - Quick 3-step guide
- `README_DEPLOYMENT_READY.md` - Quick overview

## Detailed Guides:

- `DEPLOYMENT_READY_GUIDE.md` - Complete step-by-step
- `HETZNER_SERVER_SETUP.md` - Server management
- `FINAL_DEPLOYMENT_SUMMARY.md` - Complete summary

## Scripts:

- `DEPLOY_COMPLETE_CLI.ps1` - 100% CLI automation ⭐
- `DEPLOY_ONE_CLICK.ps1` - Original (browser fallback)

---

## 🎯 RECOMMENDED WORKFLOW

### For Testing/MVP

1. Install Azure CLI and hcloud
2. Configure API tokens
3. Run: `.\DEPLOY_COMPLETE_CLI.ps1 -CreateServer`
4. Access system in 30 minutes

### For Production

1. Install Azure CLI
2. Run: `.\DEPLOY_COMPLETE_CLI.ps1` (prepare only)
3. Order Hetzner AX52 dedicated server
4. Wait 2-4 hours for provisioning
5. Run: `.\scripts\deploy-to-server.ps1 -ServerIP YOUR_IP`
6. Access production system in 45 minutes active time

---

**Status:** ✅ **100% CLI AUTOMATION READY**
**No Browser Required:** Everything via command-line tools
**Time to Production:** 30-45 minutes (+ server wait for dedicated)

🚀 **Let's deploy!**

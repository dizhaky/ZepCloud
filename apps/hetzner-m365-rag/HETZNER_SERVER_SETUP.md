# 🖥️ Hetzner Server Setup Guide

**Date:** 2025-10-19  
**Status:** ✅ Account Verified - Ready to Order Server  
**Account:** dizhaky@gmail.com

---

## ✅ Account Status

**Login Successful:** https://robot.hetzner.com  
**Client Number:** K1057581625  
**Current Servers:** 0 (No active servers)

**Action Required:** Order AX52 Dedicated Server

---

## 🛒 Order Hetzner AX52 Server

### Step 1: Navigate to Server Order Page

1. Go to: https://www.hetzner.com/dedicated-rootserver/matrix-ax
2. Or from Robot dashboard: https://robot.hetzner.com/order/index

### Step 2: Select AX52 Configuration

**Recommended Specifications:**
- **Model:** AX52
- **CPU:** AMD Ryzen 9 5950X (16 cores / 32 threads)
- **RAM:** 128GB DDR4 ECC
- **Storage:** 2x 3.84TB NVMe SSD (software RAID)
- **Network:** 1 Gbit/s
- **Price:** ~€108/month

### Step 3: Configuration Options

**Operating System:**
- Select: **Ubuntu 24.04 LTS** (64-bit)
- Reason: Best compatibility with deployment scripts

**Datacenter Location:**
- Recommended: **Falkenstein (FSN)** or **Helsinki (HEL)**
- Reason: Best connectivity for Europe/US

**Additional Options:**
- ✅ Add SSH key (highly recommended)
- ✅ Enable rescue system
- ❌ Skip additional IPs (not needed initially)
- ❌ Skip vSwitch (not needed for single server)

### Step 4: SSH Key Setup (Recommended)

**Generate SSH Key on Windows:**
```powershell
# Open PowerShell
ssh-keygen -t ed25519 -C "hetzner-m365-rag"

# Default location: C:\Users\YourName\.ssh\id_ed25519
# Press Enter for default location
# Set a passphrase (optional but recommended)

# Display public key
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub
```

**Add to Hetzner:**
1. In server order form, find "SSH Keys" section
2. Click "Add SSH key"
3. Paste the public key content
4. Name it: "M365-RAG-Deployment"

### Step 5: Complete Order

1. Review configuration
2. Accept terms and conditions
3. Click "Order now"
4. Confirm order
5. Wait for provisioning email (typically 2-4 hours)

---

## 📧 Post-Order: Server Details

After provisioning, you'll receive an email with:

**Server Details:**
- Server IP address
- Root password (if no SSH key)
- Server name
- Datacenter location

**Save These Details:**
- IP Address: `___________________`
- Root Password: `___________________`
- Server Name: `___________________`

---

## 🔐 Initial Server Access

### Option A: SSH with Key (Recommended)

```powershell
# From Windows PowerShell
ssh root@SERVER_IP
```

### Option B: SSH with Password

```powershell
# From Windows PowerShell
ssh root@SERVER_IP
# Enter root password when prompted
```

### Verify Access

```bash
# Once connected, verify system
uname -a
# Expected: Linux ... x86_64 GNU/Linux

# Check resources
free -h
# Expected: ~128GB total memory

df -h
# Expected: ~7TB total storage

lscpu | grep "Model name"
# Expected: AMD Ryzen 9 5950X
```

---

## 📤 Deploy M365 RAG System

Once you have server access, follow these steps:

### 1. Prepare Deployment Package

**On Windows:**
```powershell
cd C:\Dev\ZepCloud\apps\hetzner-m365-rag

# Ensure .env is updated with Azure AD credentials
notepad .env

# Create deployment archive
wsl tar -czf ../hetzner-deploy.tar.gz .
```

### 2. Upload to Server

```powershell
# Upload deployment package
scp C:\Dev\ZepCloud\apps\hetzner-deploy.tar.gz root@SERVER_IP:/tmp/

# Verify upload
ssh root@SERVER_IP "ls -lh /tmp/hetzner-deploy.tar.gz"
```

### 3. Deploy on Server

```bash
# SSH into server
ssh root@SERVER_IP

# Extract deployment files
cd /tmp
tar -xzf hetzner-deploy.tar.gz -C /opt/
mv /opt/hetzner-m365-rag /opt/m365-rag

# Verify files
ls -la /opt/m365-rag/

# Make scripts executable
cd /opt/m365-rag
chmod +x scripts/*.sh

# Run deployment script
./scripts/deploy.sh
```

**Deployment Script Will:**
1. Update system packages
2. Install Docker & Docker Compose
3. Configure firewall (UFW)
4. Install fail2ban
5. Generate Elasticsearch SSL certificates
6. Start all 11 services
7. Run health checks

**Expected Duration:** 10-15 minutes

### 4. Verify Deployment

```bash
# Check all services are running
docker compose ps

# Test API health
curl http://localhost:8000/health

# Test Elasticsearch
curl -k -u elastic:$(grep ELASTIC_PASSWORD /opt/m365-rag/.env | cut -d= -f2) https://localhost:9200/_cluster/health

# View logs
docker compose logs -f
```

---

## 🌐 Access Deployed Services

After successful deployment:

| Service | URL | Credentials |
|---------|-----|-------------|
| RAGFlow UI | http://SERVER_IP:9380 | Setup on first access |
| FastAPI | http://SERVER_IP:8000 | - |
| API Docs | http://SERVER_IP:8000/docs | Interactive Swagger UI |
| Grafana | http://SERVER_IP:3000 | admin / [from .env] |
| Prometheus | http://SERVER_IP:9090 | - |
| MinIO Console | http://SERVER_IP:9001 | minioadmin / [from .env] |

**Find Grafana Password:**
```bash
grep GRAFANA_PASSWORD /opt/m365-rag/.env
```

---

## 🧪 Test M365 Integration

### 1. Authenticate with M365

```bash
curl -X POST http://SERVER_IP:8000/m365/auth \
  -H "Content-Type: application/json" \
  -d '{"auth_type":"interactive"}'
```

Follow the URL in the response to complete authentication.

### 2. Sync SharePoint Content

```bash
curl -X POST http://SERVER_IP:8000/m365/sync/sharepoint \
  -H "Content-Type: application/json" \
  -d '{
    "site_url": "https://yourtenant.sharepoint.com/sites/yoursite"
  }'
```

### 3. Test Search

```bash
curl -X POST http://SERVER_IP:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "project report",
    "filters": {"source": "sharepoint"},
    "limit": 5
  }'
```

---

## 🔒 Post-Deployment Security

### 1. Change Root Password

```bash
passwd root
# Enter new strong password twice
```

### 2. Create Deploy User

```bash
# Already created by deployment script
# User: deploy
# Groups: sudo, docker
```

### 3. Disable Root SSH (Optional)

```bash
# Edit SSH config
nano /etc/ssh/sshd_config

# Change: PermitRootLogin yes
# To: PermitRootLogin no

# Restart SSH
systemctl restart sshd
```

### 4. Enable HTTPS

```bash
# Install Certbot
apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate (requires domain)
certbot --nginx -d rag.yourdomain.com
```

### 5. Configure Backups

```bash
# Add to crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /opt/m365-rag/scripts/backup.sh >> /var/log/m365-rag-backup.log 2>&1
```

---

## 📊 Monitoring

### Grafana Dashboards

Access: http://SERVER_IP:3000

**Default Dashboards:**
- Elasticsearch cluster health
- API performance metrics
- System resource usage
- Query performance

### Prometheus Metrics

Access: http://SERVER_IP:9090

**Key Metrics:**
- Query latency (p50, p95, p99)
- Document indexing rate
- Cache hit/miss ratio
- Error rates

### System Monitoring

```bash
# Check service status
docker compose ps

# View logs
docker compose logs -f api

# System resources
htop

# Disk usage
df -h

# Docker stats
docker stats
```

---

## 🐛 Troubleshooting

### Deployment Script Fails

```bash
# View full logs
./scripts/deploy.sh 2>&1 | tee deploy.log

# Check specific service
docker compose logs elasticsearch
docker compose logs api
```

### Out of Memory

```bash
# Check memory usage
free -h
docker stats

# Adjust limits in docker-compose.yml
nano docker-compose.yml
# Reduce: ES_JAVA_OPTS from -Xmx16g to -Xmx8g
docker compose restart
```

### Services Won't Start

```bash
# Restart all services
cd /opt/m365-rag
docker compose down
docker compose up -d

# Check Docker network
docker network ls
docker network inspect hetzner-m365-rag_m365-rag-network
```

### Firewall Blocking Access

```bash
# Check UFW status
ufw status

# Allow specific port
ufw allow 8000/tcp
ufw reload
```

---

## 💰 Cost Summary

**Monthly Costs:**
- Hetzner AX52: €108 (~$117 USD)
- Bandwidth: Included (unlimited @ 1 Gbit/s)
- Support: Free community support

**Annual Cost:** €1,296 (~$1,404 USD)

**Savings vs Azure:** $8,000-14,000/year

**Break-Even:** ~2 months

---

## 📞 Support Resources

### Hetzner Support

- **Status Page:** https://status.hetzner.com/
- **Docs:** https://docs.hetzner.com/
- **Community:** https://community.hetzner.com/
- **Support Ticket:** https://robot.hetzner.com/support/index

### Project Documentation

- **Deployment Guide:** `DEPLOYMENT_READY_GUIDE.md`
- **Status:** `DEPLOYMENT_STATUS.md`
- **M365 Config:** `docs/M365_ENV_VARIABLES.md`
- **Security:** `docs/SECURITY_HARDENING_GUIDE.md`

---

## ✅ Quick Start Checklist

- [ ] Order Hetzner AX52 server
- [ ] Receive provisioning email (2-4 hours)
- [ ] Save server IP and credentials
- [ ] Test SSH access
- [ ] Ensure .env has Azure AD credentials
- [ ] Create deployment archive
- [ ] Upload to server
- [ ] Run deployment script
- [ ] Verify all services
- [ ] Access Grafana and configure
- [ ] Test M365 authentication
- [ ] Sync initial content
- [ ] Configure backups
- [ ] Enable HTTPS (optional)

---

**Status:** Ready to order server  
**Next Action:** Order AX52 server at https://www.hetzner.com/dedicated-rootserver/matrix-ax  
**Estimated Total Time:** 3-4 hours (including provisioning wait)


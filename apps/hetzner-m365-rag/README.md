# 🚀 Hetzner M365 RAG System

## Production-ready RAG system for Microsoft 365 content with enterprise search capabilities

[![Status](https://img.shields.io/badge/Status-Production%20Ready-green)](https://github.com)
[![Automation](https://img.shields.io/badge/Automation-100%25%20CLI-blue)](https://github.com)
[![Cost](https://img.shields.io/badge/Cost-€26-€108%2Fmonth-orange)](https://github.com)

---

## ⚡ QUICK START

### One Command Deployment

```powershell

cd C:\Dev\ZepCloud\apps\hetzner-m365-rag
.\DEPLOY_COMPLETE_CLI.ps1 -CreateServer

```

**That's it!** Your system will be running in 30 minutes.

---

## 📖 WHAT YOU GET

### Complete RAG System

- **Vector Search** - Semantic search across all M365 content

- **Full-Text Search** - Traditional keyword search

- **M365 Integration** - SharePoint, OneDrive, Teams, Email

- **Production UI** - RAGFlow interface

- **REST API** - FastAPI with interactive docs

- **Monitoring** - Grafana dashboards + Prometheus

- **Object Storage** - MinIO S3-compatible storage

### 11 Services Included

1. Elasticsearch 8.15 - Vector + full-text search

2. PostgreSQL 16 - Metadata database

3. Redis 7 - Query caching

4. MinIO - Object storage

5. RAGFlow - Production UI

6. FastAPI - Integration API

7. Nginx - Reverse proxy

8. Prometheus - Metrics collection

9. Grafana - Visualization

10. Elasticsearch Exporter - Metrics

11. PostgreSQL Exporter - Metrics

---

## 💰 COST OPTIONS

### Hetzner Cloud (cx51) - Testing/MVP

- **8 vCPUs, 32GB RAM**

- **€26.40/month** ($29)

- Instant provisioning (5 min)

- Perfect for testing and small teams

- **Save $771-1,471/month vs Azure**

### Hetzner Dedicated (AX52) - Production

- **16 cores, 128GB RAM**

- **€108/month** ($117)

- 2-4 hour provisioning

- Perfect for production workloads

- **Save $683-1,383/month vs Azure**

### Azure Alternative

- **$800-1,500/month**

- **ROI: 1-2 months** on either Hetzner option!

---

## 🎯 DEPLOYMENT GUIDES

Choose your path:

### ⭐ CLI-Based (Recommended)

## 100% Command-line automation - No browser needed

📄 **See:** [CLI_DEPLOYMENT_GUIDE.md](CLI_DEPLOYMENT_GUIDE.md)

```powershell

# Install tools

winget install Microsoft.AzureCLI

# Download hcloud from GitHub

# Deploy

.\DEPLOY_COMPLETE_CLI.ps1 -CreateServer

```

### 📝 Step-by-Step

## Detailed instructions for each step

📄 **See:** [DEPLOYMENT_READY_GUIDE.md](DEPLOYMENT_READY_GUIDE.md)

### 🚀 Quick Start

## Get up and running fast

📄 **See:** [START_HERE.md](START_HERE.md)

---

## 📦 WHAT'S INCLUDED

### Automation Scripts

- ✅ `DEPLOY_COMPLETE_CLI.ps1` - 100% CLI automation ⭐

- ✅ `DEPLOY_ONE_CLICK.ps1` - One-click deployment

- ✅ `prepare-env.ps1` - Environment setup

- ✅ `create-azure-ad-app.ps1` - Azure AD via CLI

- ✅ `setup-hetzner-server.ps1` - Server creation via CLI

- ✅ `deploy-to-server.ps1` - Automated deployment

- ✅ `deploy.sh` - Server-side deployment (Bash)

### Documentation

- 📖 CLI_DEPLOYMENT_GUIDE.md - CLI automation guide

- 📖 START_HERE.md - Quick 3-step guide

- 📖 DEPLOYMENT_READY_GUIDE.md - Complete guide

- 📖 HETZNER_SERVER_SETUP.md - Server management

- 📖 FINAL_DEPLOYMENT_SUMMARY.md - Complete summary

- 📄 PASSWORDS_GENERATED.txt - Password reference

- 📄 SERVER_INFO.txt - Server details (after creation)

### Configuration

- ✅ Complete `.env` file with secure passwords

- ✅ Docker Compose for 11 services

- ✅ Nginx reverse proxy config

- ✅ Prometheus monitoring config

- ✅ Grafana dashboards

- ✅ SSL certificate generation

- ✅ UFW firewall rules

- ✅ Fail2ban security

- ✅ Daily automated backups

---

## 🔒 SECURITY

- **Secure Passwords** - 32-64 character cryptographic passwords

- **SSL/TLS** - Automatic certificate generation

- **Firewall** - UFW configured automatically

- **Brute Force Protection** - Fail2ban configured

- **JWT Authentication** - API security

- **Automated Backups** - Daily at 2 AM

- **1Password Integration** - Credential management

---

## 🌐 ACCESS URLS

After deployment:

| Service | URL | Purpose |
|---------|-----|---------|
| RAGFlow UI | http://SERVER_IP:9380 | Main interface |
| FastAPI | http://SERVER_IP:8000 | API endpoint |
| API Docs | http://SERVER_IP:8000/docs | Interactive docs |
| Grafana | http://SERVER_IP:3000 | Monitoring |
| Prometheus | http://SERVER_IP:9090 | Metrics |
| MinIO | http://SERVER_IP:9001 | Object storage |

---

## 📊 SYSTEM REQUIREMENTS

### Minimum (Cloud cx51)

- 8 vCPUs

- 32GB RAM

- 360GB SSD

- Ubuntu 24.04 LTS

### Recommended (Dedicated AX52)

- 16 cores

- 128GB RAM

- 2x 3.84TB NVMe SSD

- Ubuntu 24.04 LTS

---

## 🚀 FEATURES

### M365 Integration

- ✅ SharePoint document indexing

- ✅ OneDrive file search

- ✅ Teams message search

- ✅ Email content search

- ✅ Delegated authentication

- ✅ Incremental sync

### Search Capabilities

- ✅ Vector/semantic search

- ✅ Full-text keyword search

- ✅ Hybrid search (combines both)

- ✅ Metadata filtering

- ✅ Multi-language support

- ✅ Document ranking

### API Features

- ✅ RESTful API

- ✅ Interactive docs (Swagger)

- ✅ JWT authentication

- ✅ Rate limiting

- ✅ Query caching

- ✅ Batch operations

### Monitoring

- ✅ Service health dashboards

- ✅ Query performance metrics

- ✅ Resource utilization

- ✅ Error tracking

- ✅ Alert configuration

- ✅ Log aggregation

---

## ⏱️ DEPLOYMENT TIME

### Cloud Server (cx51)

- **Preparation:** 5 minutes

- **Server Creation:** 5 minutes (automated)

- **Deployment:** 15 minutes

- **Total:** ~25-30 minutes

### Dedicated Server (AX52)

- **Preparation:** 5 minutes

- **Server Ordering:** 10 minutes

- **Wait for Provisioning:** 2-4 hours

- **Deployment:** 15 minutes

- **Total Active Time:** ~30 minutes

---

## 🆘 SUPPORT

### Documentation (2)

- [CLI Deployment Guide](CLI_DEPLOYMENT_GUIDE.md)

- [Complete Deployment Guide](DEPLOYMENT_READY_GUIDE.md)

- [Server Setup Guide](HETZNER_SERVER_SETUP.md)

- [Quick Start](START_HERE.md)

### Troubleshooting

See the troubleshooting sections in:

- [CLI_DEPLOYMENT_GUIDE.md](CLI_DEPLOYMENT_GUIDE.md#troubleshooting)

- [DEPLOYMENT_READY_GUIDE.md](DEPLOYMENT_READY_GUIDE.md)

### Hetzner Support

- Status: https://status.hetzner.com/

- Community: https://community.hetzner.com/

- Docs: https://docs.hetzner.com/

---

## 📄 LICENSE

This project includes:

- Elasticsearch (Elastic License 2.0)

- PostgreSQL (PostgreSQL License)

- Redis (BSD 3-Clause)

- MinIO (AGPL v3)

- RAGFlow (Apache 2.0)

- Custom integration code (MIT)

See individual component licenses for details.

---

## 🎯 NEXT STEPS

1. **Read:** [START_HERE.md](START_HERE.md)

2. **Deploy:** Run `.\DEPLOY_COMPLETE_CLI.ps1 -CreateServer`

3. **Access:** http://YOUR_SERVER_IP:9380

4. **Enjoy:** Your production RAG system!

---

**Status:** ✅ **Production Ready**
**Automation:** 100% CLI-based
**Time to Deploy:** 25-30 minutes
**Cost:** Starting at €26.40/month

🚀 **Let's build something amazing!**

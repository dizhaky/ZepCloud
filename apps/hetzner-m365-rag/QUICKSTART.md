# Quick Start Guide

## Get Your M365 RAG System Running in 30 Minutes

---

## Prerequisites

✅ Hetzner AX52 server with Ubuntu 24.04
✅ OpenAI API key
✅ M365 tenant with admin access
✅ Domain name (optional)

---

## Step 1: Upload Files (5 minutes)

```bash

# From your local machine

cd path/to/hetzner-m365-rag
tar -czf deploy.tar.gz .
scp deploy.tar.gz root@YOUR_SERVER_IP:/tmp/

```

---

## Step 2: Run Deployment (10 minutes)

```bash

# SSH into server

ssh root@YOUR_SERVER_IP

# Extract and deploy

cd /tmp
tar -xzf deploy.tar.gz -C /tmp/m365-rag-deploy
cd /tmp/m365-rag-deploy
chmod +x scripts/deploy.sh
./scripts/deploy.sh

```

## Answer "yes" when prompted.

The script will:

- ✅ Update system packages
- ✅ Configure firewall
- ✅ Install Docker
- ✅ Set up project structure
- ✅ Generate secure passwords
- ✅ Start all services
- ✅ Configure automated backups

---

## Step 3: Configure API Keys (5 minutes)

```bash

# Edit environment file

vi /data/m365-rag/.env

# Add your keys

OPENAI_API_KEY=sk-your-key-here
AZURE_CLIENT_ID=your-client-id
AZURE_TENANT_ID=your-tenant-id

# Save and exit (:wq)

# Restart services

cd /data/m365-rag
docker compose restart

```

---

## Step 4: Verify Deployment (5 minutes)

```bash

# Check all services are running

docker compose ps

# Test API health

curl http://localhost:8000/health

# Test Elasticsearch

curl -u elastic:$(grep ELASTIC_PASSWORD .env | cut -d'=' -f2) \
  http://localhost:9200/_cluster/health

```

**Expected:** All services should show "healthy" or "running"

---

## Step 5: Access UIs (5 minutes)

Open in your browser:

**RAGFlow UI** (Main Interface)

```

http://YOUR_SERVER_IP:9380

```

**Grafana** (Monitoring)

```

http://YOUR_SERVER_IP:3000
Username: admin
Password: (check .env for GRAFANA_PASSWORD)

```

**MinIO Console** (Storage)

```

http://YOUR_SERVER_IP:9001
Username: minioadmin
Password: (check .env for MINIO_ROOT_PASSWORD)

```

---

## Step 6: Configure M365 Sync (Optional, 10 minutes)

### A. Register Azure AD App

1. Go to https://portal.azure.com
2. Navigate to: Azure AD → App registrations
3. Click "New registration"
4. Name: "M365 RAG Connector"
5. Click "Register"
6. Note the **Application (client) ID**
7. Note the **Directory (tenant) ID**

### B. Add API Permissions

1. Go to: API permissions → Add a permission
2. Select: Microsoft Graph → Application permissions
3. Add these permissions:
   - Files.Read.All
   - Sites.Read.All
   - Mail.Read
   - User.Read.All
   - Team.ReadBasic.All
4. Click "Grant admin consent"

### C. Test Authentication

```bash

cd /data/m365-rag
python3 api/m365_auth.py

```

Follow the browser authentication prompt.

### D. Start Initial Sync

```bash

curl -X POST http://localhost:8000/ingest/m365/sync \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "sharepoint",
    "delta_sync": false
  }'

```

Monitor progress in RAGFlow UI.

---

## What's Next

### Test the System

1. **Upload a test document:**
   - Go to RAGFlow UI
   - Click "Datasets" → "M365 Documents"
   - Upload a PDF with images/tables

2. **Search for content:**
   - Enter a natural language query
   - Verify results appear
   - Check citations

3. **Monitor performance:**
   - Open Grafana
   - View Elasticsearch dashboard
   - Check query latency

### Production Configuration

1. **Set up SSL:**

   ```bash
   certbot certonly --standalone -d your-domain.com
   ```

2. **Enable HTTPS in nginx:**
   - Edit `/data/m365-rag/config/nginx/nginx.conf`
   - Uncomment HTTPS server block
   - Restart: `docker compose restart nginx`

3. **Configure alerts:**
   - Open Grafana → Alerting
   - Set up email notifications
   - Configure alert rules

### Ongoing Maintenance

- **Daily:** Check Grafana dashboards
- **Weekly:** Review backup logs
- **Monthly:** Update Docker images

---

## Troubleshooting

### Services Won't Start

```bash

# Check Docker daemon

systemctl status docker

# View logs

docker compose logs --tail=100

# Restart all services

docker compose down && docker compose up -d

```

### Elasticsearch Issues

```bash

# Check cluster health

curl -u elastic:PASSWORD http://localhost:9200/_cluster/health

# View logs (2)

docker compose logs elasticsearch --tail=100

# Restart Elasticsearch

docker compose restart elasticsearch

```

### Can't Access UIs

```bash

# Check firewall

ufw status

# Check nginx

docker compose logs nginx

# Verify ports are open

netstat -tuln | grep -E '8000|9380|3000'

```

---

## Getting Help

- 📖 **Full documentation:** `/data/m365-rag/README.md`
- 📋 **Deployment checklist:** `/data/m365-rag/docs/DEPLOYMENT_CHECKLIST.md`
- 🔧 **Troubleshooting:** `/data/m365-rag/README.md#troubleshooting`
- 💬 **Support:** Open a GitHub issue

---

## Success Checklist

- [x] All services running and healthy
- [x] API responding to health checks
- [x] RAGFlow UI accessible
- [x] Grafana dashboards working
- [x] M365 authentication configured
- [x] Test document uploaded successfully
- [x] Search functionality working
- [x] Backups scheduled
- [x] Monitoring active

## 🎉 Congratulations! Your M365 RAG System is live!

---

**Pro Tip:** Bookmark the RAGFlow UI and Grafana dashboards for quick access.

**Need more features?** Check the [full documentation](README.md) for advanced configuration options.

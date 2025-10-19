# M365 RAG System - Hetzner Deployment

**Version:** 1.0.0  
**Last Updated:** October 18, 2025  
**Status:** Production Ready

---

## 🎯 Overview

This is a complete self-hosted M365 RAG (Retrieval-Augmented Generation) system deployed on Hetzner AX52 infrastructure, featuring:

- **Elasticsearch 8.15** - Vector search engine with kNN support
- **RAG-Anything** - Multimodal document processing (images, tables, equations)
- **RAGFlow** - Production UI with citations and agent workflows
- **PostgreSQL 16** - Metadata and user database with pgvector
- **Redis 7** - Caching layer for query optimization
- **MinIO** - S3-compatible object storage
- **Prometheus + Grafana** - Comprehensive monitoring
- **FastAPI** - Custom integration layer
- **M365 Connectors** - SharePoint, OneDrive, Teams, Outlook, Calendar, Contacts

**Annual Cost Savings:** $8,000-14,000 vs Azure  
**Hardware:** Hetzner AX52 (128GB RAM, 2x3.84TB NVMe) - $108/month

---

## 🚀 Quick Start

### Prerequisites

- Hetzner AX52 server with Ubuntu 24.04 LTS
- Domain name (optional but recommended)
- OpenAI API key
- Microsoft 365 tenant with admin access

### Installation

1. **Upload project files to server:**
   ```bash
   scp -r . root@YOUR_SERVER_IP:/tmp/m365-rag-deploy
   ```

2. **Run deployment script:**
   ```bash
   ssh root@YOUR_SERVER_IP
   cd /tmp/m365-rag-deploy
   chmod +x scripts/deploy.sh
   ./scripts/deploy.sh
   ```

3. **Configure environment:**
   ```bash
   vi /data/m365-rag/.env
   # Add your OpenAI API key and Azure AD credentials
   ```

4. **Restart services:**
   ```bash
   cd /data/m365-rag
   docker compose restart
   ```

5. **Verify deployment:**
   ```bash
   docker compose ps
   curl http://localhost:8000/health
   ```

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────┐
│          User Layer (RAGFlow UI)            │
│                Port 80/443                   │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         Application Layer                    │
│  ┌──────────────┐    ┌──────────────┐      │
│  │   RAGFlow    │    │   API Server │      │
│  │   (Port 9380)│    │   (Port 8000)│      │
│  └──────────────┘    └──────────────┘      │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│            Data Layer                        │
│  ┌─────────────────────────────────────┐   │
│  │ Elasticsearch (16GB, Port 9200)     │   │
│  └─────────────────────────────────────┘   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │PostgreSQL│ │  Redis   │ │  MinIO   │   │
│  │ (4GB)    │ │  (2GB)   │ │  (2GB)   │   │
│  └──────────┘ └──────────┘ └──────────┘   │
└─────────────────────────────────────────────┘
```

---

## 🔧 Configuration Files

### Core Configuration

- `docker-compose.yml` - Service orchestration
- `.env` - Environment variables and secrets
- `config/nginx/nginx.conf` - Reverse proxy configuration
- `config/elasticsearch/elasticsearch.yml` - Search engine config
- `config/prometheus/prometheus.yml` - Monitoring config

### Scripts

- `scripts/deploy.sh` - Initial deployment
- `scripts/backup.sh` - Automated backups
- `scripts/restore.sh` - Disaster recovery
- `scripts/init-db.sql` - Database initialization

---

## 🐳 Docker Services

| Service | Port | Memory | Purpose |
|---------|------|--------|---------|
| Elasticsearch | 9200 | 16GB | Vector + full-text search |
| PostgreSQL | 5432 | 4GB | Metadata + user database |
| Redis | 6379 | 2GB | Query caching |
| MinIO | 9000/9001 | 2GB | Object storage |
| RAGFlow | 9380 | 8GB | Production UI |
| API | 8000 | 4GB | Integration layer |
| Nginx | 80/443 | 512MB | Reverse proxy |
| Prometheus | 9090 | 1GB | Metrics collection |
| Grafana | 3000 | 512MB | Visualization |

**Total RAM Usage:** ~38GB (90GB available on AX52)

---

## 📡 API Endpoints

### Health Check
```bash
GET /health
Response: {
  "status": "healthy",
  "services": {
    "elasticsearch": "ok",
    "postgres": "ok",
    "redis": "ok"
  }
}
```

### Search
```bash
POST /search
Body: {
  "query": "quarterly report",
  "top_k": 10,
  "search_mode": "hybrid"
}
```

### Upload Document
```bash
POST /ingest/upload
Form Data:
  file: <file>
  metadata: {"source": "manual", "author": "System"}
```

### M365 Sync
```bash
POST /ingest/m365/sync
Body: {
  "source_type": "sharepoint",
  "site_url": "https://tenant.sharepoint.com/sites/site",
  "delta_sync": true
}
```

---

## 🔐 Security

### Authentication

- **Azure AD OAuth** for M365 integration
- **JWT tokens** for API authentication
- **RBAC** (Role-Based Access Control)

### Data Protection

- **Disk encryption** (LUKS) for sensitive data
- **TLS 1.3** for all connections
- **X-Pack Security** in Elasticsearch
- **Secure password generation** (32-byte random)

### Network Security

- **UFW firewall** (SSH, HTTP, HTTPS only)
- **Fail2ban** for brute-force protection
- **Rate limiting** via Redis

### Enhanced Security Measures

Additional security enhancements have been implemented to further strengthen the system:

- **Security Hardening Guide** - System-level security configurations, container security, network segmentation, and data encryption enhancements ([docs/SECURITY_HARDENING_GUIDE.md](docs/SECURITY_HARDENING_GUIDE.md))
- **Monitoring and Alerting Configuration** - Log aggregation, intrusion detection, security event monitoring, and automated security scanning ([docs/MONITORING_AND_ALERTING_CONFIGURATION.md](docs/MONITORING_AND_ALERTING_CONFIGURATION.md))
- **Disaster Recovery and Backup Security** - Secure backup storage, backup encryption, recovery point objectives, and recovery time objectives ([docs/DISASTER_RECOVERY_AND_BACKUP_SECURITY_PLAN.md](docs/DISASTER_RECOVERY_AND_BACKUP_SECURITY_PLAN.md))

For a comprehensive overview of all security enhancements, see [docs/SECURITY_ENHANCEMENTS_SUMMARY.md](docs/SECURITY_ENHANCEMENTS_SUMMARY.md).

---

## 💾 Backup & Recovery

### Automated Backups

Daily backups at 2:00 AM (configured via cron):

```bash
/data/m365-rag/scripts/backup.sh
```

**Backup includes:**
- Elasticsearch snapshots
- PostgreSQL dumps
- Redis data
- Configuration files
- Scripts

**Retention:** 30 days

### Manual Backup

```bash
cd /data/m365-rag
./scripts/backup.sh
```

### Restore from Backup

```bash
cd /data/m365-rag
./scripts/restore.sh <backup_date>
# Example: ./scripts/restore.sh 20251018_020000
```

**RTO:** 4 hours  
**RPO:** 1 hour

---

## 📊 Monitoring

### Grafana Dashboards

Access: `http://YOUR_SERVER_IP:3000`

**Pre-configured dashboards:**
- Elasticsearch cluster health
- API performance metrics
- System resource usage
- Query performance

### Prometheus Metrics

Access: `http://YOUR_SERVER_IP:9090`

**Key metrics:**
- Query latency (p50, p95, p99)
- Document indexing rate
- Cache hit/miss ratio
- Error rates

### Alerts

Configured alerts for:
- High CPU usage (>80%)
- High memory usage (>85%)
- Low disk space (<20%)
- Elasticsearch cluster red/yellow
- API errors (>5% rate)

---

## 🔄 M365 Integration

### Supported Sources

- ✅ SharePoint (sites, document libraries)
- ✅ OneDrive (personal files, folders)
- ✅ Teams (chats, channels, files)
- ✅ Outlook (email attachments)
- ✅ Calendar (events, meetings)
- ✅ Contacts (people, organizations)

### Authentication Methods

1. **Interactive Browser Auth** (recommended)
2. **Device Code Flow** (fallback)
3. **Application Permissions** (for service accounts)

### Initial Sync

```bash
cd /data/m365-rag
python3 api/m365_sync.py --source sharepoint --full
```

### Incremental Sync

Automated hourly via cron:
```bash
0 * * * * cd /data/m365-rag && python3 api/m365_sync.py --source all --delta
```

---

## 🧪 Testing

### Health Check

```bash
curl http://localhost:8000/health
```

### Search Test

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query":"test","top_k":5}'
```

### Elasticsearch Test

```bash
curl -u elastic:PASSWORD http://localhost:9200/_cluster/health
```

### Load Testing

```bash
cd /data/m365-rag
pip install locust
locust -f tests/locustfile.py --host http://localhost:8000
```

---

## 🛠️ Maintenance

### Daily Tasks

```bash
# Check system health
docker compose ps
curl http://localhost:8000/health

# View logs
docker compose logs -f --tail=100

# Monitor resources
docker stats
```

### Weekly Tasks

```bash
# Update Docker images
docker compose pull
docker compose up -d

# Check backup logs
tail -f /var/log/m365-rag-backup.log

# Review slow queries
docker compose exec elasticsearch cat /_cat/tasks
```

### Monthly Tasks

```bash
# System updates
apt update && apt upgrade -y

# Clean old logs
find /data/m365-rag/logs -name "*.log" -mtime +30 -delete

# Review capacity planning
docker exec elasticsearch curl localhost:9200/_cat/allocation
```

---

## 🚨 Troubleshooting

### Elasticsearch Won't Start

```bash
# Check logs
docker compose logs elasticsearch

# Common fixes:
# 1. Increase memory
docker compose down
# Edit docker-compose.yml: increase ES_JAVA_OPTS
docker compose up -d

# 2. Fix permissions
sudo chown -R 1000:1000 /data/m365-rag/data/elasticsearch
```

### High Memory Usage

```bash
# Check memory usage
docker stats

# Reduce Elasticsearch heap
# Edit docker-compose.yml:
ES_JAVA_OPTS: "-Xms8g -Xmx8g"  # Reduce from 16g
```

### Slow Queries

```bash
# Enable slow query logging
docker exec elasticsearch curl -X PUT "localhost:9200/documents/_settings" \
  -H 'Content-Type: application/json' \
  -u elastic:PASSWORD \
  -d '{"index.search.slowlog.threshold.query.warn": "2s"}'

# Check slow queries
docker compose logs elasticsearch | grep "took_millis"
```

### Services Not Starting

```bash
# Check Docker daemon
systemctl status docker

# Check disk space
df -h

# Check service logs
docker compose logs --tail=100
```

---

## 📈 Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Query Latency (p50) | <500ms | - |
| Query Latency (p95) | <2s | - |
| Document Indexing | 100 docs/min | - |
| Concurrent Users | 50+ | - |
| System Uptime | 99.5% | - |

---

## 📞 Support

### Documentation

- Implementation Guide: `docs/IMPLEMENTATION_GUIDE.md`
- Architecture Specification: `docs/ARCHITECTURE.md`
- API Documentation: `docs/API.md`

### Community

- GitHub Issues
- Discord: (TBD)
- Email: support@example.com

---

## 🎉 What's Next?

After deployment:

1. **Configure M365 sync** - Connect your SharePoint sites
2. **Upload test documents** - Verify multimodal processing
3. **Set up monitoring alerts** - Configure email notifications
4. **Train users** - Provide onboarding for RAGFlow UI
5. **Plan scaling** - Monitor usage and plan capacity

---

## 📝 License

[Add your license here]

---

**Questions?** Check the documentation in `docs/` or open a GitHub issue.

**Ready to deploy?** Run `./scripts/deploy.sh` to get started!


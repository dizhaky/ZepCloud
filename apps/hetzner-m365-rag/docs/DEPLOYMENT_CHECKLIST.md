# M365 RAG System - Deployment Checklist

Use this checklist to ensure a complete and successful deployment.

---

## Pre-Deployment

### Infrastructure

- [ ] Hetzner AX52 server ordered and provisioned
- [ ] Server IP address received
- [ ] SSH access configured with key-based authentication
- [ ] Domain name purchased (optional but recommended)
- [ ] DNS records created pointing to server IP

### Accounts & API Keys

- [ ] OpenAI API account created with billing enabled
- [ ] Azure AD tenant access confirmed
- [ ] M365 admin permissions verified
- [ ] Azure AD app registered for M365 integration
- [ ] API permissions configured and admin consent granted

### Local Preparation

- [ ] Project files downloaded/cloned
- [ ] `.env` file prepared with all required values
- [ ] SSL certificates ready (or plan to use Let's Encrypt)

---

## Phase 1: Server Setup

### System Configuration

- [ ] SSH into server as root
- [ ] System packages updated (`apt update && apt upgrade`)
- [ ] Required packages installed (curl, wget, git, vim, htop, etc.)
- [ ] UFW firewall configured (ports 22, 80, 443)
- [ ] Fail2ban installed and configured
- [ ] Unattended upgrades enabled

### Docker Installation

- [ ] Docker Engine installed
- [ ] Docker Compose v2 installed
- [ ] Docker storage configured (`/data/docker`)
- [ ] Docker daemon running and enabled
- [ ] Deploy user created and added to docker group

### Disk Configuration

- [ ] RAID 1 configured (if not already done by Hetzner)
- [ ] Data partition created (`/data`)
- [ ] Backup partition created (`/backup`)
- [ ] LUKS encryption enabled for `/data` (recommended)
- [ ] Partitions mounted and added to `/etc/fstab`

---

## Phase 2: Application Deployment

### Project Setup

- [ ] Project files uploaded to `/data/m365-rag`
- [ ] Ownership set to deploy user (`chown -R deploy:deploy`)
- [ ] Permissions verified (scripts executable)
- [ ] `.env` file created with all secrets
- [ ] `.env` file permissions set to 600

### Docker Services

- [ ] Docker Compose configuration validated
- [ ] Docker images pulled (`docker compose pull`)
- [ ] Elasticsearch started and healthy
- [ ] PostgreSQL started and healthy
- [ ] Redis started and healthy
- [ ] MinIO started and healthy
- [ ] RAGFlow started and healthy
- [ ] API server started and healthy
- [ ] Nginx started and healthy
- [ ] Prometheus started
- [ ] Grafana started
- [ ] All services showing "healthy" status

### Service Verification

- [ ] Elasticsearch cluster green: `curl -u elastic:PASSWORD http://localhost:9200/_cluster/health`
- [ ] PostgreSQL accessible: `docker compose exec postgres psql -U raguser -d m365_rag -c "SELECT 1"`
- [ ] Redis accessible: `docker compose exec redis redis-cli ping`
- [ ] MinIO console accessible: `http://YOUR_SERVER_IP:9001`
- [ ] API health check passing: `curl http://localhost:8000/health`
- [ ] RAGFlow UI accessible: `http://YOUR_SERVER_IP:9380`
- [ ] Grafana accessible: `http://YOUR_SERVER_IP:3000`

---

## Phase 3: M365 Integration

### Azure AD Configuration

- [ ] App registration created in Azure AD
- [ ] Redirect URIs configured
- [ ] API permissions added (Files.Read.All, Sites.Read.All, etc.)
- [ ] Admin consent granted
- [ ] Client ID and Tenant ID noted
- [ ] Client secret created (if using app permissions)
- [ ] Credentials added to `.env` file

### Authentication Testing

- [ ] M365 auth module tested: `python3 api/m365_auth.py`
- [ ] Token acquisition successful
- [ ] Graph API access verified
- [ ] SharePoint sites accessible
- [ ] OneDrive files accessible

### Initial Sync

- [ ] SharePoint sites configured for sync
- [ ] Test document upload successful
- [ ] Document appears in Elasticsearch
- [ ] Document visible in RAGFlow UI
- [ ] Search functionality working

---

## Phase 4: SSL & Security

### SSL Certificates

- [ ] Certbot installed
- [ ] SSL certificate obtained: `certbot certonly --standalone -d your-domain.com`
- [ ] Certificates copied to nginx config directory
- [ ] Nginx configuration updated for HTTPS
- [ ] HTTP to HTTPS redirect configured
- [ ] HSTS enabled
- [ ] Certificate auto-renewal configured

### Security Hardening

- [ ] Lynis security audit run
- [ ] Security issues addressed
- [ ] AIDE intrusion detection installed
- [ ] SSH key-only authentication enforced
- [ ] Root login disabled
- [ ] Firewall rules verified
- [ ] Fail2ban active and monitoring

---

## Phase 5: Monitoring & Backups

### Monitoring Setup

- [ ] Grafana datasource configured (Prometheus)
- [ ] Elasticsearch dashboard imported (ID: 2322)
- [ ] Custom dashboards created for API metrics
- [ ] Alert rules configured (CPU, memory, disk)
- [ ] Email alerts configured (if desired)
- [ ] Alert testing completed

### Backup Configuration

- [ ] Backup script tested: `./scripts/backup.sh`
- [ ] Backup directory created: `/backup/m365-rag`
- [ ] Cron job configured (daily at 2 AM)
- [ ] Off-site backup configured (Hetzner Storage Box or similar)
- [ ] Backup retention policy set (30 days)
- [ ] Restore procedure tested
- [ ] RTO and RPO documented

---

## Phase 6: Testing & Validation

### Functional Testing

- [ ] Document upload test
- [ ] Search functionality test
- [ ] Multimodal processing test (images/tables)
- [ ] M365 sync test (SharePoint, OneDrive)
- [ ] RAGFlow Q&A test
- [ ] Citation grounding verified
- [ ] Agent workflow test (if using)

### Performance Testing

- [ ] Load test with Locust (10-100 concurrent users)
- [ ] Query latency measured (p50, p95, p99)
- [ ] Indexing throughput measured
- [ ] Resource utilization monitored
- [ ] Bottlenecks identified and addressed
- [ ] Cache hit ratio verified

### User Acceptance Testing

- [ ] Test user accounts created
- [ ] Test scenarios prepared
- [ ] Users trained on RAGFlow UI
- [ ] Feedback collected
- [ ] Issues documented
- [ ] Critical issues resolved

---

## Go-Live

### Final Verification

- [ ] All services healthy and stable
- [ ] No errors in logs
- [ ] Backups running successfully
- [ ] Monitoring active with no alerts
- [ ] SSL certificates valid
- [ ] Domain resolving correctly
- [ ] All API endpoints accessible
- [ ] M365 sync running smoothly

### Documentation

- [ ] User guide created
- [ ] Admin runbook completed
- [ ] API documentation published
- [ ] Troubleshooting guide available
- [ ] Contact information updated

### Communication

- [ ] Stakeholders notified of go-live
- [ ] Users onboarded
- [ ] Support channels established
- [ ] Announcement sent

### Post-Launch

- [ ] Monitor closely for first 48 hours
- [ ] Address any issues immediately
- [ ] Collect user feedback
- [ ] Plan improvements based on usage

---

## Post-Deployment Monitoring

### First Week

- [ ] Daily health checks
- [ ] Daily backup verification
- [ ] User feedback collection
- [ ] Performance metrics review
- [ ] Error rate monitoring

### First Month

- [ ] Weekly capacity planning review
- [ ] Weekly security audit
- [ ] User satisfaction survey
- [ ] Feature request collection
- [ ] System optimization based on usage

---

## Success Criteria

- [ ] All services running with 99%+ uptime
- [ ] Query latency p95 < 2 seconds
- [ ] Zero data loss
- [ ] User satisfaction > 80%
- [ ] M365 sync completing successfully
- [ ] Backups completing without errors
- [ ] No critical security issues

---

## Troubleshooting Resources

If you encounter issues, refer to:

- **README.md** - General documentation
- **ARCHITECTURE.md** - System architecture details
- **API documentation** - API endpoints and usage
- **Docker logs** - `docker compose logs [service]`
- **Support** - GitHub Issues or contact support

---

**Deployment Complete?** 🎉

Once all items are checked, you have a production-ready M365 RAG system!

**Questions?** Refer to the documentation or open a support ticket.


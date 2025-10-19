# Production Verification Guide

This guide explains how to use the comprehensive verification scripts to ensure both applications (Hetzner M365 RAG and
  Azure RAG Setup) are running correctly in production.

## Overview

The verification system consists of three scripts:

1. **`scripts/verify-production.sh`** - Comprehensive verification for both applications
2. **`apps/hetzner-m365-rag/scripts/verify-production.sh`** - Hetzner-specific verification
3. **`apps/azure-rag-setup/verify-production.sh`** - Azure-specific verification

## Quick Start

### Comprehensive Verification (Both Applications)

```bash

# From the project root directory

./scripts/verify-production.sh

```

This script will:

- Verify Hetzner M365 RAG deployment (Docker services, endpoints, resources)
- Verify Azure RAG Setup deployment (Python environment, Azure connectivity, M365 auth)
- Generate comprehensive status report
- Check system resources and security

### Hetzner-Specific Verification

```bash

# On the Hetzner server

cd /data/m365-rag
./scripts/verify-production.sh

```

This script will:

- Check Docker services status
- Verify all endpoints are accessible
- Check system resources (disk, memory, CPU)
- Validate security configurations
- Verify backup systems
- Check monitoring and alerting

### Azure-Specific Verification

```bash

# On the local machine

cd /Users/danizhaky/Dev/ZepCloud/azure-rag-setup
./verify-production.sh

```

This script will:

- Check Python environment and dependencies
- Verify environment variables configuration
- Test Azure services connectivity
- Validate M365 authentication
- Check system resources
- Run health checks

## What Gets Verified

### Hetzner M365 RAG Checks

1. **Docker Services**
   - Docker daemon status
   - Service container status (Elasticsearch, PostgreSQL, Redis, etc.)
   - Service health checks

2. **Service Endpoints**
   - API endpoint (`http://localhost:8000/health`)
   - Elasticsearch (`https://localhost:9200/_cluster/health`)
   - RAGFlow UI (`http://localhost:9380`)
   - Grafana (`http://localhost:3000`)
   - MinIO Console (`http://localhost:9001`)
   - Prometheus (`http://localhost:9090`)

3. **System Resources**
   - Disk space usage
   - Memory utilization
   - CPU load average

4. **Security Configuration**
   - Firewall status
   - Environment file permissions
   - Fail2ban status

5. **Backup Systems**
   - Backup script existence and permissions
   - Backup directory availability
   - Cron job configuration

6. **Monitoring and Alerting**
   - Prometheus accessibility
   - Grafana accessibility
   - Elasticsearch exporter status

7. **M365 Integration**
   - Credential configuration
   - Sync script availability

### Azure RAG Setup Checks

1. **Python Environment**
   - Python 3 installation
   - Virtual environment status
   - Required package availability

2. **Environment Variables**
   - `.env` file existence
   - Required Azure and M365 credentials

3. **Azure Services Connectivity**
   - Azure AI Search accessibility
   - Azure Blob Storage connectivity

4. **M365 Authentication**
   - Authentication test execution
   - Credential validation

5. **Service Status**
   - M365 indexer status
   - Sync progress tracking

6. **System Resources**
   - Local disk space
   - Memory usage

7. **RAG-Anything Integration**
   - Orchestration script availability
   - Enhanced feature status

## Output Format

All scripts provide colored output with clear status indicators:

- ✅ **Success** - Green checkmark for working components
- ⚠️ **Warning** - Yellow warning for issues that don't prevent operation
- ❌ **Error** - Red X for critical issues that need attention

## Sample Output

```

╔══════════════════════════════════════════════════════════════════════════════╗
║              Comprehensive Production Verification                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

ℹ️  Starting comprehensive production verification
ℹ️  Running with root privileges

╔══════════════════════════════════════════════════════════════════════════════╗
║              Hetzner M365 RAG Verification                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

ℹ️  Checking Docker services...
✅ Docker service is running
✅ docker-compose.yml found
ℹ️  Checking service status...
  Service: elasticsearch, Status: running, Health: healthy
  Service: postgres, Status: running, Health: healthy
  Service: redis, Status: running, Health: healthy
ℹ️  Service Summary: 9/9 running, 9/9 healthy
✅ All services are running
✅ All services are healthy

ℹ️  Checking service endpoints...
✅ API endpoint (http://localhost:8000/health) is accessible
✅ Elasticsearch endpoint (https://localhost:9200/_cluster/health) is accessible
✅ RAGFlow UI endpoint (http://localhost:9380) is accessible
ℹ️  Endpoint Summary: 6/6 endpoints accessible

✅ Disk usage is normal: 45%
✅ Memory usage is normal: 62.5%
✅ CPU load is normal: 1.2

╔══════════════════════════════════════════════════════════════════════════════╗
║              Azure RAG Setup Verification                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

ℹ️  Checking Python environment...
✅ Python version: Python 3.14.0
✅ Virtual environment is activated: /Users/danizhaky/Dev/ZepCloud/venv
✅ Package azure-search-documents is installed
✅ Package azure-storage-blob is installed

ℹ️  Checking environment variables...
✅ .env file found
✅ Environment variable AZURE_SEARCH_SERVICE_NAME is set
✅ Environment variable AZURE_SEARCH_ADMIN_KEY is set

ℹ️  Checking Azure services connectivity...
✅ Azure AI Search is accessible

ℹ️  Checking M365 authentication...
✅ M365 authentication test passed

╔══════════════════════════════════════════════════════════════════════════════╗
║                    Verification Completed                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

ℹ️  Verification log available at: /var/log/comprehensive-production-verify.log
ℹ️  For detailed information, check the generated status report

```

## Troubleshooting

### Common Issues and Solutions

#### Docker Services Not Running (Hetzner)

```bash

# Check Docker status

systemctl status docker

# Start Docker service

sudo systemctl start docker

# Check service logs

cd /data/m365-rag
docker compose logs elasticsearch
docker compose logs api

```

#### Azure Connectivity Issues

```bash

# Check environment variables

cd /Users/danizhaky/Dev/ZepCloud/azure-rag-setup
cat .env

# Test Azure Search connectivity manually

curl -H "api-key: $AZURE_SEARCH_ADMIN_KEY" \
  "https://$AZURE_SEARCH_SERVICE_NAME.search.windows.net/indexes?api-version=2023-11-01"

```

#### M365 Authentication Failures

```bash

# Run authentication test

cd /Users/danizhaky/Dev/ZepCloud/azure-rag-setup
python3 m365_indexer.py test-auth

# Check credentials in .env file

# Ensure M365_CLIENT_ID, M365_CLIENT_SECRET, M365_TENANT_ID are correct

```

#### High Resource Usage

```bash

# Check disk usage

df -h

# Check memory usage

free -h

# Check Docker container resource usage

docker stats

```

## Automation

### Cron Job Setup (Hetzner)

Add to crontab for automated daily checks:

```bash

# Edit crontab

sudo crontab -e

# Add daily verification at 6 AM

0 6 * * * /data/m365-rag/scripts/verify-production.sh >> /var/log/m365-rag-daily-verify.log 2>&1

```

### Cron Job Setup (Azure)

Add to crontab for automated daily checks:

```bash

# Edit crontab (2)

crontab -e

# Add daily verification at 6 AM (2)

0 6 * * * cd /Users/danizhaky/Dev/ZepCloud/azure-rag-setup && ./verify-production.sh >> /tmp/azure-rag-daily-verify.log
  2>&1

```

## Log Files

- **Hetzner verification log**: `/var/log/m365-rag-production-verify.log`
- **Azure verification log**: `/tmp/azure-rag-production-verify.log`
- **Comprehensive verification log**: `/var/log/comprehensive-production-verify.log`
- **Daily verification logs**: Check cron job output files

## Status Reports

Status reports are generated in `/tmp/` with timestamps:

- `m365-rag-production-status-report-YYYYMMDD-HHMMSS.txt`
- `azure-rag-production-status-report-YYYYMMDD-HHMMSS.txt`
- `comprehensive-production-status-report-YYYYMMDD-HHMMSS.txt`

## Exit Codes

All scripts return appropriate exit codes:

- `0` - Success (all checks passed)
- `1` - Error (critical issues found)

This makes them suitable for use in monitoring systems and CI/CD pipelines.

## Integration with Monitoring

The verification scripts can be integrated with existing monitoring systems:

### Nagios/Icinga

```bash

# Check command definition

define command {
    command_name    check_m365_rag
    command_line    $USER1$/check_script.sh $ARG1$
}

# Service definition

define service {
    service_description    M365 RAG Status
    check_command          check_m365_rag!/data/m365-rag/scripts/verify-production.sh
}

```

### Prometheus

The scripts can be used as blackbox exporters or integrated with existing Prometheus setup.

## Support

For issues with the verification scripts:

1. Check the log files for detailed error messages
2. Review the troubleshooting section above
3. Check that all prerequisites are met (Docker, Python, credentials)
4. Verify network connectivity to required services

## Maintenance

The verification scripts should be updated when:

- New services are added to the deployments
- New endpoints need to be monitored
- New environment variables are required
- Security requirements change

---

**Last Updated:** October 19, 2025
**Version:** 1.0.0
**Status:** Production Ready

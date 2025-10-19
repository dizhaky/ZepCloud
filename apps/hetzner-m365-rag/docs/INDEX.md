# M365 RAG System Documentation Index

## Overview

This document provides an organized index of all documentation for the M365 RAG System deployed on Hetzner
  infrastructure.

## Core Documentation

### System Overview

- [README.md](../README.md) - Main project documentation with system overview, installation, and usage instructions

### Quick Start Guides

- [QUICK_START.md](../QUICK_START.md) - Quick start guide for deployment
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Checklist for deployment process

### Configuration Guides

- [ACCOUNT_SETUP_GUIDE.md](ACCOUNT_SETUP_GUIDE.md) - Guide for setting up accounts and credentials
- [M365_ENV_VARIABLES.md](M365_ENV_VARIABLES.md) - Documentation of environment variables for M365 integration
- [DEPLOYMENT_PREPARATION.md](DEPLOYMENT_PREPARATION.md) - Preparation steps before deployment
- [ROBUST_DEPLOYMENT.md](ROBUST_DEPLOYMENT.md) - Robust deployment procedures and verification

## Security Documentation

### Core Security

- [FIREWALL_CONFIGURATION.md](FIREWALL_CONFIGURATION.md) - Firewall configuration guide
- [SSL_CERTIFICATES.md](SSL_CERTIFICATES.md) - SSL certificate configuration
- [ELASTICSEARCH_SSL_SETUP.md](ELASTICSEARCH_SSL_SETUP.md) - Elasticsearch SSL setup
- [BACKUP_CONFIGURATION.md](BACKUP_CONFIGURATION.md) - Backup configuration guide
- [1PASSWORD_INTEGRATION.md](1PASSWORD_INTEGRATION.md) - 1Password integration guide

### Enhanced Security (New)

- [SECURITY_HARDENING_GUIDE.md](SECURITY_HARDENING_GUIDE.md) - System-level security configurations, container security,

  network segmentation, and data encryption enhancements

- [MONITORING_AND_ALERTING_CONFIGURATION.md](MONITORING_AND_ALERTING_CONFIGURATION.md) - Log aggregation, intrusion

  detection, security event monitoring, and automated security scanning

- [DISASTER_RECOVERY_AND_BACKUP_SECURITY_PLAN.md](DISASTER_RECOVERY_AND_BACKUP_SECURITY_PLAN.md) - Secure backup

  storage, backup encryption, recovery point objectives, and recovery time objectives

- [SECURITY_ENHANCEMENTS_SUMMARY.md](SECURITY_ENHANCEMENTS_SUMMARY.md) - Comprehensive summary of all security

  enhancements

## Technical Documentation

### API Documentation

- [API Documentation](../api/README.md) - API layer documentation

### Database Configuration

- [init-db.sql](../scripts/init-db.sql) - Database initialization script

### Service Configuration

- [docker-compose.yml](../docker-compose.yml) - Docker Compose configuration
- [config/elasticsearch/elasticsearch.yml](../config/elasticsearch/elasticsearch.yml) - Elasticsearch configuration
- [config/nginx/nginx.conf](../config/nginx/nginx.conf) - Nginx configuration
- [config/prometheus/prometheus.yml](../config/prometheus/prometheus.yml) - Prometheus configuration

## Scripts Documentation

### Deployment Scripts

- [deploy.sh](../scripts/deploy.sh) - Main deployment script
- [robust-deploy.sh](../scripts/robust-deploy.sh) - Robust deployment script
- [deployment-prep.sh](../scripts/deployment-prep.sh) - Deployment preparation script
- [verify-deployment.sh](../scripts/verify-deployment.sh) - Deployment verification script

### Security Scripts

- [setup-firewall.sh](../scripts/setup-firewall.sh) - Firewall setup script
- [setup-ssl.sh](../scripts/setup-ssl.sh) - SSL setup script
- [generate-es-certs.sh](../scripts/generate-es-certs.sh) - Elasticsearch certificate generation script

### Backup and Recovery Scripts

- [backup.sh](../scripts/backup.sh) - Backup script
- [restore.sh](../scripts/restore.sh) - Restore script

### Configuration Scripts

- [generate-env-from-1password.ps1](../scripts/generate-env-from-1password.ps1) - Generate environment file from

  1Password

- [setup-1password-items.ps1](../scripts/setup-1password-items.ps1) - Setup 1Password items

## Maintenance Documentation

### Maintenance Procedures

- [BUG_FIXES.md](BUG_FIXES.md) - Bug fixes documentation
- [BUG_FIXES_ROUND2.md](BUG_FIXES_ROUND2.md) - Additional bug fixes documentation

## Testing Documentation

### Testing Procedures

- [test_deployment.sh](../tests/test_deployment.sh) - Deployment testing script
- [test_api.py](../tests/test_api.py) - API testing script
- [locustfile.py](../tests/locustfile.py) - Load testing script

This index is maintained to help users navigate the documentation efficiently. For any questions or issues, please refer
  to the support information in the main README.

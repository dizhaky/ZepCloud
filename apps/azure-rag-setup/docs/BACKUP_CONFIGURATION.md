# Backup Configuration for Azure RAG System

## Overview

This document describes the backup configuration for the Azure RAG System in a production environment. Regular backups
  are essential for data protection and disaster recovery.

## Backup Strategy

The Azure RAG System implements a comprehensive backup strategy that includes:

1. **Automated Daily Backups**: Full system backups performed daily
2. **Multiple Backup Components**: Elasticsearch data and application configuration
3. **Retention Policy**: 30-day backup retention with automatic cleanup
4. **Off-site Storage**: Recommendations for off-site backup storage

## Backup Components

### 1. Elasticsearch Snapshots

Elasticsearch data is backed up using the snapshot feature:

```bash

# Create Elasticsearch snapshot

docker exec m365-elasticsearch curl -X PUT "localhost:9200/_snapshot/backup/$BACKUP_DATE?wait_for_completion=true" \
    -u "elastic:$ELASTIC_PASSWORD" \
    -H 'Content-Type: application/json' \
    -d '{
        "indices": "*",
        "ignore_unavailable": true,
        "include_global_state": false
    }'

```

### 2. Configuration Files

Application configuration files are backed up:

```bash

# Backup configuration files

tar -czf "$BACKUP_DIR/$DATE/configs.tar.gz" \
    -C /opt/azure-rag-setup \
    .env \
    docker-compose.yml

```

### 3. Scripts

Backup scripts are also backed up:

```bash

# Backup scripts

tar -czf "$BACKUP_DIR/$DATE/scripts.tar.gz" \
    -C /opt/azure-rag-setup \
    scripts/

```

## Backup Directory Structure

Backups are stored in the following directory structure:

```

/backup/azure-rag/
├── 20251019_020000/
│   ├── elasticsearch_snapshot.json
│   ├── configs.tar.gz
│   ├── scripts.tar.gz
│   └── manifest.txt
├── 20251018_020000/
│   └── ...
└── ...

```

## Automated Backup Script

The system includes an automated backup script (`scripts/backup.sh`) that:

1. Creates timestamped backup directories
2. Backs up all system components
3. Calculates backup size
4. Creates backup manifest
5. Cleans up old backups based on retention policy

### Running Backups Manually

```bash

# Run backup manually

cd /opt/azure-rag-setup
./scripts/backup.sh

```

## Backup Retention Policy

The system implements a 30-day backup retention policy:

```bash

# Clean up backups older than 30 days

find "$BACKUP_DIR" -type d -mtime +30 -exec rm -rf {} + 2>/dev/null || true

```

## Off-site Backup Recommendations

For production environments, it's recommended to implement off-site backups:

### Azure Blob Storage

```bash

# Install Azure CLI

curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Configure Azure credentials

az login

# Copy backups to Azure Blob Storage

az storage blob upload-batch \
    --account-name yourstorageaccount \
    --destination your-container \
    --source /backup/azure-rag/ \
    --destination-path azure-rag-backups/

```

### AWS S3

```bash

# Install AWS CLI

sudo apt install awscli

# Configure AWS credentials

aws configure

# Copy backups to S3

aws s3 sync /backup/azure-rag/ s3://your-backup-bucket/azure-rag-backups/

```

## Backup Verification

Regular backup verification is essential to ensure backups are valid:

```bash

# Verify configuration backup

tar -tzf "$BACKUP_DIR/$DATE/configs.tar.gz" | head -10

# Verify Elasticsearch snapshot

docker exec m365-elasticsearch curl -u "elastic:$ELASTIC_PASSWORD" \
    "localhost:9200/_snapshot/backup/$BACKUP_DATE?pretty"

```

## Restore Procedure

The system includes a restore script (`scripts/restore.sh`) that can restore from any backup:

```bash

# Restore from specific backup

cd /opt/azure-rag-setup
./scripts/restore.sh 20251019_020000

```

## Monitoring and Alerts

### Backup Status Monitoring

```bash

# Check backup logs

tail -f /var/log/azure-rag-backup.log

# Check last backup success

ls -la /backup/azure-rag/ | tail -5

```

### Health Checks

```bash

# Verify backup directory exists and has content

df -h /backup
ls -la /backup/azure-rag/

# Check cron job status

crontab -l

```

## Disaster Recovery Plan

### RTO (Recovery Time Objective)

- **Target**: 2 hours for full system recovery
- **Components**:
  - 30 minutes for infrastructure provisioning
  - 60 minutes for data restoration
  - 30 minutes for service validation

### RPO (Recovery Point Objective)

- **Target**: 24 hours (maximum data loss)
- **Achieved by**: Daily backups at 2:00 AM

## Testing Backup and Restore

Regular testing of backup and restore procedures is essential:

```bash

# Test restore to temporary location

./scripts/restore.sh 20251019_020000

# Verify restored data

docker exec m365-elasticsearch curl -u "elastic:$ELASTIC_PASSWORD" \
    "localhost:9200/_cat/indices?v"

```

## Security Considerations

### Backup Encryption

For sensitive environments, consider encrypting backups:

```bash

# Encrypt backup with GPG

gpg --symmetric --cipher-algo AES256 configs.tar.gz

# Decrypt backup

gpg configs.tar.gz.gpg

```

### Access Control

Ensure backup directories have proper permissions:

```bash

# Set proper ownership and permissions

chown -R deploy:deploy /backup/azure-rag
chmod 700 /backup/azure-rag

```

## Performance Considerations

### Backup Window

The backup process should be scheduled during low-usage periods:

- **Recommended time**: 2:00 AM (early morning)
- **Duration**: Approximately 15-30 minutes depending on data size

### Resource Usage

Monitor resource usage during backup:

```bash

# Monitor backup process resource usage

htop
iotop -o

```

## Troubleshooting

### Common Issues

1. **Backup fails due to insufficient disk space**:

   ```bash
   # Check disk space
   df -h /backup
   ```

2. **Elasticsearch snapshot fails**:

   ```bash
   # Check Elasticsearch logs
   docker logs m365-elasticsearch
   ```

### Diagnostic Commands

```bash

# Check backup script execution

sudo tail -f /var/log/azure-rag-backup.log

# Verify cron job execution

grep CRON /var/log/syslog | grep backup

# Check backup directory permissions

ls -la /backup/

```

## Best Practices

1. **Regular Testing**: Test backup and restore procedures monthly
2. **Multiple Copies**: Maintain multiple backup copies in different locations
3. **Monitoring**: Monitor backup success and failures
4. **Documentation**: Document backup procedures and recovery steps
5. **Security**: Secure backup files with proper access controls
6. **Retention**: Implement appropriate retention policies
7. **Validation**: Regularly validate backup integrity

This backup configuration ensures your Azure RAG System data is protected and can be recovered in case of failures or
  disasters.

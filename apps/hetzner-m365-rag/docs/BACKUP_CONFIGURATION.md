# Backup Configuration for M365 RAG System

## Overview

This document describes the backup configuration for the M365 RAG System in a production environment. Regular backups are essential for data protection and disaster recovery.

## Backup Strategy

The M365 RAG System implements a comprehensive backup strategy that includes:

1. **Automated Daily Backups**: Full system backups performed daily
2. **Multiple Backup Components**: Database, configuration files, and application data
3. **Retention Policy**: 30-day backup retention with automatic cleanup
4. **Off-site Storage**: Recommendations for off-site backup storage

## Backup Components

### 1. Elasticsearch Snapshots

Elasticsearch data is backed up using the snapshot feature:

```bash
# Create Elasticsearch snapshot
docker exec elasticsearch curl -X PUT "localhost:9200/_snapshot/backup/$BACKUP_DATE?wait_for_completion=true" \
    -u "elastic:$ELASTIC_PASSWORD" \
    -H 'Content-Type: application/json' \
    -d '{
        "indices": "*",
        "ignore_unavailable": true,
        "include_global_state": false
    }'
```

### 2. PostgreSQL Database

PostgreSQL database is backed up using pg_dump:

```bash
# Backup PostgreSQL database
docker exec -t postgres pg_dump -U raguser m365_rag | gzip > "$BACKUP_DIR/$DATE/postgres.sql.gz"
```

### 3. Redis Data

Redis data is backed up by copying the dump file:

```bash
# Backup Redis data
docker exec redis redis-cli SAVE
docker cp redis:/data/dump.rdb "$BACKUP_DIR/$DATE/redis_dump.rdb"
```

### 4. MinIO Configuration

MinIO configuration is backed up:

```bash
# Backup MinIO configuration
docker exec minio mc alias set local http://localhost:9000 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD
docker exec minio mc admin config export local > "$BACKUP_DIR/$DATE/minio_config.json"
```

### 5. Configuration Files

Application configuration files are backed up:

```bash
# Backup configuration files
tar -czf "$BACKUP_DIR/$DATE/configs.tar.gz" \
    -C /data/m365-rag \
    config/ \
    docker-compose.yml \
    .env
```

### 6. Scripts

Backup scripts are also backed up:

```bash
# Backup scripts
tar -czf "$BACKUP_DIR/$DATE/scripts.tar.gz" \
    -C /data/m365-rag \
    scripts/
```

## Backup Directory Structure

Backups are stored in the following directory structure:

```
/backup/m365-rag/
├── 20251019_020000/
│   ├── postgres.sql.gz
│   ├── redis_dump.rdb
│   ├── minio_config.json
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
cd /data/m365-rag
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

### Hetzner Storage Box

```bash
# Mount Hetzner Storage Box
sudo mount -t cifs //SERVER.storagebox.de/backup /mnt/storagebox \
    -o username=USERNAME,password=PASSWORD,uid=1000,gid=1000

# Copy backups to Storage Box
rsync -avz /backup/m365-rag/ /mnt/storagebox/m365-rag-backups/
```

### AWS S3

```bash
# Install AWS CLI
sudo apt install awscli

# Configure AWS credentials
aws configure

# Copy backups to S3
aws s3 sync /backup/m365-rag/ s3://your-backup-bucket/m365-rag-backups/
```

## Backup Verification

Regular backup verification is essential to ensure backups are valid:

```bash
# Verify PostgreSQL backup
gunzip < "$BACKUP_DIR/$DATE/postgres.sql.gz" | head -20

# Verify Redis backup
file "$BACKUP_DIR/$DATE/redis_dump.rdb"

# Verify configuration backup
tar -tzf "$BACKUP_DIR/$DATE/configs.tar.gz" | head -10
```

## Restore Procedure

The system includes a restore script (`scripts/restore.sh`) that can restore from any backup:

```bash
# Restore from specific backup
cd /data/m365-rag
./scripts/restore.sh 20251019_020000
```

## Monitoring and Alerts

### Backup Status Monitoring

```bash
# Check backup logs
tail -f /var/log/m365-rag-backup.log

# Check last backup success
ls -la /backup/m365-rag/ | tail -5
```

### Health Checks

```bash
# Verify backup directory exists and has content
df -h /backup
ls -la /backup/m365-rag/

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
docker exec postgres psql -U raguser m365_rag -c "SELECT count(*) FROM documents;"
```

## Security Considerations

### Backup Encryption

For sensitive environments, consider encrypting backups:

```bash
# Encrypt backup with GPG
gpg --symmetric --cipher-algo AES256 postgres.sql.gz

# Decrypt backup
gpg postgres.sql.gz.gpg
```

### Access Control

Ensure backup directories have proper permissions:

```bash
# Set proper ownership and permissions
chown -R deploy:deploy /backup/m365-rag
chmod 700 /backup/m365-rag
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

2. **PostgreSQL backup fails**:
   ```bash
   # Check PostgreSQL logs
   docker logs postgres
   ```

3. **Elasticsearch snapshot fails**:
   ```bash
   # Check Elasticsearch logs
   docker logs elasticsearch
   ```

### Diagnostic Commands

```bash
# Check backup script execution
sudo tail -f /var/log/m365-rag-backup.log

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

This backup configuration ensures your M365 RAG System data is protected and can be recovered in case of failures or disasters.
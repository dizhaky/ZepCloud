#!/bin/bash
# Automated Backup Script for M365 RAG System
# Run daily via cron: 0 2 * * * /data/m365-rag/scripts/backup.sh

set -e

# Configuration
BACKUP_DIR="/backup/m365-rag"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔄 Starting M365 RAG System Backup - $DATE${NC}"

# Create backup directory
mkdir -p "$BACKUP_DIR/$DATE"

# 1. Backup Elasticsearch
echo -e "${YELLOW}📊 Backing up Elasticsearch...${NC}"
docker exec elasticsearch curl -X PUT "localhost:9200/_snapshot/backup/$DATE?wait_for_completion=true" \
    -u "elastic:$ELASTIC_PASSWORD" \
    -H 'Content-Type: application/json' \
    -d '{
        "indices": "*",
        "ignore_unavailable": true,
        "include_global_state": false
    }' || echo -e "${RED}❌ Elasticsearch backup failed${NC}"

# 2. Backup PostgreSQL
echo -e "${YELLOW}🗄️  Backing up PostgreSQL...${NC}"
docker exec -t postgres pg_dump -U raguser m365_rag | gzip > "$BACKUP_DIR/$DATE/postgres.sql.gz"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ PostgreSQL backup successful${NC}"
else
    echo -e "${RED}❌ PostgreSQL backup failed${NC}"
fi

# 3. Backup Redis (if needed)
echo -e "${YELLOW}💾 Backing up Redis...${NC}"
docker exec redis redis-cli SAVE
docker cp redis:/data/dump.rdb "$BACKUP_DIR/$DATE/redis_dump.rdb" || echo -e "${RED}❌ Redis backup failed${NC}"

# 4. Backup MinIO data
echo -e "${YELLOW}📦 Backing up MinIO configuration...${NC}"
docker exec minio mc alias set local http://localhost:9000 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD
docker exec minio mc admin config export local > "$BACKUP_DIR/$DATE/minio_config.json" || echo -e "${RED}❌ MinIO config backup failed${NC}"

# 5. Backup configuration files
echo -e "${YELLOW}⚙️  Backing up configuration files...${NC}"
tar -czf "$BACKUP_DIR/$DATE/configs.tar.gz" \
    -C /data/m365-rag \
    config/ \
    docker-compose.yml \
    .env || echo -e "${RED}❌ Config backup failed${NC}"

# 6. Backup scripts
echo -e "${YELLOW}📜 Backing up scripts...${NC}"
tar -czf "$BACKUP_DIR/$DATE/scripts.tar.gz" \
    -C /data/m365-rag \
    scripts/ || echo -e "${RED}❌ Scripts backup failed${NC}"

# Calculate backup size
BACKUP_SIZE=$(du -sh "$BACKUP_DIR/$DATE" | cut -f1)
echo -e "${GREEN}📊 Backup size: $BACKUP_SIZE${NC}"

# Create backup manifest
cat > "$BACKUP_DIR/$DATE/manifest.txt" <<EOF
M365 RAG System Backup
Date: $DATE
Size: $BACKUP_SIZE
Components:
- Elasticsearch snapshot
- PostgreSQL database dump
- Redis data
- MinIO configuration
- Application configs
- Scripts

Backup completed at: $(date)
EOF

# Remove old backups
echo -e "${YELLOW}🧹 Cleaning up old backups (older than $RETENTION_DAYS days)...${NC}"
find "$BACKUP_DIR" -type d -mtime +$RETENTION_DAYS -exec rm -rf {} + 2>/dev/null || true

# Verify backup
if [ -f "$BACKUP_DIR/$DATE/postgres.sql.gz" ]; then
    echo -e "${GREEN}✅ Backup completed successfully!${NC}"
    echo -e "${GREEN}📁 Location: $BACKUP_DIR/$DATE${NC}"
    
    # Optional: Send notification (uncomment if needed)
    # curl -X POST "https://your-webhook-url" -d "Backup completed: $DATE"
else
    echo -e "${RED}❌ Backup verification failed!${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 Backup process finished${NC}"


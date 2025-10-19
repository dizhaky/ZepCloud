#!/bin/bash
# Restore Script for M365 RAG System
# Usage: ./restore.sh <backup_date>
# Example: ./restore.sh 20251018_020000

set -e

# Check if backup date is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <backup_date>"
    echo "Example: $0 20251018_020000"
    echo ""
    echo "Available backups:"
    ls -1 /backup/m365-rag/
    exit 1
fi

BACKUP_DATE=$1
BACKUP_DIR="/backup/m365-rag/$BACKUP_DATE"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verify backup exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${RED}❌ Backup directory not found: $BACKUP_DIR${NC}"
    exit 1
fi

echo -e "${YELLOW}⚠️  WARNING: This will restore data from backup $BACKUP_DATE${NC}"
echo -e "${YELLOW}⚠️  All current data will be replaced!${NC}"
echo ""
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

echo -e "${GREEN}🔄 Starting restore from backup: $BACKUP_DATE${NC}"

# 1. Stop all services
echo -e "${YELLOW}🛑 Stopping services...${NC}"
cd /data/m365-rag
docker compose stop

# 2. Restore PostgreSQL
echo -e "${YELLOW}🗄️  Restoring PostgreSQL...${NC}"
if [ -f "$BACKUP_DIR/postgres.sql.gz" ]; then
    docker compose start postgres
    sleep 10
    gunzip < "$BACKUP_DIR/postgres.sql.gz" | docker exec -i postgres psql -U raguser m365_rag
    echo -e "${GREEN}✅ PostgreSQL restored${NC}"
else
    echo -e "${RED}❌ PostgreSQL backup file not found${NC}"
fi

# 3. Restore Redis
echo -e "${YELLOW}💾 Restoring Redis...${NC}"
if [ -f "$BACKUP_DIR/redis_dump.rdb" ]; then
    docker compose start redis
    sleep 5
    docker cp "$BACKUP_DIR/redis_dump.rdb" redis:/data/dump.rdb
    docker compose restart redis
    echo -e "${GREEN}✅ Redis restored${NC}"
else
    echo -e "${RED}❌ Redis backup file not found${NC}"
fi

# 4. Restore Elasticsearch
echo -e "${YELLOW}📊 Restoring Elasticsearch...${NC}"
docker compose start elasticsearch
sleep 20
docker exec elasticsearch curl -X POST "localhost:9200/_snapshot/backup/$BACKUP_DATE/_restore" \
    -u "elastic:$ELASTIC_PASSWORD" \
    -H 'Content-Type: application/json' \
    -d '{
        "indices": "*",
        "ignore_unavailable": true,
        "include_global_state": false
    }' || echo -e "${RED}❌ Elasticsearch restore failed${NC}"

# 5. Restore configurations
echo -e "${YELLOW}⚙️  Restoring configuration files...${NC}"
if [ -f "$BACKUP_DIR/configs.tar.gz" ]; then
    tar -xzf "$BACKUP_DIR/configs.tar.gz" -C /data/m365-rag/
    echo -e "${GREEN}✅ Configurations restored${NC}"
else
    echo -e "${RED}❌ Config backup file not found${NC}"
fi

# 6. Start all services
echo -e "${YELLOW}🚀 Starting all services...${NC}"
docker compose up -d

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
sleep 30

# Verify services
echo -e "${YELLOW}🔍 Verifying services...${NC}"
docker compose ps

echo -e "${GREEN}✅ Restore completed!${NC}"
echo -e "${GREEN}📁 Restored from: $BACKUP_DIR${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Verify services are running: docker compose ps"
echo "2. Check API health: curl http://localhost:8000/health"
echo "3. Access RAGFlow UI: http://YOUR_SERVER_IP:9380"
echo "4. Check Elasticsearch: curl -u elastic:PASSWORD http://localhost:9200/_cluster/health"


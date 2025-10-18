#!/bin/bash
# M365 Automated Sync Script
# Run this via cron for automated M365 synchronization

cd /Users/danizhaky/Dev/ZepCloud/azure-rag-setup

# Log file
LOG_FILE="logs/m365_sync_$(date +%Y%m%d_%H%M%S).log"
mkdir -p logs

echo "=== M365 Sync Started: $(date) ===" >> $LOG_FILE

# Run full M365 sync
python3 m365_indexer.py sync >> $LOG_FILE 2>&1

# Check status
python3 m365_indexer.py status >> $LOG_FILE 2>&1

# Run indexer to process new documents
python3 maintenance.py --non-interactive --action run-indexer >> $LOG_FILE 2>&1

echo "=== M365 Sync Completed: $(date) ===" >> $LOG_FILE

# Keep only last 30 days of logs
find logs/ -name "m365_sync_*.log" -mtime +30 -delete

#!/bin/bash
# Setup cron jobs for M365 automated sync

echo "🔧 Setting up M365 automated sync schedule"
echo "=========================================="
echo ""

# Create cron job entries
CRON_ENTRIES="# M365 RAG Sync - Automated scheduling
# Run full M365 sync every 6 hours
0 */6 * * * cd /Users/danizhaky/Dev/ZepCloud/azure-rag-setup && ./m365_sync_cron.sh

# Run indexer every hour to process new documents
0 * * * * cd /Users/danizhaky/Dev/ZepCloud/azure-rag-setup && python3 maintenance.py --non-interactive --action run-indexer >> logs/indexer_cron.log 2>&1

# Daily health check at 9 AM
0 9 * * * cd /Users/danizhaky/Dev/ZepCloud/azure-rag-setup && python3 maintenance.py --non-interactive --action health >> logs/health_cron.log 2>&1
"

echo "📋 Proposed cron schedule:"
echo "$CRON_ENTRIES"
echo ""
echo "To install these cron jobs, run:"
echo "  (crontab -l 2>/dev/null; echo \"\$CRON_ENTRIES\") | crontab -"
echo ""
echo "Or manually add to crontab:"
echo "  crontab -e"
echo ""

# Save to file for reference
echo "$CRON_ENTRIES" > m365_crontab.txt
echo "✅ Cron configuration saved to m365_crontab.txt"

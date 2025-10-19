# RAG-Anything Integration - Production Deployment Guide

**Date:** October 18, 2025
**Status:** Ready for Production
**Test Pass Rate:** 100% (6/6 tests)

---

## ✅ Pre-Deployment Checklist

### 1. System Requirements

- [x] Python 3.14 installed
- [x] Azure AI Search service running
- [x] Azure Blob Storage configured
- [x] M365 authentication working
- [x] 40-field index schema deployed

### 2. Dependencies

- [x] All Python packages installed
- [x] Graph builder tested
- [x] Enhanced indexers created
- [x] Orchestrator working

### 3. Testing

- [x] Integration tests pass (100%)
- [x] Azure schema updated
- [x] M365 authentication verified
- [x] Relationship extraction working

---

## 🚀 Deployment Steps

### Step 1: Backup Current Setup

```bash

cd /Users/danizhaky/Dev/ZepCloud/azure-rag-setup

# Backup current progress files

cp sharepoint_progress.json sharepoint_progress.json.backup
cp onedrive_progress.json onedrive_progress.json.backup 2>/dev/null || true

# Backup cron jobs

crontab -l > cron_backup_$(date +%Y%m%d).txt

echo "✅ Backup complete"

```

### Step 2: Update Cron Jobs

```bash

# Edit crontab

crontab -e

```

## Add/Update:

```bash

# ============================================

# M365 Enhanced Sync with Graph Relationships

# ============================================ (2)

# SharePoint enhanced sync - every 6 hours

0 */6 * * * cd /Users/danizhaky/Dev/ZepCloud/azure-rag-setup && /usr/local/bin/python3 orchestrate_rag_anything.py
  --source sharepoint >> /tmp/sharepoint-enhanced-sync.log 2>&1

# OneDrive sync (standard) - every 6 hours, offset by 2 hours

0 2,8,14,20 * * * cd /Users/danizhaky/Dev/ZepCloud/azure-rag-setup && /usr/local/bin/python3 m365_onedrive_indexer.py >>
  /tmp/onedrive-sync.log 2>&1

# Exchange sync (standard) - every 6 hours, offset by 4 hours

0 4,10,16,22 * * * cd /Users/danizhaky/Dev/ZepCloud/azure-rag-setup && /usr/local/bin/python3 m365_exchange_indexer.py
  >> /tmp/exchange-sync.log 2>&1

# Graph export - daily at 2 AM

0 2 * * * cd /Users/danizhaky/Dev/ZepCloud/azure-rag-setup && cp sharepoint_graph.json sharepoint_graph_backup_$(date
  +\%Y\%m\%d).json 2>/dev/null || true

# Cleanup old logs - weekly on Sunday at 3 AM

0 3 * * 0 find /tmp -name "*-sync.log" -mtime +7 -delete

```

## Save and verify:

```bash

crontab -l | grep -i m365

```

### Step 3: Create Monitoring Script

```bash

cat > /Users/danizhaky/Dev/ZepCloud/azure-rag-setup/monitor_rag_integration.sh << 'EOF'
#!/bin/bash

# Monitor RAG-Anything Integration Health

echo "=================================================="
echo "RAG-Anything Integration Health Check"
echo "$(date)"
echo "=================================================="

cd /Users/danizhaky/Dev/ZepCloud/azure-rag-setup

# Check last sync times

echo -e "\n📅 Last Sync Times:"
echo "SharePoint: $(grep -o '"last_sync": "[^"]*"' sharepoint_progress_enhanced.json 2>/dev/null | head -1 || echo
  'Never')"
echo "OneDrive: $(grep -o '"last_sync": "[^"]*"' onedrive_progress.json 2>/dev/null | head -1 || echo 'Never')"

# Check graph statistics

echo -e "\n📊 Graph Statistics:"
if [ -f sharepoint_graph.json ]; then
    python3 -c "
import json
with open('sharepoint_graph.json', 'r') as f:
    data = json.load(f)
    stats = data.get('stats', {})
    print(f\"  Documents: {stats.get('total_documents', 0)}\")
    print(f\"  Entities: {stats.get('total_entities', 0)}\")
    print(f\"  Topics: {stats.get('total_topics', 0)}\")
    print(f\"  Citations: {stats.get('total_citations', 0)}\")
"
else
    echo "  Graph not yet generated"
fi

# Check recent logs

echo -e "\n📋 Recent Log Activity:"
if [ -f /tmp/sharepoint-enhanced-sync.log ]; then
    echo "SharePoint Enhanced Sync:"
    tail -5 /tmp/sharepoint-enhanced-sync.log | sed 's/^/  /'
else
    echo "  No SharePoint enhanced logs yet"
fi

# Check for errors

echo -e "\n⚠️  Recent Errors (last 24h):"
find /tmp -name "*-sync.log" -mtime -1 -exec grep -l "ERROR\|FAIL" {} \; 2>/dev/null | while read log; do
    echo "  $(basename $log): $(grep -c "ERROR\|FAIL" $log) errors"
done || echo "  No errors found"

# Azure AI Search status

echo -e "\n🔍 Azure AI Search Status:"
python3 orchestrate_rag_anything.py --status 2>/dev/null | grep -A 5 "SharePoint:" || echo "  Could not retrieve status"

echo -e "\n=================================================="
echo "Health check complete"
echo "=================================================="
EOF

chmod +x monitor_rag_integration.sh

```

### Step 4: Initial Production Sync

```bash

# Run first production sync with monitoring

cd /Users/danizhaky/Dev/ZepCloud/azure-rag-setup

echo "Starting initial production sync..."
date

# Sync SharePoint with graph relationships

python3 orchestrate_rag_anything.py --source sharepoint 2>&1 | tee initial_sync_$(date +%Y%m%d_%H%M%S).log

echo "Initial sync complete"
date

# Check results

python3 orchestrate_rag_anything.py --status

# View graph

cat sharepoint_graph.json | jq '.stats'

```

### Step 5: Verify in TypingMind

1. **Open TypingMind**
2. **Test Enhanced Queries:**

```

# Query 1: Find documents with tables

Search for documents that contain tables

# Query 2: Find related documents

Show me documents related to [specific document]

# Query 3: Find by entity

Find all documents mentioning Dan Izhaky and show related documents

# Query 4: High-value documents

Find documents with the most relationships

```

3. **Verify Results:**

- Check that relationship metadata appears
- Verify multimodal flags work
- Confirm graph relationships are returned

---

## 📊 Monitoring & Maintenance

### Daily Checks

```bash

# Run health check

./monitor_rag_integration.sh

# Check sync logs

tail -50 /tmp/sharepoint-enhanced-sync.log

```

### Weekly Review

```bash

# Generate weekly report

cat > weekly_report.sh << 'EOF'
#!/bin/bash
echo "=== Weekly RAG-Anything Report ==="
echo "Week of: $(date +%Y-%m-%d)"

# Document counts

echo -e "\n📈 Documents Processed:"
python3 -c "
import json
files = ['sharepoint_progress_enhanced.json', 'onedrive_progress.json']
total = 0
for f in files:
    try:
        with open(f, 'r') as file:
            data = json.load(file)
            count = data.get('total_documents', 0)
            print(f'  {f}: {count}')
            total += count
    except:
        pass
print(f'  Total: {total}')
"

# Graph growth

echo -e "\n📊 Graph Growth:"
python3 -c "
import json, glob
graphs = sorted(glob.glob('sharepoint_graph_backup_*.json'))
if graphs:
    with open(graphs[-1], 'r') as f:
        data = json.load(f)
        stats = data.get('stats', {})
        print(f\"  Documents in graph: {stats.get('total_documents', 0)}\")
        print(f\"  Relationships: {stats.get('total_citations', 0)}\")
"

# Error summary

echo -e "\n⚠️  Error Summary:"
grep -c "ERROR\|FAIL" /tmp/*-sync.log 2>/dev/null || echo "  No errors"

EOF
chmod +x weekly_report.sh

# Run it

./weekly_report.sh

```

### Monthly Optimization

```bash

# Analyze relationship quality

python3 -c "
import json
with open('sharepoint_graph.json', 'r') as f:
    data = json.load(f)

# Find highly connected documents

docs = data.get('documents', {})
scores = [(doc_id, doc.get('relationships', {}).get('relationship_score', 0))
          for doc_id, doc in docs.items()]
scores.sort(key=lambda x: x[1], reverse=True)

print('Top 10 Most Connected Documents:')
for i, (doc_id, score) in enumerate(scores[:10], 1):
    print(f'{i}. {doc_id}: {score:.2f}')
"

# Clean up old backups

find . -name "sharepoint_graph_backup_*.json" -mtime +30 -delete
find . -name "*_test_report_*.json" -mtime +7 -delete

```

---

## 🔧 Rollback Plan

If issues occur, rollback to standard indexers:

```bash

# 1. Stop enhanced sync

crontab -l | grep -v "orchestrate_rag_anything" | crontab -

# 2. Restore old cron jobs

crontab cron_backup_YYYYMMDD.txt

# 3. Restore progress files

mv sharepoint_progress.json.backup sharepoint_progress.json

# 4. Continue with standard indexers

python3 m365_sharepoint_indexer.py

```

---

## 📝 Production Checklist

### Before Go-Live

- [ ] All tests passing (100%)
- [ ] Azure schema updated (40 fields)
- [ ] Backups created
- [ ] Cron jobs updated
- [ ] Monitoring script created
- [ ] Initial sync completed successfully
- [ ] TypingMind queries verified

### After Go-Live

- [ ] Monitor logs for 24 hours
- [ ] Check graph growth daily for 1 week
- [ ] Verify no sync errors
- [ ] Confirm TypingMind integration working
- [ ] Document any issues encountered

### Week 1

- [ ] Run health check daily
- [ ] Review sync logs
- [ ] Check relationship quality
- [ ] Gather user feedback from TypingMind
- [ ] Optimize if needed

---

## 🎯 Success Metrics

Track these metrics weekly:

1. **Document Coverage**

   - Target: 95%+ of M365 documents indexed
   - Current: Check with `./monitor_rag_integration.sh`

2. **Relationship Quality**

   - Target: Avg 3+ relationships per document
   - Current: Check graph statistics

3. **Sync Reliability**

   - Target: <1% error rate
   - Current: Review error logs

4. **Query Performance**

   - Target: Relationship queries <2 seconds
   - Current: Test in TypingMind

5. **User Satisfaction**
   - Target: Positive feedback on relationship discovery
   - Current: Collect feedback from team

---

## 🆘 Emergency Contacts

## System Issues:

- Check logs: `/tmp/*-sync.log`
- Run diagnostics: `./monitor_rag_integration.sh`
- Test suite: `python3 test_rag_anything_integration.py`

## Azure Issues:

- Check status: `python3 orchestrate_rag_anything.py --status`
- Review schema: `python3 update_azure_schema_enhanced.py`

## M365 Auth Issues:

- Refresh token: `python3 m365_auth.py`
- Check credentials: `source ./get_m365_credentials.sh`

---

## ✅ Deployment Complete

**Status:** Production Ready
**Date Deployed:** ******\_\_\_******
**Deployed By:** ******\_\_\_******
**Initial Sync:** ******\_\_\_******

**Next Review:** 1 week from deployment

---

**Congratulations!** 🎉

Your RAG-Anything integration is now in production with:

- ✅ Document relationship graphs
- ✅ Multimodal content detection
- ✅ Entity co-occurrence tracking
- ✅ Automated sync every 6 hours
- ✅ Comprehensive monitoring

The system will automatically:

1. Sync M365 data every 6 hours
2. Build relationship graphs
3. Update Azure AI Search
4. Enable relationship-based queries in TypingMind

Monitor daily for the first week, then weekly ongoing.

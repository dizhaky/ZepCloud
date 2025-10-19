# RAG-Anything M365 Integration - Quick Start Guide 🚀

**Last Updated:** October 18, 2025
**Status:** Production Ready ✅

---

## 🎯 Quick Commands

### **Check System Status**

```bash

cd /Users/danizhaky/Dev/ZepCloud/azure-rag-setup
python3 orchestrate_rag_anything.py --status

```

## Expected Output:

```

📊 RAG-Anything Integration Status
📁 SharePoint: 69 documents, 60 relationships
📊 Graph: 69 documents, 3 entities
✅ All enhanced features operational

```

---

### **Sync SharePoint Documents**

#### **Test Sync (2 sites, ~5 minutes)**

```bash

python3 orchestrate_rag_anything.py --source sharepoint --limit 2

```

#### **Full Sync (42 sites, ~90 minutes)**

```bash

python3 orchestrate_rag_anything.py --source sharepoint

```

#### **Batch Sync (10 sites at a time)**

```bash

python3 orchestrate_rag_anything.py --source sharepoint --limit 10

```

---

### **View Results**

#### **Graph Statistics**

```bash

cat sharepoint_graph.json | python3 -m json.tool | grep -A 5 "stats"

```

#### **Progress Tracking**

```bash

cat sharepoint_progress.json | python3 -m json.tool

```

#### **Recent Documents**

```bash

cat sharepoint_graph.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
docs = list(data.get('documents', {}).items())[:5]
for doc_id, info in docs:
    print(f\"📄 {info['metadata'].get('metadata_storage_name', 'Unknown')}\")
    print(f\"   Entities: {len(info.get('extracted_entities', []))}\")
    print(f\"   Related: {len(info.get('related_documents', []))}\")
    print()
"

```

---

### **Test Azure AI Search**

#### **Query Documents with Tables**

```bash

curl -X POST "https://$(grep AZURE_SEARCH_SERVICE_NAME .env | cut -d= -f2).search.windows.net/indexes/training-data-index/docs/search?api-version=2023-11-01" \
  -H "Content-Type: application/json" \
  -H "api-key: $(grep AZURE_SEARCH_ADMIN_KEY .env | cut -d= -f2)" \
  -d '{
    "search": "*",
    "filter": "has_tables eq true",
    "select": "metadata_storage_name,tables_count",
    "top": 5
  }' | python3 -m json.tool

```

#### **Query Highly Connected Documents**

```bash

curl -X POST "https://$(grep AZURE_SEARCH_SERVICE_NAME .env | cut -d= -f2).search.windows.net/indexes/training-data-index/docs/search?api-version=2023-11-01" \
  -H "Content-Type: application/json" \
  -H "api-key: $(grep AZURE_SEARCH_ADMIN_KEY .env | cut -d= -f2)" \
  -d '{
    "search": "*",
    "filter": "relationship_score gt 3.0",
    "orderby": "relationship_score desc",
    "select": "metadata_storage_name,relationship_score",
    "top": 5
  }' | python3 -m json.tool

```

---

### **Update Azure Schema**

## Add new enhanced fields to existing index:

```bash

python3 update_azure_schema_enhanced.py

```

## Expected Output: (2)

```

✅ Index schema updated successfully!
📊 Final index has 40 fields
🎯 New Capabilities Enabled:
   ✅ Multimodal content detection
   ✅ Document relationship tracking
   ✅ Graph-based search and filtering

```

---

### **Run Tests**

#### **All Tests**

```bash

python3 -m pytest test_rag_anything_integration.py -v

```

#### **Specific Test**

```bash

# Test graph builder

python3 -m pytest test_rag_anything_integration.py::TestRAGAnythingIntegration::test_1_graph_builder -v

# Test Azure schema

python3 -m pytest test_rag_anything_integration.py::TestRAGAnythingIntegration::test_2_azure_ai_search_schema -v

# Test indexer

python3 -m pytest test_rag_anything_integration.py::TestRAGAnythingIntegration::test_3_enhanced_sharepoint_indexer -v

```

---

## 🔍 TypingMind Query Examples

### **Find Documents with Tables**

```

Show me all documents that contain tables

```

_Behind the scenes:_ `filter: "has_tables eq true"`

### **Find Related Documents**

```

Find documents related to "employee benefits"

```

_Behind the scenes:_ Search + `relationship_score` ranking

### **Find Highly Cited Documents**

```

Show me the most referenced documents

```

_Behind the scenes:_ `orderby: "cites_count desc"`

---

## 🛠️ Troubleshooting

### **Issue: Authentication Failed**

```bash

# Check credentials

grep M365_CLIENT_ID .env
grep M365_TENANT_ID .env

# Get credentials from 1Password

op read "op://Personal/M365 RAG Indexer/M365_CLIENT_ID"

```

### **Issue: Azure Connection Failed**

```bash

# Verify Azure credentials

python3 -c "
import os
from dotenv import load_dotenv
import requests

load_dotenv()
service = os.getenv('AZURE_SEARCH_SERVICE_NAME')
key = os.getenv('AZURE_SEARCH_ADMIN_KEY')

response = requests.get(
    f'https://{service}.search.windows.net/indexes?api-version=2023-11-01',
    headers={'api-key': key}
)

if response.status_code == 200:
    print(f'✅ Connected to {service}')
    indexes = [idx['name'] for idx in response.json()['value']]
    print(f'📊 Indexes: {', '.join(indexes)}')
else:
    print(f'❌ Error: {response.status_code}')
"

```

### **Issue: Graph Not Building**

```bash

# Check graph file

if [ -f sharepoint_graph.json ]; then
    echo "✅ Graph file exists"
    python3 -c "import json; json.load(open('sharepoint_graph.json'))" && echo "✅ Valid JSON" || echo "❌ Invalid JSON"
else
    echo "❌ Graph file not found - run a sync first"
fi

```

### **Issue: Sync Interrupted**

```bash

# Resume with batch processing

python3 orchestrate_rag_anything.py --source sharepoint --limit 5

# Check progress

cat sharepoint_progress.json | python3 -m json.tool | head -20

```

---

## 📊 Monitoring Commands

### **System Health Check**

```bash

echo "=== RAG-Anything Health Check ==="
echo ""
echo "📁 Files:"
[ -f orchestrate_rag_anything.py ] && echo "  ✅ Orchestrator" || echo "  ❌ Orchestrator missing"
[ -f m365_sharepoint_indexer_enhanced.py ] && echo "  ✅ Enhanced indexer" || echo "  ❌ Enhanced indexer missing"
[ -f raganything-processor/graph_builder.py ] && echo "  ✅ Graph builder" || echo "  ❌ Graph builder missing"
[ -f sharepoint_graph.json ] && echo "  ✅ Graph data" || echo "  ⚠️  Graph data (will be created on first sync)"
echo ""
echo "🔐 Credentials:"
grep -q "M365_CLIENT_ID" .env && echo "  ✅ M365 credentials" || echo "  ❌ M365 credentials missing"
grep -q "AZURE_SEARCH_SERVICE_NAME" .env && echo "  ✅ Azure credentials" || echo "  ❌ Azure credentials missing"
echo ""
echo "📊 Status:"
python3 orchestrate_rag_anything.py --status 2>&1 | grep -E "(Documents|Relationships|Entities)" | head -5

```

### **Performance Metrics**

```bash

# Documents per site

cat sharepoint_progress.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
sites = data.get('sites', {})
for site_id, info in sites.items():
    name = info.get('name', 'Unknown')
    docs = info.get('documents_processed', 0)
    print(f'{name}: {docs} docs')
"

# Graph density

cat sharepoint_graph.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
stats = data.get('stats', {})
docs = stats.get('total_documents', 0)
rels = stats.get('total_relationships', 0)
if docs > 0:
    density = rels / docs
    print(f'Graph density: {density:.2f} relationships/doc')
"

```

---

## 🚀 Production Deployment

### **1. Enable Automated Sync**

Edit crontab:

```bash

crontab -e

```

Add line:

```

0 3 * * * cd /Users/danizhaky/Dev/ZepCloud/azure-rag-setup && python3 orchestrate_rag_anything.py --source sharepoint >>
  /tmp/rag_sync.log 2>&1

```

### **2. Monitor Logs**

```bash

# View recent sync activity

tail -f /tmp/rag_sync.log

# Check last sync time

cat sharepoint_progress.json | python3 -c "import json, sys; print('Last sync:', json.load(sys.stdin).get('last_sync',
  'Never'))"

```

### **3. Verify TypingMind Access**

Open TypingMind and test:

```

Find documents with tables about employee benefits

```

Expected: Documents matching query with enhanced table content

---

## 📚 Documentation

- **Installation Complete:** `INSTALLATION_COMPLETE.md`
- **Technical Guide:** `RAG_ANYTHING_INTEGRATION.md`
- **Deployment Guide:** `DEPLOYMENT_GUIDE.md`
- **Code Quality:** `CODE_QUALITY_REPORT.md`
- **Architecture:** `raganything-processor/README.md`

---

## 🎯 Common Workflows

### **Daily Check**

```bash

cd /Users/danizhaky/Dev/ZepCloud/azure-rag-setup
python3 orchestrate_rag_anything.py --status

```

### **Weekly Sync**

```bash

cd /Users/danizhaky/Dev/ZepCloud/azure-rag-setup
python3 orchestrate_rag_anything.py --source sharepoint

```

### **Monthly Verification**

```bash

cd /Users/danizhaky/Dev/ZepCloud/azure-rag-setup
python3 -m pytest test_rag_anything_integration.py -v
python3 orchestrate_rag_anything.py --status

```

---

## 💡 Pro Tips

1. **Start Small:** Use `--limit 2` for testing
2. **Batch Process:** Use `--limit 10` for large syncs
3. **Monitor Progress:** Check `sharepoint_progress.json` during sync
4. **View Graph:** Use `cat sharepoint_graph.json | python3 -m json.tool`
5. **Test Azure:** Query with filters like `has_tables eq true`

---

## ✅ Success Indicators

| Check      | Command                                              | Expected                        |
| ---------- | ---------------------------------------------------- | ------------------------------- |
| Status     | `python3 orchestrate_rag_anything.py --status`       | Shows documents & relationships |
| Graph      | `cat sharepoint_graph.json`                          | Valid JSON with stats           |
| Azure      | Check fields                                         | 40 fields including enhanced    |
| Tests      | `python3 -m pytest test_rag_anything_integration.py` | 6/6 passing                     |
| TypingMind | Query documents                                      | Returns enhanced results        |

---

**Quick Start Guide - Ready to Use!** 🚀

For detailed information, see `INSTALLATION_COMPLETE.md`

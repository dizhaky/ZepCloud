#!/bin/bash
# Monitor SharePoint sync progress

echo "════════════════════════════════════════════════════════════"
echo "📊 SHAREPOINT SYNC MONITOR"
echo "════════════════════════════════════════════════════════════"
echo ""

# Check if process is running
if [ -f .sync_pid ]; then
    PID=$(cat .sync_pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ Sync process is RUNNING (PID: $PID)"
    else
        echo "⚠️  Sync process COMPLETED or STOPPED"
    fi
else
    echo "⚠️  No sync process found"
fi

echo ""
echo "📊 Current Progress:"
python3 << 'EOF'
import json
import os
from datetime import datetime

# Read progress file
try:
    with open('sharepoint_progress.json', 'r') as f:
        data = json.load(f)

    print(f"   Last Sync: {data.get('last_sync', 'Unknown')}")
    print(f"   Sites Processed: {len(data.get('sites', {}))}")
    print(f"   Total Documents: {data.get('total_documents', 0)}")
    print(f"   Total Size: {data.get('total_size_bytes', 0) / (1024*1024):.2f} MB")

    print()
    print("📁 Sites:")
    for site_id, site_info in data.get('sites', {}).items():
        name = site_info.get('name', 'Unknown')
        docs = site_info.get('documents_processed', 0)
        print(f"   • {name}: {docs} documents")

except Exception as e:
    print(f"   Error reading progress: {e}")

print()
print("📈 Graph Statistics:")
try:
    with open('sharepoint_graph.json', 'r') as f:
        graph = json.load(f)

    stats = graph.get('stats', {})
    print(f"   Documents in graph: {stats.get('total_documents', 0)}")
    print(f"   Entities tracked: {stats.get('total_entities', 0)}")
    print(f"   Citations: {stats.get('total_citations', 0)}")
    print(f"   Relationships: {stats.get('total_relationships', 0)}")
except Exception as e:
    print(f"   Error reading graph: {e}")
EOF

echo ""
echo "📄 Recent Log Activity (last 15 lines):"
tail -15 full_sync_*.log 2>/dev/null | grep -v "^$" | tail -10 || echo "   (No recent activity)"

echo ""
echo "════════════════════════════════════════════════════════════"



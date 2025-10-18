#!/bin/bash

# Comprehensive Error Monitoring Script
LOG_FILE=$(ls -t m365_final_sync_*.log 2>/dev/null | head -1)

if [ -z "$LOG_FILE" ]; then
    echo "❌ No log file found"
    exit 1
fi

echo "🔍 COMPREHENSIVE ERROR MONITORING"
echo "=================================="
echo "Log file: $LOG_FILE"
echo ""

# Monitor for errors in real-time
tail -f "$LOG_FILE" | while read line; do
    # Check for various error patterns
    if echo "$line" | grep -iq "error\|fail\|exception\|traceback\|❌"; then
        echo "🚨 ERROR: $line"
    elif echo "$line" | grep -iq "429\|rate limit\|⏸️"; then
        echo "⏸️  RATE LIMIT: $line"
    elif echo "$line" | grep -iq "warning\|⚠️"; then
        echo "⚠️  WARNING: $line"
    elif echo "$line" | grep -iq "retry"; then
        echo "🔄 RETRY: $line"
    elif echo "$line" | grep -iq "✅.*success\|completed\|100%"; then
        echo "✅ SUCCESS: $line"
    fi
done

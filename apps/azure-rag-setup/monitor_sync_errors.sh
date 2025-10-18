#!/bin/bash
echo "🔍 REAL-TIME SYNC MONITORING"
echo "============================"
echo ""
echo "Monitoring for errors in real-time..."
echo "Press Ctrl+C to stop"
echo ""

tail -f m365_full_sync_20251018_085538.log 2>/dev/null | grep --line-buffered -i "fail\|error\|denied\|cannot\|skip\|⚠️\|❌\|exception" --color=always

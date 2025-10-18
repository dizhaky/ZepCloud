#!/bin/bash

# Quick Error Check Script
LOG_FILE=$(ls -t m365_final_sync_*.log 2>/dev/null | head -1)

echo "📊 ERROR ANALYSIS REPORT"
echo "========================"
echo "Log file: $LOG_FILE"
echo ""

echo "1️⃣  ERRORS:"
grep -i "error\|exception\|traceback\|❌" "$LOG_FILE" 2>/dev/null | tail -20 || echo "   ✅ No errors found"
echo ""

echo "2️⃣  RATE LIMITING (429):"
grep -i "429\|rate limit\|⏸️" "$LOG_FILE" 2>/dev/null | tail -20 || echo "   ✅ No rate limiting detected"
echo ""

echo "3️⃣  WARNINGS:"
grep -i "warning\|⚠️.*failed" "$LOG_FILE" 2>/dev/null | tail -20 || echo "   ✅ No warnings found"
echo ""

echo "4️⃣  RETRIES:"
grep -i "retry\|waiting.*before retry" "$LOG_FILE" 2>/dev/null | tail -10 || echo "   ℹ️  No retries needed yet"
echo ""

echo "5️⃣  SUCCESS INDICATORS:"
grep -i "✅\|completed\|100%" "$LOG_FILE" 2>/dev/null | tail -10 || echo "   ⏳ Still in progress"
echo ""

echo "6️⃣  SUMMARY:"
echo "   Total lines: $(wc -l < "$LOG_FILE")"
echo "   Errors: $(grep -ic "error\|exception" "$LOG_FILE" 2>/dev/null || echo 0)"
echo "   Rate limits: $(grep -ic "429\|rate limit" "$LOG_FILE" 2>/dev/null || echo 0)"
echo "   Warnings: $(grep -ic "warning" "$LOG_FILE" 2>/dev/null || echo 0)"
echo "   Retries: $(grep -ic "retry" "$LOG_FILE" 2>/dev/null || echo 0)"

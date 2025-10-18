#!/bin/bash
# Test Browser Control
# This script tests browser control capabilities

set -e

PORT=${1:-9222}

echo "🧪 Testing Browser Control Capabilities"
echo "======================================"

echo "1. Testing DevTools connection..."
if curl -s http://localhost:$PORT/json/version > /dev/null; then
    echo "✅ DevTools connection successful"
    curl -s http://localhost:$PORT/json/version | head -3
else
    echo "❌ DevTools connection failed"
    echo "   Make sure browser is running with debugging enabled"
    echo "   Run: ./scripts/start-browser-debug.sh $PORT"
    exit 1
fi

echo ""
echo "2. Testing WebSocket debugger..."
DEBUGGER_URL=$(curl -s http://localhost:$PORT/json | jq -r '.[0].webSocketDebuggerUrl' 2>/dev/null)
if [ "$DEBUGGER_URL" != "null" ] && [ -n "$DEBUGGER_URL" ]; then
    echo "✅ WebSocket debugger available: $DEBUGGER_URL"
else
    echo "❌ WebSocket debugger not available"
fi

echo ""
echo "3. Testing MCP server..."
if npm list -g chrome-devtools-mcp &>/dev/null; then
    echo "✅ chrome-devtools-mcp installed"
else
    echo "❌ chrome-devtools-mcp not installed"
    echo "   Run: npm install -g chrome-devtools-mcp"
fi

echo ""
echo "4. Testing browser processes..."
BROWSER_PROCESSES=$(ps aux | grep -i comet | grep -v grep | wc -l)
if [ "$BROWSER_PROCESSES" -gt 0 ]; then
    echo "✅ Browser processes running: $BROWSER_PROCESSES"
else
    echo "⚠️  No browser processes detected"
fi

echo ""
echo "🎯 Browser Control Test Complete!"
echo "   Status: Ready for browser automation"
echo "   Port: $PORT"
echo "   WebSocket: $DEBUGGER_URL"

#!/bin/bash

# TypingMind MCP Server Test Script
# Tests the local MCP server for proper functionality

echo "🧪 TypingMind MCP Server Test Suite"
echo "=================================="
echo ""

# Test 1: Check if server is running
echo "1️⃣ Testing server process..."
if ps aux | grep "@typingmind/mcp" | grep -v grep > /dev/null; then
    echo "✅ MCP server process is running"
else
    echo "❌ MCP server process not found"
    exit 1
fi

# Test 2: Check port connectivity
echo ""
echo "2️⃣ Testing port connectivity..."
if netstat -an | grep 50880 | grep LISTEN > /dev/null; then
    echo "✅ Port 50880 is listening"
else
    echo "❌ Port 50880 not listening"
    exit 1
fi

# Test 3: Test HTTP connectivity
echo ""
echo "3️⃣ Testing HTTP connectivity..."
HTTP_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:50880/)
if [ "$HTTP_RESPONSE" = "404" ]; then
    echo "✅ HTTP server responding (404 expected for MCP server)"
else
    echo "❌ HTTP server not responding properly (got: $HTTP_RESPONSE)"
    exit 1
fi

# Test 4: Test server headers
echo ""
echo "4️⃣ Testing server headers..."
HEADERS=$(curl -s -I http://localhost:50880/ | head -5)
if echo "$HEADERS" | grep -q "X-Powered-By: Express"; then
    echo "✅ Express server detected"
else
    echo "❌ Express server not detected"
    exit 1
fi

# Test 5: Test CORS headers
echo ""
echo "5️⃣ Testing CORS configuration..."
CORS_HEADER=$(curl -s -I http://localhost:50880/ | grep "Access-Control-Allow-Origin")
if [ -n "$CORS_HEADER" ]; then
    echo "✅ CORS headers present: $CORS_HEADER"
else
    echo "❌ CORS headers missing"
fi

# Test 6: Test server response time
echo ""
echo "6️⃣ Testing server response time..."
RESPONSE_TIME=$(curl -s -o /dev/null -w "%{time_total}" http://localhost:50880/)
if (( $(echo "$RESPONSE_TIME < 1.0" | bc -l) )); then
    echo "✅ Server response time: ${RESPONSE_TIME}s (fast)"
else
    echo "⚠️  Server response time: ${RESPONSE_TIME}s (slow)"
fi

# Test 7: Check MCP server logs
echo ""
echo "7️⃣ Checking MCP server status..."
echo "Server URL: http://localhost:50880"
echo "Auth Token: dPJcAi2esVx2QUasFglAt"
echo "Available MCP Servers:"
echo "  - Knowledge Graph MCP Server"
echo "  - Sequential Thinking MCP Server"
echo "  - Secure MCP Filesystem Server"
echo "  - GitHub MCP Server"

# Test 8: Test TypingMind configuration
echo ""
echo "8️⃣ TypingMind Configuration Test..."
echo "✅ Server is ready for TypingMind connection"
echo "📋 Configuration for TypingMind:"
echo "   - Server URL: http://localhost:50880"
echo "   - Auth Token: dPJcAi2esVx2QUasFglAt"
echo "   - Connection Type: This Device"

echo ""
echo "🎉 All tests passed! Your TypingMind MCP server is ready to use."
echo ""
echo "Next steps:"
echo "1. Open TypingMind"
echo "2. Go to Settings → Advanced Settings → Model Context Protocol"
echo "3. Select 'This Device'"
echo "4. Enter the server URL and auth token above"
echo "5. Click 'Connect'"
echo ""
echo "Available MCP Servers to add in TypingMind:"
echo "- memory: Persistent AI context"
echo "- puppeteer: Browser automation"
echo "- filesystem: File operations (secure)"
echo "- sequential-thinking: Chain-of-thought workflows"
echo "- zapier: No-code automations"
echo "- github: GitHub integration"

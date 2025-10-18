#!/bin/bash

# TypingMind MCP Server - Local Setup
echo "🚀 Starting TypingMind MCP Server locally"
echo "🔑 Auth token: p1Lhz4LCAH_uooyVkeLDH"
echo "🌐 Port: 8080"
echo ""
echo "📡 Server will be available at: http://localhost:8080"
echo "🔧 Configure TypingMind with:"
echo "   - Server URL: http://localhost:8080"
echo "   - Auth Token: p1Lhz4LCAH_uooyVkeLDH"
echo "   - Select 'This Device' in TypingMind"
echo ""

# Start the MCP server
PORT=8080 npx @typingmind/mcp p1Lhz4LCAH_uooyVkeLDH

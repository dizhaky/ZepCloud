#!/bin/bash
set -e

echo "🚀 Starting TypingMind MCP Server"
echo "🔑 Auth token: $AUTH_TOKEN"
echo "🌐 Port: $PORT"

# Set default values
export PORT=${PORT:-8080}
export AUTH_TOKEN=${AUTH_TOKEN:-p1Lhz4LCAH_uooyVkeLDH}

echo "Running: PORT=$PORT npx @typingmind/mcp $AUTH_TOKEN"
exec npx @typingmind/mcp $AUTH_TOKEN

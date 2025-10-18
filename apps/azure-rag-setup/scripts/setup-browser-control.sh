#!/bin/bash
# Browser Control Setup Script
# This script sets up browser control capabilities for the project

set -e

echo "🚀 Setting up Browser Control Capabilities"
echo "=========================================="

# Check if chrome-devtools-mcp is installed
if ! npm list -g chrome-devtools-mcp &>/dev/null; then
    echo "📦 Installing chrome-devtools-mcp..."
    npm install -g chrome-devtools-mcp
    echo "✅ chrome-devtools-mcp installed"
else
    echo "✅ chrome-devtools-mcp already installed"
fi

# Check if Comet is available
if [ -f "/Applications/Comet.app/Contents/MacOS/Comet" ]; then
    echo "✅ Comet browser found"
    BROWSER="Comet"
    BROWSER_PATH="/Applications/Comet.app/Contents/MacOS/Comet"
elif [ -f "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
    echo "✅ Chrome browser found"
    BROWSER="Chrome"
    BROWSER_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
else
    echo "❌ No supported browser found"
    exit 1
fi

echo ""
echo "🔧 Browser Control Configuration:"
echo "   Browser: $BROWSER"
echo "   Path: $BROWSER_PATH"
echo "   Debug Port: 9222"

echo ""
echo "📚 Documentation available:"
echo "   - .cursor/rules/browser-control-settings.md"
echo "   - docs/agent-browser-control-guide.md"
echo "   - .cursor/commands/agent-instructions.md"
echo "   - docs/agent-capabilities.md"

echo ""
echo "🎯 Quick Start Commands:"
echo "   Start browser: $BROWSER_PATH --remote-debugging-port=9222"
echo "   Test connection: curl -s http://localhost:9222/json/version"
echo "   Use MCP server: BROWSER=\"$BROWSER\" CHROME_DEBUG_PORT=\"9222\" npx chrome-devtools-mcp@latest --isolated"

echo ""
echo "✅ Browser Control Setup Complete!"

#!/bin/bash
# Start Browser with Debugging
# This script starts the browser with debugging enabled

set -e

PORT=${1:-9222}
BROWSER=${2:-Comet}

echo "🌐 Starting $BROWSER with debugging on port $PORT"

case $BROWSER in
    "Comet")
        if [ -f "/Applications/Comet.app/Contents/MacOS/Comet" ]; then
            /Applications/Comet.app/Contents/MacOS/Comet --remote-debugging-port=$PORT &
            echo "✅ Comet started with debugging on port $PORT"
        else
            echo "❌ Comet not found"
            exit 1
        fi
        ;;
    "Chrome")
        if [ -f "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
            /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=$PORT --user-data-dir=/tmp/chrome-debug --no-first-run --no-default-browser-check &
            echo "✅ Chrome started with debugging on port $PORT"
        else
            echo "❌ Chrome not found"
            exit 1
        fi
        ;;
    *)
        echo "❌ Unsupported browser: $BROWSER"
        echo "Supported browsers: Comet, Chrome"
        exit 1
        ;;
esac

echo ""
echo "🔧 Debug Information:"
echo "   Port: $PORT"
echo "   Browser: $BROWSER"
echo "   Test: curl -s http://localhost:$PORT/json/version"
echo "   WebSocket: ws://localhost:$PORT/devtools/browser/"

echo ""
echo "🎯 Next steps:"
echo "   1. Test connection: curl -s http://localhost:$PORT/json/version"
echo "   2. Use MCP server: BROWSER=\"$BROWSER\" CHROME_DEBUG_PORT=\"$PORT\" npx chrome-devtools-mcp@latest --isolated"

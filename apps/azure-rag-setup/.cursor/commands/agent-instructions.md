# Agent Instructions

## Browser Control Capabilities

This agent has browser control capabilities configured:

- **Default browser**: Comet (ai.perplexity.comet)
- **User profile**: Full authenticated access
- **Debug port**: 9222 (configurable)
- **MCP server**: chrome-devtools-mcp@0.8.1

## Usage Commands

### Start Browser Debugging

```bash
# Start Comet with debugging
/Applications/Comet.app/Contents/MacOS/Comet --remote-debugging-port=9222

# Start Chrome with debugging
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug --no-first-run --no-default-browser-check
```

### Test Connection

```bash
# Test DevTools connection
curl -s http://localhost:9222/json/version

# Get WebSocket debugger URL
curl -s http://localhost:9222/json | jq -r '.[0].webSocketDebuggerUrl'
```

### Use MCP Server

```bash
# Configure for Comet
BROWSER="Comet" BROWSER_PATH="/Applications/Comet.app/Contents/MacOS/Comet" CHROME_DEBUG_PORT="9222" npx chrome-devtools-mcp@latest --isolated

# Configure for Chrome
BROWSER="Chrome" BROWSER_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" CHROME_DEBUG_PORT="9222" npx chrome-devtools-mcp@latest --isolated
```

## Capabilities

### Browser Control

- Navigate to authenticated websites
- Access user credentials and saved data
- Interact with logged-in services
- Fill forms with user information
- Control browser tabs and windows
- Execute actions as authenticated user

### Technical Features

- Take screenshots
- Execute JavaScript
- Inspect page elements
- Monitor network requests
- Debug web applications
- Automate user workflows

## Security Notes

- 🔒 User credentials are preserved and secure
- 🔒 AI can only control browser, not access passwords directly
- 🔒 All actions performed as authenticated user
- 🔒 Existing login sessions remain intact

## Quick Start

1. **Check browser status**: `ps aux | grep -i comet`
2. **Start debugging**: `/Applications/Comet.app/Contents/MacOS/Comet --remote-debugging-port=9222`
3. **Test connection**: `curl -s http://localhost:9222/json/version`
4. **Begin control**: Use MCP server for browser automation

## Documentation

- **Settings**: `.cursor/browser-control-settings.md`
- **Guide**: `.cursor/agent-browser-control-guide.md`
- **Capabilities**: `.cursor/agent-capabilities.md`

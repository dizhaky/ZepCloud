# Browser Control Settings

## Overview

This document contains the browser control capabilities and settings for the Cursor project template.

## Browser Control with User Credentials

### Default System Browser

- **Browser**: Comet (ai.perplexity.comet)
- **User Profile**: Full access to existing browser sessions
- **Credentials**: Login sessions, cookies, and saved data preserved
- **Process Status**: Comet running with user profile (PID 1911)

### Control Capabilities

- ✅ Navigate to authenticated websites (Gmail, GitHub, social media)
- ✅ Access saved passwords and autofill data
- ✅ Interact with logged-in services as authenticated user
- ✅ Fill forms with saved personal information
- ✅ Access bookmarks and browsing history
- ✅ Control tabs and windows
- ✅ Execute actions as authenticated user

### Technical Implementation

- **Chrome DevTools Protocol**: Active on port 9222/9223
- **WebSocket Debugger**: Available for real-time control
- **MCP Server**: chrome-devtools-mcp@0.8.1 configured
- **Browser Automation**: Ready for Cursor IDE integration

### Security Notes

- 🔒 Credentials stored in browser profile (secure)
- 🔒 AI can only control browser, not access passwords directly
- 🔒 All actions performed as authenticated user
- 🔒 Existing login sessions remain intact

## Usage Commands

### Start Browser with Debugging

```bash
# Start Comet with debugging enabled
/Applications/Comet.app/Contents/MacOS/Comet --remote-debugging-port=9222 --user-data-dir="$HOME/Library/Application Support/Comet"

# Start Chrome with debugging enabled
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug --no-first-run --no-default-browser-check
```

### Control via MCP Server

```bash
# Configure for Comet
BROWSER="Comet" BROWSER_PATH="/Applications/Comet.app/Contents/MacOS/Comet" CHROME_DEBUG_PORT="9222" npx chrome-devtools-mcp@latest --isolated

# Configure for Chrome
BROWSER="Chrome" BROWSER_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" CHROME_DEBUG_PORT="9222" npx chrome-devtools-mcp@latest --isolated
```

### Test Browser Control

```bash
# Test DevTools connection
curl -s http://localhost:9222/json/version

# Get WebSocket debugger URL
curl -s http://localhost:9222/json | jq -r '.[0].webSocketDebuggerUrl'
```

## MCP Configuration

### Chrome DevTools MCP Server

```json
{
  "chrome-devtools": {
    "command": "npx",
    "args": ["chrome-devtools-mcp@latest", "--isolated"],
    "env": {
      "BROWSER": "Comet",
      "BROWSER_PATH": "/Applications/Comet.app/Contents/MacOS/Comet",
      "CHROME_DEBUG_PORT": "9222",
      "CHROME_HEADLESS": "false"
    }
  }
}
```

## Available Browser Control Features

### Navigation

- Navigate to any URL
- Open new tabs and windows
- Control browser history

### Interaction

- Click elements
- Type text
- Scroll pages
- Fill forms

### Inspection

- Take screenshots
- Inspect elements
- Monitor network requests
- Debug JavaScript

### Automation

- Execute JavaScript
- Control page interactions
- Automate user workflows
- Test web applications

## Security Considerations

1. **Credential Access**: Browser control uses existing authenticated sessions
2. **Profile Isolation**: Each debugging session can use separate profiles
3. **Permission Scope**: AI can only control browser, not access system credentials
4. **Session Persistence**: Existing login sessions remain intact

## Troubleshooting

### Common Issues

- **Port conflicts**: Use different ports (9222, 9223, 9224, etc.)
- **Profile access**: Ensure correct user-data-dir path
- **Permission errors**: Run with appropriate user permissions

### Debug Commands

```bash
# Check running browsers
ps aux | grep -i comet

# Test DevTools connection
curl -s http://localhost:9222/json/version

# List available tabs
curl -s http://localhost:9222/json
```

## Integration with Cursor IDE

The browser control capabilities are fully integrated with Cursor IDE through:

- MCP server configuration
- Chrome DevTools Protocol
- Real-time browser automation
- AI-powered web interaction

This enables seamless browser control within the Cursor development environment.

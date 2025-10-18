# Agent Browser Control Guide

## How to Tell Cursor Agents About Browser Control

This guide explains how to inform other Cursor agents about browser control capabilities and how to use them effectively.

## Quick Reference for Agents

### Browser Control Capabilities

```markdown
I can control the browser with user credentials:

- Default browser: Comet (ai.perplexity.comet)
- User profile access: Full authenticated sessions
- Credentials preserved: Login sessions, cookies, saved data
- Control methods: Chrome DevTools Protocol + MCP server
```

### Agent Instructions

```markdown
To enable browser control for this agent:

1. Check if chrome-devtools-mcp is installed: `npm list -g chrome-devtools-mcp`
2. Start browser with debugging: `/Applications/Comet.app/Contents/MacOS/Comet --remote-debugging-port=9222`
3. Test connection: `curl -s http://localhost:9222/json/version`
4. Use MCP server: `npx chrome-devtools-mcp@latest --isolated`
```

## Agent Communication Templates

### For New Agents

````markdown
## Browser Control Available

This project has browser control capabilities configured:

- **Browser**: Comet with user credentials
- **Debug Port**: 9222 (configurable)
- **MCP Server**: chrome-devtools-mcp@0.8.1
- **User Sessions**: Authenticated access to logged-in services

### Usage

```bash
# Start browser with debugging
/Applications/Comet.app/Contents/MacOS/Comet --remote-debugging-port=9222

# Control via MCP
BROWSER="Comet" CHROME_DEBUG_PORT="9222" npx chrome-devtools-mcp@latest --isolated
```
````

### Capabilities

- Navigate to authenticated websites
- Access saved passwords and autofill
- Interact with logged-in services
- Fill forms with user data
- Control tabs and windows
- Execute actions as authenticated user

````

### For Existing Agents
```markdown
## Browser Control Status

✅ **Browser Control**: Available and configured
✅ **User Credentials**: Full access to authenticated sessions
✅ **MCP Server**: chrome-devtools-mcp ready
✅ **Debug Protocol**: Chrome DevTools Protocol active

### Quick Start
1. Check browser status: `ps aux | grep -i comet`
2. Start debugging: `/Applications/Comet.app/Contents/MacOS/Comet --remote-debugging-port=9222`
3. Test connection: `curl -s http://localhost:9222/json/version`
4. Begin control: Use MCP server for browser automation
````

## Agent Configuration Files

### .cursor/agent-instructions.md

````markdown
# Agent Instructions

## Browser Control

This agent has browser control capabilities:

- Default browser: Comet
- User profile: Full authenticated access
- Debug port: 9222
- MCP server: chrome-devtools-mcp

## Usage Commands

```bash
# Start browser debugging
/Applications/Comet.app/Contents/MacOS/Comet --remote-debugging-port=9222

# Test connection
curl -s http://localhost:9222/json/version

# Use MCP server
BROWSER="Comet" CHROME_DEBUG_PORT="9222" npx chrome-devtools-mcp@latest --isolated
```
````

## Capabilities

- Navigate to authenticated websites
- Access user credentials and saved data
- Interact with logged-in services
- Control browser tabs and windows
- Execute actions as authenticated user

````

### .cursor/agent-capabilities.md
```markdown
# Agent Capabilities

## Browser Control
- **Status**: Available and configured
- **Browser**: Comet with user credentials
- **Authentication**: Full access to logged-in sessions
- **Control**: Chrome DevTools Protocol + MCP server
- **Security**: User credentials preserved and secure

## Available Actions
- Navigate to any URL
- Access authenticated websites
- Fill forms with user data
- Control browser interactions
- Take screenshots
- Execute JavaScript
- Monitor network requests
- Debug web applications
````

## Agent Communication Methods

### 1. Direct Instructions

```markdown
## Browser Control Available

I can control the browser with your credentials:

- Browser: Comet (your default)
- User sessions: Authenticated access
- Control method: Chrome DevTools Protocol
- MCP server: chrome-devtools-mcp

To use: Start browser with debugging, then use MCP server for control.
```

### 2. Configuration Sharing

```markdown
## Project Browser Control

This project has browser control configured:

- MCP server: chrome-devtools-mcp@0.8.1
- Browser: Comet with user profile
- Debug port: 9222
- User credentials: Preserved and accessible

See .cursor/browser-control-settings.md for details.
```

### 3. Quick Setup Commands

````markdown
## Browser Control Setup

```bash
# Install MCP server
npm install -g chrome-devtools-mcp

# Start browser with debugging
/Applications/Comet.app/Contents/MacOS/Comet --remote-debugging-port=9222

# Test connection
curl -s http://localhost:9222/json/version

# Use MCP server
BROWSER="Comet" CHROME_DEBUG_PORT="9222" npx chrome-devtools-mcp@latest --isolated
```
````

````

## Agent Handoff Templates

### For Project Transfer
```markdown
## Browser Control Capabilities

This project includes browser control:
- **Status**: Configured and ready
- **Browser**: Comet with user credentials
- **MCP Server**: chrome-devtools-mcp@0.8.1
- **Debug Port**: 9222 (configurable)
- **User Sessions**: Full authenticated access

### Quick Start
1. Check browser: `ps aux | grep -i comet`
2. Start debugging: `/Applications/Comet.app/Contents/MacOS/Comet --remote-debugging-port=9222`
3. Test: `curl -s http://localhost:9222/json/version`
4. Control: Use MCP server for browser automation

### Documentation
- Settings: `.cursor/browser-control-settings.md`
- Capabilities: `.cursor/agent-capabilities.md`
- Instructions: `.cursor/agent-instructions.md`
````

### For Agent Collaboration

```markdown
## Browser Control Status

✅ **Available**: Browser control with user credentials
✅ **Configured**: MCP server and debug protocol
✅ **Ready**: Can control browser with authenticated sessions
✅ **Documented**: Complete setup and usage instructions

### Usage

- Start browser with debugging
- Use MCP server for control
- Access authenticated websites
- Interact with logged-in services
```

## Agent Memory Integration

### For Byterover MCP

````markdown
## Browser Control Knowledge

This project has browser control capabilities:

- Default browser: Comet with user credentials
- MCP server: chrome-devtools-mcp@0.8.1
- Debug protocol: Chrome DevTools Protocol
- User sessions: Authenticated access preserved

### Usage Commands

```bash
# Start browser debugging
/Applications/Comet.app/Contents/MacOS/Comet --remote-debugging-port=9222

# Test connection
curl -s http://localhost:9222/json/version

# Use MCP server
BROWSER="Comet" CHROME_DEBUG_PORT="9222" npx chrome-devtools-mcp@latest --isolated
```
````

### Capabilities

- Navigate to authenticated websites
- Access user credentials and saved data
- Interact with logged-in services
- Control browser tabs and windows
- Execute actions as authenticated user

````

## Agent Testing

### Verification Commands
```bash
# Check browser status
ps aux | grep -i comet

# Test debug connection
curl -s http://localhost:9222/json/version

# Verify MCP server
npx chrome-devtools-mcp@latest --help

# Check project configuration
ls -la .cursor/browser-control-settings.md
````

### Success Indicators

- ✅ Browser running with debugging
- ✅ DevTools protocol responding
- ✅ MCP server available
- ✅ User sessions accessible
- ✅ Browser control functional

## Troubleshooting

### Common Issues

- **Port conflicts**: Use different ports (9222, 9223, 9224)
- **Permission errors**: Check browser permissions
- **MCP server issues**: Reinstall chrome-devtools-mcp
- **Connection failures**: Restart browser with debugging

### Debug Commands

```bash
# Check running processes
ps aux | grep -i comet

# Test debug connection
curl -s http://localhost:9222/json/version

# List available tabs
curl -s http://localhost:9222/json

# Test MCP server
npx chrome-devtools-mcp@latest --help
```

## Summary

This guide provides comprehensive instructions for:

- Informing other Cursor agents about browser control
- Sharing configuration and capabilities
- Providing quick setup commands
- Enabling agent collaboration
- Troubleshooting common issues

Use these templates and instructions to ensure all Cursor agents understand and can utilize browser control capabilities.

# TypingMind MCP Server - Local Setup

A local Model Context Protocol (MCP) server for TypingMind running on your Mac.

## 🚀 Quick Start

### Start the Server

```bash

# Option 1: Using npm script

npm start

# Option 2: Using shell script

./start-mcp.sh

# Option 3: Direct command

PORT=8080 npx @typingmind/mcp p1Lhz4LCAH_uooyVkeLDH

```

## 🔧 Configure TypingMind

1. **Open TypingMind** → **Settings** → **Advanced Settings** → **Model Context Protocol**
2. **Select "This Device"** (not Remote Server)
3. **Server should auto-detect** or manually enter:
   - **Server URL**: `http://localhost:8080`
   - **Auth Token**: `p1Lhz4LCAH_uooyVkeLDH`
4. **Click "Connect"**

## 📋 Add MCP Servers

Once connected, click **"Edit Servers"** and add this JSON:

```json

{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "zapier": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-zapier"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    }
  }
}

```

## 🎯 Available MCP Servers

- **memory**: Persistent AI context and memory
- **puppeteer**: Browser automation and web scraping
- **filesystem**: File system access (use carefully)
- **sequential-thinking**: Chain-of-thought workflows
- **zapier**: No-code automation integrations
- **github**: GitHub API integration

## 🔒 Security Notes

- The `filesystem` server has access to your local files - use with caution
- Keep your auth token secure
- The server runs locally, so it's only accessible from your Mac

## 🛠️ Troubleshooting

- **Server not starting**: Make sure port 8080 is not in use
- **TypingMind can't connect**: Ensure you selected "This Device" not "Remote Server"
- **MCP servers not loading**: Check the JSON syntax in "Edit Servers"

## 📊 Server Status

- **URL**: http://localhost:8080
- **Auth Token**: p1Lhz4LCAH_uooyVkeLDH
- **Status**: Check terminal output for "MCP runner server running"

## 🚀 Benefits of Local Setup

- ✅ **Fast**: No network latency
- ✅ **Secure**: Runs on your machine only
- ✅ **Reliable**: No external dependencies
- ✅ **Free**: No cloud hosting costs
- ✅ **Full Control**: Complete access to all features

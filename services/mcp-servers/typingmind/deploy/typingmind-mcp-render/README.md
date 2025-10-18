# TypingMind MCP Server for Render.com

A Model Context Protocol (MCP) server designed for TypingMind, deployed on Render.com.

## 🚀 Deploy to Render.com

### Option 1: Render Dashboard

1. Go to [render.com](https://render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Use these settings:
   - **Build Command**: `npm install`
   - **Start Command**: `npm start`
   - **Environment**: Node.js

### Option 2: Render CLI

```bash
# Install Render CLI
npm install -g @render/cli

# Login to Render
render login

# Deploy
render deploy
```

## 🔧 Environment Variables

Set these in Render dashboard:

- `AUTH_TOKEN`: `p1Lhz4LCAH_uooyVkeLDH`
- `NODE_ENV`: `production`
- `PORT`: `10000` (Render sets this automatically)

## 📡 TypingMind Configuration

1. **Open TypingMind** → **Settings** → **Advanced Settings** → **Model Context Protocol**
2. **Select "Remote Server"**
3. **Enter your Render URL**: `https://your-app-name.onrender.com`
4. **Enter Auth Token**: `p1Lhz4LCAH_uooyVkeLDH`

## 📋 MCP Servers JSON

Add this to TypingMind's "Edit Servers":

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

## 🔒 Security

- Keep your AUTH_TOKEN secure
- Render provides HTTPS automatically
- Monitor your Render app logs for security

## 📊 Monitoring

Render provides built-in monitoring:

- Logs: Available in Render dashboard
- Metrics: CPU, Memory, Network usage
- Alerts: Configure in Render dashboard

# 🚀 Deploy TypingMind MCP Server to Render.com

## Quick Deployment Steps

### 1. Go to Render.com

- Visit: https://render.com
- Sign up/Login with your GitHub account

### 2. Create New Web Service

- Click **"New"** → **"Web Service"**
- Connect your GitHub account
- Select repository: `dizhaky/typingmind-mcp-render`

### 3. Configure Service

Use these exact settings:

**Basic Settings:**

- **Name**: `typingmind-mcp-server`
- **Environment**: `Node`
- **Region**: `Oregon (US West)`
- **Branch**: `main`
- **Root Directory**: (leave empty)

**Build & Deploy:**

- **Build Command**: `npm install`
- **Start Command**: `npm start`

**Advanced Settings:**

- **Plan**: `Free`
- **Auto-Deploy**: `Yes`

### 4. Set Environment Variables

In the Render dashboard, go to **Environment** tab and add:

| Key          | Value                   |
| ------------ | ----------------------- |
| `AUTH_TOKEN` | `p1Lhz4LCAH_uooyVkeLDH` |
| `NODE_ENV`   | `production`            |
| `PORT`       | `10000`                 |

### 5. Deploy

- Click **"Create Web Service"**
- Wait for deployment (2-3 minutes)
- You'll get a URL like: `https://typingmind-mcp-server.onrender.com`

### 6. Configure TypingMind

Once deployed, configure TypingMind:

1. **Open TypingMind** → **Settings** → **Advanced Settings** → **Model Context Protocol**
2. **Select "Remote Server"**
3. **Enter your Render URL**: `https://typingmind-mcp-server.onrender.com`
4. **Enter Auth Token**: `p1Lhz4LCAH_uooyVkeLDH`
5. **Click "Connect"**

### 7. Add MCP Servers

Once connected, click **"Edit Servers"** and add:

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

## ✅ Success!

Your TypingMind MCP server will be running on Render.com with all the MCP plugins available!

## 🔧 Troubleshooting

- If deployment fails, check the logs in Render dashboard
- Make sure all environment variables are set correctly
- The free plan has some limitations but should work for MCP servers

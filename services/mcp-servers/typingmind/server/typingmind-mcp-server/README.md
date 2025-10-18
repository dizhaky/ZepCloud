# TypingMind MCP Server for Railway

A Model Context Protocol (MCP) server designed for TypingMind, deployed on Railway.

## 🚀 Quick Deploy to Railway

### Option 1: Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Deploy from this directory
railway up
```

### Option 2: Railway Dashboard

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub repository
5. Railway will auto-detect Node.js and deploy

## 🔧 Configuration

### Environment Variables

Set these in Railway dashboard:

- `PORT`: Railway sets this automatically
- `NODE_ENV`: Set to `production`
- `MCP_AUTH_TOKEN`: Your secure authentication token
- `MCP_SERVER_URL`: Your Railway app URL (auto-generated)

### TypingMind Configuration

1. Open TypingMind Settings
2. Go to Advanced Settings → Model Context Protocol
3. Select "Remote Server"
4. Enter your Railway app URL: `https://your-app.railway.app`
5. Enter your auth token

## 📡 Endpoints

- `GET /health` - Health check
- `GET /mcp` - MCP server info

## 🛠️ Local Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

## 🔒 Security

- Use strong, random auth tokens
- Railway handles HTTPS automatically
- Monitor your Railway app logs for security

## 📊 Monitoring

Railway provides built-in monitoring:

- Logs: Available in Railway dashboard
- Metrics: CPU, Memory, Network usage
- Alerts: Configure in Railway dashboard

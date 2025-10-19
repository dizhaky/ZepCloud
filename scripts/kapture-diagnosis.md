# Kapture MCP Server Diagnosis

## 🔍 Issue Analysis

Based on the MCP logs, Kapture MCP server is experiencing connection issues:

```

2025-10-19 11:56:07.256 [error] No server info found
2025-10-19 11:56:07.259 [error] No server info found

```

## ✅ Current Status

**Kapture MCP is configured correctly** in `.cursor/mcp.json`:

```json

{
  "kapture": {
    "command": "npx",
    "args": ["-y", "@kapture/mcp"],
    "env": {
      "BROWSER": "chrome",
      "AUTO_ACTIVATE": "true",
      "PERSISTENT": "true",
      "AUTO_RECOVER": "true"
    }
  }
}

```

## 🔧 Root Cause

The "No server info found" errors indicate that **Kapture MCP requires the Kapture browser extension** to be installed
  and active.

## 🛠️ Solution Steps

### 1. Install Kapture Browser Extension

## Chrome:

- Visit: https://chrome.google.com/webstore/detail/kapture
- Click "Add to Chrome"
- Enable the extension

## Edge:

- Visit: https://microsoftedge.microsoft.com/addons/detail/kapture
- Click "Get"
- Enable the extension

### 2. Restart Cursor

After installing the extension:

1. Close Cursor completely
2. Reopen Cursor
3. Wait for MCP servers to reconnect

### 3. Test Kapture MCP

Run the health check:

```bash

npm run mcp:health

```

Expected result:

```

| Kapture | ✅ Working | Browser automation configured |

```

### 4. Test Browser Automation

Once working, you can test:

```typescript

// List browser tabs
mcp_kapture_list_tabs()

// Create new tab
mcp_kapture_new_tab()

// Navigate to URL
mcp_kapture_navigate({ tabId: "tab-id", url: "https://example.com" })

```

## 🔄 Alternative Solutions

If Kapture continues to have issues, consider these alternatives:

### Option 1: Playwright MCP

```json

{
  "playwright": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-playwright"]
  }
}

```

### Option 2: Puppeteer MCP

```json

{
  "puppeteer": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
  }
}

```

### Option 3: Selenium MCP

```json

{
  "selenium": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-selenium"]
  }
}

```

## 📊 Current MCP Status

| Server | Status | Issue |
|--------|--------|-------|
| ByteRover | ✅ Working | None |
| Git | ✅ Working | None |
| Task Master | ✅ Working | None |
| Kapture | ⚠️ Extension Required | Needs browser extension |
| GitKraken | ✅ Working | None |
| Memory | ✅ Working | None |
| Filesystem | ✅ Working | None |
| GitHub | ⚠️ Needs Token | Needs GitHub token |

## 🎯 Next Steps

1. **Install Kapture browser extension**
2. **Restart Cursor**
3. **Run health check**: `npm run mcp:health`
4. **Test browser automation**

Once the extension is installed, Kapture MCP will work perfectly for browser automation tasks!

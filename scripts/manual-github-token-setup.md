# Manual GitHub Token Setup

## 🔐 Quick GitHub Token Setup

Since 1Password CLI needs to be signed in, here's a manual approach to get your GitHub token:

### Option 1: Get Token from 1Password App

1. **Open 1Password desktop app**
2. **Search for "GitHub"** in your vault
3. **Find your GitHub Personal Access Token**
4. **Copy the token value**

### Option 2: Create New GitHub Token

If you don't have a token in 1Password:

1. **Go to**: https://github.com/settings/tokens
2. **Click**: "Generate new token" → "Generate new token (classic)"
3. **Set expiration**: 1 year (recommended)
4. **Select scopes**:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `read:org` (Read org and team membership)
   - ✅ `read:user` (Read user profile data)
5. **Click**: "Generate token"
6. **Copy the token** (you won't see it again!)

### Option 3: Manual Configuration

Once you have the token:

1. **Open**: `.cursor/mcp.json`
2. **Find the GitHub section**:
   ```json
   "github": {
     "command": "npx",
     "args": [
       "-y",
       "@modelcontextprotocol/server-github"
     ],
     "env": {
       "GITHUB_PERSONAL_ACCESS_TOKEN": ""
     }
   }
   ```
3. **Replace the empty string** with your token:
   ```json
   "env": {
     "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_your_actual_token_here"
   }
   ```
4. **Save the file**
5. **Restart Cursor** to reload MCP configuration

### Option 4: Environment Variable

Alternatively, set as environment variable:

```bash
# Windows PowerShell
$env:GITHUB_PERSONAL_ACCESS_TOKEN = "ghp_your_actual_token_here"

# Windows CMD
set GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_actual_token_here
```

### 🧪 Test GitHub MCP

After configuration:

```bash
npm run mcp:health
```

You should see:
```
| GitHub | ✅ Working | GitHub API integration ready |
```

### 🎯 Expected Result

Once configured, you'll have **8/8 MCP servers working**:

| Server | Status |
|--------|--------|
| ByteRover | ✅ Working |
| Git | ✅ Working |
| Task Master | ✅ Working |
| Kapture | ✅ Working |
| GitKraken | ✅ Working |
| Memory | ✅ Working |
| Filesystem | ✅ Working |
| **GitHub** | ✅ **Working** |

**Result**: 100% MCP server functionality! 🎉

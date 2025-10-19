# Cursor IDE Troubleshooting

## Serialization Error Fix

**Error**: `ConnectError: [internal] Serialization error in aiserver.v1.StreamUnifiedChatRequestWithTools`

### Quick Fixes (Try in Order)

#### 1. Restart Cursor IDE
- Close all Cursor windows
- Reopen and retry

#### 2. Reduce Context (Temporary)
Run these commands in PowerShell:
```powershell
# Temporarily disable YOLO mode
code .cursor/settings.json
# Set cursor.yoloMode to false
```

#### 3. Disable Some MCP Servers Temporarily
Edit `.cursor/mcp.json`:
- Comment out Kapture (largest) temporarily
- Keep only GitKraken and ByteRover active

#### 4. Clear Cursor Cache
```powershell
# Close Cursor first, then run:
Remove-Item -Recurse -Force "$env:APPDATA\Cursor\Cache"
Remove-Item -Recurse -Force "$env:APPDATA\Cursor\CachedData"
```

#### 5. Simplify Workspace Rules (Last Resort)
Temporarily move some `.mdc` files:
```powershell
# Create backup
mkdir .cursor\rules\backup
Move-Item .cursor\rules\azure-integration.mdc .cursor\rules\backup\
Move-Item .cursor\rules\mcp-servers.mdc .cursor\rules\backup\
```

### Root Causes

1. **Too many MCP tools** - 50+ tools from multiple servers
2. **Large workspace rules** - 1,930 lines across multiple files
3. **Complex git status** - Many unstaged changes increase context
4. **Large project** - Multiple apps and services

### Prevention

1. **Commit or stash changes** regularly to reduce git status context
2. **Only enable needed MCP servers** for current task
3. **Use specific queries** instead of broad requests
4. **Close unnecessary files** in IDE

### If Nothing Works

1. Create minimal test workspace
2. Report bug to Cursor support with:
   - Error message
   - MCP server list
   - Workspace size
   - Cursor version

### Recommended Configuration

For large projects like ZepCloud, use:
```json
{
  "cursor.agent.maxContextFiles": 10,
  "cursor.ai.maxContextLines": 5000,
  "cursor.mcp.maxToolsPerRequest": 20
}
```

This prevents context overload while maintaining functionality.


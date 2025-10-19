# MCP Health Check Guide

## Overview

This guide explains how to test and verify that all MCP (Model Context Protocol) servers are working correctly in the ZepCloud project.

## Quick Start

### Automatic Health Check

Run the health check script:

```bash
# Using npm script
npm run mcp:health

# Or directly with Node.js
node scripts/mcp-health-check.js
```

### Manual Health Check

Test each MCP server individually in Cursor:

1. **ByteRover Knowledge Management**
   ```typescript
   mcp_byterover-mcp_byterover-retrieve-knowledge({ query: "test", limit: 1 })
   mcp_byterover-mcp_byterover-store-knowledge({ messages: "Health check" })
   ```

2. **Git Operations**
   ```typescript
   mcp_git_git_status({ repo_path: "." })
   ```

3. **Task Management**
   ```typescript
   mcp_task-master-ai_get_tasks({ projectRoot: "C:\\Dev\\ZepCloud" })
   ```

4. **Browser Automation**
   ```typescript
   mcp_kapture_list_tabs({})
   ```

5. **Memory System**
   ```typescript
   // Test memory operations if available
   ```

6. **Filesystem Access**
   ```typescript
   list_dir({ target_directory: "." })
   ```

7. **GitHub Integration**
   ```typescript
   // Test GitHub operations if token configured
   ```

## Expected Results

### ✅ All Servers Working

```
## MCP Server Health Check Results

| Server | Status | Notes |
|--------|--------|-------|
| ByteRover | ✅ Working | Knowledge retrieval/storage functional |
| Git | ✅ Working | Repository operations available |
| Task Master | ✅ Working | Task management functional |
| Kapture | ✅ Working | Browser automation ready |
| Memory | ✅ Working | Session memory available |
| Filesystem | ✅ Working | File operations functional |
| GitHub | ✅ Working | GitHub API integration ready |
```

### ⚠️ Some Servers Need Attention

```
| Server | Status | Notes |
|--------|--------|-------|
| ByteRover | ✅ Working | Knowledge management functional |
| Git | ✅ Working | Repository operations available |
| Task Master | ❌ Failed | Task management not available |
| Kapture | ✅ Working | Browser automation ready |
| Memory | ✅ Working | Session memory available |
| Filesystem | ✅ Working | File operations functional |
| GitHub | ⚠️ Needs Token | Configure GITHUB_PERSONAL_ACCESS_TOKEN |
```

## Troubleshooting

### ByteRover Issues

**Error**: `Memory access requires authentication`

**Solution**:
1. Visit https://byterover.dev
2. Create/login to account
3. Install ByteRover Cursor extension
4. Run "ByteRover: Login" command
5. Restart Cursor

### Git Issues

**Error**: `git command not found`

**Solution**:
1. Install Git: https://git-scm.com/downloads
2. Verify: `git --version`
3. Configure: `git config --global user.name "Your Name"`

### Task Master Issues

**Error**: `task-master-ai not found`

**Solution**:
1. Check `.cursor/mcp.json` configuration
2. Verify `task-master-ai` is in mcpServers
3. Restart Cursor to reload MCP servers

### Kapture Issues

**Error**: `Browser not found`

**Solution**:
1. Install Chrome/Chromium browser
2. Check `BROWSER_PATH` in `.cursor/mcp.json`
3. Update browser path if needed

### Memory Issues

**Error**: `Memory server not responding`

**Solution**:
1. Check memory MCP configuration
2. Verify Node.js is installed
3. Test with: `npx @modelcontextprotocol/server-memory`

### Filesystem Issues

**Error**: `Permission denied`

**Solution**:
1. Check file permissions
2. Verify project path in configuration
3. Run as administrator if needed

### GitHub Issues

**Error**: `GitHub token required`

**Solution**:
1. Generate token: https://github.com/settings/tokens
2. Add to `.cursor/mcp.json`:
   ```json
   "github": {
     "env": {
       "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_your_token_here"
     }
   }
   ```

## Configuration Files

### `.cursor/mcp.json`

Main MCP server configuration:

```json
{
  "mcpServers": {
    "byterover-mcp": {
      "url": "https://mcp.byterover.dev/mcp?machineId=..."
    },
    "git": {
      "command": "npx",
      "args": ["-y", "mcp-git@0.0.4", "--repository", "."]
    },
    "task-master-ai": {
      "command": "npx",
      "args": ["-y", "task-master-ai"]
    },
    "kapture": {
      "command": "npx",
      "args": ["-y", "@kapture/mcp"],
      "env": {
        "BROWSER": "chrome"
      }
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:\\Dev\\ZepCloud"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": ""
      }
    }
  }
}
```

### `scripts/mcp-health-check.js`

Automated health check script that:
- Tests all configured MCP servers
- Reports status and errors
- Provides troubleshooting suggestions
- Generates summary report

## Best Practices

### 1. Run Health Check at Session Start

Always test MCP servers before starting development:

```bash
npm run mcp:health
```

### 2. Monitor Server Status

Check server status regularly:
- After configuration changes
- After Cursor updates
- When experiencing issues

### 3. Keep Configuration Updated

- Update MCP server versions regularly
- Test new servers before adding to production
- Document any custom configurations

### 4. Handle Failures Gracefully

- Continue with available servers
- Document which functionality is unavailable
- Plan workarounds for missing servers

## Integration with Development Workflow

### Pre-Development Checklist

1. ✅ Run MCP health check
2. ✅ Verify all required servers working
3. ✅ Note any unavailable functionality
4. ✅ Plan workarounds if needed

### During Development

- Use working MCP servers for enhanced productivity
- Fall back to standard tools if MCP servers fail
- Report persistent issues for troubleshooting

### Post-Development

- Store knowledge with ByteRover
- Update task status with Task Master
- Commit changes with Git MCP
- Document any new patterns discovered

## Advanced Configuration

### Custom MCP Servers

Add custom servers to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "custom-server": {
      "command": "node",
      "args": ["path/to/custom-server.js"],
      "env": {
        "CUSTOM_VAR": "value"
      }
    }
  }
}
```

### Environment Variables

Set environment variables for MCP servers:

```bash
# Windows
set GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here

# Linux/Mac
export GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here
```

### Debugging MCP Servers

Enable debug logging:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "server-package", "--debug"]
    }
  }
}
```

## References

- [MCP Documentation](https://modelcontextprotocol.io/)
- [ByteRover](https://byterover.dev)
- [Cursor MCP Integration](https://cursor.sh/docs)
- [GitHub Personal Access Tokens](https://github.com/settings/tokens)

---

**Last Updated**: October 19, 2025  
**Version**: 1.0

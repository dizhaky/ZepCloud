# ZepCloud Folder Structure Guide

## Overview

This document explains the reorganized folder structure of the ZepCloud project, designed for better maintainability and logical organization.

## Structure Explanation

### `/apps/` - Core Applications

Contains the main applications and services that form the core of the ZepCloud ecosystem.

- **`zepcloud-core/`**: Main application code (previously in `src/`)
- **`azure-rag-setup/`**: Azure RAG setup and configuration (moved from root)

### `/services/` - External Services

Contains MCP servers and external service implementations.

- **`mcp-servers/typingmind/`**: TypingMind MCP server
  - **`local/`**: Local development setup (previously `typingmind-mcp-local/`)
  - **`server/`**: Server implementation (previously `typingmind-mcp-server/`)
  - **`deploy/`**: Deployment configs (previously `typingmind-mcp-render/`)

### `/tools/` - Development Tools

Contains utility scripts and diagnostic tools.

- **`scripts/`**: Python utility scripts (all `*.py` files moved here)
- **`diagnostics/`**: Diagnostic and troubleshooting tools

### `/docs/` - Documentation

Organized documentation by category.

- **`agents/`**: Agent configuration files (`AGENT.md`, `AGENTS.md`, `CLAUDE.md`)
- **`architecture/`**: System architecture documentation
- **`guides/`**: Setup guides and tutorials (`typingmind-tool-fix.md`)

### `/config/` - Configuration

Project configuration files.

- **`.cursorrules`**: Cursor IDE configuration (moved from `src/`)

## Migration Summary

### Files Moved:

- `src/main.py` → `apps/zepcloud-core/main.py`
- `src/.cursorrules` → `config/.cursorrules`
- `azure-rag-setup/` → `apps/azure-rag-setup/`
- `typingmind-mcp-local/` → `services/mcp-servers/typingmind/local/`
- `typingmind-mcp-server/` → `services/mcp-servers/typingmind/server/`
- `typingmind-mcp-render/` → `services/mcp-servers/typingmind/deploy/`
- `*.py` files → `tools/scripts/`
- `AGENT.md`, `AGENTS.md`, `CLAUDE.md` → `docs/agents/`
- `typingmind-tool-fix.md` → `docs/guides/`

## Benefits of New Structure

1. **Logical Grouping**: Related components are grouped together
2. **Scalability**: Easy to add new applications, services, or tools
3. **Clarity**: Clear separation of concerns
4. **Maintainability**: Easier to find and manage components
5. **Documentation**: Centralized documentation with clear categorization

## Best Practices

When adding new components:

1. **Applications**: Add to `apps/` with descriptive folder names
2. **Services**: Add to `services/` with service-specific subfolders
3. **Tools**: Add to `tools/` with appropriate categorization
4. **Documentation**: Add to `docs/` with proper categorization
5. **Configuration**: Add to `config/` for project-wide settings

## Navigation Tips

- Use the main `README.md` for project overview
- Check individual component READMEs for specific setup instructions
- Refer to `docs/guides/` for detailed tutorials
- Use `docs/agents/` for AI agent configuration

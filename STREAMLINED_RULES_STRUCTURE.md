# Streamlined Rules Structure

## Date

October 19, 2025

## Overview

This document provides a comprehensive overview of the streamlined rules structure for the ZepCloud project. The
  structure has been optimized to eliminate redundancy while maintaining clear organization and easy maintenance.

## Current Structure

### Root Level

- **`.cursorrules`** - Main Kilo Code methodology (1,006 lines)
  - Contains systematic workflow methodology
  - Automation settings (YOLO mode)
  - Code quality standards
  - Testing requirements
  - Browser automation standards
  - ByteRover integration instructions

### Modular Rules Directory (`.cursor/rules/`)

The modular rules are organized by technology stack and purpose:

1. **`byterover-rules.mdc`** - ByteRover MCP integration (24 lines)
   - **Purpose**: Knowledge management and retrieval patterns
   - **When Applied**: Always
   - **Key Features**: Store/Retrieve knowledge guidelines

2. **`python-backend.mdc`** - Python/FastAPI standards (200 lines)
   - **Purpose**: Python backend development standards
   - **When Applied**: `**/*.py` files
   - **Key Features**: Type hints, async/await, SQLAlchemy 2.0, testing

3. **`typescript-frontend.mdc`** - TypeScript/React standards (250 lines)
   - **Purpose**: TypeScript and React frontend standards
   - **When Applied**: `**/*.ts`, `**/*.tsx` files
   - **Key Features**: Strict TypeScript, React hooks, performance optimization

4. **`azure-integration.mdc`** - Azure & ZepCloud patterns (200 lines)
   - **Purpose**: Azure-specific integration patterns
   - **When Applied**: On demand
   - **Key Features**: ZepCloud memory, Azure Search, Microsoft 365 Graph API

5. **`mcp-servers.mdc`** - MCP server development (250 lines)
   - **Purpose**: MCP server development standards
   - **When Applied**: `**/mcp-servers/**/*` files
   - **Key Features**: Server patterns, tool definitions, error handling

### Configuration Files

- **`.cursor/mcp.json`** - MCP server configuration
- **`.cursor/README.md`** - Documentation for the cursor configuration

## Benefits of Current Structure

### ✅ Single Source of Truth

- Root `.cursorrules` contains the main methodology
- Modular files contain technology-specific patterns
- No duplicate content across files

### ✅ Modular Organization

- Specific concerns separated into dedicated files
- Easy to enable/disable specific rule sets
- Clear separation by technology stack

### ✅ Easy Maintenance

- Update once, apply everywhere
- Version control friendly
- Clear file naming and organization

### ✅ Context-Aware Application

- Rules activate based on file type
- Project-specific patterns in dedicated files
- No rule conflicts or duplication

## Rule Application Order

1. **Root `.cursorrules`** (highest priority)
   - Applied to all files
   - Contains general methodology

2. **Modular `.cursor/rules/*.mdc`**
   - Applied based on `globs` pattern
   - Context-specific rules

3. **External integrations** (`.kilocode/rules/`)
   - Tool-specific configurations

## File Type Activation

| File Type | Active Rules |
|-----------|-------------|
| `*.py` | Root + python-backend.mdc + azure-integration.mdc |
| `*.ts`, `*.tsx` | Root + typescript-frontend.mdc |
| `mcp-servers/**/*` | Root + typescript-frontend.mdc + mcp-servers.mdc |
| All files | Root + byterover-rules.mdc |

## Recent Cleanup (October 2025)

### Files Removed

The following redundant files were removed to eliminate duplication:

- `AGENTS.md` (root directory)
- `CLAUDE.md` (root directory)
- `docs/agents/AGENT.md`
- `docs/agents/AGENTS.md`
- `docs/agents/CLAUDE.md`
- `.kilocode/rules/byterover-rules.md`
- `.clinerules/byterover-rules.md`

All removed files contained identical content to `.cursor/rules/byterover-rules.mdc`, which remains as the canonical
  source for ByteRover integration rules.

## Best Practices for Rule Management

### Adding New Rules

1. For general methodology updates: Edit root `.cursorrules`
2. For technology-specific patterns: Edit the appropriate `.mdc` file
3. For new technology stacks: Create a new `.mdc` file with proper frontmatter

### Frontmatter Format for .mdc Files

```yaml

---
description: What this rule file covers
alwaysApply: true/false
globs: ["file/patterns/*.ext"]  # Optional
---

```

## Quick Reference

### Common Tasks

- **Update automation settings**: Edit root `.cursorrules`
- **Add Python pattern**: Edit `.cursor/rules/python-backend.mdc`
- **Add TypeScript pattern**: Edit `.cursor/rules/typescript-frontend.mdc`
- **Add Azure integration**: Edit `.cursor/rules/azure-integration.mdc`
- **Add MCP server pattern**: Edit `.cursor/rules/mcp-servers.mdc`

### For Detailed Information

- **Main Rules**: `.cursorrules` - Complete Kilo Code methodology
- **Technology Patterns**: Individual `.mdc` files
- **Project Documentation**: `docs/` folder

## Verification

- All rule files are properly organized
- No duplicate content exists
- Context-aware application works correctly
- Easy to maintain and update

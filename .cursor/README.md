# Cursor Rules Configuration

## 📁 Structure Overview

This directory contains the Cursor IDE configuration for the ZepCloud project. Rules are organized in a modular, maintainable structure.

```
.cursor/
├── README.md                      ← This file
├── mcp.json                       ← MCP server configuration
└── rules/                         ← Modular rule files
    ├── byterover-rules.mdc        ← ByteRover MCP integration
    ├── python-backend.mdc         ← Python/FastAPI standards
    ├── typescript-frontend.mdc    ← TypeScript/React standards
    ├── azure-integration.mdc      ← Azure & ZepCloud patterns
    └── mcp-servers.mdc            ← MCP server development
```

## 🎯 How Rules Are Applied

Cursor loads rules in this order:

1. **Root `.cursorrules`** (highest priority)
   - Main Kilo Code methodology
   - Automation settings (YOLO mode)
   - General development workflow

2. **Modular `.cursor/rules/*.mdc`** (context-specific)
   - Automatically applied based on file type
   - Can be toggled on/off as needed

3. **Integration rules** (`.kilocode/rules/`)
   - External tool integrations

## 📚 Rule Files

### `byterover-rules.mdc`
**Purpose**: ByteRover MCP knowledge management integration  
**When Applied**: Always  
**Key Features**:
- Store knowledge after completing tasks
- Retrieve knowledge before starting new work
- Pattern recognition and reuse

### `python-backend.mdc`
**Purpose**: Python backend development standards  
**When Applied**: `**/*.py` files  
**Key Features**:
- FastAPI patterns
- SQLAlchemy 2.0 queries
- Type hints and async/await
- Testing with pytest
- Security best practices

### `typescript-frontend.mdc`
**Purpose**: TypeScript and React frontend standards  
**When Applied**: `**/*.ts`, `**/*.tsx` files  
**Key Features**:
- Strict TypeScript (no 'any')
- React hooks and components
- State management patterns
- API integration
- Performance optimization

### `azure-integration.mdc`
**Purpose**: Azure-specific patterns and ZepCloud integration  
**When Applied**: On demand  
**Key Features**:
- ZepCloud memory management
- Azure Search integration
- Microsoft 365 Graph API
- Browser extension patterns
- Error handling and retry logic

### `mcp-servers.mdc`
**Purpose**: MCP server development standards  
**When Applied**: `**/mcp-servers/**/*` files  
**Key Features**:
- Server structure patterns
- Tool definition standards
- Error handling
- Testing strategies
- Deployment configurations

## 🔧 Configuration

### Root `.cursorrules`
Contains the main Kilo Code methodology with:
- Task analysis and planning phases
- Code quality standards
- Testing requirements
- Documentation standards
- Automation settings (auto-accept, auto-save, auto-run)

### Modular Rules (`.mdc` files)
Each `.mdc` file has:
```yaml
---
description: What this rule file covers
alwaysApply: true/false
globs: ["file/patterns/*.ext"]
---
```

## 🎨 Benefits of This Structure

### ✅ Single Source of Truth
- One place to update core methodology (root `.cursorrules`)
- No duplicate content across files

### ✅ Modular Organization
- Specific concerns in separate files
- Easy to enable/disable specific rule sets
- Clear separation by technology stack

### ✅ Easy Maintenance
- Update once, apply everywhere
- Version control friendly
- Clear file naming and organization

### ✅ Context-Aware
- Rules activate based on file type
- Project-specific patterns in dedicated files
- No rule conflicts or duplication

## 📝 Adding New Rules

To add a new modular rule:

1. Create a new `.mdc` file in `.cursor/rules/`
2. Add frontmatter with description, globs, and alwaysApply
3. Document patterns with examples
4. Update this README

Example:
```markdown
---
description: Database migration standards
alwaysApply: false
globs: ["**/migrations/*.py"]
---

# Database Migration Standards

## Patterns
...
```

## 🚀 Quick Reference

### When to Use Which File

| Working On | Active Rules |
|-----------|-------------|
| Python API | Root + python-backend.mdc + azure-integration.mdc |
| React UI | Root + typescript-frontend.mdc |
| MCP Server | Root + typescript-frontend.mdc + mcp-servers.mdc |
| Integration | Root + azure-integration.mdc |

### Common Tasks

**Update automation settings:**
- Edit root `.cursorrules`

**Add Python pattern:**
- Edit `.cursor/rules/python-backend.mdc`

**Add TypeScript pattern:**
- Edit `.cursor/rules/typescript-frontend.mdc`

**Add Azure integration:**
- Edit `.cursor/rules/azure-integration.mdc`

## 📖 Documentation

For detailed methodology, see:
- Root `.cursorrules` - Complete Kilo Code workflow
- Individual `.mdc` files - Technology-specific patterns
- `docs/` folder - Project documentation

---

**Last Updated**: October 2024  
**Maintained By**: Development Team  
**Questions?**: Check the root `.cursorrules` for comprehensive guidance


# Cursor IDE Configuration for Azure RAG Setup

This directory contains comprehensive Cursor IDE configuration files that enable autonomous AI-assisted development with browser automation and systematic workflow methodology.

## 📁 Configuration Files

### Core Configuration

- **`.cursorrules`** - Main rules file with Kilo Code systematic workflow methodology
- **`settings.json`** - Complete Cursor IDE settings with YOLO mode and auto-run everything
- **`mcp.json`** - MCP server configuration with browser automation tools

### Rules Directory

- **`rules/auto-run-everything.mdc`** - Auto-accept and auto-execute configuration
- **`rules/browser-automation-defaults.mdc`** - Browser automation settings
- **`rules/azure-rag-project-context.mdc`** - Project-specific context and guidelines
- **`rules/comprehensive-agent-config.mdc`** - Consolidated agent configuration

## 🚀 Key Features

### Auto-Run Everything (YOLO Mode)

- **Auto-accept all changes** without confirmation dialogs
- **Auto-execute commands** without user approval
- **Auto-save files** with 1-second delay
- **Eliminate "Keep All" button** and confirmation dialogs
- **Silent mode** for continuous operation

### Browser Automation

- **Auto-activate browser** by default
- **Persistent browser sessions** with auto-recovery
- **Comet browser integration** with debug port 9222
- **MCP browser tools** (chrome-devtools, firecrawl, cursor-browser-extension)
- **End-to-end testing** capabilities

### Systematic Workflow (Kilo Code)

- **Context-first analysis** before making changes
- **Incremental development** with validation checkpoints
- **Quality-first implementation** with comprehensive testing
- **Performance-aware development** with optimization
- **Architecture-aware development** following established patterns

### Advanced AI Integration

- **Cline patterns** for systematic problem solving
- **ByteRover integration** for knowledge management
- **Comprehensive testing** with edge case coverage
- **Advanced error handling** with recovery strategies
- **Performance optimization** with built-in monitoring

## 🔧 Configuration Details

### Auto-Accept Settings

```json
{
  "cursor.yoloMode": true,
  "cursor.agent.autoAccept": true,
  "cursor.ai.autoApplyChanges": true,
  "cursor.agent.skipConfirmation": true,
  "cursor.agent.showDiff": false,
  "cursor.agent.showConfirmationDialog": false
}
```

### Auto-Execute Commands

```json
{
  "cursor.agent.autoRunCommands": true,
  "cursor.agent.commandApproval": false,
  "cursor.agent.autoExecuteCommands": true,
  "cursor.terminal.autoApprove": true
}
```

### Browser Automation

```json
{
  "cursor.browser.autoActivate": true,
  "cursor.browser.defaultEnabled": true,
  "cursor.browser.autoStart": true,
  "cursor.browser.persistent": true,
  "cursor.browser.autoRecover": true
}
```

### Auto-Save Configuration

```json
{
  "files.autoSave": "afterDelay",
  "files.autoSaveDelay": 1000,
  "files.autoSaveWhenNoErrors": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll": true,
    "source.organizeImports": true
  }
}
```

## 🎯 Project Context

### Azure RAG Setup Integration

This configuration is specifically designed for the Azure RAG Setup project, which includes:

- **Azure Search** for enterprise search capabilities
- **Microsoft 365 Integration** (SharePoint, Teams, OneDrive, Calendar, Contacts)
- **ZepCloud Memory Management** for persistent AI memory
- **TypingMind Integration** for AI chat interface
- **Railway Backend** at https://dans-knowledge-production.up.railway.app
- **Browser Automation** via Kapture MCP for end-to-end testing

### Development Preferences

1. **Backend Development:** Python with FastAPI
2. **API Integration:** REST endpoints with proper error handling
3. **Memory Management:** ZepCloud integration for all AI features
4. **Code Style:** Follow existing patterns and conventions
5. **Browser Testing:** Comprehensive end-to-end testing

## 🛠️ MCP Server Configuration

### Available Tools

- **Git MCP** - Version control operations
- **Task Master AI** - Task management and project planning
- **Chrome DevTools** - Browser automation and testing
- **Firecrawl** - Web scraping and content extraction
- **Cursor Browser Extension** - Additional browser automation

### Browser Automation Tools

- `mcp_chrome-devtools_browser_navigate` - Navigate to URLs
- `mcp_chrome-devtools_browser_wait_for` - Wait for elements or time
- `mcp_chrome-devtools_browser_snapshot` - Capture accessibility snapshots
- `mcp_chrome-devtools_browser_take_screenshot` - Take screenshots
- `mcp_chrome-devtools_browser_click` - Click elements
- `mcp_chrome-devtools_browser_type` - Type text
- `mcp_chrome-devtools_browser_hover` - Hover over elements
- `mcp_chrome-devtools_browser_select_option` - Select dropdown options
- `mcp_chrome-devtools_browser_press_key` - Press keyboard keys

## 📋 Quality Standards

### Code Quality Requirements

- **Type hints** for all Python functions
- **Async/await** for database operations and API calls
- **Comprehensive error handling** with try/catch blocks
- **Detailed logging** with appropriate log levels
- **Pydantic models** for request/response validation
- **SQLAlchemy 2.0 style** queries

### Testing Standards

- **Unit tests** for all business logic (>80% coverage)
- **Integration tests** for API endpoints
- **End-to-end tests** with browser automation
- **Edge cases and error scenarios** covered
- **Performance tests** for critical paths

### Security Standards

- **Input validation** with Pydantic
- **SQL injection prevention** with parameterized queries
- **File upload security** with type and size checks
- **CORS policies** properly configured
- **Authentication** and authorization implemented

## 🔄 Workflow Process

### 1. Task Analysis & Planning

- Understand requirements completely
- Analyze current state and dependencies
- Decompose into manageable subtasks
- Define success criteria and test strategy

### 2. Execution Guidelines

- Start small with working code
- Follow established patterns
- Write self-documenting code
- Handle errors proactively
- Maintain context awareness

### 3. Testing & Validation

- Unit tests for all functions
- Integration tests for interactions
- Edge cases and error scenarios
- Regression testing

### 4. Refactoring & Optimization

- Measure before optimizing
- Focus on hot paths
- Validate improvements
- Document decisions

### 5. Documentation & Completion

- Code documentation with JSDoc/docstrings
- User documentation with examples
- Developer documentation with setup guides
- Complete checklist verification

## 🎉 Benefits

### Development Efficiency

- **No interruption** from confirmation dialogs
- **Continuous operation** without manual intervention
- **Automatic file saving** prevents data loss
- **Browser always ready** for testing

### Quality Assurance

- **Comprehensive testing** with browser automation
- **Automatic error detection** and fixing
- **Consistent code formatting** and linting
- **Real-time validation** of changes

### Project Integration

- **Seamless Azure RAG** development workflow
- **Automatic ZepCloud** memory integration
- **Microsoft 365** service testing
- **End-to-end verification** of all components

## 📚 Additional Resources

- **Kilo Code Methodology** - Systematic workflow approach
- **Cline Integration** - Advanced AI coding patterns
- **ByteRover Integration** - Knowledge management system
- **Browser Automation** - End-to-end testing capabilities
- **Quality Standards** - Code quality and testing requirements

## 🔧 Maintenance

This configuration is designed to be:

- **Self-maintaining** with automatic updates
- **Project-aware** with Azure RAG context
- **Quality-focused** with built-in standards
- **Performance-optimized** with monitoring
- **Architecture-consistent** with established patterns

The Cursor agent now operates in full autonomous mode while maintaining quality and safety standards for the Azure RAG Setup project.

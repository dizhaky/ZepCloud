# ZepCloud Project

A comprehensive development workspace for AI-powered applications and MCP (Model Context Protocol) services.

## Project Structure

```
ZepCloud/
├── apps/                          # Core applications
│   ├── zepcloud-core/            # Main application
│   └── azure-rag-setup/          # Azure RAG setup and configuration
├── services/                     # MCP and external services
│   └── mcp-servers/              # MCP server implementations
│       └── typingmind/           # TypingMind MCP server
│           ├── local/            # Local development setup
│           ├── server/           # Server implementation
│           └── deploy/           # Deployment configurations
├── tools/                         # Development and utility tools
│   ├── scripts/                  # Python utility scripts
│   └── diagnostics/              # Diagnostic and troubleshooting tools
├── docs/                         # Documentation
│   ├── agents/                   # Agent configuration and rules
│   ├── architecture/             # System architecture documentation
│   └── guides/                   # Setup and usage guides
├── config/                       # Configuration files
└── README.md                     # This file
```

## Components

### Applications (`apps/`)

- **zepcloud-core/**: Main application code
- **azure-rag-setup/**: Azure RAG (Retrieval-Augmented Generation) setup and configuration

### Services (`services/`)

- **mcp-servers/typingmind/**: TypingMind MCP server implementation
  - **local/**: Local development environment
  - **server/**: Production server implementation
  - **deploy/**: Deployment configurations (Render, Railway, etc.)

### Tools (`tools/`)

- **scripts/**: Python utility scripts for development
- **diagnostics/**: Troubleshooting and diagnostic tools

### Documentation (`docs/`)

- **agents/**: AI agent configuration and rules
- **architecture/**: System architecture and design documents
- **guides/**: Setup guides and tutorials

### Configuration (`config/`)

- Project configuration files and settings

## Getting Started

1. Navigate to the specific component you want to work with
2. Check the component's README for specific setup instructions
3. Follow the guides in `docs/guides/` for detailed setup procedures

## Development

Each component has its own development environment and dependencies. Check individual component READMEs for specific setup instructions.

## Contributing

Please follow the established folder structure when adding new components:

- Applications go in `apps/`
- Services go in `services/`
- Tools go in `tools/`
- Documentation goes in `docs/`
- Configuration goes in `config/`

#!/bin/bash
# Cursor Project Template Quick Setup Script
# This script sets up a new project with Cursor best practices and 1Password integration

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse command line arguments
USE_1PASSWORD=false
PROJECT_NAME=""
TEMPLATE_TYPE="basic"

while [[ $# -gt 0 ]]; do
    case $1 in
        --1password)
            USE_1PASSWORD=true
            shift
            ;;
        --name)
            PROJECT_NAME="$2"
            shift 2
            ;;
        --template)
            TEMPLATE_TYPE="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --1password     Enable 1Password integration"
            echo "  --name NAME     Set project name (default: current directory)"
            echo "  --template TYPE Set template type (basic|python|node|react) (default: basic)"
            echo "  --help          Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Get project name if not provided
if [ -z "$PROJECT_NAME" ]; then
    PROJECT_NAME=$(basename "$(pwd)")
fi

print_status "🚀 Setting up Cursor project: $PROJECT_NAME"
print_status "Template type: $TEMPLATE_TYPE"
print_status "1Password integration: $([ "$USE_1PASSWORD" = true ] && echo "Enabled" || echo "Disabled")"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    print_status "Initializing Git repository..."
    git init
    print_success "Git repository initialized"
fi

# Create basic project structure
print_status "Creating project structure..."

# Create directories
mkdir -p .cursor
mkdir -p .vscode
mkdir -p docs
mkdir -p scripts
mkdir -p config
mkdir -p tests

# Create .gitignore
cat > .gitignore << 'EOF'
# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/

# IDE
.vscode/settings.json
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Environment variables
.env
.env.local
.env.*.local

# Logs
*.log
logs/

# Build outputs
dist/
build/
*.egg-info/

# Temporary files
*.tmp
*.temp
EOF

print_success "Created .gitignore"

# Create README.md
cat > README.md << EOF
# $PROJECT_NAME

A Cursor-optimized project with best practices and development tools.

## Getting Started

### Prerequisites
- [Cursor](https://cursor.sh/) - AI-powered code editor
- Git
$([ "$USE_1PASSWORD" = true ] && echo "- [1Password CLI](https://developer.1password.com/docs/cli/) - For secure credential management")

### Setup
1. Clone this repository
2. Install dependencies: \`npm install\` (if applicable)
3. Configure environment variables (see .env.example)
$([ "$USE_1PASSWORD" = true ] && echo "4. Set up 1Password integration: \`op signin\`")

### Development
- Use Cursor for AI-assisted development
- Follow the coding standards defined in .cursor/
- Run tests: \`npm test\` (if applicable)

## Project Structure
\`\`\`
.
├── .cursor/          # Cursor-specific configuration
├── .vscode/          # VS Code settings (compatible with Cursor)
├── docs/             # Documentation
├── scripts/          # Build and utility scripts
├── config/           # Configuration files
└── tests/            # Test files
\`\`\`

## Contributing
1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License
[Add your license here]
EOF

print_success "Created README.md"

# Create .cursor directory structure
mkdir -p .cursor/rules
mkdir -p .cursor/commands
mkdir -p .cursor/templates

# Create basic Cursor rules
cat > .cursor/rules/project-rules.md << 'EOF'
# Project Rules

## Code Style
- Use consistent indentation (2 spaces for JS/TS, 4 spaces for Python)
- Follow language-specific naming conventions
- Write self-documenting code with clear variable names

## File Organization
- Keep related files together
- Use descriptive file and directory names
- Separate concerns (models, views, controllers, etc.)

## Documentation
- Write clear commit messages
- Document complex logic
- Keep README.md updated
- Use JSDoc/docstrings for functions

## Security
- Never commit secrets or API keys
- Use environment variables for configuration
- Validate all inputs
- Follow OWASP security guidelines

## Testing
- Write tests for new features
- Maintain good test coverage
- Use descriptive test names
- Test edge cases and error conditions
EOF

print_success "Created Cursor rules"

# Create environment template
cat > .env.example << 'EOF'
# Environment Configuration
# Copy this file to .env and fill in your values

# Application
APP_NAME=My App
APP_ENV=development
DEBUG=true

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# API Keys (use 1Password for production)
API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here

# External Services
EXTERNAL_API_URL=https://api.example.com
EOF

print_success "Created .env.example"

# Template-specific setup
case $TEMPLATE_TYPE in
    "python")
        print_status "Setting up Python template..."

        # Create requirements.txt
        cat > requirements.txt << 'EOF'
# Core dependencies
python-dotenv==1.0.0
requests==2.31.0

# Development dependencies
pytest==7.4.0
black==23.7.0
flake8==6.0.0
mypy==1.5.1
EOF

        # Create basic Python structure
        mkdir -p src
        cat > src/__init__.py << 'EOF'
"""Main package for the application."""
__version__ = "0.1.0"
EOF

        cat > src/main.py << 'EOF'
"""Main application entry point."""
import os
from dotenv import load_dotenv

def main():
    """Main application function."""
    load_dotenv()
    print("Hello from your Python app!")

if __name__ == "__main__":
    main()
EOF

        # Create pytest configuration
        cat > pytest.ini << 'EOF'
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
EOF

        print_success "Python template setup complete"
        ;;

    "node"|"react")
        print_status "Setting up Node.js template..."

        # Create package.json
        cat > package.json << 'EOF'
{
  "name": "'$PROJECT_NAME'",
  "version": "1.0.0",
  "description": "A Cursor-optimized project",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js",
    "test": "jest",
    "lint": "eslint src/",
    "format": "prettier --write src/"
  },
  "keywords": ["cursor", "node", "javascript"],
  "author": "",
  "license": "MIT",
  "dependencies": {
    "dotenv": "^16.3.1",
    "express": "^4.18.2"
  },
  "devDependencies": {
    "nodemon": "^3.0.1",
    "jest": "^29.7.0",
    "eslint": "^8.50.0",
    "prettier": "^3.0.3"
  }
}
EOF

        # Create basic Node.js structure
        mkdir -p src
        cat > src/index.js << 'EOF'
const express = require('express');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

app.get('/', (req, res) => {
  res.json({ message: 'Hello from your Node.js app!' });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
EOF

        print_success "Node.js template setup complete"
        ;;

    "basic")
        print_status "Basic template setup complete"
        ;;
esac

# 1Password integration setup
if [ "$USE_1PASSWORD" = true ]; then
    print_status "Setting up 1Password integration..."

    # Check if 1Password CLI is installed
    if ! command -v op &> /dev/null; then
        print_error "1Password CLI not found. Please install it first:"
        print_error "https://developer.1password.com/docs/cli/get-started/"
        exit 1
    fi

    # Check if user is signed in to 1Password
    if ! op account get &>/dev/null; then
        print_warning "Not signed in to 1Password CLI"
        print_warning "Please run: op signin"
        print_warning "Then run this script again"
        exit 1
    fi

    # Create 1Password integration script
    cat > scripts/setup-1password.sh << 'EOF'
#!/bin/bash
# 1Password Integration Setup Script

set -e

echo "🔐 Setting up 1Password integration..."

# Create 1Password item for project credentials
ITEM_TITLE="$PROJECT_NAME - Development Credentials"
ITEM_NAME="$(echo $PROJECT_NAME | tr '[:upper:]' '[:lower:]' | tr ' ' '-')-dev-credentials"
VAULT_NAME="Private"

echo "Creating 1Password item: $ITEM_TITLE"

# Check if item already exists
if op item get "$ITEM_NAME" &>/dev/null; then
    echo "⚠️  Item '$ITEM_NAME' already exists"
    echo "   Updating existing item..."
    op item edit "$ITEM_NAME" \
        --title "$ITEM_TITLE" \
        --field "Project Name"="$PROJECT_NAME" \
        --field "Environment"="Development" \
        --field "Created Date"="$(date -u +"%Y-%m-%d %H:%M:%S UTC")" \
        --field "Purpose"="Development environment credentials" \
        --field "Status"="Active"
else
    echo "   Creating new 1Password item..."
    op item create \
        --title "$ITEM_TITLE" \
        --vault "$VAULT_NAME" \
        --category "Login" \
        --field "Project Name"="$PROJECT_NAME" \
        --field "Environment"="Development" \
        --field "Created Date"="$(date -u +"%Y-%m-%d %H:%M:%S UTC")" \
        --field "Purpose"="Development environment credentials" \
        --field "Status"="Active"
fi

echo "✅ 1Password integration setup complete!"
echo ""
echo "📝 To add credentials to your 1Password item:"
echo "   op item edit $ITEM_NAME"
echo ""
echo "🔍 To retrieve credentials:"
echo "   op item get $ITEM_NAME"
EOF

    chmod +x scripts/setup-1password.sh

    # Update .env.example with 1Password references
    cat >> .env.example << 'EOF'

# 1Password Integration
# Uncomment and configure these if using 1Password CLI
# OP_VAULT=Private
# OP_ITEM_NAME=your-project-dev-credentials

# Example: Retrieve credentials from 1Password
# DATABASE_URL=$(op item get your-project-dev-credentials --fields "Database URL" --format json | jq -r '.value')
# API_KEY=$(op item get your-project-dev-credentials --fields "API Key" --format json | jq -r '.value')
EOF

    # Create 1Password helper script
    cat > scripts/get-credentials.sh << 'EOF'
#!/bin/bash
# Helper script to retrieve credentials from 1Password

set -e

ITEM_NAME="$(echo $PROJECT_NAME | tr '[:upper:]' '[:lower:]' | tr ' ' '-')-dev-credentials"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <field-name>"
    echo ""
    echo "Available fields:"
    op item get "$ITEM_NAME" --fields | grep -v "title" | cut -d: -f1
    exit 1
fi

FIELD_NAME="$1"
op item get "$ITEM_NAME" --fields "$FIELD_NAME" --format json | jq -r '.value'
EOF

    chmod +x scripts/get-credentials.sh

    print_success "1Password integration setup complete"
    print_status "Run 'scripts/setup-1password.sh' to create your 1Password item"
fi

# Create VS Code settings (compatible with Cursor)
cat > .vscode/settings.json << 'EOF'
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/node_modules": true,
    "**/.git": true
  },
  "search.exclude": {
    "**/node_modules": true,
    "**/__pycache__": true
  }
}
EOF

print_success "Created VS Code settings"

# Create initial commit
print_status "Creating initial commit..."
git add .
git commit -m "Initial commit: Cursor project template setup

- Added project structure
- Configured Cursor rules and settings
- Set up development environment
$([ "$USE_1PASSWORD" = true ] && echo "- Integrated 1Password for credential management")"

print_success "Initial commit created"

# Final summary
echo ""
print_success "🎉 Project setup complete!"
echo ""
echo "📁 Project structure created:"
echo "   - .cursor/          # Cursor configuration"
echo "   - .vscode/          # VS Code settings"
echo "   - docs/             # Documentation"
echo "   - scripts/          # Utility scripts"
echo "   - config/           # Configuration files"
echo "   - tests/            # Test files"
echo ""

if [ "$USE_1PASSWORD" = true ]; then
    echo "🔐 1Password integration:"
    echo "   - Run: scripts/setup-1password.sh"
    echo "   - Add credentials: op item edit $(echo $PROJECT_NAME | tr '[:upper:]' '[:lower:]' | tr ' ' '-')-dev-credentials"
    echo "   - Get credentials: scripts/get-credentials.sh <field-name>"
    echo ""
fi

echo "🚀 Next steps:"
echo "1. Install dependencies (if applicable)"
echo "2. Configure environment variables"
echo "3. Start developing with Cursor!"
echo ""
echo "📚 Documentation:"
echo "   - README.md - Project overview"
echo "   - .cursor/rules/ - Development guidelines"
echo "   - docs/ - Additional documentation"
echo ""
print_success "Happy coding! 🎯"

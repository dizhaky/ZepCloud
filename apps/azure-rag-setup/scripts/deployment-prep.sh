#!/bin/bash
# Deployment Preparation Script for Azure RAG System
# Checks dependencies, validates configuration, and prepares for deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    Azure RAG System Deployment Preparation                   ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}⚠️  Note: Some checks may require root privileges for full functionality${NC}"
    echo ""
fi

# Function to check command availability
check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✅ $1: Installed${NC}"
        return 0
    else
        echo -e "${RED}❌ $1: Not found${NC}"
        return 1
    fi
}

# Function to check Docker service
check_docker_service() {
    if systemctl is-active --quiet docker; then
        echo -e "${GREEN}✅ Docker: Running${NC}"
        return 0
    else
        echo -e "${RED}❌ Docker: Not running${NC}"
        return 1
    fi
}

# Function to check file existence
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅ $2: Found${NC}"
        return 0
    else
        echo -e "${RED}❌ $2: Not found${NC}"
        return 1
    fi
}

# Function to check environment variables
check_env_var() {
    if [ -n "${!1}" ]; then
        echo -e "${GREEN}✅ $1: Set${NC}"
        return 0
    else
        echo -e "${RED}❌ $1: Not set${NC}"
        return 1
    fi
}

# Function to validate password strength
validate_password() {
    local password="$1"
    local var_name="$2"
    
    if [ ${#password} -ge 12 ]; then
        echo -e "${GREEN}✅ $var_name: Strong password${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  $var_name: Weak password (minimum 12 characters recommended)${NC}"
        return 1
    fi
}

echo -e "${YELLOW}🔍 Phase 1: Checking System Dependencies...${NC}"

# Check essential commands
echo ""
echo -e "${BLUE}📦 Essential Commands:${NC}"
check_command "docker"
check_command "docker-compose"
check_command "git"
check_command "curl"
check_command "openssl"
check_command "ufw"

# Check Docker service
echo ""
echo -e "${BLUE}🐳 Docker Service:${NC}"
check_docker_service

echo ""
echo -e "${YELLOW}🔍 Phase 2: Validating Environment Configuration...${NC}"

# Check project directory
PROJECT_DIR="/opt/azure-rag-setup"
if [ ! -d "$PROJECT_DIR" ]; then
    PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi

echo ""
echo -e "${BLUE}📁 Project Directory:${NC}"
check_file "$PROJECT_DIR/.env" "Environment file (.env)"
check_file "$PROJECT_DIR/docker-compose.yml" "Docker Compose configuration"
check_file "$PROJECT_DIR/scripts/deploy.sh" "Deployment script"

# Load environment variables
echo ""
echo -e "${BLUE}🔐 Environment Variables:${NC}"
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a
    source "$PROJECT_DIR/.env"
    set +a
    echo -e "${GREEN}✅ Environment variables loaded${NC}"
else
    echo -e "${RED}❌ Environment file not found${NC}"
fi

# Check required environment variables
echo ""
echo -e "${BLUE}🔑 Required Variables:${NC}"
check_env_var "ELASTIC_PASSWORD"
check_env_var "AZURE_TENANT_ID"
check_env_var "AZURE_CLIENT_ID"
check_env_var "AZURE_CLIENT_SECRET"

# Validate password strength
echo ""
echo -e "${BLUE}🛡️  Password Security:${NC}"
if [ -n "$ELASTIC_PASSWORD" ]; then
    validate_password "$ELASTIC_PASSWORD" "ELASTIC_PASSWORD"
fi

echo ""
echo -e "${YELLOW}🔍 Phase 3: Checking SSL Configuration...${NC}"

# Check SSL certificates
echo ""
echo -e "${BLUE}🔐 SSL Certificates:${NC}"
check_file "$PROJECT_DIR/config/ssl/openssl.cnf" "SSL configuration file"

echo ""
echo -e "${YELLOW}🔍 Phase 4: Checking Firewall Configuration...${NC}"

# Check firewall status
echo ""
echo -e "${BLUE}🔥 Firewall:${NC}"
if command -v ufw &> /dev/null; then
    if ufw status | grep -q "Status: active"; then
        echo -e "${GREEN}✅ UFW: Active${NC}"
        
        # Check required ports
        if ufw status | grep -q "22/tcp"; then
            echo -e "${GREEN}✅ SSH (22/tcp): Allowed${NC}"
        else
            echo -e "${YELLOW}⚠️  SSH (22/tcp): Not explicitly allowed${NC}"
        fi
        
        if ufw status | grep -q "80/tcp"; then
            echo -e "${GREEN}✅ HTTP (80/tcp): Allowed${NC}"
        else
            echo -e "${YELLOW}⚠️  HTTP (80/tcp): Not explicitly allowed${NC}"
        fi
        
        if ufw status | grep -q "443/tcp"; then
            echo -e "${GREEN}✅ HTTPS (443/tcp): Allowed${NC}"
        else
            echo -e "${YELLOW}⚠️  HTTPS (443/tcp): Not explicitly allowed${NC}"
        fi
        
        if ufw status | grep -q "5001/tcp"; then
            echo -e "${GREEN}✅ Flask API (5001/tcp): Allowed${NC}"
        else
            echo -e "${YELLOW}⚠️  Flask API (5001/tcp): Not explicitly allowed${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  UFW: Inactive${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  UFW: Not installed${NC}"
fi

echo ""
echo -e "${YELLOW}📋 Phase 5: Azure AD Application Setup Instructions${NC}"

echo ""
echo -e "${BLUE}📝 Azure AD Application Registration:${NC}"
echo "To set up Azure integration, you need to register an application in Azure AD:"
echo ""
echo "1. Go to Azure Portal (https://portal.azure.com)"
echo "2. Navigate to Azure Active Directory > App registrations"
echo "3. Click 'New registration'"
echo "4. Enter application name: 'Azure RAG System'"
echo "5. Select supported account type: 'Accounts in this organizational directory only'"
echo "6. Click 'Register'"
echo ""
echo "After registration, note the following values:"
echo "  - Application (client) ID"
echo "  - Directory (tenant) ID"
echo ""
echo "Then configure API permissions:"
echo "1. In the app registration, go to 'API permissions'"
echo "2. Click 'Add a permission' > 'Microsoft Graph'"
echo "3. Select 'Application permissions' or 'Delegated permissions'"
echo "4. Add the following permissions:"
echo "   - Files.Read.All"
echo "   - Sites.Read.All"
echo "   - Mail.Read"
echo "   - Calendars.Read"
echo "   - Contacts.Read"
echo "   - User.Read.All"
echo "5. Click 'Grant admin consent for [your tenant]'"
echo ""
echo "Finally, create a client secret:"
echo "1. Go to 'Certificates & secrets'"
echo "2. Click 'New client secret'"
echo "3. Enter a description and expiration"
echo "4. Copy the secret value (you'll need it for the .env file)"

echo ""
echo -e "${YELLOW}🔧 Phase 6: Next Steps${NC}"

echo ""
echo -e "${BLUE}📝 Configuration Checklist:${NC}"
echo "1. Update .env file with your Azure AD credentials:"
echo "   - AZURE_TENANT_ID=your-tenant-id"
echo "   - AZURE_CLIENT_ID=your-client-id"
echo "   - AZURE_CLIENT_SECRET=your-client-secret"
echo ""
echo "2. Generate a strong password for Elasticsearch:"
echo "   - ELASTIC_PASSWORD=YourStrongPasswordHere123!"
echo ""
echo "3. Review and update any other configuration values as needed"
echo ""
echo "4. Generate SSL certificates if not already done:"
echo "   cd $PROJECT_DIR"
echo "   openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/azure-rag-key.pem -out /etc/ssl/certs/azure-rag-cert.pem -config config/ssl/openssl.cnf"
echo ""
echo "5. Set up firewall rules:"
echo "   sudo ./scripts/setup-firewall.sh"
echo ""
echo "6. Run the deployment:"
echo "   docker-compose up -d"
echo ""

echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    Preparation Complete!                                     ║${NC}"
echo -e "${GREEN}║                                                                              ║${NC}"
echo -e "${GREEN}║ Next steps:                                                                  ║${NC}"
echo -e "${GREEN}║ 1. Configure Azure AD application (see instructions above)                   ║${NC}"
echo -e "${GREEN}║ 2. Update .env with your credentials                                         ║${NC}"
echo -e "${GREEN}║ 3. Set up firewall: sudo ./scripts/setup-firewall.sh                         ║${NC}"
echo -e "${GREEN}║ 4. Start services: docker-compose up -d                                     ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Exit with success status
exit 0
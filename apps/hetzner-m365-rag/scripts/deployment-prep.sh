#!/bin/bash
# Deployment Preparation Script for M365 RAG System
# Checks dependencies, validates configuration, and prepares for deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    M365 RAG System Deployment Preparation                    ║${NC}"
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
PROJECT_DIR="/data/m365-rag"
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
check_env_var "POSTGRES_PASSWORD"
check_env_var "REDIS_PASSWORD"
check_env_var "MINIO_ROOT_PASSWORD"
check_env_var "JWT_SECRET_KEY"
check_env_var "RAGFLOW_SECRET_KEY"
check_env_var "GRAFANA_ADMIN_PASSWORD"

# Validate password strength
echo ""
echo -e "${BLUE}🛡️  Password Security:${NC}"
if [ -n "$ELASTIC_PASSWORD" ]; then
    validate_password "$ELASTIC_PASSWORD" "ELASTIC_PASSWORD"
fi

if [ -n "$POSTGRES_PASSWORD" ]; then
    validate_password "$POSTGRES_PASSWORD" "POSTGRES_PASSWORD"
fi

if [ -n "$REDIS_PASSWORD" ]; then
    validate_password "$REDIS_PASSWORD" "REDIS_PASSWORD"
fi

if [ -n "$MINIO_ROOT_PASSWORD" ]; then
    validate_password "$MINIO_ROOT_PASSWORD" "MINIO_ROOT_PASSWORD"
fi

if [ -n "$JWT_SECRET_KEY" ]; then
    if [ ${#JWT_SECRET_KEY} -ge 32 ]; then
        echo -e "${GREEN}✅ JWT_SECRET_KEY: Strong secret (32+ characters)${NC}"
    else
        echo -e "${YELLOW}⚠️  JWT_SECRET_KEY: Weak secret (minimum 32 characters recommended)${NC}"
    fi
fi

if [ -n "$RAGFLOW_SECRET_KEY" ]; then
    if [ ${#RAGFLOW_SECRET_KEY} -ge 32 ]; then
        echo -e "${GREEN}✅ RAGFLOW_SECRET_KEY: Strong secret (32+ characters)${NC}"
    else
        echo -e "${YELLOW}⚠️  RAGFLOW_SECRET_KEY: Weak secret (minimum 32 characters recommended)${NC}"
    fi
fi

if [ -n "$GRAFANA_ADMIN_PASSWORD" ]; then
    validate_password "$GRAFANA_ADMIN_PASSWORD" "GRAFANA_ADMIN_PASSWORD"
fi

echo ""
echo -e "${YELLOW}🔍 Phase 3: Checking SSL Configuration...${NC}"

# Check SSL certificates
echo ""
echo -e "${BLUE}🔐 SSL Certificates:${NC}"
check_file "$PROJECT_DIR/config/elasticsearch/certs/elasticsearch.crt" "Elasticsearch SSL certificate"
check_file "$PROJECT_DIR/config/elasticsearch/certs/elasticsearch.key" "Elasticsearch SSL private key"
check_file "$PROJECT_DIR/config/elasticsearch/certs/ca.crt" "Elasticsearch CA certificate"

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
echo "To set up M365 integration, you need to register an application in Azure AD:"
echo ""
echo "1. Go to Azure Portal (https://portal.azure.com)"
echo "2. Navigate to Azure Active Directory > App registrations"
echo "3. Click 'New registration'"
echo "4. Enter application name: 'M365 RAG System'"
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
echo "   - M365_CLIENT_ID=your-application-client-id"
echo "   - M365_CLIENT_SECRET=your-client-secret"
echo "   - M365_TENANT_ID=your-tenant-id"
echo ""
echo "2. Update .env file with your OpenAI API key:"
echo "   - OPENAI_API_KEY=your-openai-api-key"
echo ""
echo "3. Review and update any other configuration values as needed"
echo ""
echo "4. Generate SSL certificates if not already done:"
echo "   cd $PROJECT_DIR"
echo "   ./scripts/generate-es-certs.sh"
echo ""
echo "5. Run the deployment script:"
echo "   ./scripts/deploy.sh"

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    Preparation Complete!                                     ║${NC}"
echo -e "${GREEN}║                                                                              ║${NC}"
echo -e "${GREEN}║ Next steps:                                                                  ║${NC}"
echo -e "${GREEN}║ 1. Configure Azure AD application (see instructions above)                   ║${NC}"
echo -e "${GREEN}║ 2. Update .env with your credentials                                         ║${NC}"
echo -e "${GREEN}║ 3. Run deployment script: ./scripts/deploy.sh                               ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Exit with success status
exit 0
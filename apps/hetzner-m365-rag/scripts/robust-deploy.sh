#!/bin/bash
# Robust Deployment Script for M365 RAG System
# This script provides a comprehensive deployment with validation and error handling

set -euo pipefail

# Configuration
PROJECT_DIR="/data/m365-rag"
BACKUP_DIR="/backup/m365-rag"
LOG_FILE="/var/log/m365-rag-deploy.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Status update function
status_update() {
    log "$1"
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Success message function
success() {
    log "$1"
    echo -e "${GREEN}✅ $1${NC}"
}

# Warning message function
warning() {
    log "WARNING: $1"
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Error message function
error() {
    log "ERROR: $1"
    echo -e "${RED}❌ $1${NC}" >&2
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then 
        error "Please run as root or with sudo"
        exit 1
    fi
    success "Running with root privileges"
}

# Check system dependencies
check_dependencies() {
    status_update "Checking system dependencies..."
    
    local missing_deps=()
    
    # Check essential commands
    for cmd in docker docker-compose git curl openssl ufw jq; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_deps+=("$cmd")
            error "$cmd is not installed"
        else
            success "$cmd is installed"
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        error "Missing dependencies: ${missing_deps[*]}"
        echo "Please install missing dependencies and re-run the script"
        return 1
    fi
    
    # Check Docker service
    if ! systemctl is-active --quiet docker; then
        error "Docker service is not running"
        echo "Start Docker service: systemctl start docker"
        return 1
    else
        success "Docker service is running"
    fi
    
    success "All dependencies are satisfied"
}

# Validate environment configuration
validate_environment() {
    status_update "Validating environment configuration..."
    
    # Check project directory
    if [ ! -d "$PROJECT_DIR" ]; then
        error "Project directory $PROJECT_DIR does not exist"
        return 1
    fi
    
    # Check required files
    local required_files=(
        "$PROJECT_DIR/.env"
        "$PROJECT_DIR/docker-compose.yml"
        "$PROJECT_DIR/scripts/deploy.sh"
    )
    
    local missing_files=()
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            missing_files+=("$file")
            error "Required file missing: $file"
        else
            success "Found required file: $file"
        fi
    done
    
    if [ ${#missing_files[@]} -ne 0 ]; then
        error "Missing required files: ${missing_files[*]}"
        return 1
    fi
    
    # Load environment variables
    set -a
    if ! source "$PROJECT_DIR/.env"; then
        error "Failed to load environment variables from $PROJECT_DIR/.env"
        return 1
    fi
    set +a
    success "Environment variables loaded successfully"
    
    # Check required environment variables
    local required_vars=(
        "ELASTIC_PASSWORD"
        "POSTGRES_PASSWORD"
        "MINIO_ROOT_PASSWORD"
        "OPENAI_API_KEY"
        "M365_CLIENT_ID"
        "M365_CLIENT_SECRET"
        "M365_TENANT_ID"
    )
    
    local missing_vars=()
    for var in "${required_vars[@]}"; do
        if [ -z "${!var:-}" ]; then
            missing_vars+=("$var")
            error "Required environment variable not set: $var"
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        error "Missing required environment variables: ${missing_vars[*]}"
        echo "Please update $PROJECT_DIR/.env with all required values"
        return 1
    fi
    
    # Validate password strength
    validate_password() {
        local password="$1"
        local var_name="$2"
        
        if [ ${#password} -lt 12 ]; then
            warning "$var_name: Weak password (minimum 12 characters recommended)"
        else
            success "$var_name: Strong password"
        fi
    }
    
    validate_password "$ELASTIC_PASSWORD" "ELASTIC_PASSWORD"
    validate_password "$POSTGRES_PASSWORD" "POSTGRES_PASSWORD"
    validate_password "$MINIO_ROOT_PASSWORD" "MINIO_ROOT_PASSWORD"
    
    success "Environment configuration validation completed"
}

# Set up SSL certificates
setup_ssl() {
    status_update "Setting up SSL certificates..."
    
    # Check if certificates already exist
    if [ -f "$PROJECT_DIR/config/elasticsearch/certs/elasticsearch.crt" ]; then
        success "SSL certificates already exist, skipping generation"
        return 0
    fi
    
    # Generate Elasticsearch SSL certificates
    status_update "Generating Elasticsearch SSL certificates..."
    if [ -f "$PROJECT_DIR/scripts/generate-es-certs.sh" ]; then
        if su - deploy -c "cd $PROJECT_DIR && bash scripts/generate-es-certs.sh"; then
            success "Elasticsearch SSL certificates generated successfully"
        else
            error "Failed to generate Elasticsearch SSL certificates"
            return 1
        fi
    else
        warning "Elasticsearch certificate generation script not found, skipping"
    fi
    
    success "SSL certificate setup completed"
}

# Configure firewall rules
configure_firewall() {
    status_update "Configuring firewall rules..."
    
    # Check if UFW is installed
    if ! command -v ufw &> /dev/null; then
        warning "UFW not installed, skipping firewall configuration"
        return 0
    fi
    
    # Reset firewall to default state
    status_update "Resetting firewall to default state..."
    if ! ufw --force reset; then
        warning "Failed to reset firewall, continuing with existing configuration"
    fi
    
    # Configure default policies
    status_update "Setting default firewall policies..."
    ufw default deny incoming || warning "Failed to set default deny incoming policy"
    ufw default allow outgoing || warning "Failed to set default allow outgoing policy"
    
    # Allow essential services
    status_update "Configuring essential service rules..."
    
    # SSH - Allow from anywhere (consider restricting to specific IPs in production)
    if ufw allow 22/tcp comment 'SSH'; then
        success "SSH (22/tcp) allowed"
    else
        warning "Failed to allow SSH (22/tcp)"
    fi
    
    # HTTP - Allow from anywhere
    if ufw allow 80/tcp comment 'HTTP'; then
        success "HTTP (80/tcp) allowed"
    else
        warning "Failed to allow HTTP (80/tcp)"
    fi
    
    # HTTPS - Allow from anywhere
    if ufw allow 443/tcp comment 'HTTPS'; then
        success "HTTPS (443/tcp) allowed"
    else
        warning "Failed to allow HTTPS (443/tcp)"
    fi
    
    # Enable firewall
    status_update "Enabling firewall..."
    if ufw --force enable; then
        success "Firewall enabled successfully"
    else
        error "Failed to enable firewall"
        return 1
    fi
    
    # Display status
    ufw status numbered || warning "Failed to display firewall status"
    
    success "Firewall configuration completed"
}

# Start all services using docker-compose
start_services() {
    status_update "Starting all services using docker-compose..."
    
    # Switch to deploy user and start services
    status_update "Pulling latest images..."
    if ! su - deploy -c "cd $PROJECT_DIR && docker compose pull"; then
        warning "Failed to pull latest images, continuing with existing images"
    else
        success "Latest images pulled successfully"
    fi
    
    status_update "Starting services..."
    if ! su - deploy -c "cd $PROJECT_DIR && docker compose up -d"; then
        error "Failed to start services"
        return 1
    fi
    
    success "Services started successfully"
}

# Verify that all services are running correctly
verify_services() {
    status_update "Verifying that all services are running correctly..."
    
    # Wait for services to start
    status_update "Waiting for services to start (60 seconds)..."
    sleep 60
    
    # Check service status
    status_update "Checking service status..."
    if ! su - deploy -c "cd $PROJECT_DIR && docker compose ps"; then
        warning "Failed to check service status"
    fi
    
    # Check if all services are healthy
    local unhealthy_services
    unhealthy_services=$(su - deploy -c "cd $PROJECT_DIR && docker compose ps --format json" 2>/dev/null | jq -r '.[] | select(.State != "running" or .Health != "healthy") | .Service' 2>/dev/null || echo "")
    
    if [ -n "$unhealthy_services" ]; then
        warning "Unhealthy services detected:"
        echo "$unhealthy_services"
        echo "Check logs: cd $PROJECT_DIR && docker compose logs --tail=50"
    else
        success "All services are running and healthy"
    fi
    
    success "Service verification completed"
}

# Main deployment function
main() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                    M365 RAG System Robust Deployment                         ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Initialize log file
    mkdir -p "$(dirname "$LOG_FILE")"
    touch "$LOG_FILE"
    log "Starting M365 RAG System deployment"
    
    # Execute deployment steps
    if ! check_root; then
        exit 1
    fi
    
    if ! check_dependencies; then
        error "Dependency check failed, exiting"
        exit 1
    fi
    
    if ! validate_environment; then
        error "Environment validation failed, exiting"
        exit 1
    fi
    
    if ! setup_ssl; then
        error "SSL setup failed, exiting"
        exit 1
    fi
    
    if ! configure_firewall; then
        error "Firewall configuration failed, exiting"
        exit 1
    fi
    
    if ! start_services; then
        error "Service startup failed, exiting"
        exit 1
    fi
    
    if ! verify_services; then
        warning "Service verification failed, but deployment may still be successful"
    fi
    
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    Deployment Completed Successfully!                        ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    status_update "Deployment log available at: $LOG_FILE"
    status_update "Check service status: cd $PROJECT_DIR && docker compose ps"
    status_update "View logs: cd $PROJECT_DIR && docker compose logs -f"
    
    log "Deployment completed successfully"
}

# Run main function
main "$@"
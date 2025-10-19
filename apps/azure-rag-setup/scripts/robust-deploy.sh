#!/bin/bash
# Robust Deployment Script for Azure RAG System
# This script provides a comprehensive deployment with validation and error handling

set -euo pipefail

# Configuration
PROJECT_DIR="/opt/azure-rag-setup"
BACKUP_DIR="/backup/azure-rag"
LOG_FILE="/var/log/azure-rag-deploy.log"

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
        # Try to find the project directory relative to this script
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
        if [ ! -d "$PROJECT_DIR" ]; then
            error "Project directory $PROJECT_DIR does not exist"
            return 1
        fi
    fi
    
    # Check required files
    local required_files=(
        "$PROJECT_DIR/docker-compose.yml"
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
    
    # Load environment variables from env.elasticsearch if it exists, otherwise from .env
    local env_file=""
    if [ -f "$PROJECT_DIR/env.elasticsearch" ]; then
        env_file="$PROJECT_DIR/env.elasticsearch"
    elif [ -f "$PROJECT_DIR/.env" ]; then
        env_file="$PROJECT_DIR/.env"
    fi
    
    if [ -n "$env_file" ]; then
        set -a
        if ! source "$env_file"; then
            error "Failed to load environment variables from $env_file"
            return 1
        fi
        set +a
        success "Environment variables loaded successfully from $env_file"
    else
        warning "No environment file found (.env or env.elasticsearch)"
    fi
    
    # Check required environment variables
    local required_vars=(
        "ELASTIC_PASSWORD"
        "AZURE_TENANT_ID"
        "AZURE_CLIENT_ID"
        "AZURE_CLIENT_SECRET"
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
        echo "Please update your environment file with all required values"
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
    
    success "Environment configuration validation completed"
}

# Set up SSL certificates
setup_ssl() {
    status_update "Setting up SSL certificates..."
    
    # Create SSL directory if it doesn't exist
    local ssl_dir="$PROJECT_DIR/config/ssl"
    mkdir -p "$ssl_dir"
    
    # Check if certificates already exist
    if [ -f "/etc/ssl/certs/azure-rag-cert.pem" ] && [ -f "/etc/ssl/private/azure-rag-key.pem" ]; then
        success "SSL certificates already exist, skipping generation"
        return 0
    fi
    
    # Generate self-signed certificates using the existing openssl.cnf
    status_update "Generating self-signed SSL certificates..."
    if [ -f "$ssl_dir/openssl.cnf" ]; then
        mkdir -p /etc/ssl/certs /etc/ssl/private
        if openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout /etc/ssl/private/azure-rag-key.pem \
            -out /etc/ssl/certs/azure-rag-cert.pem \
            -config "$ssl_dir/openssl.cnf"; then
            chmod 644 /etc/ssl/certs/azure-rag-cert.pem
            chmod 600 /etc/ssl/private/azure-rag-key.pem
            success "SSL certificates generated successfully"
        else
            warning "Failed to generate SSL certificates"
        fi
    else
        warning "SSL configuration file not found, skipping certificate generation"
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
    
    # Flask API port
    if ufw allow 5001/tcp comment 'Flask API'; then
        success "Flask API (5001/tcp) allowed"
    else
        warning "Failed to allow Flask API (5001/tcp)"
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

# Configure Elasticsearch index
configure_elasticsearch_index() {
    status_update "Configuring Elasticsearch index..."
    
    # Wait for Elasticsearch to be ready
    status_update "Waiting for Elasticsearch to start (60 seconds)..."
    sleep 60
    
    # Check if Elasticsearch is accessible
    if curl -u elastic:"$ELASTIC_PASSWORD" -s http://localhost:9200/_cluster/health > /dev/null; then
        success "Elasticsearch is accessible"
        
        # Check if index exists
        if curl -u elastic:"$ELASTIC_PASSWORD" -s http://localhost:9200/m365-documents > /dev/null; then
            success "Elasticsearch index already exists"
        else
            status_update "Creating Elasticsearch index..."
            # Run the index creation script if it exists
            if [ -f "$PROJECT_DIR/create_simple_index.py" ]; then
                if python3 "$PROJECT_DIR/create_simple_index.py"; then
                    success "Elasticsearch index created successfully"
                else
                    warning "Failed to create Elasticsearch index using Python script"
                fi
            else
                warning "Index creation script not found, skipping index creation"
            fi
        fi
    else
        warning "Elasticsearch is not accessible, skipping index configuration"
    fi
    
    success "Elasticsearch index configuration completed"
}

# Start all services using docker-compose
start_services() {
    status_update "Starting all services using docker-compose..."
    
    # Change to project directory
    cd "$PROJECT_DIR"
    
    # Pull latest images
    status_update "Pulling latest images..."
    if ! docker-compose pull; then
        warning "Failed to pull latest images, continuing with existing images"
    else
        success "Latest images pulled successfully"
    fi
    
    # Start services
    status_update "Starting services..."
    if ! docker-compose up -d; then
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
    if ! docker-compose ps; then
        warning "Failed to check service status"
    fi
    
    # Check if all services are healthy
    local unhealthy_services
    unhealthy_services=$(docker-compose ps --format json 2>/dev/null | jq -r '.[] | select(.State != "running" or .Health != "healthy") | .Service' 2>/dev/null || echo "")
    
    if [ -n "$unhealthy_services" ]; then
        warning "Unhealthy services detected:"
        echo "$unhealthy_services"
        echo "Check logs: cd $PROJECT_DIR && docker-compose logs --tail=50"
    else
        success "All services are running and healthy"
    fi
    
    success "Service verification completed"
}

# Main deployment function
main() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                    Azure RAG System Robust Deployment                        ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Initialize log file
    mkdir -p "$(dirname "$LOG_FILE")"
    touch "$LOG_FILE"
    log "Starting Azure RAG System deployment"
    
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
    
    if ! configure_elasticsearch_index; then
        warning "Elasticsearch index configuration failed, but deployment may still be successful"
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
    status_update "Check service status: cd $PROJECT_DIR && docker-compose ps"
    status_update "View logs: cd $PROJECT_DIR && docker-compose logs -f"
    
    log "Deployment completed successfully"
}

# Run main function
main "$@"
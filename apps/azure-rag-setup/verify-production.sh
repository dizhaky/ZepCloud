#!/bin/bash
# Production Verification Script for Azure RAG Setup
# This script performs comprehensive verification of the Azure RAG deployment

set -euo pipefail

# Configuration
PROJECT_DIR="/Users/danizhaky/Dev/ZepCloud/azure-rag-setup"
LOG_FILE="/tmp/azure-rag-production-verify.log"

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

# Check if running in correct directory
check_directory() {
    if [ ! -d "$PROJECT_DIR" ]; then
        error "Project directory $PROJECT_DIR does not exist"
        exit 1
    fi
    
    if [ ! -f "$PROJECT_DIR/README.md" ]; then
        error "Not in Azure RAG Setup project directory"
        exit 1
    fi
    
    cd "$PROJECT_DIR"
    success "Working in correct project directory"
}

# Check Python environment
check_python_environment() {
    status_update "Checking Python environment..."
    
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is not installed"
        return 1
    fi
    
    # Check Python version
    local python_version
    python_version=$(python3 --version 2>&1)
    success "Python version: $python_version"
    
    # Check if virtual environment is activated
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        success "Virtual environment is activated: $VIRTUAL_ENV"
    else
        warning "Virtual environment is not activated"
    fi
    
    # Check required packages
    local required_packages=("azure-search-documents" "azure-storage-blob" "msal" "python-dotenv")
    local missing_packages=()
    
    for package in "${required_packages[@]}"; do
        if python3 -c "import $package" 2>/dev/null; then
            success "Package $package is installed"
        else
            warning "Package $package is not installed"
            missing_packages+=("$package")
        fi
    done
    
    if [ ${#missing_packages[@]} -gt 0 ]; then
        warning "Missing packages: ${missing_packages[*]}"
    fi
}

# Check environment variables
check_environment_variables() {
    status_update "Checking environment variables..."
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        warning ".env file not found"
        return 1
    fi
    
    # Load environment variables
    set -a
    source .env
    set +a
    
    # Check required variables
    local required_vars=("AZURE_SEARCH_SERVICE_NAME" "AZURE_SEARCH_ADMIN_KEY" "AZURE_SEARCH_INDEX_NAME" 
                        "AZURE_STORAGE_ACCOUNT_NAME" "AZURE_STORAGE_ACCOUNT_KEY" "AZURE_STORAGE_CONTAINER_NAME"
                        "M365_CLIENT_ID" "M365_CLIENT_SECRET" "M365_TENANT_ID")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var:-}" ]; then
            warning "Environment variable $var is not set"
            missing_vars+=("$var")
        else
            success "Environment variable $var is set"
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        error "Missing required environment variables: ${missing_vars[*]}"
        return 1
    fi
}

# Check Azure services connectivity
check_azure_connectivity() {
    status_update "Checking Azure services connectivity..."
    
    # Check Azure AI Search
    local search_endpoint="https://${AZURE_SEARCH_SERVICE_NAME}.search.windows.net"
    if curl -sf -H "api-key: ${AZURE_SEARCH_ADMIN_KEY}" "${search_endpoint}/indexes/${AZURE_SEARCH_INDEX_NAME}?api-version=2023-11-01" > /dev/null 2>&1; then
        success "Azure AI Search is accessible"
    else
        warning "Azure AI Search is not accessible"
    fi
    
    # Check Azure Blob Storage
    local storage_endpoint="https://${AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
    if curl -sf "${storage_endpoint}/${AZURE_STORAGE_CONTAINER_NAME}?restype=container&comp=list&sv=2020-08-04" -H "Authorization: SharedKey ${AZURE_STORAGE_ACCOUNT_NAME}:$(echo -n \"${AZURE_STORAGE_ACCOUNT_KEY}\" | base64)" > /dev/null 2>&1; then
        success "Azure Blob Storage is accessible"
    else
        warning "Azure Blob Storage is not accessible"
    fi
}

# Check M365 authentication
check_m365_authentication() {
    status_update "Checking M365 authentication..."
    
    # Run authentication test
    if python3 m365_indexer.py test-auth > /tmp/m365-auth-test.log 2>&1; then
        success "M365 authentication test passed"
    else
        warning "M365 authentication test failed"
        cat /tmp/m365-auth-test.log
    fi
}

# Check service status
check_service_status() {
    status_update "Checking service status..."
    
    # Run status check
    if python3 m365_indexer.py status > /tmp/m365-status.log 2>&1; then
        success "M365 service status check completed"
        cat /tmp/m365-status.log
    else
        warning "M365 service status check failed"
        cat /tmp/m365-status.log
    fi
}

# Check system resources
check_system_resources() {
    status_update "Checking system resources..."
    
    # Check disk space
    local disk_usage
    disk_usage=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$disk_usage" -gt 90 ]; then
        warning "Disk usage is high: ${disk_usage}%"
    elif [ "$disk_usage" -gt 80 ]; then
        warning "Disk usage is moderate: ${disk_usage}%"
    else
        success "Disk usage is normal: ${disk_usage}%"
    fi
    
    # Check memory usage
    local memory_usage
    memory_usage=$(free | awk 'NR==2{printf "%.2f", $3*100/$2 }' 2>/dev/null || echo "0")
    
    # Convert to integer for comparison
    local memory_usage_int=${memory_usage%.*}
    
    if [ "$memory_usage_int" -gt 90 ]; then
        warning "Memory usage is high: ${memory_usage}%"
    elif [ "$memory_usage_int" -gt 80 ]; then
        warning "Memory usage is moderate: ${memory_usage}%"
    else
        success "Memory usage is normal: ${memory_usage}%"
    fi
}

# Check backup configuration
check_backup() {
    status_update "Checking backup configuration..."
    
    # Check if backup directory exists
    if [ -d "/tmp/backups" ]; then
        success "Backup directory exists"
    else
        warning "Backup directory does not exist"
    fi
    
    # Check if cron job is configured
    if crontab -l 2>/dev/null | grep -q "m365_indexer.py"; then
        success "Backup/sync cron job is configured"
    else
        warning "Backup/sync cron job is not configured"
    fi
}

# Check monitoring and alerting
check_monitoring() {
    status_update "Checking monitoring and alerting..."
    
    # Check if maintenance script exists
    if [ -f "maintenance.py" ]; then
        success "Maintenance script exists"
    else
        warning "Maintenance script not found"
    fi
    
    # Run health check
    if python3 maintenance.py --non-interactive --action health --output json > /tmp/health-report.json 2>&1; then
        success "Health check completed"
        local health_score
        health_score=$(jq -r '.health_score' /tmp/health-report.json 2>/dev/null || echo "0")
        status_update "Health score: $health_score/100"
        
        if [ "$health_score" -ge 75 ]; then
            success "System health is good"
        elif [ "$health_score" -ge 50 ]; then
            warning "System health is moderate"
        else
            error "System health is poor"
        fi
    else
        warning "Health check failed"
        cat /tmp/health-report.json
    fi
}

# Check RAG-Anything integration
check_rag_anything() {
    status_update "Checking RAG-Anything integration..."
    
    # Check if orchestration script exists
    if [ -f "orchestrate_rag_anything.py" ]; then
        success "RAG-Anything orchestration script exists"
    else
        warning "RAG-Anything orchestration script not found"
    fi
    
    # Check status
    if python3 orchestrate_rag_anything.py --status > /tmp/rag-anything-status.log 2>&1; then
        success "RAG-Anything status check completed"
        cat /tmp/rag-anything-status.log
    else
        warning "RAG-Anything status check failed"
        cat /tmp/rag-anything-status.log
    fi
}

# Generate status report
generate_status_report() {
    status_update "Generating status report..."
    
    local report_file="/tmp/azure-rag-production-status-report-$(date +%Y%m%d-%H%M%S).txt"
    
    {
        echo "Azure RAG Setup Production Status Report"
        echo "Generated: $(date)"
        echo "========================================"
        echo ""
        
        echo "System Information:"
        uname -a
        echo ""
        
        echo "Python Information:"
        python3 --version
        echo ""
        
        echo "Disk Usage:"
        df -h .
        echo ""
        
        echo "Memory Usage:"
        free -h 2>/dev/null || echo "Memory info not available"
        echo ""
        
        echo "Environment Variables:"
        env | grep -E "AZURE|M365" | sort
        echo ""
        
        echo "Cron Jobs:"
        crontab -l 2>/dev/null || echo "No crontab"
        echo ""
        
    } > "$report_file"
    
    success "Status report generated: $report_file"
    echo "Report location: $report_file"
}

# Main verification function
main() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║              Azure RAG Setup Production Verification                          ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Initialize log file
    touch "$LOG_FILE"
    log "Starting Azure RAG Setup production verification"
    
    # Execute verification steps
    if ! check_directory; then
        exit 1
    fi
    
    if ! check_python_environment; then
        warning "Python environment check had issues"
    fi
    
    if ! check_environment_variables; then
        warning "Environment variables check had issues"
    fi
    
    if ! check_azure_connectivity; then
        warning "Azure connectivity check had issues"
    fi
    
    if ! check_m365_authentication; then
        warning "M365 authentication check had issues"
    fi
    
    if ! check_service_status; then
        warning "Service status check had issues"
    fi
    
    if ! check_system_resources; then
        warning "System resources check had issues"
    fi
    
    if ! check_backup; then
        warning "Backup configuration check had issues"
    fi
    
    if ! check_monitoring; then
        warning "Monitoring and alerting check had issues"
    fi
    
    if ! check_rag_anything; then
        warning "RAG-Anything integration check had issues"
    fi
    
    if ! generate_status_report; then
        warning "Failed to generate status report"
    fi
    
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    Verification Completed                                    ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    status_update "Verification log available at: $LOG_FILE"
    status_update "For detailed information, check the generated status report"
    
    log "Verification completed"
}

# Run main function
main "$@"
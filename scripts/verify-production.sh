#!/bin/bash
# Comprehensive Production Verification Script
# This script verifies both the Hetzner M365 RAG and Azure RAG Setup deployments

set -euo pipefail

# Configuration
HETZNER_PROJECT_DIR="/data/m365-rag"
AZURE_PROJECT_DIR="/Users/danizhaky/Dev/ZepCloud/azure-rag-setup"
LOG_FILE="/var/log/comprehensive-production-verify.log"

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

# Check if running as root (for Hetzner checks)
check_root() {
    if [ "$EUID" -ne 0 ]; then 
        warning "Not running as root - some checks may be limited"
        return 1
    fi
    success "Running with root privileges"
}

# Verify Hetzner M365 RAG deployment
verify_hetzner_deployment() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║              Hetzner M365 RAG Verification                                   ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Check if project directory exists
    if [ ! -d "$HETZNER_PROJECT_DIR" ]; then
        warning "Hetzner project directory $HETZNER_PROJECT_DIR does not exist"
        return 1
    fi
    
    # Change to project directory
    cd "$HETZNER_PROJECT_DIR"
    
    # Check Docker services
    status_update "Checking Docker services..."
    
    # Check if Docker is running
    if ! systemctl is-active --quiet docker 2>/dev/null; then
        warning "Docker service is not running"
    else
        success "Docker service is running"
    fi
    
    # Check if docker-compose.yml exists
    if [ ! -f "docker-compose.yml" ]; then
        warning "docker-compose.yml not found"
    else
        success "docker-compose.yml found"
    fi
    
    # Check if services are running
    status_update "Checking service status..."
    
    # Get service status in JSON format
    local service_status
    service_status=$(docker compose ps --format json 2>/dev/null || true)
    
    if [ -z "$service_status" ]; then
        warning "No services found or unable to retrieve service status"
    else
        # Parse service status
        echo "$service_status" | jq -r '.[] | "Service: \(.Service), Status: \(.State), Health: \(.Health)"' | while read -r line; do
            echo "  $line"
        done
        
        # Count services
        local total_services
        total_services=$(echo "$service_status" | jq -r 'length')
        
        local running_services
        running_services=$(echo "$service_status" | jq -r '[.[] | select(.State == "running")] | length')
        
        local healthy_services
        healthy_services=$(echo "$service_status" | jq -r '[.[] | select(.Health == "healthy")] | length')
        
        status_update "Service Summary: $running_services/$total_services running, $healthy_services/$total_services healthy"
        
        if [ "$running_services" -eq "$total_services" ]; then
            success "All services are running"
        else
            local stopped_services=$((total_services - running_services))
            warning "$stopped_services services are not running"
        fi
        
        if [ "$healthy_services" -eq "$total_services" ]; then
            success "All services are healthy"
        else
            local unhealthy_services=$((total_services - healthy_services))
            warning "$unhealthy_services services are not healthy"
        fi
    fi
    
    # Check service endpoints
    status_update "Checking service endpoints..."
    
    # Service endpoints to check
    local endpoints=(
        "http://localhost:8000/health:API"
        "https://localhost:9200/_cluster/health:Elasticsearch"
        "http://localhost:9380:RAGFlow UI"
        "http://localhost:3000:Grafana"
        "http://localhost:9001:MinIO Console"
        "http://localhost:9090:Prometheus"
    )
    
    local working_endpoints=0
    local total_endpoints=${#endpoints[@]}
    
    for endpoint_info in "${endpoints[@]}"; do
        local url="${endpoint_info%%:*}"
        local name="${endpoint_info#*:}"
        
        if curl -sfk "$url" > /dev/null 2>&1; then
            success "$name endpoint ($url) is accessible"
            ((working_endpoints++))
        else
            warning "$name endpoint ($url) is not accessible"
        fi
    done
    
    status_update "Endpoint Summary: $working_endpoints/$total_endpoints endpoints accessible"
    
    # Check system resources
    status_update "Checking system resources..."
    
    # Check disk space
    local disk_usage
    disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    
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
    
    # Check CPU load
    local cpu_load
    cpu_load=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
    
    # Convert to integer for comparison (multiply by 100 to handle decimals)
    local cpu_load_int
    cpu_load_int=$(echo "$cpu_load * 100" | bc 2>/dev/null | cut -d'.' -f1 2>/dev/null || echo "0")
    
    # For a 4-core system, load average > 4.0 is high
    if [ "$cpu_load_int" -gt 400 ]; then
        warning "CPU load is high: ${cpu_load}"
    elif [ "$cpu_load_int" -gt 300 ]; then
        warning "CPU load is moderate: ${cpu_load}"
    else
        success "CPU load is normal: ${cpu_load}"
    fi
    
    # Check security configuration
    status_update "Checking security configuration..."
    
    # Check environment file permissions
    if [ -f ".env" ]; then
        local env_perms
        env_perms=$(stat -c %a ".env" 2>/dev/null || echo "000")
        
        if [ "$env_perms" = "600" ]; then
            success "Environment file has secure permissions"
        else
            warning "Environment file permissions are not secure: $env_perms"
        fi
    else
        warning "Environment file not found"
    fi
    
    # Check backup configuration
    status_update "Checking backup configuration..."
    
    # Check if backup script exists and is executable
    if [ -f "scripts/backup.sh" ] && [ -x "scripts/backup.sh" ]; then
        success "Backup script exists and is executable"
    else
        warning "Backup script missing or not executable"
    fi
    
    # Check if backup directory exists
    if [ -d "/backup" ]; then
        success "Backup directory exists"
    else
        warning "Backup directory does not exist"
    fi
}

# Verify Azure RAG Setup deployment
verify_azure_deployment() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║              Azure RAG Setup Verification                                    ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Check if project directory exists
    if [ ! -d "$AZURE_PROJECT_DIR" ]; then
        warning "Azure project directory $AZURE_PROJECT_DIR does not exist"
        return 1
    fi
    
    # Change to project directory
    cd "$AZURE_PROJECT_DIR"
    
    # Check Python environment
    status_update "Checking Python environment..."
    
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        warning "Python 3 is not installed"
    else
        # Check Python version
        local python_version
        python_version=$(python3 --version 2>&1)
        success "Python version: $python_version"
    fi
    
    # Check environment variables
    status_update "Checking environment variables..."
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        warning ".env file not found"
    else
        success ".env file found"
    fi
    
    # Check Azure services connectivity
    status_update "Checking Azure services connectivity..."
    
    # Load environment variables if .env exists
    if [ -f ".env" ]; then
        set -a
        source .env
        set +a
        
        # Check required variables
        if [ -n "${AZURE_SEARCH_SERVICE_NAME:-}" ] && [ -n "${AZURE_SEARCH_ADMIN_KEY:-}" ]; then
            local search_endpoint="https://${AZURE_SEARCH_SERVICE_NAME}.search.windows.net"
            if curl -sf -H "api-key: ${AZURE_SEARCH_ADMIN_KEY}" "${search_endpoint}/indexes?api-version=2023-11-01" > /dev/null 2>&1; then
                success "Azure AI Search is accessible"
            else
                warning "Azure AI Search is not accessible"
            fi
        else
            warning "Azure Search credentials not configured"
        fi
    fi
    
    # Check M365 authentication
    status_update "Checking M365 authentication..."
    
    # Run authentication test if script exists
    if [ -f "m365_indexer.py" ]; then
        if python3 m365_indexer.py test-auth > /tmp/m365-auth-test.log 2>&1; then
            success "M365 authentication test passed"
        else
            warning "M365 authentication test failed"
        fi
    else
        warning "M365 indexer script not found"
    fi
    
    # Check system resources
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
}

# Generate comprehensive status report
generate_comprehensive_report() {
    status_update "Generating comprehensive status report..."
    
    local report_file="/tmp/comprehensive-production-status-report-$(date +%Y%m%d-%H%M%S).txt"
    
    {
        echo "Comprehensive Production Status Report"
        echo "Generated: $(date)"
        echo "========================================"
        echo ""
        
        echo "System Information:"
        uname -a
        echo ""
        
        echo "Docker Information (if available):"
        docker --version 2>/dev/null || echo "Docker not installed or not accessible"
        echo ""
        
        echo "Python Information (if available):"
        python3 --version 2>/dev/null || echo "Python not installed or not accessible"
        echo ""
        
        echo "Disk Usage:"
        df -h
        echo ""
        
        echo "Memory Usage:"
        free -h 2>/dev/null || echo "Memory info not available"
        echo ""
        
        echo "CPU Load:"
        uptime
        echo ""
        
    } > "$report_file"
    
    success "Comprehensive status report generated: $report_file"
    echo "Report location: $report_file"
}

# Main verification function
main() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║              Comprehensive Production Verification                            ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Initialize log file
    mkdir -p "$(dirname "$LOG_FILE")"
    touch "$LOG_FILE"
    log "Starting comprehensive production verification"
    
    # Check root privileges
    check_root
    
    # Verify both deployments
    verify_hetzner_deployment
    verify_azure_deployment
    
    # Generate comprehensive report
    generate_comprehensive_report
    
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    Verification Completed                                    ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    status_update "Verification log available at: $LOG_FILE"
    status_update "For detailed information, check the generated status report"
    
    log "Comprehensive verification completed"
}

# Run main function
main "$@"
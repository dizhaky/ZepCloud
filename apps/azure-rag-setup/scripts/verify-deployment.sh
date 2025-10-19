#!/bin/bash
# Deployment Verification Script for Azure RAG System
# This script checks if all services are running correctly and provides a status report

set -euo pipefail

# Configuration
PROJECT_DIR="/opt/azure-rag-setup"
LOG_FILE="/var/log/azure-rag-verify.log"

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

# Check Docker services
check_docker_services() {
    status_update "Checking Docker services..."
    
    # Check if Docker is running
    if ! systemctl is-active --quiet docker; then
        error "Docker service is not running"
        return 1
    fi
    success "Docker service is running"
    
    # Try to find the project directory
    if [ ! -d "$PROJECT_DIR" ]; then
        # Try to find the project directory relative to this script
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
        if [ ! -d "$PROJECT_DIR" ]; then
            error "Project directory $PROJECT_DIR does not exist"
            return 1
        fi
    fi
    
    # Check if docker-compose.yml exists
    if [ ! -f "$PROJECT_DIR/docker-compose.yml" ]; then
        error "docker-compose.yml not found in $PROJECT_DIR"
        return 1
    fi
    
    # Check if services are running
    status_update "Checking service status..."
    
    # Get service status in JSON format
    local service_status
    service_status=$(cd "$PROJECT_DIR" && docker-compose ps --format json 2>/dev/null || true)
    
    if [ -z "$service_status" ]; then
        warning "No services found or unable to retrieve service status"
        return 0
    fi
    
    # Parse service status
    echo "$service_status" | jq -r '.[] | "Service: \(.Service), Status: \(.State), Health: \(.Health)"' 2>/dev/null | while read -r line; do
        echo "  $line"
    done || echo "$service_status" | while read -r line; do
        echo "  $line"
    done
    
    # Count services
    local total_services
    total_services=$(echo "$service_status" | jq -r 'length' 2>/dev/null || echo "0")
    
    if [ "$total_services" = "0" ]; then
        total_services=$(echo "$service_status" | wc -l)
    fi
    
    local running_services
    running_services=$(echo "$service_status" | jq -r '[.[] | select(.State == "running")] | length' 2>/dev/null || echo "0")
    
    if [ "$running_services" = "0" ]; then
        running_services=$(echo "$service_status" | grep -c "running" || echo "0")
    fi
    
    local healthy_services
    healthy_services=$(echo "$service_status" | jq -r '[.[] | select(.Health == "healthy")] | length' 2>/dev/null || echo "0")
    
    if [ "$healthy_services" = "0" ]; then
        healthy_services=$(echo "$service_status" | grep -c "healthy" || echo "0")
    fi
    
    status_update "Service Summary: $running_services/$total_services running, $healthy_services/$total_services healthy"
    
    if [ "$running_services" -eq "$total_services" ] && [ "$total_services" -gt 0 ]; then
        success "All services are running"
    elif [ "$total_services" -gt 0 ]; then
        local stopped_services=$((total_services - running_services))
        warning "$stopped_services services are not running"
    fi
    
    if [ "$healthy_services" -eq "$total_services" ] && [ "$total_services" -gt 0 ]; then
        success "All services are healthy"
    elif [ "$total_services" -gt 0 ]; then
        local unhealthy_services=$((total_services - healthy_services))
        warning "$unhealthy_services services are not healthy"
    fi
}

# Check service endpoints
check_service_endpoints() {
    status_update "Checking service endpoints..."
    
    # Service endpoints to check
    local endpoints=(
        "http://localhost:5001/health:Flask API"
        "http://localhost:9200/_cluster/health:Elasticsearch"
        "http://localhost:9998/tika:Apache Tika"
    )
    
    local working_endpoints=0
    local total_endpoints=${#endpoints[@]}
    
    for endpoint_info in "${endpoints[@]}"; do
        local url="${endpoint_info%%:*}"
        local name="${endpoint_info#*:}"
        
        # Add a small delay to avoid overwhelming services
        sleep 2
        
        if curl -sf "$url" > /dev/null 2>&1; then
            success "$name endpoint ($url) is accessible"
            ((working_endpoints++))
        else
            warning "$name endpoint ($url) is not accessible"
        fi
    done
    
    status_update "Endpoint Summary: $working_endpoints/$total_endpoints endpoints accessible"
}

# Check system resources
check_system_resources() {
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
    memory_usage=$(free | awk 'NR==2{printf "%.2f", $3*100/$2 }')
    
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
    cpu_load_int=$(echo "$cpu_load * 100" | bc | cut -d'.' -f1)
    
    # For a 4-core system, load average > 4.0 is high
    if [ "$cpu_load_int" -gt 400 ]; then
        warning "CPU load is high: ${cpu_load}"
    elif [ "$cpu_load_int" -gt 300 ]; then
        warning "CPU load is moderate: ${cpu_load}"
    else
        success "CPU load is normal: ${cpu_load}"
    fi
}

# Check security configuration
check_security() {
    status_update "Checking security configuration..."
    
    # Check firewall status
    if command -v ufw &> /dev/null && ufw status | grep -q "Status: active"; then
        success "Firewall is active"
    else
        warning "Firewall is not active"
    fi
    
    # Check environment file permissions if it exists
    local env_files=("$PROJECT_DIR/.env" "$PROJECT_DIR/env.elasticsearch")
    for env_file in "${env_files[@]}"; do
        if [ -f "$env_file" ]; then
            local env_perms
            env_perms=$(stat -c %a "$env_file" 2>/dev/null || echo "000")
            
            if [ "$env_perms" = "600" ] || [ "$env_perms" = "400" ]; then
                success "Environment file $env_file has secure permissions"
            else
                warning "Environment file $env_file permissions are not secure: $env_perms"
            fi
        fi
    done
    
    # Check for SSL certificates
    if [ -f "/etc/ssl/certs/azure-rag-cert.pem" ] && [ -f "/etc/ssl/private/azure-rag-key.pem" ]; then
        success "SSL certificates are installed"
    else
        warning "SSL certificates not found"
    fi
}

# Check Elasticsearch index
check_elasticsearch_index() {
    status_update "Checking Elasticsearch index..."
    
    # Load environment variables to get ELASTIC_PASSWORD
    local env_file=""
    if [ -f "$PROJECT_DIR/env.elasticsearch" ]; then
        env_file="$PROJECT_DIR/env.elasticsearch"
    elif [ -f "$PROJECT_DIR/.env" ]; then
        env_file="$PROJECT_DIR/.env"
    fi
    
    if [ -n "$env_file" ]; then
        set -a
        source "$env_file"
        set +a
    fi
    
    # Check if Elasticsearch is accessible
    if curl -u elastic:"${ELASTIC_PASSWORD:-YourStrongPassword123!}" -s http://localhost:9200/_cluster/health > /dev/null; then
        success "Elasticsearch is accessible"
        
        # Check if index exists
        local index_status
        index_status=$(curl -u elastic:"${ELASTIC_PASSWORD:-YourStrongPassword123!}" -s -o /dev/null -w "%{http_code}" http://localhost:9200/m365-documents)
        
        if [ "$index_status" = "200" ]; then
            success "Elasticsearch index exists"
            
            # Get document count
            local doc_count
            doc_count=$(curl -u elastic:"${ELASTIC_PASSWORD:-YourStrongPassword123!}" -s http://localhost:9200/m365-documents/_count | jq -r '.count' 2>/dev/null || echo "unknown")
            status_update "Index document count: $doc_count"
        else
            warning "Elasticsearch index does not exist or is not accessible"
        fi
    else
        warning "Elasticsearch is not accessible"
    fi
}

# Generate status report
generate_status_report() {
    status_update "Generating status report..."
    
    local report_file="/tmp/azure-rag-status-report-$(date +%Y%m%d-%H%M%S).txt"
    
    {
        echo "Azure RAG System Status Report"
        echo "Generated: $(date)"
        echo "========================================"
        echo ""
        
        echo "System Information:"
        uname -a
        echo ""
        
        echo "Docker Information:"
        docker --version
        echo ""
        
        echo "Docker Compose Status:"
        if [ -d "$PROJECT_DIR" ]; then
            cd "$PROJECT_DIR" && docker-compose ps 2>/dev/null || echo "Unable to retrieve Docker Compose status"
        else
            echo "Project directory not found"
        fi
        echo ""
        
        echo "Disk Usage:"
        df -h
        echo ""
        
        echo "Memory Usage:"
        free -h
        echo ""
        
        echo "CPU Load:"
        uptime
        echo ""
        
        echo "Network Connections:"
        netstat -tulpn | grep -E "(80|443|9200|5001|9998)" 2>/dev/null || echo "No relevant network connections found"
        echo ""
        
        echo "Firewall Status:"
        ufw status 2>/dev/null || echo "UFW not installed or accessible"
        echo ""
        
    } > "$report_file"
    
    success "Status report generated: $report_file"
    echo "Report location: $report_file"
}

# Main verification function
main() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                    Azure RAG System Verification                             ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Initialize log file
    mkdir -p "$(dirname "$LOG_FILE")"
    touch "$LOG_FILE"
    log "Starting Azure RAG System verification"
    
    # Execute verification steps
    if ! check_root; then
        exit 1
    fi
    
    if ! check_docker_services; then
        warning "Docker services check had issues"
    fi
    
    if ! check_service_endpoints; then
        warning "Service endpoints check had issues"
    fi
    
    if ! check_system_resources; then
        warning "System resources check had issues"
    fi
    
    if ! check_security; then
        warning "Security configuration check had issues"
    fi
    
    if ! check_elasticsearch_index; then
        warning "Elasticsearch index check had issues"
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
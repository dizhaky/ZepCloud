#!/bin/bash
# Production Verification Script for M365 RAG System
# This script performs comprehensive verification of the Hetzner M365 RAG deployment

set -euo pipefail

# Configuration
PROJECT_DIR="/data/m365-rag"
LOG_FILE="/var/log/m365-rag-production-verify.log"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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
    
    # Check if project directory exists
    if [ ! -d "$PROJECT_DIR" ]; then
        error "Project directory $PROJECT_DIR does not exist"
        return 1
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
    service_status=$(su - deploy -c "cd $PROJECT_DIR && docker compose ps --format json" 2>/dev/null || true)
    
    if [ -z "$service_status" ]; then
        warning "No services found or unable to retrieve service status"
        return 0
    fi
    
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
}

# Check service endpoints
check_service_endpoints() {
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
    
    # Check environment file permissions
    if [ -f "$PROJECT_DIR/.env" ]; then
        local env_perms
        env_perms=$(stat -c %a "$PROJECT_DIR/.env" 2>/dev/null || echo "000")
        
        if [ "$env_perms" = "600" ]; then
            success "Environment file has secure permissions"
        else
            warning "Environment file permissions are not secure: $env_perms"
        fi
    else
        warning "Environment file not found"
    fi
    
    # Check for fail2ban
    if systemctl is-active --quiet fail2ban; then
        success "Fail2ban is running"
    else
        warning "Fail2ban is not running"
    fi
}

# Check backup configuration
check_backup() {
    status_update "Checking backup configuration..."
    
    # Check if backup script exists and is executable
    if [ -f "$PROJECT_DIR/scripts/backup.sh" ] && [ -x "$PROJECT_DIR/scripts/backup.sh" ]; then
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
    
    # Check if cron job is configured
    if crontab -u deploy -l 2>/dev/null | grep -q "backup.sh"; then
        success "Backup cron job is configured"
    else
        warning "Backup cron job is not configured"
    fi
}

# Check monitoring and alerting
check_monitoring() {
    status_update "Checking monitoring and alerting..."
    
    # Check if Prometheus is accessible
    if curl -sf http://localhost:9090/status > /dev/null 2>&1; then
        success "Prometheus is accessible"
    else
        warning "Prometheus is not accessible"
    fi
    
    # Check if Grafana is accessible
    if curl -sf http://localhost:3000/login > /dev/null 2>&1; then
        success "Grafana is accessible"
    else
        warning "Grafana is not accessible"
    fi
    
    # Check if Elasticsearch exporter is running
    if curl -sf http://localhost:9114/metrics > /dev/null 2>&1; then
        success "Elasticsearch exporter is running"
    else
        warning "Elasticsearch exporter is not running"
    fi
}

# Check M365 integration
check_m365_integration() {
    status_update "Checking M365 integration..."
    
    # Check if M365 credentials are configured
    if [ -f "$PROJECT_DIR/.env" ]; then
        if grep -q "M365_CLIENT_ID" "$PROJECT_DIR/.env" && \
           grep -q "M365_CLIENT_SECRET" "$PROJECT_DIR/.env" && \
           grep -q "M365_TENANT_ID" "$PROJECT_DIR/.env"; then
            success "M365 credentials are configured"
        else
            warning "M365 credentials are not fully configured"
        fi
    else
        warning "Environment file not found"
    fi
    
    # Check if M365 sync script exists
    if [ -f "$PROJECT_DIR/api/m365_sync.py" ]; then
        success "M365 sync script exists"
    else
        warning "M365 sync script not found"
    fi
}

# Generate status report
generate_status_report() {
    status_update "Generating status report..."
    
    local report_file="/tmp/m365-rag-production-status-report-$(date +%Y%m%d-%H%M%S).txt"
    
    {
        echo "M365 RAG System Production Status Report"
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
        su - deploy -c "cd $PROJECT_DIR && docker compose ps" 2>/dev/null || echo "Unable to retrieve Docker Compose status"
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
        netstat -tulpn | grep -E "(80|443|9200|8000|9380|3000|9000|9090)" 2>/dev/null || echo "No relevant network connections found"
        echo ""
        
        echo "Firewall Status:"
        ufw status 2>/dev/null || echo "UFW not installed or accessible"
        echo ""
        
        echo "Cron Jobs:"
        crontab -u deploy -l 2>/dev/null || echo "No crontab for deploy user"
        echo ""
        
    } > "$report_file"
    
    success "Status report generated: $report_file"
    echo "Report location: $report_file"
}

# Main verification function
main() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║              M365 RAG System Production Verification                          ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Initialize log file
    mkdir -p "$(dirname "$LOG_FILE")"
    touch "$LOG_FILE"
    log "Starting M365 RAG System production verification"
    
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
    
    if ! check_backup; then
        warning "Backup configuration check had issues"
    fi
    
    if ! check_monitoring; then
        warning "Monitoring and alerting check had issues"
    fi
    
    if ! check_m365_integration; then
        warning "M365 integration check had issues"
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
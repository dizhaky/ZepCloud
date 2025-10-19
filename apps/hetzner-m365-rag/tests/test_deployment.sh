#!/bin/bash
# Deployment Verification Test Script
# Run after deployment to verify all services are working

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  M365 RAG Deployment Verification     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""

# Configuration
API_URL="http://localhost:8000"
RAGFLOW_URL="http://localhost:9380"
GRAFANA_URL="http://localhost:3000"
MINIO_URL="http://localhost:9001"
PROMETHEUS_URL="http://localhost:9090"

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
run_test() {
    local test_name=$1
    local test_command=$2
    
    echo -n "Testing $test_name... "
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

echo -e "${YELLOW}Phase 1: Docker Services${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Docker daemon running" "systemctl is-active docker"
run_test "All containers running" "[ \$(docker compose ps -q | wc -l) -ge 10 ]"
run_test "Elasticsearch healthy" "docker inspect elasticsearch | grep -q '\"Status\":\"healthy\"'"
run_test "PostgreSQL healthy" "docker inspect postgres | grep -q '\"Status\":\"healthy\"'"
run_test "Redis healthy" "docker inspect redis | grep -q '\"Status\":\"healthy\"'"
run_test "MinIO healthy" "docker inspect minio | grep -q '\"Status\":\"healthy\"'"

echo ""
echo -e "${YELLOW}Phase 2: Service Endpoints${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "API health check" "curl -sf $API_URL/health"
run_test "Elasticsearch cluster" "curl -sf http://localhost:9200/_cluster/health"
run_test "RAGFlow UI accessible" "curl -sf $RAGFLOW_URL"
run_test "Grafana accessible" "curl -sf $GRAFANA_URL"
run_test "MinIO console accessible" "curl -sf $MINIO_URL"
run_test "Prometheus accessible" "curl -sf $PROMETHEUS_URL"

echo ""
echo -e "${YELLOW}Phase 3: API Functionality${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "API accepts search requests" "curl -sf -X POST $API_URL/search -H 'Content-Type: application/json' -d '{\"query\":\"test\",\"top_k\":5}'"
run_test "API returns JSON" "curl -sf $API_URL/health | jq -e .status"

echo ""
echo -e "${YELLOW}Phase 4: Elasticsearch${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Elasticsearch cluster green/yellow" "curl -sf http://localhost:9200/_cluster/health | jq -e '.status' | grep -q 'green\\|yellow'"
run_test "Documents index exists" "curl -sf http://localhost:9200/documents"
run_test "Images index exists" "curl -sf http://localhost:9200/images"
run_test "Knowledge graph index exists" "curl -sf http://localhost:9200/knowledge_graph"

echo ""
echo -e "${YELLOW}Phase 5: PostgreSQL${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "PostgreSQL accepting connections" "docker exec postgres pg_isready -U raguser"
run_test "Database exists" "docker exec postgres psql -U raguser -d m365_rag -c 'SELECT 1'"
run_test "Tables created" "docker exec postgres psql -U raguser -d m365_rag -c '\\dt' | grep -q documents"

echo ""
echo -e "${YELLOW}Phase 6: Storage & Cache${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Redis responding" "docker exec redis redis-cli ping | grep -q PONG"
run_test "MinIO API accessible" "curl -sf http://localhost:9000/minio/health/live"
run_test "MinIO bucket exists" "docker exec minio mc ls local/ | grep -q m365-documents || true"

echo ""
echo -e "${YELLOW}Phase 7: Monitoring${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Prometheus collecting metrics" "curl -sf $PROMETHEUS_URL/api/v1/targets | jq -e '.data.activeTargets'"
run_test "Elasticsearch exporter running" "curl -sf http://localhost:9114/metrics"

echo ""
echo -e "${YELLOW}Phase 8: Security${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Firewall active" "ufw status | grep -q active"
run_test "Fail2ban running" "systemctl is-active fail2ban"
run_test "Environment file secured" "[ \$(stat -c %a /data/m365-rag/.env 2>/dev/null || echo 000) -eq 600 ]"

echo ""
echo -e "${YELLOW}Phase 9: Backups${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Backup script exists" "[ -f /data/m365-rag/scripts/backup.sh ]"
run_test "Backup script executable" "[ -x /data/m365-rag/scripts/backup.sh ]"
run_test "Backup directory exists" "[ -d /backup/m365-rag ]"
run_test "Cron job configured" "crontab -u deploy -l | grep -q backup.sh"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}Test Results${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ ALL TESTS PASSED!                  ║${NC}"
    echo -e "${GREEN}║  Deployment is healthy and ready       ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${YELLOW}╔════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║  ⚠️  SOME TESTS FAILED                 ║${NC}"
    echo -e "${YELLOW}║  Review failed tests above             ║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════╝${NC}"
    echo ""
    echo "Common issues:"
    echo "- Services still starting up (wait 60s and retry)"
    echo "- Missing API keys in .env file"
    echo "- Elasticsearch needs more memory"
    echo "- Firewall blocking connections"
    echo ""
    echo "Check logs: cd /data/m365-rag && docker compose logs --tail=100"
    exit 1
fi


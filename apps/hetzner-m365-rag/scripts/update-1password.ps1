# Update 1Password with Complete Deployment Information
# This script stores all credentials and configuration in 1Password

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Updating 1Password with Deployment Info" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# Check if 1Password CLI is installed
$opInstalled = Get-Command op -ErrorAction SilentlyContinue
if (-not $opInstalled) {
    Write-Host "[ERROR] 1Password CLI not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Install with:" -ForegroundColor Yellow
    Write-Host "  winget install 1Password.1Password-CLI" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "[OK] 1Password CLI found" -ForegroundColor Green

# Check if signed in
$signInCheck = op account list 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[INFO] Not signed in to 1Password. Signing in..." -ForegroundColor Yellow
    op signin
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] 1Password sign-in failed!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "[OK] 1Password authenticated" -ForegroundColor Green
Write-Host ""

$projectRoot = Split-Path -Parent $PSScriptRoot

# Read .env file
$envPath = Join-Path $projectRoot ".env"
if (-not (Test-Path $envPath)) {
    Write-Host "[ERROR] .env file not found!" -ForegroundColor Red
    Write-Host "Please run prepare-env.ps1 first!" -ForegroundColor Yellow
    exit 1
}

Write-Host "[INFO] Reading configuration..." -ForegroundColor Yellow

$envContent = Get-Content $envPath -Raw
$envLines = Get-Content $envPath

# Parse environment variables
$config = @{}
foreach ($line in $envLines) {
    if ($line -match '^([A-Z_]+)=(.+)$') {
        $key = $Matches[1]
        $value = $Matches[2]
        $config[$key] = $value
    }
}

# Read server info if exists
$serverInfoPath = Join-Path $projectRoot "SERVER_INFO.txt"
$serverIP = "Not yet created"
$serverName = "Not yet created"

if (Test-Path $serverInfoPath) {
    $serverContent = Get-Content $serverInfoPath -Raw
    if ($serverContent -match "IP Address: (.+)") {
        $serverIP = $Matches[1].Trim()
    }
    if ($serverContent -match "Server Name: (.+)") {
        $serverName = $Matches[1].Trim()
    }
}

Write-Host "[OK] Configuration loaded" -ForegroundColor Green
Write-Host ""

# Create/Update main deployment item
Write-Host "[STEP 1/5] Creating M365 RAG Deployment item..." -ForegroundColor Yellow

$deploymentNotes = @"
M365 RAG System - Complete Deployment Information

=== DEPLOYMENT STATUS ===
Status: $(if (Test-Path $serverInfoPath) { "DEPLOYED" } else { "CONFIGURED - Ready to Deploy" })
Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Environment: Production

=== HETZNER SERVER ===
Server Name: $serverName
Server IP: $serverIP
Console: https://console.hetzner.cloud/
Account: dizhaky@gmail.com

=== ACCESS URLS (After Deployment) ===
RAGFlow UI:  http://$serverIP:9380
FastAPI:     http://$serverIP:8000
API Docs:    http://$serverIP:8000/docs
Grafana:     http://$serverIP:3000
Prometheus:  http://$serverIP:9090
MinIO:       http://$serverIP:9001

=== AZURE AD ===
Tenant ID: $($config['M365_TENANT_ID'])
Client ID: $($config['M365_CLIENT_ID'])
Client Secret: $($config['M365_CLIENT_SECRET'])
Portal: https://portal.azure.com

=== SERVICE PASSWORDS ===
All service passwords are stored in separate items below.
See: M365 RAG - [Service Name] items

=== DOCUMENTATION ===
Location: C:\Dev\ZepCloud\apps\hetzner-m365-rag\
Main Guide: CLI_DEPLOYMENT_GUIDE.md
Quick Start: START_HERE.md

=== DEPLOYMENT COMMAND ===
cd C:\Dev\ZepCloud\apps\hetzner-m365-rag
.\DEPLOY_COMPLETE_CLI.ps1 -CreateServer

=== SSH ACCESS ===
ssh root@$serverIP
cd /opt/m365-rag

=== MONITORING ===
docker compose ps
docker compose logs -f
curl http://localhost:8000/health
"@

try {
    # Try to create new item
    $result = op item create `
        --category "Server" `
        --title "M365 RAG System - Deployment" `
        --vault Employee `
        --tags "m365,rag,hetzner,production" `
        "url=http://$serverIP:8000" `
        "username=admin" `
        "notesPlain=$deploymentNotes" `
        2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] Deployment item created!" -ForegroundColor Green
    } else {
        Write-Host "[INFO] Updating existing item..." -ForegroundColor Yellow
        # Item exists, try to update
        op item edit "M365 RAG System - Deployment" `
            --vault Employee `
            "notesPlain=$deploymentNotes" `
            2>&1 | Out-Null
        Write-Host "[SUCCESS] Deployment item updated!" -ForegroundColor Green
    }
} catch {
    Write-Host "[WARNING] Could not create/update deployment item: $_" -ForegroundColor Yellow
}

Write-Host ""

# Create/Update Elasticsearch item
Write-Host "[STEP 2/5] Creating Elasticsearch credentials..." -ForegroundColor Yellow

$esNotes = @"
Elasticsearch Credentials for M365 RAG System

URL: https://$serverIP:9200
Username: elastic
Password: $($config['ELASTIC_PASSWORD'])

Health Check:
curl -k -u elastic:$($config['ELASTIC_PASSWORD']) https://localhost:9200/_cluster/health

Configuration:
- Heap Size: 16GB
- SSL: Enabled (self-signed)
- Ports: 9200 (HTTPS), 9300 (transport)
"@

try {
    op item create `
        --category "Login" `
        --title "M365 RAG - Elasticsearch" `
        --vault Employee `
        --tags "m365,rag,elasticsearch,database" `
        "url=https://$serverIP:9200" `
        "username=elastic" `
        "password=$($config['ELASTIC_PASSWORD'])" `
        "notesPlain=$esNotes" `
        2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] Elasticsearch credentials stored!" -ForegroundColor Green
    } else {
        op item edit "M365 RAG - Elasticsearch" --vault Employee "password=$($config['ELASTIC_PASSWORD'])" 2>&1 | Out-Null
        Write-Host "[SUCCESS] Elasticsearch credentials updated!" -ForegroundColor Green
    }
} catch {
    Write-Host "[WARNING] Could not store Elasticsearch credentials" -ForegroundColor Yellow
}

Write-Host ""

# Create/Update PostgreSQL item
Write-Host "[STEP 3/5] Creating PostgreSQL credentials..." -ForegroundColor Yellow

$pgNotes = @"
PostgreSQL Credentials for M365 RAG System

Host: localhost (from server)
Port: 5432
Database: $($config['POSTGRES_DB'])
Username: $($config['POSTGRES_USER'])
Password: $($config['POSTGRES_PASSWORD'])

Connection String:
postgresql://$($config['POSTGRES_USER']):$($config['POSTGRES_PASSWORD'])@localhost:5432/$($config['POSTGRES_DB'])

Usage:
docker compose exec postgres psql -U $($config['POSTGRES_USER']) -d $($config['POSTGRES_DB'])
"@

try {
    op item create `
        --category "Database" `
        --title "M365 RAG - PostgreSQL" `
        --vault Employee `
        --tags "m365,rag,postgresql,database" `
        "url=postgresql://localhost:5432" `
        "username=$($config['POSTGRES_USER'])" `
        "password=$($config['POSTGRES_PASSWORD'])" `
        "database=$($config['POSTGRES_DB'])" `
        "notesPlain=$pgNotes" `
        2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] PostgreSQL credentials stored!" -ForegroundColor Green
    } else {
        op item edit "M365 RAG - PostgreSQL" --vault Employee "password=$($config['POSTGRES_PASSWORD'])" 2>&1 | Out-Null
        Write-Host "[SUCCESS] PostgreSQL credentials updated!" -ForegroundColor Green
    }
} catch {
    Write-Host "[WARNING] Could not store PostgreSQL credentials" -ForegroundColor Yellow
}

Write-Host ""

# Create/Update MinIO item
Write-Host "[STEP 4/5] Creating MinIO credentials..." -ForegroundColor Yellow

$minioNotes = @"
MinIO Credentials for M365 RAG System

Console URL: http://$serverIP:9001
API URL: http://$serverIP:9000
Access Key: $($config['MINIO_ROOT_USER'])
Secret Key: $($config['MINIO_ROOT_PASSWORD'])

Usage:
- Upload documents via console
- S3-compatible API for programmatic access
- Bucket: rag-documents (auto-created)
"@

try {
    op item create `
        --category "Login" `
        --title "M365 RAG - MinIO Storage" `
        --vault Employee `
        --tags "m365,rag,minio,storage,s3" `
        "url=http://$serverIP:9001" `
        "username=$($config['MINIO_ROOT_USER'])" `
        "password=$($config['MINIO_ROOT_PASSWORD'])" `
        "notesPlain=$minioNotes" `
        2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] MinIO credentials stored!" -ForegroundColor Green
    } else {
        op item edit "M365 RAG - MinIO Storage" --vault Employee "password=$($config['MINIO_ROOT_PASSWORD'])" 2>&1 | Out-Null
        Write-Host "[SUCCESS] MinIO credentials updated!" -ForegroundColor Green
    }
} catch {
    Write-Host "[WARNING] Could not store MinIO credentials" -ForegroundColor Yellow
}

Write-Host ""

# Create/Update Grafana item
Write-Host "[STEP 5/5] Creating Grafana credentials..." -ForegroundColor Yellow

$grafanaNotes = @"
Grafana Monitoring for M365 RAG System

URL: http://$serverIP:3000
Username: $($config['GRAFANA_USER'])
Password: $($config['GRAFANA_PASSWORD'])

Dashboards:
- System Overview
- Elasticsearch Cluster Health
- API Performance Metrics
- Query Analytics

Data Sources:
- Prometheus: http://prometheus:9090
- Elasticsearch: https://elasticsearch:9200
"@

try {
    op item create `
        --category "Login" `
        --title "M365 RAG - Grafana Monitoring" `
        --vault Employee `
        --tags "m365,rag,grafana,monitoring" `
        "url=http://$serverIP:3000" `
        "username=$($config['GRAFANA_USER'])" `
        "password=$($config['GRAFANA_PASSWORD'])" `
        "notesPlain=$grafanaNotes" `
        2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] Grafana credentials stored!" -ForegroundColor Green
    } else {
        op item edit "M365 RAG - Grafana Monitoring" --vault Employee "password=$($config['GRAFANA_PASSWORD'])" 2>&1 | Out-Null
        Write-Host "[SUCCESS] Grafana credentials updated!" -ForegroundColor Green
    }
} catch {
    Write-Host "[WARNING] Could not store Grafana credentials" -ForegroundColor Yellow
}

Write-Host ""

# Display summary
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  1Password Update Complete!" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Stored/Updated Items:" -ForegroundColor Green
Write-Host "  ✓ M365 RAG System - Deployment (main item)" -ForegroundColor White
Write-Host "  ✓ M365 RAG - Elasticsearch" -ForegroundColor White
Write-Host "  ✓ M365 RAG - PostgreSQL" -ForegroundColor White
Write-Host "  ✓ M365 RAG - MinIO Storage" -ForegroundColor White
Write-Host "  ✓ M365 RAG - Grafana Monitoring" -ForegroundColor White
Write-Host ""
Write-Host "All items saved in: Employee vault" -ForegroundColor Yellow
Write-Host "Tags: m365, rag, hetzner, production" -ForegroundColor Yellow
Write-Host ""
Write-Host "Access credentials anytime:" -ForegroundColor Yellow
Write-Host "  1Password -> Employee vault -> Search: M365 RAG" -ForegroundColor Cyan
Write-Host ""


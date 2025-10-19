# =============================================================================
# M365 RAG System - Automated WSL2 Deployment Script
# =============================================================================
# This script automates the entire deployment process in WSL2
# Run this AFTER WSL2 installation and system restart

param(
    [switch]$SkipWSLCheck,
    [switch]$SkipEnvCheck
)

$ErrorActionPreference = "Continue"

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "   M365 RAG - AUTOMATED WSL2 DEPLOYMENT" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

# -----------------------------------------------------------------------------
# Phase 1: Verify WSL2 is ready
# -----------------------------------------------------------------------------
if (-not $SkipWSLCheck) {
    Write-Host "Phase 1: Verifying WSL2 installation..." -ForegroundColor Yellow
    
    try {
        $wslStatus = wsl --status 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] WSL2 is not installed or not ready" -ForegroundColor Red
            Write-Host "Please run: wsl --install" -ForegroundColor Yellow
            Write-Host "Then restart your computer and run this script again." -ForegroundColor Yellow
            exit 1
        }
        Write-Host "[OK] WSL2 is installed" -ForegroundColor Green
    }
    catch {
        Write-Host "[ERROR] Could not check WSL2 status: $_" -ForegroundColor Red
        exit 1
    }
}

# -----------------------------------------------------------------------------
# Phase 2: Check environment configuration
# -----------------------------------------------------------------------------
if (-not $SkipEnvCheck) {
    Write-Host "`nPhase 2: Checking environment configuration..." -ForegroundColor Yellow
    
    $projectDir = Split-Path -Parent $PSScriptRoot
    $envFile = Join-Path $projectDir ".env"
    
    if (-not (Test-Path $envFile)) {
        Write-Host "[ERROR] .env file not found at: $envFile" -ForegroundColor Red
        Write-Host "Creating from template..." -ForegroundColor Yellow
        Copy-Item (Join-Path $projectDir ".env.example") -Destination $envFile
    }
    
    $envContent = Get-Content $envFile -Raw
    
    $missingConfigs = @()
    if ($envContent -match "M365_CLIENT_ID=your-" -or $envContent -match "M365_CLIENT_ID=`$") {
        $missingConfigs += "M365_CLIENT_ID"
    }
    if ($envContent -match "M365_CLIENT_SECRET=your-" -or $envContent -match "M365_CLIENT_SECRET=`$") {
        $missingConfigs += "M365_CLIENT_SECRET"
    }
    if ($envContent -match "M365_TENANT_ID=your-" -or $envContent -match "M365_TENANT_ID=`$") {
        $missingConfigs += "M365_TENANT_ID"
    }
    if ($envContent -match "OPENAI_API_KEY=your-" -or $envContent -match "OPENAI_API_KEY=`$") {
        $missingConfigs += "OPENAI_API_KEY"
    }
    
    if ($missingConfigs.Count -gt 0) {
        Write-Host "[WARN] The following required variables need configuration in .env:" -ForegroundColor Yellow
        foreach ($config in $missingConfigs) {
            Write-Host "  - $config" -ForegroundColor Red
        }
        Write-Host "`nPlease edit .env file with your actual credentials before continuing." -ForegroundColor Yellow
        Write-Host "Press Enter after updating .env, or Ctrl+C to exit and configure later..." -ForegroundColor Cyan
        $null = Read-Host
    }
    else {
        Write-Host "[OK] Environment configuration looks good" -ForegroundColor Green
    }
}

# -----------------------------------------------------------------------------
# Phase 3: Copy project to WSL2
# -----------------------------------------------------------------------------
Write-Host "`nPhase 3: Copying project to WSL2..." -ForegroundColor Yellow

$windowsProjectPath = (Get-Location).Path
$wslProjectPath = "/home/$(wsl whoami)/m365-rag"

Write-Host "Windows path: $windowsProjectPath" -ForegroundColor Gray
Write-Host "WSL path: $wslProjectPath" -ForegroundColor Gray

# Create directory in WSL
wsl bash -c "mkdir -p $wslProjectPath"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to create WSL directory" -ForegroundColor Red
    exit 1
}

# Copy files to WSL (excluding large directories)
Write-Host "Copying files to WSL (this may take a moment)..." -ForegroundColor Gray
wsl bash -c "rsync -av --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' --exclude='data' --exclude='logs' --exclude='backups' --exclude='node_modules' /mnt/c/Dev/ZepCloud/apps/hetzner-m365-rag/ $wslProjectPath/"

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Project copied to WSL2" -ForegroundColor Green
}
else {
    Write-Host "[WARN] rsync not available, using cp..." -ForegroundColor Yellow
    wsl bash -c "cp -r /mnt/c/Dev/ZepCloud/apps/hetzner-m365-rag/* $wslProjectPath/ 2>/dev/null || true"
    Write-Host "[OK] Project copied to WSL2" -ForegroundColor Green
}

# -----------------------------------------------------------------------------
# Phase 4: Install Docker in WSL2
# -----------------------------------------------------------------------------
Write-Host "`nPhase 4: Installing Docker in WSL2..." -ForegroundColor Yellow

$dockerInstallScript = @'
#!/bin/bash
set -e

echo "Checking if Docker is already installed..."
if command -v docker &> /dev/null; then
    echo "[OK] Docker is already installed"
    docker --version
    exit 0
fi

echo "Installing Docker..."

# Update package list
sudo apt-get update -qq

# Install prerequisites
sudo apt-get install -y -qq \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update -qq
sudo apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start Docker service
sudo service docker start

# Add current user to docker group
sudo usermod -aG docker $USER

echo "[OK] Docker installed successfully"
docker --version
'@

# Write install script to WSL
$dockerInstallScript | wsl bash -c "cat > /tmp/install-docker.sh"
wsl bash -c "chmod +x /tmp/install-docker.sh"

# Run install script
Write-Host "Running Docker installation (this may take 5-10 minutes)..." -ForegroundColor Gray
wsl bash -c "/tmp/install-docker.sh"

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Docker installed in WSL2" -ForegroundColor Green
}
else {
    Write-Host "[ERROR] Docker installation failed" -ForegroundColor Red
    Write-Host "You may need to install Docker Desktop instead: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# -----------------------------------------------------------------------------
# Phase 5: Generate SSL certificates
# -----------------------------------------------------------------------------
Write-Host "`nPhase 5: Generating SSL certificates..." -ForegroundColor Yellow

wsl bash -c "cd $wslProjectPath && chmod +x scripts/generate-es-certs.sh && ./scripts/generate-es-certs.sh"

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] SSL certificates generated" -ForegroundColor Green
}
else {
    Write-Host "[WARN] SSL certificate generation had issues, but continuing..." -ForegroundColor Yellow
}

# -----------------------------------------------------------------------------
# Phase 6: Start services with Docker Compose
# -----------------------------------------------------------------------------
Write-Host "`nPhase 6: Starting all services..." -ForegroundColor Yellow

$deployCommand = @'
cd $wslProjectPath
echo "Starting Docker Compose..."
sudo docker compose up -d

echo "Waiting for services to start (30 seconds)..."
sleep 30

echo "Checking service health..."
sudo docker compose ps

echo ""
echo "Testing API health endpoint..."
curl -s http://localhost:8000/health || echo "API not ready yet"
'@

wsl bash -c $deployCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Services started successfully" -ForegroundColor Green
}
else {
    Write-Host "[WARN] Some services may not have started correctly" -ForegroundColor Yellow
    Write-Host "Check logs with: wsl bash -c 'cd $wslProjectPath && sudo docker compose logs'" -ForegroundColor Gray
}

# -----------------------------------------------------------------------------
# Phase 7: Display access information
# -----------------------------------------------------------------------------
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "   DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Access URLs:" -ForegroundColor Yellow
Write-Host "  API:        http://localhost:8000" -ForegroundColor Cyan
Write-Host "  API Docs:   http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  RAGFlow:    http://localhost" -ForegroundColor Cyan
Write-Host "  Grafana:    http://localhost:3000 (admin / see .env)" -ForegroundColor Cyan
Write-Host "  Prometheus: http://localhost:9090" -ForegroundColor Cyan

Write-Host "`nUseful Commands:" -ForegroundColor Yellow
Write-Host "  View logs:       wsl bash -c 'cd $wslProjectPath && sudo docker compose logs -f'" -ForegroundColor Gray
Write-Host "  Check status:    wsl bash -c 'cd $wslProjectPath && sudo docker compose ps'" -ForegroundColor Gray
Write-Host "  Restart:         wsl bash -c 'cd $wslProjectPath && sudo docker compose restart'" -ForegroundColor Gray
Write-Host "  Stop:            wsl bash -c 'cd $wslProjectPath && sudo docker compose down'" -ForegroundColor Gray
Write-Host "  Enter WSL:       wsl" -ForegroundColor Gray
Write-Host "  SSH to project:  wsl bash -c 'cd $wslProjectPath && bash'" -ForegroundColor Gray

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "  1. Test API: curl http://localhost:8000/health" -ForegroundColor White
Write-Host "  2. Authenticate M365: curl -X POST http://localhost:8000/m365/auth" -ForegroundColor White
Write-Host "  3. Check documentation: .\DEPLOY_NOW.md" -ForegroundColor White

Write-Host "`n========================================`n" -ForegroundColor Green



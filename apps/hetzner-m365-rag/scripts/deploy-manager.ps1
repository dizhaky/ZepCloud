# =============================================================================
# M365 RAG System - Smart Deployment Manager
# =============================================================================
# Automatically detects environment and chooses best deployment method

$ErrorActionPreference = "Continue"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   SMART DEPLOYMENT MANAGER" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Navigate to project root
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
Set-Location $projectRoot

Write-Host "Project: M365 RAG System" -ForegroundColor White
Write-Host "Location: $projectRoot`n" -ForegroundColor Gray

# -----------------------------------------------------------------------------
# Environment Detection
# -----------------------------------------------------------------------------
Write-Host "Detecting deployment environment...`n" -ForegroundColor Yellow

$hasWSL = $false
$hasDocker = $false
$hasDockerDesktop = $false

# Check WSL2
Write-Host "[1/3] Checking WSL2..." -ForegroundColor Gray
try {
    $wslOutput = wsl --status 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0) {
        $hasWSL = $true
        Write-Host "      WSL2: Available" -ForegroundColor Green
    }
    else {
        Write-Host "      WSL2: Not installed" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "      WSL2: Not available" -ForegroundColor Yellow
}

# Check Docker Desktop
Write-Host "[2/3] Checking Docker Desktop..." -ForegroundColor Gray
if (Get-Process "Docker Desktop" -ErrorAction SilentlyContinue) {
    $hasDockerDesktop = $true
    Write-Host "      Docker Desktop: Running" -ForegroundColor Green
}
else {
    Write-Host "      Docker Desktop: Not running" -ForegroundColor Yellow
}

# Check Docker CLI
Write-Host "[3/3] Checking Docker CLI..." -ForegroundColor Gray
try {
    docker --version 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $hasDocker = $true
        Write-Host "      Docker CLI: Available" -ForegroundColor Green
    }
    else {
        Write-Host "      Docker CLI: Not found" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "      Docker CLI: Not found" -ForegroundColor Yellow
}

# -----------------------------------------------------------------------------
# Decision Logic
# -----------------------------------------------------------------------------
Write-Host "`nAnalyzing deployment options...`n" -ForegroundColor Yellow

if ($hasDocker -and $hasDockerDesktop) {
    # Best case: Docker Desktop is running
    Write-Host "SELECTED: Native Docker Desktop Deployment" -ForegroundColor Green -BackgroundColor Black
    Write-Host "Reason: Docker Desktop detected and running`n" -ForegroundColor Gray
    
    Write-Host "Executing deployment...`n" -ForegroundColor Yellow
    
    # Check/create .env
    if (-not (Test-Path ".env")) {
        Write-Host "[INFO] Creating .env from template..." -ForegroundColor Yellow
        Copy-Item ".env.example" -Destination ".env"
        Write-Host "[OK] .env created - please configure with your credentials`n" -ForegroundColor Green
    }
    
    # Generate SSL certs
    Write-Host "Generating SSL certificates..." -ForegroundColor Yellow
    & "bash" "scripts/generate-es-certs.sh"
    
    # Start services
    Write-Host "`nStarting all services with Docker Compose..." -ForegroundColor Yellow
    docker-compose up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n[SUCCESS] Deployment completed!" -ForegroundColor Green
        Write-Host "`nAccess URLs:" -ForegroundColor Yellow
        Write-Host "  API: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "  Docs: http://localhost:8000/docs" -ForegroundColor Cyan
        Write-Host "  RAGFlow: http://localhost" -ForegroundColor Cyan
        Write-Host "  Grafana: http://localhost:3000`n" -ForegroundColor Cyan
    }
    else {
        Write-Host "`n[ERROR] Deployment failed" -ForegroundColor Red
        Write-Host "Check logs with: docker-compose logs`n" -ForegroundColor Yellow
    }
}
elseif ($hasWSL) {
    # Good case: WSL2 is available
    Write-Host "SELECTED: WSL2 Automated Deployment" -ForegroundColor Green -BackgroundColor Black
    Write-Host "Reason: WSL2 detected, Docker can be installed automatically`n" -ForegroundColor Gray
    
    Write-Host "Launching WSL2 deployment script...`n" -ForegroundColor Yellow
    & "$scriptPath\auto-deploy-wsl.ps1"
}
else {
    # Need to install WSL2 first
    Write-Host "SELECTED: WSL2 Installation + Deployment" -ForegroundColor Green -BackgroundColor Black
    Write-Host "Reason: Best option for Windows development`n" -ForegroundColor Gray
    
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "   INSTALLATION REQUIRED" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    Write-Host "WSL2 is not installed. This is required for deployment." -ForegroundColor Yellow
    Write-Host "`nOptions:" -ForegroundColor White
    Write-Host "  [1] Install WSL2 now (RECOMMENDED)" -ForegroundColor Green
    Write-Host "  [2] Install Docker Desktop instead" -ForegroundColor Yellow
    Write-Host "  [3] Prepare for remote Hetzner deployment" -ForegroundColor Cyan
    Write-Host "  [4] Exit and install manually`n" -ForegroundColor Gray
    
    $choice = Read-Host "Select option (1-4)"
    
    switch ($choice) {
        "1" {
            Write-Host "`nInstalling WSL2..." -ForegroundColor Yellow
            Write-Host "This will:" -ForegroundColor White
            Write-Host "  - Enable Windows Subsystem for Linux" -ForegroundColor Gray
            Write-Host "  - Install Ubuntu distribution" -ForegroundColor Gray
            Write-Host "  - Require system restart" -ForegroundColor Gray
            Write-Host "`nPress Enter to continue or Ctrl+C to cancel..." -ForegroundColor Cyan
            $null = Read-Host
            
            Start-Process powershell -Verb RunAs -ArgumentList "wsl --install; Read-Host 'Installation complete. Press Enter to close'"
            
            Write-Host "`n[INFO] WSL2 installation started" -ForegroundColor Green
            Write-Host "[INFO] After installation and restart, run this script again:`n" -ForegroundColor Yellow
            Write-Host "  .\scripts\deploy-manager.ps1`n" -ForegroundColor Cyan
        }
        "2" {
            Write-Host "`nOpening Docker Desktop download page..." -ForegroundColor Yellow
            Start-Process "https://www.docker.com/products/docker-desktop"
            Write-Host "`n[INFO] After installing Docker Desktop, run this script again:`n" -ForegroundColor Yellow
            Write-Host "  .\scripts\deploy-manager.ps1`n" -ForegroundColor Cyan
        }
        "3" {
            Write-Host "`nPreparing for remote Hetzner deployment..." -ForegroundColor Yellow
            
            if (-not (Test-Path ".env")) {
                Copy-Item ".env.example" -Destination ".env"
                Write-Host "[OK] .env created from template" -ForegroundColor Green
            }
            
            Write-Host "`nDeployment package ready!" -ForegroundColor Green
            Write-Host "`nNext steps:" -ForegroundColor Yellow
            Write-Host "  1. Edit .env with your credentials" -ForegroundColor White
            Write-Host "  2. Transfer to server: scp -r . root@YOUR_SERVER_IP:/opt/m365-rag/" -ForegroundColor Cyan
            Write-Host "  3. SSH to server: ssh root@YOUR_SERVER_IP" -ForegroundColor Cyan
            Write-Host "  4. Run: cd /opt/m365-rag && ./scripts/deploy.sh`n" -ForegroundColor Cyan
            
            Write-Host "See DEPLOY_INSTRUCTIONS.txt for detailed guide`n" -ForegroundColor Gray
        }
        default {
            Write-Host "`nExiting. Run again when ready to deploy.`n" -ForegroundColor Yellow
        }
    }
}

Write-Host "========================================`n" -ForegroundColor Cyan



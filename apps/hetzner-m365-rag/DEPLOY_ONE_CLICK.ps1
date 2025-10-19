# M365 RAG System - One-Click Deployment Preparation
# This script automates the entire pre-deployment setup

param(
    [switch]$SkipAzureAD,
    [string]$ServerIP
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     M365 RAG System - One-Click Deployment Prep       ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$startTime = Get-Date

# Navigate to script directory
$scriptDir = $PSScriptRoot
cd $scriptDir

# Step 1: Generate Environment Configuration
Write-Host "[STEP 1/4] Generating secure environment configuration..." -ForegroundColor Yellow
if (Test-Path ".\scripts\prepare-env.ps1") {
    & ".\scripts\prepare-env.ps1"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Environment preparation failed!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[ERROR] prepare-env.ps1 not found!" -ForegroundColor Red
    exit 1
}

Write-Host "[SUCCESS] Step 1 complete!" -ForegroundColor Green
Write-Host ""

# Step 2: Create Azure AD App Registration
if (-not $SkipAzureAD) {
    Write-Host "[STEP 2/4] Creating Azure AD app registration..." -ForegroundColor Yellow
    
    # Check if Azure CLI is available
    $azInstalled = Get-Command az -ErrorAction SilentlyContinue
    
    if ($azInstalled) {
        if (Test-Path ".\scripts\create-azure-ad-app.ps1") {
            & ".\scripts\create-azure-ad-app.ps1"
            if ($LASTEXITCODE -ne 0) {
                Write-Host "[WARNING] Azure AD setup failed. You can do this manually." -ForegroundColor Yellow
                Write-Host "Run: .\scripts\azure-ad-setup-helper.ps1" -ForegroundColor White
            } else {
                Write-Host "[SUCCESS] Step 2 complete!" -ForegroundColor Green
            }
        } else {
            Write-Host "[WARNING] create-azure-ad-app.ps1 not found!" -ForegroundColor Yellow
        }
    } else {
        Write-Host "[INFO] Azure CLI not found. Skipping automated Azure AD setup." -ForegroundColor Yellow
        Write-Host "[INFO] Please run manually: .\scripts\azure-ad-setup-helper.ps1" -ForegroundColor Yellow
    }
} else {
    Write-Host "[STEP 2/4] Skipping Azure AD setup (--SkipAzureAD flag set)" -ForegroundColor Yellow
}

Write-Host ""

# Step 3: Create Deployment Archive
Write-Host "[STEP 3/4] Creating deployment archive..." -ForegroundColor Yellow
if (Test-Path ".\scripts\create-deployment-archive.ps1") {
    & ".\scripts\create-deployment-archive.ps1"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Archive creation failed!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[ERROR] create-deployment-archive.ps1 not found!" -ForegroundColor Red
    exit 1
}

Write-Host "[SUCCESS] Step 3 complete!" -ForegroundColor Green
Write-Host ""

# Step 4: Upload to Server (if ServerIP provided)
if ($ServerIP) {
    Write-Host "[STEP 4/4] Uploading to Hetzner server..." -ForegroundColor Yellow
    
    $archivePath = Join-Path (Split-Path -Parent $scriptDir) "hetzner-m365-rag-deploy.tar.gz"
    
    if (Test-Path $archivePath) {
        Write-Host "[INFO] Uploading archive to $ServerIP..." -ForegroundColor Yellow
        scp $archivePath "root@${ServerIP}:/tmp/"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[SUCCESS] Upload complete!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Now SSH into the server and run:" -ForegroundColor Yellow
            Write-Host "  ssh root@$ServerIP" -ForegroundColor Cyan
            Write-Host "  cd /tmp" -ForegroundColor Cyan
            Write-Host "  tar -xzf hetzner-m365-rag-deploy.tar.gz -C /opt/" -ForegroundColor Cyan
            Write-Host "  mv /opt/hetzner-m365-rag /opt/m365-rag" -ForegroundColor Cyan
            Write-Host "  cd /opt/m365-rag && chmod +x scripts/*.sh" -ForegroundColor Cyan
            Write-Host "  ./scripts/deploy.sh" -ForegroundColor Cyan
        } else {
            Write-Host "[ERROR] Upload failed!" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "[ERROR] Archive not found: $archivePath" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[STEP 4/4] Server upload skipped (no --ServerIP provided)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "When your server is ready, upload with:" -ForegroundColor Yellow
    $archivePath = Join-Path (Split-Path -Parent $scriptDir) "hetzner-m365-rag-deploy.tar.gz"
    Write-Host "  scp '$archivePath' root@SERVER_IP:/tmp/" -ForegroundColor Cyan
}

Write-Host ""

# Calculate duration
$endTime = Get-Date
$duration = $endTime - $startTime

# Final Summary
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║              Deployment Preparation Complete!          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Preparation completed in: $($duration.TotalMinutes.ToString('0.0')) minutes" -ForegroundColor Green
Write-Host ""
Write-Host "Files Created:" -ForegroundColor Yellow
Write-Host "  ✓ .env (with secure passwords)" -ForegroundColor Green
Write-Host "  ✓ PASSWORDS_GENERATED.txt" -ForegroundColor Green
Write-Host "  ✓ hetzner-m365-rag-deploy.tar.gz" -ForegroundColor Green

if (-not $SkipAzureAD) {
    Write-Host "  ✓ Azure AD app registration" -ForegroundColor Green
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host ""

if ($SkipAzureAD) {
    Write-Host "1. Create Azure AD app registration:" -ForegroundColor White
    Write-Host "   .\scripts\azure-ad-setup-helper.ps1" -ForegroundColor Cyan
    Write-Host ""
}

if (-not $ServerIP) {
    Write-Host "2. Order Hetzner AX52 server:" -ForegroundColor White
    Write-Host "   https://www.hetzner.com/dedicated-rootserver/matrix-ax" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "3. When server is ready, upload and deploy:" -ForegroundColor White
    Write-Host "   scp hetzner-m365-rag-deploy.tar.gz root@SERVER_IP:/tmp/" -ForegroundColor Cyan
    Write-Host "   ssh root@SERVER_IP" -ForegroundColor Cyan
    Write-Host "   cd /tmp && tar -xzf hetzner-m365-rag-deploy.tar.gz -C /opt/" -ForegroundColor Cyan
    Write-Host "   mv /opt/hetzner-m365-rag /opt/m365-rag" -ForegroundColor Cyan
    Write-Host "   cd /opt/m365-rag && chmod +x scripts/*.sh && ./scripts/deploy.sh" -ForegroundColor Cyan
} else {
    Write-Host "2. SSH into server and complete deployment:" -ForegroundColor White
    Write-Host "   ssh root@$ServerIP" -ForegroundColor Cyan
    Write-Host "   cd /tmp && tar -xzf hetzner-m365-rag-deploy.tar.gz -C /opt/" -ForegroundColor Cyan
    Write-Host "   mv /opt/hetzner-m365-rag /opt/m365-rag" -ForegroundColor Cyan
    Write-Host "   cd /opt/m365-rag && chmod +x scripts/*.sh && ./scripts/deploy.sh" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Documentation:" -ForegroundColor Yellow
Write-Host "  - DEPLOYMENT_READY_GUIDE.md - Complete guide" -ForegroundColor White
Write-Host "  - HETZNER_SERVER_SETUP.md - Server setup" -ForegroundColor White
Write-Host "  - README_DEPLOYMENT_READY.md - Quick reference" -ForegroundColor White
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""


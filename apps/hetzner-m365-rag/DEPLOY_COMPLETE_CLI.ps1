# M365 RAG System - Complete CLI-Based Deployment
# This script automates EVERYTHING using CLI tools

param(
    [switch]$CreateServer,
    [string]$ServerIP,
    [switch]$SkipAzureAD
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   M365 RAG - Complete CLI-Based Deployment (100%)   ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$startTime = Get-Date
Set-Location $PSScriptRoot

# Step 1: Environment Setup
Write-Host "[STEP 1/6] Setting up environment..." -ForegroundColor Yellow
if (Test-Path ".\scripts\prepare-env.ps1") {
    & ".\scripts\prepare-env.ps1"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Environment setup failed!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[ERROR] prepare-env.ps1 not found!" -ForegroundColor Red
    exit 1
}
Write-Host "[SUCCESS] Step 1 complete!" -ForegroundColor Green
Write-Host ""

# Step 2: Azure AD Setup
if (-not $SkipAzureAD) {
    Write-Host "[STEP 2/6] Setting up Azure AD app..." -ForegroundColor Yellow
    
    $azInstalled = Get-Command az -ErrorAction SilentlyContinue
    
    if ($azInstalled) {
        if (Test-Path ".\scripts\create-azure-ad-app.ps1") {
            & ".\scripts\create-azure-ad-app.ps1"
            if ($LASTEXITCODE -ne 0) {
                Write-Host "[WARNING] Automated Azure AD setup failed." -ForegroundColor Yellow
                Write-Host "[INFO] Falling back to manual input..." -ForegroundColor Yellow
                if (Test-Path ".\scripts\azure-ad-setup-helper.ps1") {
                    & ".\scripts\azure-ad-setup-helper.ps1"
                }
            }
        }
    } else {
        Write-Host "[INFO] Azure CLI not found. Using manual setup..." -ForegroundColor Yellow
        if (Test-Path ".\scripts\azure-ad-setup-helper.ps1") {
            & ".\scripts\azure-ad-setup-helper.ps1"
        }
    }
    Write-Host "[SUCCESS] Step 2 complete!" -ForegroundColor Green
} else {
    Write-Host "[STEP 2/6] Skipping Azure AD setup" -ForegroundColor Yellow
}
Write-Host ""

# Step 3: Create Deployment Archive
Write-Host "[STEP 3/6] Creating deployment archive..." -ForegroundColor Yellow
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

# Step 4: Create/Get Server
if ($CreateServer) {
    Write-Host "[STEP 4/6] Creating Hetzner Cloud server..." -ForegroundColor Yellow
    
    $hcloudInstalled = Get-Command hcloud -ErrorAction SilentlyContinue
    
    if ($hcloudInstalled) {
        if (Test-Path ".\scripts\setup-hetzner-server.ps1") {
            & ".\scripts\setup-hetzner-server.ps1"
            if ($LASTEXITCODE -eq 0) {
                # Extract server IP from SERVER_INFO.txt
                $serverInfoPath = ".\SERVER_INFO.txt"
                if (Test-Path $serverInfoPath) {
                    $serverInfo = Get-Content $serverInfoPath
                    $ServerIP = ($serverInfo | Select-String "IP Address: (.+)").Matches.Groups[1].Value.Trim()
                    Write-Host "[OK] Server IP: $ServerIP" -ForegroundColor Green
                }
            }
        }
    } else {
        Write-Host "[WARNING] hcloud CLI not found!" -ForegroundColor Yellow
        Write-Host "[INFO] Install with: https://github.com/hetznercloud/cli" -ForegroundColor Yellow
        Write-Host "[INFO] Or order dedicated server manually: https://www.hetzner.com/dedicated-rootserver/matrix-ax" -ForegroundColor Yellow
        $ServerIP = Read-Host "Enter server IP address"
    }
    
    Write-Host "[SUCCESS] Step 4 complete!" -ForegroundColor Green
} elseif ($ServerIP) {
    Write-Host "[STEP 4/6] Using provided server IP: $ServerIP" -ForegroundColor Yellow
} else {
    Write-Host "[STEP 4/6] Server creation skipped" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To create server later:" -ForegroundColor Yellow
    Write-Host "  .\scripts\setup-hetzner-server.ps1" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or order dedicated AX52:" -ForegroundColor Yellow
    Write-Host "  https://www.hetzner.com/dedicated-rootserver/matrix-ax" -ForegroundColor Cyan
}
Write-Host ""

# Step 5: Upload Archive
if ($ServerIP) {
    Write-Host "[STEP 5/6] Uploading to server..." -ForegroundColor Yellow
    
    $archivePath = Join-Path (Split-Path -Parent $PSScriptRoot) "hetzner-m365-rag-deploy.tar.gz"
    
    if (Test-Path $archivePath) {
        scp $archivePath "root@${ServerIP}:/tmp/"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[SUCCESS] Upload complete!" -ForegroundColor Green
        } else {
            Write-Host "[ERROR] Upload failed!" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "[ERROR] Archive not found: $archivePath" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[STEP 5/6] Upload skipped (no server IP)" -ForegroundColor Yellow
}
Write-Host ""

# Step 6: Deploy on Server
if ($ServerIP) {
    Write-Host "[STEP 6/6] Deploying on server..." -ForegroundColor Yellow
    
    if (Test-Path ".\scripts\deploy-to-server.ps1") {
        & ".\scripts\deploy-to-server.ps1" -ServerIP $ServerIP -SkipUpload
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[SUCCESS] Step 6 complete!" -ForegroundColor Green
        } else {
            Write-Host "[ERROR] Deployment failed!" -ForegroundColor Red
            exit 1
        }
    }
} else {
    Write-Host "[STEP 6/6] Deployment skipped (no server IP)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "When server is ready, deploy with:" -ForegroundColor Yellow
    Write-Host "  .\scripts\deploy-to-server.ps1 -ServerIP YOUR_SERVER_IP" -ForegroundColor Cyan
}
Write-Host ""

# Final Summary
$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║            Deployment Process Complete!              ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Completed in: $($duration.TotalMinutes.ToString('0.0')) minutes" -ForegroundColor Green
Write-Host ""

if ($ServerIP) {
    Write-Host "Your M365 RAG System is now running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Access URLs:" -ForegroundColor Yellow
    Write-Host "  RAGFlow UI:  http://$ServerIP:9380" -ForegroundColor Cyan
    Write-Host "  FastAPI:     http://$ServerIP:8000" -ForegroundColor Cyan
    Write-Host "  API Docs:    http://$ServerIP:8000/docs" -ForegroundColor Cyan
    Write-Host "  Grafana:     http://$ServerIP:3000" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host "Preparation Complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "  1. Create server: .\scripts\setup-hetzner-server.ps1" -ForegroundColor White
    Write-Host "  2. Or order AX52: https://www.hetzner.com/dedicated-rootserver/matrix-ax" -ForegroundColor White
    Write-Host "  3. Deploy: .\scripts\deploy-to-server.ps1 -ServerIP YOUR_IP" -ForegroundColor White
    Write-Host ""
}

Write-Host "Documentation:" -ForegroundColor Yellow
Write-Host "  - START_HERE.md - Quick guide" -ForegroundColor White
Write-Host "  - FINAL_DEPLOYMENT_SUMMARY.md - Complete summary" -ForegroundColor White
Write-Host ""


# Deploy to Hetzner Server - Automated Upload and Deployment

param(
    [Parameter(Mandatory=$true)]
    [string]$ServerIP,
    [switch]$SkipUpload
)

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Deploying to Hetzner Server" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = Split-Path -Parent $PSScriptRoot
$archiveName = "hetzner-m365-rag-deploy.tar.gz"
$archivePath = Join-Path (Split-Path -Parent $projectRoot) $archiveName

# Upload deployment package
if (-not $SkipUpload) {
    Write-Host "[STEP 1/2] Uploading deployment package..." -ForegroundColor Yellow
    Write-Host "  From: $archivePath" -ForegroundColor Gray
    Write-Host "  To: root@${ServerIP}:/tmp/" -ForegroundColor Gray
    Write-Host ""
    
    if (-not (Test-Path $archivePath)) {
        Write-Host "[ERROR] Deployment archive not found!" -ForegroundColor Red
        Write-Host "Please run: .\scripts\create-deployment-archive.ps1" -ForegroundColor Yellow
        exit 1
    }
    
    scp $archivePath "root@${ServerIP}:/tmp/"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Upload failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "[SUCCESS] Upload complete!" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "[STEP 1/2] Skipping upload (--SkipUpload flag set)" -ForegroundColor Yellow
    Write-Host ""
}

# Deploy on server
Write-Host "[STEP 2/2] Deploying on server..." -ForegroundColor Yellow
Write-Host "  Connecting to: root@$ServerIP" -ForegroundColor Gray
Write-Host ""

$deployScript = @"
#!/bin/bash
set -e

echo "[INFO] Extracting deployment package..."
cd /tmp
tar -xzf hetzner-m365-rag-deploy.tar.gz -C /opt/
mv /opt/hetzner-m365-rag /opt/m365-rag 2>/dev/null || true

echo "[INFO] Setting permissions..."
cd /opt/m365-rag
chmod +x scripts/*.sh

echo "[INFO] Starting deployment..."
./scripts/deploy.sh

echo "[SUCCESS] Deployment complete!"
"@

# Save script to temp file
$tempScript = "$env:TEMP\deploy-script.sh"
$deployScript | Out-File -FilePath $tempScript -Encoding UTF8 -NoNewline

# Upload and execute script
scp $tempScript "root@${ServerIP}:/tmp/deploy-script.sh"
ssh root@$ServerIP "chmod +x /tmp/deploy-script.sh && /tmp/deploy-script.sh"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host "  Deployment Complete!" -ForegroundColor Cyan
    Write-Host "===================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Your M365 RAG system is now running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Access URLs:" -ForegroundColor Yellow
    Write-Host "  RAGFlow UI:  http://$ServerIP:9380" -ForegroundColor Cyan
    Write-Host "  FastAPI:     http://$ServerIP:8000" -ForegroundColor Cyan
    Write-Host "  API Docs:    http://$ServerIP:8000/docs" -ForegroundColor Cyan
    Write-Host "  Grafana:     http://$ServerIP:3000" -ForegroundColor Cyan
    Write-Host "  Prometheus:  http://$ServerIP:9090" -ForegroundColor Cyan
    Write-Host "  MinIO:       http://$ServerIP:9001" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "  1. Access RAGFlow at http://$ServerIP:9380" -ForegroundColor White
    Write-Host "  2. Configure M365 authentication" -ForegroundColor White
    Write-Host "  3. Start indexing your SharePoint/OneDrive content" -ForegroundColor White
    Write-Host ""
    Write-Host "Verify deployment:" -ForegroundColor Yellow
    Write-Host "  ssh root@$ServerIP" -ForegroundColor Cyan
    Write-Host "  cd /opt/m365-rag && docker compose ps" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "[ERROR] Deployment failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check logs with:" -ForegroundColor Yellow
    Write-Host "  ssh root@$ServerIP" -ForegroundColor Cyan
    Write-Host "  cd /opt/m365-rag && docker compose logs" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

# Cleanup
Remove-Item $tempScript -Force


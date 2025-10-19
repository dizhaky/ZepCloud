# Create Deployment Archive for Hetzner Server
# This script creates a tar.gz archive ready for upload

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Creating Deployment Archive" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = Split-Path -Parent $PSScriptRoot
$archiveName = "hetzner-m365-rag-deploy.tar.gz"
$archivePath = Join-Path (Split-Path -Parent $projectRoot) $archiveName

# Check if .env exists
$envPath = Join-Path $projectRoot ".env"
if (-not (Test-Path $envPath)) {
    Write-Host "[ERROR] .env file not found!" -ForegroundColor Red
    Write-Host "Please run prepare-env.ps1 first!" -ForegroundColor Yellow
    exit 1
}

# Check if Azure AD credentials are configured
$envContent = Get-Content $envPath -Raw
if ($envContent -match 'M365_CLIENT_ID=YOUR_AZURE_APP_CLIENT_ID_HERE') {
    Write-Host "[WARNING] Azure AD credentials not configured in .env!" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continue anyway? (yes/no)"
    if ($continue -ne "yes") {
        Write-Host "Cancelled. Please configure Azure AD credentials first." -ForegroundColor Yellow
        Write-Host "Run: .\scripts\azure-ad-setup-helper.ps1" -ForegroundColor White
        exit 0
    }
}

Write-Host "[INFO] Creating deployment archive..." -ForegroundColor Yellow
Write-Host ""

# Check if WSL is available
$wslAvailable = $null -ne (Get-Command wsl -ErrorAction SilentlyContinue)

if ($wslAvailable) {
    Write-Host "[INFO] Using WSL to create tar.gz archive..." -ForegroundColor Yellow
    
    # Convert Windows path to WSL path
    $wslProjectPath = $projectRoot -replace '\\', '/' -replace 'C:', '/mnt/c'
    $wslArchivePath = $archivePath -replace '\\', '/' -replace 'C:', '/mnt/c'
    
    # Create archive
    wsl tar -czf $wslArchivePath -C $wslProjectPath .
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] Archive created: $archivePath" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Failed to create archive!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[ERROR] WSL not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install WSL or manually create the archive:" -ForegroundColor Yellow
    Write-Host "  1. Install WSL: wsl --install" -ForegroundColor White
    Write-Host "  2. Or use 7-Zip/WinRAR to create tar.gz" -ForegroundColor White
    Write-Host "  3. Or create on Linux/Mac: tar -czf $archiveName ." -ForegroundColor White
    exit 1
}

# Display file info
$archiveInfo = Get-Item $archivePath
$sizeMB = [math]::Round($archiveInfo.Length / 1MB, 2)

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Archive Ready" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Archive created:" -ForegroundColor Green
Write-Host "  Path: $archivePath" -ForegroundColor White
Write-Host "  Size: $sizeMB MB" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Create Hetzner server (choose one):" -ForegroundColor White
Write-Host "   a) Automated: .\scripts\setup-hetzner-server.ps1" -ForegroundColor Cyan
Write-Host "   b) Manual: Order AX52 at https://www.hetzner.com/dedicated-rootserver/matrix-ax" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Deploy to server:" -ForegroundColor White
Write-Host "   .\scripts\deploy-to-server.ps1 -ServerIP YOUR_SERVER_IP" -ForegroundColor Cyan
Write-Host ""
Write-Host "For detailed instructions, see:" -ForegroundColor Yellow
Write-Host "  - START_HERE.md" -ForegroundColor White
Write-Host "  - HETZNER_SERVER_SETUP.md" -ForegroundColor White
Write-Host ""


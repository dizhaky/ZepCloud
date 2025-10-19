# Hetzner Server Setup - Automated via hcloud CLI
# This script creates and configures a Hetzner Cloud server

param(
    [string]$ServerName = "m365-rag-prod",
    [string]$ServerType = "cx51",  # 8 cores, 32GB RAM - good for testing, upgrade to dedicated later
    [string]$Location = "fsn1",    # Falkenstein, Germany
    [string]$Image = "ubuntu-24.04"
)

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Hetzner Cloud Server Setup - Automated" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# Check if hcloud is installed
$hcloudInstalled = Get-Command hcloud -ErrorAction SilentlyContinue
if (-not $hcloudInstalled) {
    Write-Host "[ERROR] Hetzner Cloud CLI (hcloud) is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Install with:" -ForegroundColor Yellow
    Write-Host "  winget install hetzner.hcloud-cli" -ForegroundColor White
    Write-Host ""
    Write-Host "Or download from: https://github.com/hetznercloud/cli/releases" -ForegroundColor White
    exit 1
}

Write-Host "[OK] hcloud CLI found" -ForegroundColor Green

# Check for API token
$apiToken = $env:HCLOUD_TOKEN
if (-not $apiToken) {
    Write-Host ""
    Write-Host "[INFO] HCLOUD_TOKEN not found in environment" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To get your API token:" -ForegroundColor White
    Write-Host "  1. Go to: https://console.hetzner.cloud/" -ForegroundColor Gray
    Write-Host "  2. Select your project (or create one)" -ForegroundColor Gray
    Write-Host "  3. Go to: Security > API Tokens" -ForegroundColor Gray
    Write-Host "  4. Click 'Generate API Token'" -ForegroundColor Gray
    Write-Host "  5. Name: 'M365-RAG-Deployment'" -ForegroundColor Gray
    Write-Host "  6. Permissions: Read & Write" -ForegroundColor Gray
    Write-Host "  7. Copy the token" -ForegroundColor Gray
    Write-Host ""
    
    $apiToken = Read-Host "Enter your Hetzner Cloud API token"
    
    if ([string]::IsNullOrWhiteSpace($apiToken)) {
        Write-Host "[ERROR] API token is required!" -ForegroundColor Red
        exit 1
    }
    
    # Set for current session
    $env:HCLOUD_TOKEN = $apiToken
    
    # Optionally save to .env
    $projectRoot = Split-Path -Parent $PSScriptRoot
    $envPath = Join-Path $projectRoot ".env"
    
    if (Test-Path $envPath) {
        Write-Host ""
        $save = Read-Host "Save token to .env file? (yes/no)"
        if ($save -eq "yes") {
            Add-Content -Path $envPath -Value "`nHCLOUD_TOKEN=$apiToken"
            Write-Host "[OK] Token saved to .env" -ForegroundColor Green
        }
    }
}

Write-Host "[OK] API token configured" -ForegroundColor Green
Write-Host ""

# Create SSH key if not exists
Write-Host "[INFO] Checking SSH key..." -ForegroundColor Yellow
$sshKeyPath = "$env:USERPROFILE\.ssh\id_ed25519"
$sshPubKeyPath = "$sshKeyPath.pub"

if (-not (Test-Path $sshPubKeyPath)) {
    Write-Host "[INFO] Generating SSH key..." -ForegroundColor Yellow
    ssh-keygen -t ed25519 -C "m365-rag-deployment" -f $sshKeyPath -N '""'
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] SSH key generation failed!" -ForegroundColor Red
        exit 1
    }
}

$sshPubKey = Get-Content $sshPubKeyPath -Raw
Write-Host "[OK] SSH key ready" -ForegroundColor Green

# Upload SSH key to Hetzner
Write-Host "[INFO] Uploading SSH key to Hetzner..." -ForegroundColor Yellow

$existingKey = hcloud ssh-key list -o noheader | Select-String "m365-rag-key"
if ($existingKey) {
    Write-Host "[OK] SSH key already uploaded" -ForegroundColor Green
    $sshKeyName = "m365-rag-key"
} else {
    hcloud ssh-key create --name m365-rag-key --public-key-from-file $sshPubKeyPath
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] SSH key uploaded" -ForegroundColor Green
        $sshKeyName = "m365-rag-key"
    } else {
        Write-Host "[ERROR] Failed to upload SSH key!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Create server
Write-Host "[INFO] Creating Hetzner Cloud server..." -ForegroundColor Yellow
Write-Host "  Name: $ServerName" -ForegroundColor Gray
Write-Host "  Type: $ServerType" -ForegroundColor Gray
Write-Host "  Location: $Location" -ForegroundColor Gray
Write-Host "  Image: $Image" -ForegroundColor Gray
Write-Host ""

$serverOutput = hcloud server create `
    --name $ServerName `
    --type $ServerType `
    --location $Location `
    --image $Image `
    --ssh-key $sshKeyName `
    2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Server creation failed!" -ForegroundColor Red
    Write-Host $serverOutput -ForegroundColor Red
    exit 1
}

Write-Host "[SUCCESS] Server created!" -ForegroundColor Green
Write-Host ""

# Get server details
Write-Host "[INFO] Getting server details..." -ForegroundColor Yellow
Start-Sleep -Seconds 5  # Wait for server to initialize

$serverInfo = hcloud server describe $ServerName -o json | ConvertFrom-Json
$serverIP = $serverInfo.public_net.ipv4.ip

Write-Host "[OK] Server IP: $serverIP" -ForegroundColor Green
Write-Host ""

# Wait for SSH to be ready
Write-Host "[INFO] Waiting for SSH to be ready..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0

while ($attempt -lt $maxAttempts) {
    $attempt++
    Write-Host "  Attempt $attempt/$maxAttempts..." -ForegroundColor Gray
    
    $sshTest = ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@$serverIP "echo 'ready'" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] SSH is ready!" -ForegroundColor Green
        break
    }
    
    Start-Sleep -Seconds 10
}

if ($attempt -eq $maxAttempts) {
    Write-Host "[ERROR] SSH connection timeout!" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Display summary
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Server Ready!" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server Details:" -ForegroundColor Green
Write-Host "  Name: $ServerName" -ForegroundColor White
Write-Host "  IP Address: $serverIP" -ForegroundColor White
Write-Host "  Type: $ServerType" -ForegroundColor White
Write-Host "  Location: $Location" -ForegroundColor White
Write-Host "  SSH Key: $sshKeyName" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Test SSH connection:" -ForegroundColor White
Write-Host "     ssh root@$serverIP" -ForegroundColor Cyan
Write-Host ""
Write-Host "  2. Upload deployment package:" -ForegroundColor White
Write-Host "     scp hetzner-m365-rag-deploy.tar.gz root@${serverIP}:/tmp/" -ForegroundColor Cyan
Write-Host ""
Write-Host "  3. Deploy to server:" -ForegroundColor White
Write-Host "     ssh root@$serverIP" -ForegroundColor Cyan
Write-Host "     cd /tmp && tar -xzf hetzner-m365-rag-deploy.tar.gz -C /opt/" -ForegroundColor Cyan
Write-Host "     mv /opt/hetzner-m365-rag /opt/m365-rag" -ForegroundColor Cyan
Write-Host "     cd /opt/m365-rag && chmod +x scripts/*.sh && ./scripts/deploy.sh" -ForegroundColor Cyan
Write-Host ""
Write-Host "Or run automated deployment:" -ForegroundColor Yellow
Write-Host "  .\scripts\deploy-to-server.ps1 -ServerIP $serverIP" -ForegroundColor Cyan
Write-Host ""

# Save server info
$projectRoot = Split-Path -Parent $PSScriptRoot
$serverInfoPath = Join-Path $projectRoot "SERVER_INFO.txt"

$serverInfoContent = @"
Hetzner Cloud Server Information
Created: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

Server Name: $ServerName
IP Address: $serverIP
Server Type: $ServerType
Location: $Location
Image: $Image
SSH Key: $sshKeyName

SSH Connection:
ssh root@$serverIP

Deployment Archive:
scp hetzner-m365-rag-deploy.tar.gz root@${serverIP}:/tmp/

Hetzner Console:
https://console.hetzner.cloud/

API Token: ${apiToken:0:8}...
"@

$serverInfoContent | Out-File -FilePath $serverInfoPath -Encoding UTF8

Write-Host "[OK] Server info saved to: $serverInfoPath" -ForegroundColor Green
Write-Host ""


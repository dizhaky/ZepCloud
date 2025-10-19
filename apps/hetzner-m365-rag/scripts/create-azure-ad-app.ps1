# Azure AD App Registration - Automated Creation Script
# This script creates the M365 RAG System app registration using Azure CLI

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Azure AD App Registration - Automated Setup" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Azure CLI is installed
$azInstalled = Get-Command az -ErrorAction SilentlyContinue
if (-not $azInstalled) {
    Write-Host "[ERROR] Azure CLI is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Azure CLI:" -ForegroundColor Yellow
    Write-Host "  1. Download: https://aka.ms/installazurecliwindows" -ForegroundColor White
    Write-Host "  2. Or run: winget install -e --id Microsoft.AzureCLI" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "[OK] Azure CLI found" -ForegroundColor Green

# Check if logged in
Write-Host "[INFO] Checking Azure login status..." -ForegroundColor Yellow
$accountCheck = az account show 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "[INFO] Not logged in to Azure. Starting login..." -ForegroundColor Yellow
    az login --use-device-code
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Azure login failed!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "[OK] Azure login verified" -ForegroundColor Green
Write-Host ""

# Get tenant info
Write-Host "[INFO] Getting tenant information..." -ForegroundColor Yellow
$tenantId = (az account show --query tenantId -o tsv)
$subscriptionName = (az account show --query name -o tsv)

Write-Host "[OK] Tenant ID: $tenantId" -ForegroundColor Green
Write-Host "[OK] Subscription: $subscriptionName" -ForegroundColor Green
Write-Host ""

# Create app registration
Write-Host "[INFO] Creating Azure AD app registration..." -ForegroundColor Yellow
Write-Host "  Name: M365 RAG System" -ForegroundColor Gray
Write-Host "  Redirect URI: http://localhost:8000" -ForegroundColor Gray
Write-Host ""

$appJson = az ad app create `
    --display-name "M365 RAG System" `
    --sign-in-audience AzureADMyOrg `
    --web-redirect-uris "http://localhost:8000" `
    2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to create app registration!" -ForegroundColor Red
    Write-Host $appJson -ForegroundColor Red
    exit 1
}

$app = $appJson | ConvertFrom-Json
$appId = $app.appId
$objectId = $app.id

Write-Host "[SUCCESS] App registration created!" -ForegroundColor Green
Write-Host "  Application (client) ID: $appId" -ForegroundColor White
Write-Host ""

# Create client secret
Write-Host "[INFO] Creating client secret..." -ForegroundColor Yellow
$secretJson = az ad app credential reset --id $appId --append --display-name "M365 RAG System Secret" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to create client secret!" -ForegroundColor Red
    Write-Host $secretJson -ForegroundColor Red
    exit 1
}

$secret = $secretJson | ConvertFrom-Json
$clientSecret = $secret.password

Write-Host "[SUCCESS] Client secret created!" -ForegroundColor Green
Write-Host ""

# Add Microsoft Graph API permissions
Write-Host "[INFO] Adding Microsoft Graph API permissions..." -ForegroundColor Yellow

$permissions = @(
    @{ id = "df85f4d6-205c-4ac5-a5ea-6bf408dba283"; type = "Scope" }  # Files.ReadWrite.All
    @{ id = "205e70e5-aba6-4c52-a976-6d2d46c48043"; type = "Scope" }  # Sites.ReadWrite.All
    @{ id = "570282fd-fa5c-430d-a7fd-fc8dc98a9dca"; type = "Scope" }  # Mail.Read
    @{ id = "e1fe6dd8-ba31-4d61-89e7-88639da4683d"; type = "Scope" }  # User.Read
    @{ id = "a154be20-db9c-4678-8ab7-66f6cc099a59"; type = "Scope" }  # User.Read.All
)

foreach ($perm in $permissions) {
    $permId = $perm.id
    $permType = $perm.type
    
    az ad app permission add `
        --id $appId `
        --api 00000003-0000-0000-c000-000000000000 `
        --api-permissions "$permId=$permType" `
        2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Added permission: $permId" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "[INFO] Granting admin consent..." -ForegroundColor Yellow
az ad app permission admin-consent --id $appId 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "[SUCCESS] Admin consent granted!" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Could not auto-grant admin consent. You may need to do this manually." -ForegroundColor Yellow
}

Write-Host ""

# Update .env file
Write-Host "[INFO] Updating .env file..." -ForegroundColor Yellow

$projectRoot = Split-Path -Parent $PSScriptRoot
$envPath = Join-Path $projectRoot ".env"

if (Test-Path $envPath) {
    $envContent = Get-Content $envPath -Raw
    
    $envContent = $envContent -replace 'M365_CLIENT_ID=YOUR_AZURE_APP_CLIENT_ID_HERE', "M365_CLIENT_ID=$appId"
    $envContent = $envContent -replace 'M365_CLIENT_SECRET=YOUR_AZURE_APP_CLIENT_SECRET_HERE', "M365_CLIENT_SECRET=$clientSecret"
    $envContent = $envContent -replace 'M365_TENANT_ID=YOUR_AZURE_TENANT_ID_HERE', "M365_TENANT_ID=$tenantId"
    
    $envContent | Out-File -FilePath $envPath -Encoding UTF8 -NoNewline
    
    Write-Host "[SUCCESS] .env file updated!" -ForegroundColor Green
} else {
    Write-Host "[WARNING] .env file not found. Please run prepare-env.ps1 first!" -ForegroundColor Yellow
}

Write-Host ""

# Store credentials in 1Password if available
$opInstalled = Get-Command op -ErrorAction SilentlyContinue
if ($opInstalled) {
    Write-Host "[INFO] Storing credentials in 1Password..." -ForegroundColor Yellow
    
    try {
        $notes = @"
M365 RAG System - Azure AD App Registration

Application (client) ID: $appId
Directory (tenant) ID: $tenantId
Client Secret: $clientSecret

Redirect URI: http://localhost:8000
Permissions: Files.ReadWrite.All, Sites.ReadWrite.All, Mail.Read, User.Read.All

Created: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
"@
        
        op item create `
            --category "API Credential" `
            --title "M365 RAG System - Azure AD" `
            --vault Employee `
            username="M365 RAG System" `
            credential=$clientSecret `
            "notesPlain=$notes" `
            2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[SUCCESS] Credentials stored in 1Password!" -ForegroundColor Green
        }
    } catch {
        Write-Host "[WARNING] Could not store in 1Password: $_" -ForegroundColor Yellow
    }
}

Write-Host ""

# Display summary
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Azure AD App Registration Complete!" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Application Details:" -ForegroundColor Green
Write-Host "  Name: M365 RAG System" -ForegroundColor White
Write-Host "  Application (client) ID: $appId" -ForegroundColor White
Write-Host "  Directory (tenant) ID: $tenantId" -ForegroundColor White
Write-Host "  Client Secret: $clientSecret" -ForegroundColor White
Write-Host ""
Write-Host "These credentials have been added to:" -ForegroundColor Yellow
Write-Host "  $envPath" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Order Hetzner AX52 server" -ForegroundColor White
Write-Host "  2. Run: .\scripts\create-deployment-archive.ps1" -ForegroundColor White
Write-Host "  3. Upload and deploy to server" -ForegroundColor White
Write-Host ""
Write-Host "Portal URL:" -ForegroundColor Yellow
Write-Host "  https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationMenuBlade/~/Overview/appId/$appId" -ForegroundColor Cyan
Write-Host ""


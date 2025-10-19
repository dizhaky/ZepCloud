# Azure AD App Registration Helper Script
# This script helps collect and validate Azure AD credentials

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Azure AD App Registration - Credential Helper" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "This script will help you add Azure AD credentials to your .env file." -ForegroundColor Yellow
Write-Host ""
Write-Host "First, create the Azure AD App Registration:" -ForegroundColor White
Write-Host "  1. Open: https://portal.azure.com" -ForegroundColor Gray
Write-Host "  2. Go to: Azure Active Directory > App registrations" -ForegroundColor Gray
Write-Host "  3. Click: New registration" -ForegroundColor Gray
Write-Host "  4. Name: M365 RAG System" -ForegroundColor Gray
Write-Host "  5. Account type: Single tenant" -ForegroundColor Gray
Write-Host "  6. Redirect URI: http://localhost:8000" -ForegroundColor Gray
Write-Host "  7. Click: Register" -ForegroundColor Gray
Write-Host "  8. Add permissions and grant admin consent" -ForegroundColor Gray
Write-Host ""
Write-Host "For detailed instructions, see: DEPLOYMENT_READY_GUIDE.md Step 1" -ForegroundColor Cyan
Write-Host ""

# Prompt for credentials
Write-Host "Enter your Azure AD credentials:" -ForegroundColor Yellow
Write-Host ""

$clientId = Read-Host "Application (client) ID"
if ([string]::IsNullOrWhiteSpace($clientId)) {
    Write-Host "[ERROR] Client ID is required!" -ForegroundColor Red
    exit 1
}

$clientSecret = Read-Host "Client Secret"
if ([string]::IsNullOrWhiteSpace($clientSecret)) {
    Write-Host "[ERROR] Client Secret is required!" -ForegroundColor Red
    exit 1
}

$tenantId = Read-Host "Directory (tenant) ID"
if ([string]::IsNullOrWhiteSpace($tenantId)) {
    Write-Host "[ERROR] Tenant ID is required!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Validating format..." -ForegroundColor Yellow

# Validate GUID format
$guidPattern = '^[{]?[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}[}]?$'

if ($clientId -notmatch $guidPattern) {
    Write-Host "[WARNING] Client ID doesn't look like a valid GUID" -ForegroundColor Yellow
}

if ($tenantId -notmatch $guidPattern) {
    Write-Host "[WARNING] Tenant ID doesn't look like a valid GUID" -ForegroundColor Yellow
}

Write-Host "[OK] Format validation passed" -ForegroundColor Green

# Update .env file
$projectRoot = Split-Path -Parent $PSScriptRoot
$envPath = Join-Path $projectRoot ".env"

if (-not (Test-Path $envPath)) {
    Write-Host "[ERROR] .env file not found at: $envPath" -ForegroundColor Red
    Write-Host "Please run prepare-env.ps1 first!" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Updating .env file..." -ForegroundColor Yellow

$envContent = Get-Content $envPath -Raw

# Replace placeholders
$envContent = $envContent -replace 'M365_CLIENT_ID=YOUR_AZURE_APP_CLIENT_ID_HERE', "M365_CLIENT_ID=$clientId"
$envContent = $envContent -replace 'M365_CLIENT_SECRET=YOUR_AZURE_APP_CLIENT_SECRET_HERE', "M365_CLIENT_SECRET=$clientSecret"
$envContent = $envContent -replace 'M365_TENANT_ID=YOUR_AZURE_TENANT_ID_HERE', "M365_TENANT_ID=$tenantId"

$envContent | Out-File -FilePath $envPath -Encoding UTF8 -NoNewline

Write-Host "[SUCCESS] .env file updated!" -ForegroundColor Green
Write-Host ""

# Display summary
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Configuration Complete" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Azure AD credentials have been added to:" -ForegroundColor Green
Write-Host "  $envPath" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Order Hetzner AX52 server" -ForegroundColor White
Write-Host "  2. When server is ready, run: .\scripts\create-deployment-archive.ps1" -ForegroundColor White
Write-Host "  3. Upload and deploy to server" -ForegroundColor White
Write-Host ""
Write-Host "For complete instructions, see:" -ForegroundColor Yellow
Write-Host "  - DEPLOYMENT_READY_GUIDE.md" -ForegroundColor White
Write-Host "  - HETZNER_SERVER_SETUP.md" -ForegroundColor White
Write-Host ""


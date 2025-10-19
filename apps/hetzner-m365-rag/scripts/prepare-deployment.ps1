# Hetzner M365 RAG - Deployment Preparation Script
# This script prepares the deployment configuration with secure passwords

Write-Host "`n╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Hetzner M365 RAG - Deployment Preparation           ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Function to generate secure password
function Generate-SecurePassword {
    param (
        [int]$Length = 32
    )
    $chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&"
    return -join ((1..$Length) | ForEach-Object { $chars[(Get-Random -Maximum $chars.Length)] })
}

# Check if 1Password CLI is available
Write-Host "Checking for 1Password CLI..." -ForegroundColor Yellow
$opInstalled = $null -ne (Get-Command op -ErrorAction SilentlyContinue)

if ($opInstalled) {
    Write-Host "✅ 1Password CLI found!" -ForegroundColor Green
    
    # Get OpenAI API Key from 1Password
    Write-Host "Retrieving OpenAI API Key from 1Password..." -ForegroundColor Yellow
    try {
        $openaiKey = op item get "OpenAI API Key" --vault Employee --fields credential 2>$null
        if ($openaiKey) {
            Write-Host "✅ OpenAI API Key retrieved" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️  Could not retrieve OpenAI API Key automatically" -ForegroundColor Yellow
        $openaiKey = "YOUR_OPENAI_API_KEY_HERE"
    }
} else {
    Write-Host "⚠️  1Password CLI not found. Using placeholder values." -ForegroundColor Yellow
    $openaiKey = "YOUR_OPENAI_API_KEY_HERE"
}

# Generate secure passwords
Write-Host "`nGenerating secure passwords..." -ForegroundColor Yellow
$elasticPassword = Generate-SecurePassword
$postgresPassword = Generate-SecurePassword
$minioPassword = Generate-SecurePassword
$redisPassword = Generate-SecurePassword
$grafanaPassword = Generate-SecurePassword
$jwtSecret = Generate-SecurePassword -Length 64
$ragflowSecret = Generate-SecurePassword -Length 64

Write-Host "✅ Secure passwords generated" -ForegroundColor Green

# Create .env file
$envFile = @"
# M365 RAG System - Deployment Environment Configuration
# Generated on $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
# DO NOT COMMIT THIS FILE TO GIT!

# ============================================
# ELASTICSEARCH
# ============================================
ELASTIC_PASSWORD=$elasticPassword

# ============================================
# POSTGRESQL
# ============================================
POSTGRES_USER=raguser
POSTGRES_PASSWORD=$postgresPassword
POSTGRES_DB=m365_rag

# ============================================
# MINIO (S3-compatible Object Storage)
# ============================================
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=$minioPassword

# ============================================
# OPENAI API
# ============================================
OPENAI_API_KEY=$openaiKey

# ============================================
# MICROSOFT 365 / AZURE AD CONFIGURATION
# ============================================
# IMPORTANT: Create Azure AD App Registration and update these values!
# See DEPLOYMENT_READY_GUIDE.md for detailed instructions

M365_CLIENT_ID=YOUR_AZURE_APP_CLIENT_ID_HERE
M365_CLIENT_SECRET=YOUR_AZURE_APP_CLIENT_SECRET_HERE
M365_TENANT_ID=YOUR_AZURE_TENANT_ID_HERE
M365_USE_DELEGATED_AUTH=true

# Backward compatibility
AZURE_CLIENT_ID=\${M365_CLIENT_ID}
AZURE_CLIENT_SECRET=\${M365_CLIENT_SECRET}
AZURE_TENANT_ID=\${M365_TENANT_ID}

# ============================================
# SECURITY
# ============================================
JWT_SECRET=$jwtSecret
RAGFLOW_SECRET_KEY=$ragflowSecret

# ============================================
# GRAFANA MONITORING
# ============================================
GRAFANA_USER=admin
GRAFANA_PASSWORD=$grafanaPassword

# ============================================
# APPLICATION SETTINGS
# ============================================
ENVIRONMENT=production
LOG_LEVEL=INFO
API_WORKERS=4

# ============================================
# REDIS
# ============================================
REDIS_PASSWORD=$redisPassword
"@

# Save to file
$projectRoot = Split-Path -Parent $PSScriptRoot
$envPath = Join-Path $projectRoot ".env"
$envFile | Out-File -FilePath $envPath -Encoding UTF8 -Force

Write-Host "`n✅ Environment file created: $envPath" -ForegroundColor Green

# Display summary
Write-Host "`n════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   Deployment Configuration Summary" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan

Write-Host "`n📝 Passwords Generated:" -ForegroundColor Yellow
Write-Host "   - Elasticsearch: ✅" -ForegroundColor Green
Write-Host "   - PostgreSQL: ✅" -ForegroundColor Green
Write-Host "   - MinIO: ✅" -ForegroundColor Green
Write-Host "   - Redis: ✅" -ForegroundColor Green
Write-Host "   - Grafana: ✅" -ForegroundColor Green
Write-Host "   - JWT Secret: ✅" -ForegroundColor Green
Write-Host "   - RAGFlow Secret: ✅" -ForegroundColor Green

if ($openaiKey -ne "YOUR_OPENAI_API_KEY_HERE") {
    Write-Host "`n🔑 OpenAI API Key: ✅ Retrieved from 1Password" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  OpenAI API Key: PLACEHOLDER - Update manually" -ForegroundColor Yellow
}

Write-Host "`n⚠️  Azure AD Configuration: ACTION REQUIRED" -ForegroundColor Yellow
Write-Host "   You must create an Azure AD App Registration and update:" -ForegroundColor White
Write-Host "   - M365_CLIENT_ID" -ForegroundColor White
Write-Host "   - M365_CLIENT_SECRET" -ForegroundColor White
Write-Host "   - M365_TENANT_ID" -ForegroundColor White

Write-Host "`n📖 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Create Azure AD App Registration (see DEPLOYMENT_READY_GUIDE.md)" -ForegroundColor White
Write-Host "   2. Update M365_* values in $envPath" -ForegroundColor White
Write-Host "   3. Upload project to Hetzner server" -ForegroundColor White
Write-Host "   4. Run deployment script on server" -ForegroundColor White

Write-Host "`n════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

# Save passwords to a secure file for reference
$passwordsFile = @"
# Hetzner M365 RAG - Generated Passwords
# Generated on $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
# KEEP THIS FILE SECURE!

Elasticsearch: $elasticPassword
PostgreSQL: $postgresPassword
MinIO: $minioPassword
Redis: $redisPassword
Grafana: $grafanaPassword

Access Grafana at: http://YOUR_SERVER_IP:3000
Username: admin
Password: $grafanaPassword
"@

$passwordsPath = Join-Path $projectRoot "PASSWORDS_GENERATED.txt"
$passwordsFile | Out-File -FilePath $passwordsPath -Encoding UTF8 -Force

Write-Host "📄 Passwords saved to: $passwordsPath" -ForegroundColor Cyan
Write-Host "   (Store this securely - do not commit to git!)" -ForegroundColor Yellow

Write-Host "`nPress any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")


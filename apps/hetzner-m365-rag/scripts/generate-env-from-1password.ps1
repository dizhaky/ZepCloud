<#
.SYNOPSIS
    Generate .env file from 1Password credentials
.DESCRIPTION
    Pulls all M365 RAG credentials from 1Password and generates .env file
.PARAMETER Vault
    1Password vault name (default: M365-RAG-Production)
.PARAMETER OutputFile
    Output .env file path (default: .env)
.EXAMPLE
    .\generate-env-from-1password.ps1
.EXAMPLE
    .\generate-env-from-1password.ps1 -Vault "M365-RAG-Staging" -OutputFile ".env.staging"
#>

param(
    [string]$Vault = "M365-RAG-Production",
    [string]$OutputFile = "../.env"
)

# Ensure we're in the scripts directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "`n🔐 1Password Environment Generator" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Check if 1Password CLI is installed
if (-not (Get-Command op -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: 1Password CLI (op) not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Install it with:" -ForegroundColor Yellow
    Write-Host "  winget install --id AgileBits.1Password.CLI" -ForegroundColor White
    Write-Host ""
    Write-Host "Or visit: https://1password.com/downloads/command-line/" -ForegroundColor Gray
    exit 1
}

Write-Host "✅ 1Password CLI found" -ForegroundColor Green

# Check if signed in
try {
    $null = op whoami 2>$null
    Write-Host "✅ Signed in to 1Password" -ForegroundColor Green
} catch {
    Write-Host "❌ Not signed in to 1Password" -ForegroundColor Red
    Write-Host ""
    Write-Host "Sign in with:" -ForegroundColor Yellow
    Write-Host "  op signin" -ForegroundColor White
    exit 1
}

Write-Host "`n📥 Fetching credentials from vault: $Vault" -ForegroundColor Cyan

try {
    # Fetch all credentials
    Write-Host "   → Azure AD credentials..." -ForegroundColor Gray
    $azureClientId = op item get "Azure AD M365 RAG App" --vault $Vault --fields client_id
    $azureClientSecret = op item get "Azure AD M365 RAG App" --vault $Vault --fields client_secret
    $azureTenantId = op item get "Azure AD M365 RAG App" --vault $Vault --fields tenant_id

    Write-Host "   → OpenAI credentials..." -ForegroundColor Gray
    $openaiKey = op item get "OpenAI API Key" --vault $Vault --fields api_key
    $openaiOrg = op item get "OpenAI API Key" --vault $Vault --fields organization_id

    Write-Host "   → Database credentials..." -ForegroundColor Gray
    $postgresPassword = op item get "M365 RAG PostgreSQL" --vault $Vault --fields password
    
    Write-Host "   → Elasticsearch credentials..." -ForegroundColor Gray
    $esPassword = op item get "M365 RAG Elasticsearch" --vault $Vault --fields password
    
    Write-Host "   → Redis credentials..." -ForegroundColor Gray
    $redisPassword = op item get "M365 RAG Redis" --vault $Vault --fields password

    Write-Host "   → MinIO credentials..." -ForegroundColor Gray
    $minioAccessKey = op item get "M365 RAG MinIO" --vault $Vault --fields access_key
    $minioSecretKey = op item get "M365 RAG MinIO" --vault $Vault --fields secret_key

    Write-Host "   → JWT secret..." -ForegroundColor Gray
    $jwtSecret = op item get "M365 RAG JWT Secret" --vault $Vault --fields password

    Write-Host "   → Hetzner server info..." -ForegroundColor Gray
    $hetznerIp = op item get "Hetzner AX52 Server" --vault $Vault --fields server_ip

} catch {
    Write-Host "`n❌ Error fetching credentials from 1Password" -ForegroundColor Red
    Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure all items exist in vault '$Vault':" -ForegroundColor Yellow
    Write-Host "  - Azure AD M365 RAG App" -ForegroundColor White
    Write-Host "  - OpenAI API Key" -ForegroundColor White
    Write-Host "  - M365 RAG PostgreSQL" -ForegroundColor White
    Write-Host "  - M365 RAG Elasticsearch" -ForegroundColor White
    Write-Host "  - M365 RAG Redis" -ForegroundColor White
    Write-Host "  - M365 RAG MinIO" -ForegroundColor White
    Write-Host "  - M365 RAG JWT Secret" -ForegroundColor White
    Write-Host "  - Hetzner AX52 Server" -ForegroundColor White
    Write-Host ""
    Write-Host "Create missing items with the setup script or manually in 1Password" -ForegroundColor Gray
    exit 1
}

Write-Host "✅ All credentials fetched successfully" -ForegroundColor Green

# Generate API key for this instance
$apiKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})

# Generate .env content
$timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
$envContent = @"
# ============================================
# M365 RAG System - Environment Configuration
# Generated from 1Password on $timestamp
# ============================================
# WARNING: This file is auto-generated from 1Password.
# Do not edit manually. Update credentials in 1Password and regenerate.
# ============================================

# ============================================
# DATABASE & STORAGE
# ============================================
DATABASE_URL=postgresql://raguser:$postgresPassword@postgres:5432/m365_rag
POSTGRES_USER=raguser
POSTGRES_PASSWORD=$postgresPassword
POSTGRES_DB=m365_rag

# ============================================
# ELASTICSEARCH
# ============================================
ES_HOST=elasticsearch
ES_PORT=9200
ES_USER=elastic
ES_PASSWORD=$esPassword
ES_USE_SSL=true
ES_VERIFY_CERTS=false

# ============================================
# REDIS
# ============================================
REDIS_URL=redis://:$redisPassword@redis:6379
REDIS_PASSWORD=$redisPassword

# ============================================
# MINIO (S3-compatible storage)
# ============================================
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=$minioAccessKey
MINIO_SECRET_KEY=$minioSecretKey
MINIO_BUCKET=m365-documents

# ============================================
# MICROSOFT 365 / AZURE AD
# ============================================
AZURE_CLIENT_ID=$azureClientId
AZURE_CLIENT_SECRET=$azureClientSecret
AZURE_TENANT_ID=$azureTenantId
M365_USE_DELEGATED_AUTH=false

# ============================================
# OPENAI
# ============================================
OPENAI_API_KEY=$openaiKey
OPENAI_ORG_ID=$openaiOrg

# ============================================
# SECURITY
# ============================================
JWT_SECRET=$jwtSecret
API_KEY=$apiKey

# ============================================
# HETZNER SERVER
# ============================================
HETZNER_SERVER_IP=$hetznerIp

# ============================================
# OPTIONAL: EMAIL ALERTS
# ============================================
# Uncomment and configure if needed
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=your-email@gmail.com
# SMTP_PASSWORD=your-app-password
# ALERT_EMAIL=admin@yourdomain.com
"@

Write-Host "`n📝 Writing .env file..." -ForegroundColor Cyan

# Resolve output path
$outputPath = Resolve-Path $OutputFile -ErrorAction SilentlyContinue
if (-not $outputPath) {
    $outputPath = Join-Path (Split-Path $scriptPath -Parent) (Split-Path $OutputFile -Leaf)
}

# Write to file
$envContent | Out-File -FilePath $outputPath -Encoding UTF8 -NoNewline

# Set secure permissions (Windows)
try {
    $acl = Get-Acl $outputPath
    $acl.SetAccessRuleProtection($true, $false)
    $rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
        [System.Security.Principal.WindowsIdentity]::GetCurrent().Name,
        "FullControl",
        "Allow"
    )
    $acl.SetAccessRule($rule)
    Set-Acl $outputPath $acl
    Write-Host "✅ .env file generated successfully!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  .env file created but couldn't set permissions" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📍 Location: $outputPath" -ForegroundColor Gray
Write-Host ""
Write-Host "⚠️  Important Reminders:" -ForegroundColor Yellow
Write-Host "   • Never commit .env to git (already in .gitignore)" -ForegroundColor White
Write-Host "   • Regenerate after updating credentials in 1Password" -ForegroundColor White
Write-Host "   • Keep 1Password vault locked when not in use" -ForegroundColor White
Write-Host "   • Rotate credentials every 6-12 months" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Review the generated .env file" -ForegroundColor White
Write-Host "   2. Deploy to Hetzner with: docker compose up -d" -ForegroundColor White
Write-Host "   3. Run initial M365 sync" -ForegroundColor White
Write-Host ""


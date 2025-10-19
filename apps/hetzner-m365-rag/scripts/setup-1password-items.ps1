<#
.SYNOPSIS
    Set up 1Password items for M365 RAG system
.DESCRIPTION
    Interactive script to create all necessary 1Password items for the M365 RAG system
.PARAMETER Vault
    1Password vault name (default: M365-RAG-Production)
.EXAMPLE
    .\setup-1password-items.ps1
#>

param(
    [string]$Vault = "M365-RAG-Production"
)

Write-Host "`n🔐 1Password Setup for M365 RAG System" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Check if 1Password CLI is installed
if (-not (Get-Command op -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: 1Password CLI not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Install with: winget install --id AgileBits.1Password.CLI" -ForegroundColor Yellow
    exit 1
}

# Check if signed in
try {
    $null = op whoami 2>$null
    Write-Host "✅ Signed in to 1Password" -ForegroundColor Green
} catch {
    Write-Host "❌ Not signed in to 1Password" -ForegroundColor Red
    Write-Host "Sign in with: op signin" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Create vault if it doesn't exist
Write-Host "📦 Checking for vault: $Vault" -ForegroundColor Cyan
$vaultExists = op vault list --format=json | ConvertFrom-Json | Where-Object { $_.name -eq $Vault }

if (-not $vaultExists) {
    Write-Host "   Creating vault: $Vault..." -ForegroundColor Gray
    try {
        op vault create $Vault | Out-Null
        Write-Host "   ✅ Vault created" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ Could not create vault" -ForegroundColor Red
        Write-Host "   You may need admin permissions" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "   ✅ Vault exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "📝 Let's set up your credentials!" -ForegroundColor Cyan
Write-Host "   (Press Enter to skip items you'll add later)" -ForegroundColor Gray
Write-Host ""

# Function to prompt for input
function Get-SecureInput {
    param(
        [string]$Prompt,
        [string]$Default = "",
        [bool]$IsSecret = $false
    )
    
    if ($IsSecret) {
        $secureString = Read-Host -Prompt $Prompt -AsSecureString
        $bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureString)
        $value = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
        return $value
    } else {
        $value = Read-Host -Prompt $Prompt
        if ([string]::IsNullOrWhiteSpace($value) -and $Default) {
            return $Default
        }
        return $value
    }
}

# Function to generate secure password
function New-SecurePassword {
    return -join ((65..90) + (97..122) + (48..57) + 33,35,36,37,38,42,43,45,61 | Get-Random -Count 32 | ForEach-Object {[char]$_})
}

# ============================================
# 1. Hetzner Server
# ============================================
Write-Host "1️⃣  Hetzner Server" -ForegroundColor Yellow
Write-Host "   ─────────────────" -ForegroundColor Gray

$hetznerIp = Get-SecureInput "   Server IP address"
$sshUser = Get-SecureInput "   SSH user" "root"

if ($hetznerIp) {
    Write-Host "   Creating 1Password item..." -ForegroundColor Gray
    try {
        op item create `
            --category=server `
            --vault=$Vault `
            --title="Hetzner AX52 Server" `
            server_ip=$hetznerIp `
            ssh_user=$sshUser `
            ssh_port="22" `
            --tags="hetzner,production" | Out-Null
        Write-Host "   ✅ Saved to 1Password" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️  Item might already exist or error occurred" -ForegroundColor Yellow
    }
}
Write-Host ""

# ============================================
# 2. Azure AD / M365
# ============================================
Write-Host "2️⃣  Azure AD / M365" -ForegroundColor Yellow
Write-Host "   ───────────────────" -ForegroundColor Gray

$azureClientId = Get-SecureInput "   Client ID (from Azure Portal)"
$azureTenantId = Get-SecureInput "   Tenant ID (from Azure Portal)"
$azureClientSecret = Get-SecureInput "   Client Secret" $null $true

if ($azureClientId -and $azureTenantId -and $azureClientSecret) {
    Write-Host "   Creating 1Password item..." -ForegroundColor Gray
    try {
        op item create `
            --category="API Credential" `
            --vault=$Vault `
            --title="Azure AD M365 RAG App" `
            client_id=$azureClientId `
            client_secret=$azureClientSecret `
            tenant_id=$azureTenantId `
            --tags="azure,m365" | Out-Null
        Write-Host "   ✅ Saved to 1Password" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️  Item might already exist" -ForegroundColor Yellow
    }
}
Write-Host ""

# ============================================
# 3. OpenAI
# ============================================
Write-Host "3️⃣  OpenAI API" -ForegroundColor Yellow
Write-Host "   ─────────────" -ForegroundColor Gray

$openaiKey = Get-SecureInput "   API Key (sk-...)" $null $true
$openaiOrg = Get-SecureInput "   Organization ID (optional)"

if ($openaiKey) {
    Write-Host "   Creating 1Password item..." -ForegroundColor Gray
    try {
        if ($openaiOrg) {
            op item create `
                --category="API Credential" `
                --vault=$Vault `
                --title="OpenAI API Key" `
                api_key=$openaiKey `
                organization_id=$openaiOrg `
                --tags="openai,api" | Out-Null
        } else {
            op item create `
                --category="API Credential" `
                --vault=$Vault `
                --title="OpenAI API Key" `
                api_key=$openaiKey `
                --tags="openai,api" | Out-Null
        }
        Write-Host "   ✅ Saved to 1Password" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️  Item might already exist" -ForegroundColor Yellow
    }
}
Write-Host ""

# ============================================
# 4. Database Credentials (Auto-generate)
# ============================================
Write-Host "4️⃣  Database Credentials (auto-generated)" -ForegroundColor Yellow
Write-Host "   ───────────────────────────────────────" -ForegroundColor Gray

# PostgreSQL
$postgresPassword = New-SecurePassword
Write-Host "   Creating PostgreSQL credentials..." -ForegroundColor Gray
try {
    op item create `
        --category="Database" `
        --vault=$Vault `
        --title="M365 RAG PostgreSQL" `
        database="m365_rag" `
        username="raguser" `
        "password[password]=$postgresPassword" `
        hostname="postgres" `
        port="5432" `
        --tags="postgres,database" | Out-Null
    Write-Host "   ✅ PostgreSQL saved" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  PostgreSQL item might already exist" -ForegroundColor Yellow
}

# Elasticsearch
$esPassword = New-SecurePassword
Write-Host "   Creating Elasticsearch credentials..." -ForegroundColor Gray
try {
    op item create `
        --category="Database" `
        --vault=$Vault `
        --title="M365 RAG Elasticsearch" `
        username="elastic" `
        "password[password]=$esPassword" `
        hostname="elasticsearch" `
        port="9200" `
        --tags="elasticsearch" | Out-Null
    Write-Host "   ✅ Elasticsearch saved" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Elasticsearch item might already exist" -ForegroundColor Yellow
}

# Redis
$redisPassword = New-SecurePassword
Write-Host "   Creating Redis credentials..." -ForegroundColor Gray
try {
    op item create `
        --category="Database" `
        --vault=$Vault `
        --title="M365 RAG Redis" `
        "password[password]=$redisPassword" `
        hostname="redis" `
        port="6379" `
        --tags="redis" | Out-Null
    Write-Host "   ✅ Redis saved" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Redis item might already exist" -ForegroundColor Yellow
}

# MinIO
$minioAccessKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 20 | ForEach-Object {[char]$_})
$minioSecretKey = New-SecurePassword
Write-Host "   Creating MinIO credentials..." -ForegroundColor Gray
try {
    op item create `
        --category="API Credential" `
        --vault=$Vault `
        --title="M365 RAG MinIO" `
        access_key=$minioAccessKey `
        secret_key=$minioSecretKey `
        endpoint="minio:9000" `
        bucket="m365-documents" `
        --tags="minio,storage" | Out-Null
    Write-Host "   ✅ MinIO saved" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  MinIO item might already exist" -ForegroundColor Yellow
}

# JWT Secret
$jwtSecret = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object {[char]$_})
Write-Host "   Creating JWT secret..." -ForegroundColor Gray
try {
    op item create `
        --category="Password" `
        --vault=$Vault `
        --title="M365 RAG JWT Secret" `
        "password[password]=$jwtSecret" `
        --tags="jwt,api" | Out-Null
    Write-Host "   ✅ JWT secret saved" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  JWT secret item might already exist" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Summary of created items in vault '$Vault':" -ForegroundColor Cyan
Write-Host "   • Hetzner AX52 Server" -ForegroundColor Gray
Write-Host "   • Azure AD M365 RAG App" -ForegroundColor Gray
Write-Host "   • OpenAI API Key" -ForegroundColor Gray
Write-Host "   • M365 RAG PostgreSQL" -ForegroundColor Gray
Write-Host "   • M365 RAG Elasticsearch" -ForegroundColor Gray
Write-Host "   • M365 RAG Redis" -ForegroundColor Gray
Write-Host "   • M365 RAG MinIO" -ForegroundColor Gray
Write-Host "   • M365 RAG JWT Secret" -ForegroundColor Gray
Write-Host ""
Write-Host "🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Generate .env file:" -ForegroundColor White
Write-Host "      .\generate-env-from-1password.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "   2. Review and deploy:" -ForegroundColor White
Write-Host "      cd .. && docker compose up -d" -ForegroundColor Gray
Write-Host ""


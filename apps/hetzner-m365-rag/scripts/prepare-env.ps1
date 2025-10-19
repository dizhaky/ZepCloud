# Hetzner M365 RAG - Environment Preparation Script
# Generates secure passwords and creates .env file

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Hetzner M365 RAG - Environment Preparation" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# Generate secure password function
function New-RandomPassword {
    param([int]$Length = 32)
    $chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    -join ((1..$Length) | ForEach-Object { $chars[(Get-Random -Maximum $chars.Length)] })
}

# Get OpenAI key from 1Password if available
$openaiKey = "YOUR_OPENAI_API_KEY_HERE"
if (Get-Command op -ErrorAction SilentlyContinue) {
    Write-Host "[INFO] Retrieving OpenAI API Key from 1Password..." -ForegroundColor Yellow
    try {
        $retrieved = op item get "OpenAI API Key" --vault Employee --fields credential 2>$null
        if ($retrieved) {
            $openaiKey = $retrieved
            Write-Host "[SUCCESS] OpenAI API Key retrieved from 1Password" -ForegroundColor Green
        }
    } catch {
        Write-Host "[WARNING] Could not retrieve from 1Password, using placeholder" -ForegroundColor Yellow
    }
}

# Generate passwords
Write-Host "[INFO] Generating secure passwords..." -ForegroundColor Yellow
$passwords = @{
    ELASTIC_PASSWORD = New-RandomPassword
    POSTGRES_PASSWORD = New-RandomPassword
    MINIO_ROOT_PASSWORD = New-RandomPassword
    REDIS_PASSWORD = New-RandomPassword
    GRAFANA_PASSWORD = New-RandomPassword
    JWT_SECRET = New-RandomPassword -Length 64
    RAGFLOW_SECRET_KEY = New-RandomPassword -Length 64
}
Write-Host "[SUCCESS] Passwords generated" -ForegroundColor Green

# Create .env content
$envContent = @"
# M365 RAG System - Deployment Environment Configuration
# Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
# DO NOT COMMIT TO GIT!

# ELASTICSEARCH
ELASTIC_PASSWORD=$($passwords.ELASTIC_PASSWORD)

# POSTGRESQL
POSTGRES_USER=raguser
POSTGRES_PASSWORD=$($passwords.POSTGRES_PASSWORD)
POSTGRES_DB=m365_rag

# MINIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=$($passwords.MINIO_ROOT_PASSWORD)

# OPENAI
OPENAI_API_KEY=$openaiKey

# MICROSOFT 365 - UPDATE THESE AFTER CREATING AZURE AD APP REGISTRATION
M365_CLIENT_ID=YOUR_AZURE_APP_CLIENT_ID_HERE
M365_CLIENT_SECRET=YOUR_AZURE_APP_CLIENT_SECRET_HERE
M365_TENANT_ID=YOUR_AZURE_TENANT_ID_HERE
M365_USE_DELEGATED_AUTH=true

# BACKWARD COMPATIBILITY
AZURE_CLIENT_ID=`${M365_CLIENT_ID}
AZURE_CLIENT_SECRET=`${M365_CLIENT_SECRET}
AZURE_TENANT_ID=`${M365_TENANT_ID}

# SECURITY
JWT_SECRET=$($passwords.JWT_SECRET)
RAGFLOW_SECRET_KEY=$($passwords.RAGFLOW_SECRET_KEY)

# GRAFANA
GRAFANA_USER=admin
GRAFANA_PASSWORD=$($passwords.GRAFANA_PASSWORD)

# APPLICATION
ENVIRONMENT=production
LOG_LEVEL=INFO
API_WORKERS=4

# REDIS
REDIS_PASSWORD=$($passwords.REDIS_PASSWORD)
"@

# Save .env file
$projectRoot = Split-Path -Parent $PSScriptRoot
$envPath = Join-Path $projectRoot ".env"
$envContent | Out-File -FilePath $envPath -Encoding UTF8 -NoNewline
Write-Host "[SUCCESS] Environment file created: $envPath" -ForegroundColor Green

# Save passwords reference file
$passwordsContent = @"
Hetzner M365 RAG - Generated Passwords
Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
KEEP THIS FILE SECURE!

Elasticsearch Password: $($passwords.ELASTIC_PASSWORD)
PostgreSQL Password: $($passwords.POSTGRES_PASSWORD)
MinIO Password: $($passwords.MINIO_ROOT_PASSWORD)
Redis Password: $($passwords.REDIS_PASSWORD)
Grafana Admin Password: $($passwords.GRAFANA_PASSWORD)

Grafana Access: http://YOUR_SERVER_IP:3000
  Username: admin
  Password: $($passwords.GRAFANA_PASSWORD)
"@

$passwordsPath = Join-Path $projectRoot "PASSWORDS_GENERATED.txt"
$passwordsContent | Out-File -FilePath $passwordsPath -Encoding UTF8 -NoNewline
Write-Host "[SUCCESS] Passwords saved: $passwordsPath" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Configuration Summary" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Generated Passwords:" -ForegroundColor Yellow
Write-Host "  [OK] Elasticsearch" -ForegroundColor Green
Write-Host "  [OK] PostgreSQL" -ForegroundColor Green
Write-Host "  [OK] MinIO" -ForegroundColor Green
Write-Host "  [OK] Redis" -ForegroundColor Green
Write-Host "  [OK] Grafana" -ForegroundColor Green
Write-Host "  [OK] JWT Secret" -ForegroundColor Green
Write-Host "  [OK] RAGFlow Secret" -ForegroundColor Green
Write-Host ""

if ($openaiKey -ne "YOUR_OPENAI_API_KEY_HERE") {
    Write-Host "OpenAI API Key: [OK] Retrieved from 1Password" -ForegroundColor Green
} else {
    Write-Host "OpenAI API Key: [ACTION REQUIRED] Update in .env file" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Azure AD Configuration: [ACTION REQUIRED]" -ForegroundColor Yellow
Write-Host "  Create Azure AD App Registration and update:" -ForegroundColor White
Write-Host "    - M365_CLIENT_ID" -ForegroundColor White
Write-Host "    - M365_CLIENT_SECRET" -ForegroundColor White
Write-Host "    - M365_TENANT_ID" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Create Azure AD App Registration" -ForegroundColor White
Write-Host "  2. Update M365 values in: $envPath" -ForegroundColor White
Write-Host "  3. Upload project to Hetzner server" -ForegroundColor White
Write-Host "  4. Run deployment script on server" -ForegroundColor White
Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""


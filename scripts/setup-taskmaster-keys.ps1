# Configure Task Master AI API Keys from 1Password
# Simplified version

$ErrorActionPreference = "Stop"

Write-Host "Task Master AI - API Key Setup" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$McpConfigPath = Join-Path $PSScriptRoot "..\.kilocode\mcp.json"
$Vault = "Private"

# Check 1Password CLI
Write-Host "Checking 1Password CLI..." -ForegroundColor Cyan
$opCheck = Get-Command op -ErrorAction SilentlyContinue
if (-not $opCheck) {
    Write-Host "ERROR: 1Password CLI (op) not found" -ForegroundColor Red
    Write-Host "Install from: https://developer.1password.com/docs/cli/get-started/" -ForegroundColor Yellow
    exit 1
}
Write-Host "  OK: 1Password CLI found" -ForegroundColor Green

# Check if signed in
Write-Host ""
Write-Host "Checking 1Password authentication..." -ForegroundColor Cyan
$ErrorActionPreference = "SilentlyContinue"
$opAccount = op whoami 2>&1
$ErrorActionPreference = "Stop"

if ($LASTEXITCODE -ne 0) {
    Write-Host "  Not signed in. Please sign in to 1Password..." -ForegroundColor Yellow
    Write-Host ""
    op signin
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: Failed to sign in to 1Password" -ForegroundColor Red
        exit 1
    }
}
Write-Host "  OK: Signed in to 1Password" -ForegroundColor Green

# Fetch Anthropic API Key
Write-Host ""
Write-Host "Fetching API keys..." -ForegroundColor Cyan
$anthropicKey = $null
$perplexityKey = $null

Write-Host "  Searching for Anthropic API Key..." -ForegroundColor Gray
$ErrorActionPreference = "SilentlyContinue"

# Try different field names that might contain the API key
$fieldNames = @("credential", "password", "api_key", "apikey", "key", "token")
foreach ($fieldName in $fieldNames) {
    $anthropicKey = op item get "Anthropic API Key" --vault $Vault --fields $fieldName 2>$null
    if ($LASTEXITCODE -eq 0 -and $anthropicKey) {
        Write-Host "  OK: Anthropic API Key found (field: $fieldName)" -ForegroundColor Green
        break
    }
}

if (-not $anthropicKey) {
    Write-Host "  WARNING: Anthropic API Key not found in any standard field" -ForegroundColor Yellow
}

# Fetch Perplexity API Key
Write-Host "  Searching for Perplexity API Key..." -ForegroundColor Gray
foreach ($fieldName in $fieldNames) {
    $perplexityKey = op item get "Perplexity API Key" --vault $Vault --fields $fieldName 2>$null
    if ($LASTEXITCODE -eq 0 -and $perplexityKey) {
        Write-Host "  OK: Perplexity API Key found (field: $fieldName)" -ForegroundColor Green
        break
    }
}

if (-not $perplexityKey) {
    Write-Host "  WARNING: Perplexity API Key not found in any standard field" -ForegroundColor Yellow
}

$ErrorActionPreference = "Stop"

# Check if we have at least one key
if (-not $anthropicKey -and -not $perplexityKey) {
    Write-Host ""
    Write-Host "ERROR: No API keys found in 1Password vault '$Vault'" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please create these items in 1Password:" -ForegroundColor Yellow
    Write-Host "  1. 'Anthropic API Key' - Get from https://console.anthropic.com/" -ForegroundColor Yellow
    Write-Host "  2. 'Perplexity API Key' - Get from https://www.perplexity.ai/settings/api" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Load MCP configuration
Write-Host ""
Write-Host "Updating MCP configuration..." -ForegroundColor Cyan
Write-Host "  Config: $McpConfigPath" -ForegroundColor Gray

if (-not (Test-Path $McpConfigPath)) {
    Write-Host "ERROR: MCP config not found: $McpConfigPath" -ForegroundColor Red
    exit 1
}

$mcpConfig = Get-Content $McpConfigPath -Raw | ConvertFrom-Json

# Check for task-master-ai server
$taskMasterKey = "task-master-ai"
if (-not $mcpConfig.mcpServers.PSObject.Properties.Name.Contains($taskMasterKey)) {
    Write-Host "ERROR: task-master-ai server not found in MCP config" -ForegroundColor Red
    exit 1
}

# Create env object if it doesn't exist
$taskMasterServer = $mcpConfig.mcpServers.$taskMasterKey
if (-not $taskMasterServer.env) {
    $taskMasterServer | Add-Member -NotePropertyName 'env' -NotePropertyValue @{} -Force
}

# Add API keys
$keysAdded = @()

if ($anthropicKey) {
    if (-not $taskMasterServer.env.PSObject.Properties.Name.Contains('ANTHROPIC_API_KEY')) {
        $taskMasterServer.env | Add-Member -NotePropertyName 'ANTHROPIC_API_KEY' -NotePropertyValue $anthropicKey -Force
    }
    else {
        $taskMasterServer.env.ANTHROPIC_API_KEY = $anthropicKey
    }
    $keysAdded += "Anthropic"
    Write-Host "  OK: Anthropic API key added" -ForegroundColor Green
}

if ($perplexityKey) {
    if (-not $taskMasterServer.env.PSObject.Properties.Name.Contains('PERPLEXITY_API_KEY')) {
        $taskMasterServer.env | Add-Member -NotePropertyName 'PERPLEXITY_API_KEY' -NotePropertyValue $perplexityKey -Force
    }
    else {
        $taskMasterServer.env.PERPLEXITY_API_KEY = $perplexityKey
    }
    $keysAdded += "Perplexity"
    Write-Host "  OK: Perplexity API key added" -ForegroundColor Green
}

# Backup original config
$backupPath = "$McpConfigPath.backup"
Copy-Item $McpConfigPath $backupPath -Force
Write-Host "  OK: Backup created: $backupPath" -ForegroundColor Green

# Save updated configuration
$mcpConfig | ConvertTo-Json -Depth 10 | Set-Content $McpConfigPath -Encoding UTF8
Write-Host "  OK: MCP configuration saved" -ForegroundColor Green

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "SUCCESS: Configuration Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "API Keys Configured:" -ForegroundColor Cyan
foreach ($key in $keysAdded) {
    Write-Host "  $key" -ForegroundColor Green
}
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Restart Cursor IDE" -ForegroundColor White
Write-Host "  2. Test with: task-master list" -ForegroundColor White
Write-Host ""


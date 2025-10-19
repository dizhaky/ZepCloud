# Configure Task Master AI API Keys from 1Password
# This script fetches API keys from 1Password and updates the MCP configuration

param(
    [string]$McpConfigPath = "$PSScriptRoot\..\.kilocode\mcp.json",
    [string]$Vault = "Private",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Task Master AI - API Key Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if 1Password CLI is installed
try {
    $opVersion = op --version 2>&1
    Write-Host "✓ 1Password CLI detected: $opVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ 1Password CLI (op) is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install 1Password CLI:" -ForegroundColor Yellow
    Write-Host "  https://developer.1password.com/docs/cli/get-started/" -ForegroundColor Yellow
    exit 1
}

# Check if already signed in
Write-Host ""
Write-Host "Checking 1Password authentication..." -ForegroundColor Cyan
try {
    $whoami = op whoami 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Already signed in to 1Password: $whoami" -ForegroundColor Green
    } else {
        Write-Host "Please sign in to 1Password..." -ForegroundColor Yellow
        op signin
        if ($LASTEXITCODE -ne 0) {
            Write-Host "✗ Failed to sign in to 1Password" -ForegroundColor Red
            exit 1
        }
    }
}
catch {
    Write-Host "Please sign in to 1Password..." -ForegroundColor Yellow
    op signin
}

Write-Host ""
Write-Host "Fetching API keys from 1Password..." -ForegroundColor Cyan

# Fetch Anthropic API Key
Write-Host "  → Searching for Anthropic API Key..." -ForegroundColor Gray
try {
    $anthropicKey = op item get "Anthropic API Key" --vault $Vault --fields password 2>&1
    if ($LASTEXITCODE -eq 0 -and $anthropicKey) {
        Write-Host "  ✓ Anthropic API Key found" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Anthropic API Key not found in vault '$Vault'" -ForegroundColor Red
        Write-Host "    Please create an item named 'Anthropic API Key' in 1Password" -ForegroundColor Yellow
        $anthropicKey = $null
    }
}
catch {
    Write-Host "  ✗ Error fetching Anthropic API Key: $_" -ForegroundColor Red
    $anthropicKey = $null
}

# Fetch Perplexity API Key
Write-Host "  → Searching for Perplexity API Key..." -ForegroundColor Gray
try {
    $perplexityKey = op item get "Perplexity API Key" --vault $Vault --fields password 2>&1
    if ($LASTEXITCODE -eq 0 -and $perplexityKey) {
        Write-Host "  ✓ Perplexity API Key found" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Perplexity API Key not found in vault '$Vault'" -ForegroundColor Red
        Write-Host "    Please create an item named 'Perplexity API Key' in 1Password" -ForegroundColor Yellow
        $perplexityKey = $null
    }
}
catch {
    Write-Host "  ✗ Error fetching Perplexity API Key: $_" -ForegroundColor Red
    $perplexityKey = $null
}

# Check if we got at least one key
if (-not $anthropicKey -and -not $perplexityKey) {
    Write-Host ""
    Write-Host "✗ No API keys found in 1Password" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please create the following items in 1Password:" -ForegroundColor Yellow
    Write-Host "  1. Item name: 'Anthropic API Key'" -ForegroundColor Yellow
    Write-Host "     - Add a password field with your Anthropic API key" -ForegroundColor Yellow
    Write-Host "     - Get key from: https://console.anthropic.com/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  2. Item name: 'Perplexity API Key'" -ForegroundColor Yellow
    Write-Host "     - Add a password field with your Perplexity API key" -ForegroundColor Yellow
    Write-Host "     - Get key from: https://www.perplexity.ai/settings/api" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Load existing MCP configuration
Write-Host ""
Write-Host "Updating MCP configuration..." -ForegroundColor Cyan
Write-Host "  Config file: $McpConfigPath" -ForegroundColor Gray

if (-not (Test-Path $McpConfigPath)) {
    Write-Host "✗ MCP configuration file not found: $McpConfigPath" -ForegroundColor Red
    exit 1
}

try {
    $mcpConfig = Get-Content $McpConfigPath -Raw | ConvertFrom-Json
    Write-Host "  ✓ MCP configuration loaded" -ForegroundColor Green
}
catch {
    Write-Host "✗ Failed to parse MCP configuration: $_" -ForegroundColor Red
    exit 1
}

# Check if task-master-ai server exists
if (-not $mcpConfig.mcpServers['task-master-ai']) {
    Write-Host "✗ task-master-ai server not found in MCP configuration" -ForegroundColor Red
    exit 1
}

# Update or create env section
if (-not $mcpConfig.mcpServers['task-master-ai'].env) {
    $mcpConfig.mcpServers['task-master-ai'] | Add-Member -NotePropertyName 'env' -NotePropertyValue @{} -Force
}

# Add API keys
$keysAdded = @()
if ($anthropicKey) {
    $mcpConfig.mcpServers['task-master-ai'].env.ANTHROPIC_API_KEY = $anthropicKey
    $keysAdded += "Anthropic"
    Write-Host "  ✓ Anthropic API key added" -ForegroundColor Green
}

if ($perplexityKey) {
    $mcpConfig.mcpServers['task-master-ai'].env.PERPLEXITY_API_KEY = $perplexityKey
    $keysAdded += "Perplexity"
    Write-Host "  ✓ Perplexity API key added" -ForegroundColor Green
}

# Backup original config
$backupPath = "$McpConfigPath.backup"
Copy-Item $McpConfigPath $backupPath -Force
Write-Host "  ✓ Original config backed up to: $backupPath" -ForegroundColor Green

# Save updated configuration
try {
    $mcpConfig | ConvertTo-Json -Depth 10 | Set-Content $McpConfigPath -Encoding UTF8
    Write-Host "  ✓ MCP configuration updated successfully" -ForegroundColor Green
}
catch {
    Write-Host "✗ Failed to save MCP configuration: $_" -ForegroundColor Red
    Write-Host "Restoring backup..." -ForegroundColor Yellow
    Copy-Item $backupPath $McpConfigPath -Force
    exit 1
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✓ Configuration Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "API Keys Configured:" -ForegroundColor Cyan
foreach ($key in $keysAdded) {
    Write-Host "  ✓ $key" -ForegroundColor Green
}
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Restart Cursor IDE for changes to take effect" -ForegroundColor White
Write-Host "  2. Test Task Master AI with: task-master list" -ForegroundColor White
Write-Host "  3. Parse PRD to generate tasks" -ForegroundColor White
Write-Host ""
Write-Host "Backup saved at: $backupPath" -ForegroundColor Gray
Write-Host ""


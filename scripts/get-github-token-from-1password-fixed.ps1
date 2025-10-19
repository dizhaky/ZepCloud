<#
.SYNOPSIS
    Get GitHub Personal Access Token from 1Password
.DESCRIPTION
    Retrieves GitHub token from 1Password and updates MCP configuration
.PARAMETER Vault
    1Password vault name (default: M365-RAG-Production)
.PARAMETER ItemName
    1Password item name for GitHub token (default: GitHub Personal Access Token)
.EXAMPLE
    .\get-github-token-from-1password-fixed.ps1
.EXAMPLE
    .\get-github-token-from-1password-fixed.ps1 -Vault "Private" -ItemName "GitHub Token"
#>

param(
    [string]$Vault = "M365-RAG-Production",
    [string]$ItemName = "GitHub Personal Access Token"
)

Write-Host "`n🔐 GitHub Token Retrieval from 1Password" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

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
    Write-Host "Sign in with one of these methods:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Desktop App Integration (Recommended):" -ForegroundColor White
    Write-Host "   - Open 1Password desktop app" -ForegroundColor Gray
    Write-Host "   - Enable CLI integration in settings" -ForegroundColor Gray
    Write-Host "   - Restart terminal" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Manual Sign In:" -ForegroundColor White
    Write-Host "   op account add" -ForegroundColor Gray
    Write-Host "   op signin" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Service Account:" -ForegroundColor White
    Write-Host "   Set OP_SERVICE_ACCOUNT_TOKEN environment variable" -ForegroundColor Gray
    exit 1
}

Write-Host "`n📥 Fetching GitHub token from vault: $Vault" -ForegroundColor Cyan

try {
    # Try to get the GitHub token
    Write-Host "   → Looking for item: $ItemName" -ForegroundColor Gray
    
    # Check if item exists
    $itemExists = op item get "$ItemName" --vault $Vault --format json 2>$null
    if (-not $itemExists) {
        Write-Host "❌ Item '$ItemName' not found in vault '$Vault'" -ForegroundColor Red
        Write-Host ""
        Write-Host "Available items in vault:" -ForegroundColor Yellow
        op item list --vault $Vault --format json | ConvertFrom-Json | ForEach-Object {
            Write-Host "  - $($_.title)" -ForegroundColor White
        }
        Write-Host ""
        Write-Host "Create the GitHub token item manually in 1Password or use a different item name" -ForegroundColor Gray
        exit 1
    }
    
    # Get the token (try different field names)
    $token = $null
    $fieldNames = @("token", "password", "api_key", "access_token", "github_token")
    
    foreach ($fieldName in $fieldNames) {
        try {
            $token = op item get "$ItemName" --vault $Vault --fields $fieldName --reveal 2>$null
            if ($token) {
                Write-Host "✅ Found token in field: $fieldName" -ForegroundColor Green
                break
            }
        } catch {
            # Continue to next field
        }
    }
    
    if (-not $token) {
        Write-Host "❌ No token found in item '$ItemName'" -ForegroundColor Red
        Write-Host ""
        Write-Host "Available fields in the item:" -ForegroundColor Yellow
        $itemData = op item get "$ItemName" --vault $Vault --format json | ConvertFrom-Json
        $itemData.fields | ForEach-Object {
            if ($_.id -ne "password") {
                Write-Host "  - $($_.id)" -ForegroundColor White
            }
        }
        Write-Host ""
        Write-Host "Please add a token field to the item or specify the correct field name" -ForegroundColor Gray
        exit 1
    }
    
    Write-Host "✅ GitHub token retrieved successfully" -ForegroundColor Green
    Write-Host "   Token: ${token:0:10}...${token: -10}" -ForegroundColor Gray
    
    # Update MCP configuration
    Write-Host "`n🔧 Updating MCP configuration..." -ForegroundColor Cyan
    
    $mcpConfigPath = ".cursor/mcp.json"
    if (Test-Path $mcpConfigPath) {
        $mcpConfig = Get-Content $mcpConfigPath | ConvertFrom-Json
        
        # Update GitHub MCP server with token
        if ($mcpConfig.mcpServers.github) {
            $mcpConfig.mcpServers.github.env.GITHUB_PERSONAL_ACCESS_TOKEN = $token
            
            # Save updated configuration
            $mcpConfig | ConvertTo-Json -Depth 10 | Set-Content $mcpConfigPath
            
            Write-Host "✅ MCP configuration updated with GitHub token" -ForegroundColor Green
            Write-Host "   File: $mcpConfigPath" -ForegroundColor Gray
        } else {
            Write-Host "⚠️  GitHub MCP server not found in configuration" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠️  MCP configuration file not found: $mcpConfigPath" -ForegroundColor Yellow
    }
    
    # Test the token
    Write-Host "`n🧪 Testing GitHub token..." -ForegroundColor Cyan
    try {
        $headers = @{
            "Authorization" = "token $token"
            "User-Agent" = "ZepCloud-MCP-HealthCheck"
        }
        
        $response = Invoke-RestMethod -Uri "https://api.github.com/user" -Headers $headers -Method GET
        Write-Host "✅ GitHub token is valid" -ForegroundColor Green
        Write-Host "   User: $($response.login)" -ForegroundColor Gray
        Write-Host "   Name: $($response.name)" -ForegroundColor Gray
    } catch {
        Write-Host "⚠️  GitHub token test failed: $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host "   Token may be invalid or expired" -ForegroundColor Gray
    }
    
    Write-Host "`n🎉 GitHub token setup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Restart Cursor to reload MCP configuration" -ForegroundColor White
    Write-Host "2. Run 'npm run mcp:health' to verify all servers" -ForegroundColor White
    Write-Host "3. Test GitHub MCP operations" -ForegroundColor White
    
} catch {
    Write-Host "`n❌ Error retrieving GitHub token from 1Password" -ForegroundColor Red
    Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Make sure you're signed in: op whoami" -ForegroundColor White
    Write-Host "2. Check vault name: op vault list" -ForegroundColor White
    Write-Host "3. List items: op item list --vault $Vault" -ForegroundColor White
    Write-Host "4. Create GitHub token item if it doesn't exist" -ForegroundColor White
    exit 1
}

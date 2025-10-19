<#
.SYNOPSIS
    Setup 1Password and create GitHub token item
.DESCRIPTION
    Helps set up 1Password CLI and create a GitHub Personal Access Token item
.EXAMPLE
    .\setup-1password-github-token.ps1
#>

Write-Host "`n🔐 1Password GitHub Token Setup" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan

# Check if 1Password CLI is installed
if (-not (Get-Command op -ErrorAction SilentlyContinue)) {
    Write-Host "❌ 1Password CLI not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Installing 1Password CLI..." -ForegroundColor Yellow
    
    try {
        winget install --id AgileBits.1Password.CLI --accept-package-agreements --accept-source-agreements
        Write-Host "✅ 1Password CLI installed" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to install 1Password CLI" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please install manually:" -ForegroundColor Yellow
        Write-Host "1. Visit: https://1password.com/downloads/command-line/" -ForegroundColor White
        Write-Host "2. Download and install the Windows installer" -ForegroundColor White
        Write-Host "3. Restart your terminal" -ForegroundColor White
        exit 1
    }
} else {
    Write-Host "✅ 1Password CLI found" -ForegroundColor Green
}

# Check if signed in
try {
    $null = op whoami 2>$null
    Write-Host "✅ Already signed in to 1Password" -ForegroundColor Green
} catch {
    Write-Host "❌ Not signed in to 1Password" -ForegroundColor Red
    Write-Host ""
    Write-Host "Choose your sign-in method:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Desktop App Integration (Recommended):" -ForegroundColor White
    Write-Host "   - Open 1Password desktop app" -ForegroundColor Gray
    Write-Host "   - Go to Settings > Developer" -ForegroundColor Gray
    Write-Host "   - Enable 'Use with 1Password CLI'" -ForegroundColor Gray
    Write-Host "   - Restart terminal" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Manual Sign In:" -ForegroundColor White
    Write-Host "   op account add" -ForegroundColor Gray
    Write-Host "   op signin" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Service Account:" -ForegroundColor White
    Write-Host "   Set OP_SERVICE_ACCOUNT_TOKEN environment variable" -ForegroundColor Gray
    Write-Host ""
    Write-Host "After signing in, run this script again" -ForegroundColor Yellow
    exit 1
}

# Check if GitHub token item exists
Write-Host "`n🔍 Checking for GitHub token in 1Password..." -ForegroundColor Cyan

$vaults = @("M365-RAG-Production", "Private", "Personal")
$found = $false

foreach ($vault in $vaults) {
    try {
        $items = op item list --vault $vault --format json 2>$null | ConvertFrom-Json
        $githubItems = $items | Where-Object { $_.title -like "*GitHub*" -or $_.title -like "*github*" }
        
        if ($githubItems) {
            Write-Host "✅ Found GitHub items in vault '$vault':" -ForegroundColor Green
            $githubItems | ForEach-Object {
                Write-Host "   - $($_.title)" -ForegroundColor White
            }
            $found = $true
        }
    } catch {
        # Vault doesn't exist or no access
    }
}

if (-not $found) {
    Write-Host "❌ No GitHub token found in 1Password" -ForegroundColor Red
    Write-Host ""
    Write-Host "Create a GitHub Personal Access Token:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Go to: https://github.com/settings/tokens" -ForegroundColor White
    Write-Host "2. Click 'Generate new token' > 'Generate new token (classic)'" -ForegroundColor White
    Write-Host "3. Set expiration (recommended: 1 year)" -ForegroundColor White
    Write-Host "4. Select scopes:" -ForegroundColor White
    Write-Host "   ✅ repo (Full control of private repositories)" -ForegroundColor Gray
    Write-Host "   ✅ read:org (Read org and team membership)" -ForegroundColor Gray
    Write-Host "   ✅ read:user (Read user profile data)" -ForegroundColor Gray
    Write-Host "5. Click 'Generate token'" -ForegroundColor White
    Write-Host "6. Copy the token (you won't see it again!)" -ForegroundColor White
    Write-Host ""
    Write-Host "Then add it to 1Password:" -ForegroundColor Yellow
    Write-Host "1. Open 1Password app" -ForegroundColor White
    Write-Host "2. Create new item: 'Login'" -ForegroundColor White
    Write-Host "3. Title: 'GitHub Personal Access Token'" -ForegroundColor White
    Write-Host "4. Add field: 'token' with your GitHub token" -ForegroundColor White
    Write-Host "5. Save the item" -ForegroundColor White
    Write-Host ""
    Write-Host "After adding to 1Password, run:" -ForegroundColor Yellow
    Write-Host "  .\get-github-token-from-1password.ps1" -ForegroundColor White
    exit 1
}

Write-Host "`n🎉 Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Run: .\get-github-token-from-1password.ps1" -ForegroundColor White
Write-Host "2. Or run: npm run mcp:health" -ForegroundColor White
Write-Host "3. Test GitHub MCP operations" -ForegroundColor White

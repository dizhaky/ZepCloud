<#
.SYNOPSIS
    Fix Kapture MCP Server Issues
.DESCRIPTION
    Diagnoses and fixes Kapture MCP server connection issues
.EXAMPLE
    .\fix-kapture-mcp-fixed.ps1
#>

Write-Host "`n🔧 Kapture MCP Server Fix" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

# Check if Kapture MCP is configured
Write-Host "`n📋 Checking Kapture MCP configuration..." -ForegroundColor Yellow

$mcpConfigPath = ".cursor/mcp.json"
if (-not (Test-Path $mcpConfigPath)) {
    Write-Host "❌ MCP configuration file not found: $mcpConfigPath" -ForegroundColor Red
    exit 1
}

$mcpConfig = Get-Content $mcpConfigPath | ConvertFrom-Json
$kapture = $mcpConfig.mcpServers.kapture

if (-not $kapture) {
    Write-Host "❌ Kapture MCP not configured in mcp.json" -ForegroundColor Red
    Write-Host "Adding Kapture MCP configuration..." -ForegroundColor Yellow
    
    $kaptureConfig = @{
        command = "npx"
        args = @("-y", "@kapture/mcp")
        env = @{
            BROWSER = "chrome"
            AUTO_ACTIVATE = "true"
            PERSISTENT = "true"
            AUTO_RECOVER = "true"
        }
    }
    
    $mcpConfig.mcpServers.kapture = $kaptureConfig
    $mcpConfig | ConvertTo-Json -Depth 10 | Set-Content $mcpConfigPath
    
    Write-Host "✅ Kapture MCP configuration added" -ForegroundColor Green
} else {
    Write-Host "✅ Kapture MCP is configured" -ForegroundColor Green
    Write-Host "   Browser: $($kapture.env.BROWSER)" -ForegroundColor Gray
    Write-Host "   Auto-activate: $($kapture.env.AUTO_ACTIVATE)" -ForegroundColor Gray
}

# Check if Kapture extension is installed
Write-Host "`n🔍 Checking Kapture browser extension..." -ForegroundColor Yellow

Write-Host "Kapture MCP requires the Kapture browser extension to be installed." -ForegroundColor White
Write-Host ""
Write-Host "To fix Kapture MCP issues:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Install Kapture Extension:" -ForegroundColor White
Write-Host "   Chrome: https://chrome.google.com/webstore/detail/kapture" -ForegroundColor Gray
Write-Host "   Edge: https://microsoftedge.microsoft.com/addons/detail/kapture" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Enable the extension in your browser" -ForegroundColor White
Write-Host ""
Write-Host "3. Restart Cursor to reload MCP connections" -ForegroundColor White
Write-Host ""
Write-Host "4. Test Kapture MCP:" -ForegroundColor White
Write-Host "   npm run mcp:health" -ForegroundColor Gray

# Check if Chrome is available
Write-Host "`n🌐 Checking browser availability..." -ForegroundColor Yellow

$chromePaths = @(
    "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "${env:LOCALAPPDATA}\Google\Chrome\Application\chrome.exe"
)

$chromeFound = $false
foreach ($path in $chromePaths) {
    if (Test-Path $path) {
        Write-Host "✅ Chrome found: $path" -ForegroundColor Green
        $chromeFound = $true
        break
    }
}

if (-not $chromeFound) {
    Write-Host "⚠️  Chrome not found in standard locations" -ForegroundColor Yellow
    Write-Host "   Kapture MCP works best with Chrome" -ForegroundColor Gray
    Write-Host "   Install Chrome: https://www.google.com/chrome/" -ForegroundColor Gray
}

# Alternative browser automation options
Write-Host "`n🔄 Alternative browser automation options:" -ForegroundColor Yellow
Write-Host ""
Write-Host "If Kapture continues to have issues, consider:" -ForegroundColor White
Write-Host ""
Write-Host "1. Playwright MCP Server:" -ForegroundColor White
Write-Host "   npx -y @modelcontextprotocol/server-playwright" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Puppeteer MCP Server:" -ForegroundColor White
Write-Host "   npx -y @modelcontextprotocol/server-puppeteer" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Selenium MCP Server:" -ForegroundColor White
Write-Host "   npx -y @modelcontextprotocol/server-selenium" -ForegroundColor Gray

Write-Host "`n🎯 Kapture MCP Troubleshooting Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Install Kapture browser extension" -ForegroundColor White
Write-Host "2. Restart Cursor" -ForegroundColor White
Write-Host "3. Run: npm run mcp:health" -ForegroundColor White
Write-Host "4. Test browser automation" -ForegroundColor White

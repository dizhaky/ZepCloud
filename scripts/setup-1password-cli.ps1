# Setup 1Password CLI Integration
# This script helps you configure 1Password CLI

Write-Host "`n╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     1Password CLI Setup for Hetzner Credentials       ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "Choose your setup method:`n" -ForegroundColor Yellow

Write-Host "1. Desktop App Integration (Easiest)" -ForegroundColor Green
Write-Host "   - Open 1Password desktop app" -ForegroundColor White
Write-Host "   - Go to Settings > Developer" -ForegroundColor White
Write-Host "   - Enable 'Connect with 1Password CLI'" -ForegroundColor White
Write-Host "   - Then run: op vault list" -ForegroundColor Cyan
Write-Host ""

Write-Host "2. Manual Sign-In" -ForegroundColor Green
Write-Host "   Run: op account add --address <your-account>.1password.com --email <your-email>" -ForegroundColor Cyan
Write-Host ""

Write-Host "3. Service Account Token" -ForegroundColor Green
Write-Host "   Set environment variable: `$env:OP_SERVICE_ACCOUNT_TOKEN = 'your-token'" -ForegroundColor Cyan
Write-Host ""

Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "`nAfter setup, retrieve Hetzner credentials with:" -ForegroundColor Yellow
Write-Host "  op item get 'Hetzner' --vault Private" -ForegroundColor Cyan
Write-Host ""

# Check if 1Password app is running
$op1PasswordProcess = Get-Process -Name "1Password" -ErrorAction SilentlyContinue

if ($op1PasswordProcess) {
    Write-Host "✅ 1Password desktop app is running!" -ForegroundColor Green
    Write-Host "   Enable CLI integration in Settings > Developer" -ForegroundColor White
} else {
    Write-Host "⚠️  1Password desktop app is not running" -ForegroundColor Yellow
    Write-Host "   Please start the 1Password app first" -ForegroundColor White
}

Write-Host ""


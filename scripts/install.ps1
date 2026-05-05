$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "Python is not available on PATH."
    exit 1
}
$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
python scripts/install.py
$code = $LASTEXITCODE
Pop-Location
Write-Host "Install complete. Run: python -m app.main to start JARVIS."
exit $code

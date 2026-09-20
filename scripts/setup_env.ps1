$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path ".venv")) {
    py -3.11 -m venv .venv
}

& ".venv\\Scripts\\python.exe" -m pip install --upgrade pip
& ".venv\\Scripts\\python.exe" -m pip install -r requirements.txt

Write-Host ""
Write-Host "Environment ready." -ForegroundColor Green
Write-Host "VS Code should use: .venv\\Scripts\\python.exe"
Write-Host "If Pylance still shows old diagnostics, run 'Python: Restart Language Server'."

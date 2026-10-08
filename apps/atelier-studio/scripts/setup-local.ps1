# Install Atelier Studio for LOCAL use on Windows.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "==> Atelier Studio · local setup"
Write-Host "    $Root"

$py = $null
if (Get-Command py -ErrorAction SilentlyContinue) { $py = "py -3" }
elseif (Get-Command python -ErrorAction SilentlyContinue) { $py = "python" }
else { throw "Python 3.11+ required. Install from https://www.python.org/downloads/" }

Invoke-Expression "$py -m pip install --upgrade pip"
Invoke-Expression "$py -m pip install -e ."

New-Item -ItemType Directory -Force -Path "customs","renders\desktop" | Out-Null

Write-Host ""
Write-Host "Done. Start with: .\Atelier.bat"
Write-Host "Need Blender: https://www.blender.org/download/"
Write-Host ""

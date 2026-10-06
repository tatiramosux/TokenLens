param([string]$Python = 'python')
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath $root
if (-not (Test-Path -LiteralPath '.venv/Scripts/python.exe')) {
    & $Python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao criar ambiente virtual.' }
}
& '.venv/Scripts/python.exe' -m pip install -r requirements-dev.txt
if ($LASTEXITCODE -ne 0) { throw 'Falha ao instalar dependencias.' }
& '.venv/Scripts/python.exe' -m pip install --no-build-isolation --no-deps -e ./core
if ($LASTEXITCODE -ne 0) { throw 'Falha ao instalar core.' }
Write-Host 'Pronto. Execute scripts/Start-Lab.ps1.'

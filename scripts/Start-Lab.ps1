$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath $root
& "$root/.venv/Scripts/python.exe" -m lab.server

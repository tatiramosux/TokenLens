$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
try {
    $input | Out-String | & "$root/.venv/Scripts/python.exe" "$root/bridges/claude_statusline.py" 2>$null
} catch {
    Write-Output 'TokenLens | metrica indisponivel'
}

param([switch]$Check)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$bridge = (Join-Path $root 'scripts/Claude-StatusLine.ps1').Replace('\','/')
# Forward slashes are supported by both Git Bash and PowerShell command runners.
$command = 'powershell -NoProfile -File "' + $bridge + '"'
$settings = @{ statusLine = @{ type = 'command'; command = $command } } | ConvertTo-Json -Depth 4 -Compress
if ($Check) { Write-Host 'Launcher pronto; nenhuma configuracao global foi alterada.'; exit 0 }
$previousId = $env:TOKENLENS_OBSERVATION_ID
try {
    $env:TOKENLENS_OBSERVATION_ID = [guid]::NewGuid().ToString()
    & claude --settings $settings
    $result = $LASTEXITCODE
} finally {
    $env:TOKENLENS_OBSERVATION_ID = $previousId
}
exit $result

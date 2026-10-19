param(
    [int]$Port = 4173,
    [switch]$Refresh
)

$ErrorActionPreference = 'Stop'
$taskRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$taskPython = Join-Path $taskRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $taskPython)) {
    throw 'Create the project environment first with uv sync --locked.'
}
if ($Port -lt 1024 -or $Port -gt 65535) {
    throw 'Choose a port from 1024 through 65535.'
}

Push-Location $taskRoot
try {
    if ($Refresh) {
        $taskNode = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
        $taskCodexRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' }
        $taskPluginPattern = Join-Path $taskCodexRoot 'plugins/cache/openai-curated-remote/data-analytics/*/scripts/data-app.mjs'
        $taskBuilder = Get-ChildItem -Path $taskPluginPattern -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if (-not $taskBuilder -or -not (Test-Path -LiteralPath $taskNode)) {
            throw 'The Codex Data plugin/runtime is required for this refresh path. See USAGE.md.'
        }
        & $taskPython -m grounding_verifier.error_explorer --out tools/error-explorer/src/data.json --build-status complete
        if ($LASTEXITCODE -ne 0) { throw 'Evidence export failed. Existing compiled preview was not rebuilt.' }
        & $taskNode $taskBuilder.FullName build --project-dir $PSScriptRoot --separate-data
        if ($LASTEXITCODE -ne 0) { throw 'Dashboard build failed.' }
    }
    $taskDist = Join-Path $PSScriptRoot 'dist'
    if (-not (Test-Path -LiteralPath (Join-Path $taskDist 'index.html'))) {
        throw 'No compiled preview. Run this script with -Refresh first.'
    }
    Write-Host "Error explorer: http://127.0.0.1:$Port/ (Ctrl+C to stop)"
    & $taskPython -m http.server $Port --bind 127.0.0.1 --directory $taskDist
}
finally {
    Pop-Location
}

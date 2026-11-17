# Installs only into this project; no administrator privileges required.
[CmdletBinding()]
param([string]$Python = 'python')
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
function Run-Checked([string]$Command, [string[]]$Arguments) {
    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Installation step failed: $Command (exit $LASTEXITCODE)" }
}
$pythonExe = (Get-Command $Python -ErrorAction Stop).Source
$nodeExe = (Get-Command node.exe -ErrorAction Stop).Source
$npm = (Get-Command npm.cmd -ErrorAction Stop).Source
Run-Checked $pythonExe @('-c', 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)')
$nodeVersion = [version]((& $nodeExe --version).TrimStart('v'))
if ($nodeVersion -lt [version]'22.12.0') { throw 'Node.js 22.12+ required.' }
$venv = Join-Path $root '.venv'
$venvPython = Join-Path $venv 'Scripts\python.exe'
if (-not (Test-Path $venvPython)) { Run-Checked $pythonExe @('-m', 'venv', $venv) }
$env:PYTHONNOUSERSITE = '1'
$env:PYTHONUTF8 = '1'
Run-Checked $venvPython @('-m', 'pip', 'install', '-r', (Join-Path $root 'backend/requirements-lock.txt'))
Run-Checked $venvPython @('-m', 'pip', 'check')
Push-Location (Join-Path $root 'frontend')
try {
    Run-Checked $npm @('ci', '--ignore-scripts', '--no-audit', '--no-fund')
    Run-Checked $npm @('run', 'build')
} finally { Pop-Location }
# Never overwrite an existing configuration.
if (-not (Test-Path (Join-Path $root '.env'))) { Copy-Item -LiteralPath (Join-Path $root '.env.example') -Destination (Join-Path $root '.env') }
Run-Checked $venvPython @((Join-Path $root 'tools/run_offline_tests.py'))
Write-Output 'Installation complete. Run .\Start-Viral-Prompt-Studio.ps1'

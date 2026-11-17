[CmdletBinding()]
param([int]$Port = -1, [switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { throw 'Run Install-Windows.ps1 first.' }
$arguments = @((Join-Path $PSScriptRoot 'tools\launcher.py'))
if ($Port -ge 0) { $arguments += @('--port', "$Port") }
if ($NoBrowser) { $arguments += '--no-browser' }
$env:PYTHONNOUSERSITE = '1'
$env:PYTHONUTF8 = '1'
& $python @arguments
if ($LASTEXITCODE -ne 0) { throw "Viral Prompt Studio start failed (exit $LASTEXITCODE)." }

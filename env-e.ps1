$ErrorActionPreference = 'Stop'

# Resolve repo root relative to this script so it works from any location.
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

# Core directories pinned to E:
$env:HOME = Join-Path $root '.home'
$env:USERPROFILE = $env:HOME
$env:APPDATA = Join-Path $env:HOME 'AppData\Roaming'
$env:LOCALAPPDATA = Join-Path $env:HOME 'AppData\Local'
$env:PNPM_STORE_DIR = Join-Path $root '.pnpm-store'
$env:PNPM_HOME = Join-Path $env:HOME '.pnpm'
$env:npm_config_cache = Join-Path $root '.npm-cache'
$env:TMP = Join-Path $root '.tmp'
$env:TEMP = $env:TMP

# Ensure directories exist.
@(
  $env:HOME,
  $env:APPDATA,
  $env:LOCALAPPDATA,
  $env:PNPM_STORE_DIR,
  $env:PNPM_HOME,
  $env:npm_config_cache,
  $env:TMP
) | ForEach-Object { if (-not (Test-Path $_)) { New-Item -ItemType Directory -Force -Path $_ | Out-Null } }

# Portable Node (preinstalled).
$env:NODE_EXE = Join-Path $root '.tools\node-v22.11.0-win-x64\node.exe'
$env:NPM_CLI = Join-Path $root '.tools\node-v22.11.0-win-x64\node_modules\npm\bin\npm-cli.js'

# Put Node and pnpm on PATH (pnpm will appear here after install).
$pnpmBin = Join-Path $env:PNPM_HOME 'node_modules\.bin'
$pathParts = @(
  (Join-Path $root '.tools\node-v22.11.0-win-x64'),
  $pnpmBin,
  $env:Path
) | Where-Object { $_ -and ($_ -ne '') }
$env:Path = [string]::Join(';', $pathParts)

Write-Host "Environment pinned to E: for Node/pnpm. NODE_EXE=$($env:NODE_EXE)"

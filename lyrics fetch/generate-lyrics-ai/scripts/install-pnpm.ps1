$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$nodeDir = Join-Path $root ".tools\\node-v20.11.1-win-x64"
$node = Join-Path $nodeDir "node.exe"
$npmCli = Join-Path $nodeDir "node_modules\\npm\\bin\\npm-cli.js"

if (-not (Test-Path $node)) {
  throw "Node not found at $node"
}

$env:NPM_CONFIG_PREFIX = Join-Path $root ".tools\\npm-global"
$env:NPM_CONFIG_CACHE = Join-Path $root ".tools\\npm-cache"
New-Item -ItemType Directory -Force -Path $env:NPM_CONFIG_PREFIX | Out-Null
New-Item -ItemType Directory -Force -Path $env:NPM_CONFIG_CACHE | Out-Null

Write-Host "Installing pnpm using $node..."
& $node $npmCli install -g pnpm --cache $env:NPM_CONFIG_CACHE

Write-Host "pnpm installed. Add $env:NPM_CONFIG_PREFIX\\bin to PATH for this session:"
Write-Host "`$env:PATH = '$($env:NPM_CONFIG_PREFIX)\\bin;' + `$env:PATH"

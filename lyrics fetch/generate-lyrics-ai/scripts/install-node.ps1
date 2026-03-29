$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$tools = Join-Path $root ".tools"
New-Item -ItemType Directory -Force -Path $tools | Out-Null

$url = "https://nodejs.org/dist/v20.11.1/node-v20.11.1-win-x64.zip"
$zip = Join-Path $tools "node.zip"
Write-Host "Downloading Node from $url..."
Invoke-WebRequest -Uri $url -OutFile $zip

Write-Host "Extracting Node..."
Expand-Archive -Force -Path $zip -DestinationPath $tools

$nodeDir = Join-Path $tools "node-v20.11.1-win-x64"
Write-Host "Node extracted to $nodeDir"
Write-Host "Run node from: $nodeDir\\node.exe"

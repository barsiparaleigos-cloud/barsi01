param(
  [int]$ApiPort = 8000,
  [int]$WebPort = 5173,
  [string]$HostAddress = "127.0.0.1"
)

$ErrorActionPreference = "Stop"

function Find-FreePort([int]$startPort) {
  $p = $startPort
  while ($true) {
    try {
      $listener = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction Stop | Select-Object -First 1
      if ($null -ne $listener) { $p++; continue }
    } catch {
      return $p
    }
  }
}

function Wait-HttpOk([string]$url, [int]$timeoutSeconds = 20) {
  $deadline = (Get-Date).AddSeconds($timeoutSeconds)
  while ((Get-Date) -lt $deadline) {
    try {
      $res = Invoke-WebRequest -UseBasicParsing $url -TimeoutSec 3
      if ($res.StatusCode -ge 200 -and $res.StatusCode -lt 500) { return $true }
    } catch {
      Start-Sleep -Milliseconds 400
    }
  }
  return $false
}

Push-Location (Split-Path $PSScriptRoot -Parent)
try {
  $apiPortToUse = Find-FreePort $ApiPort
  $webPortToUse = Find-FreePort $WebPort

  $pythonExe = Join-Path (Get-Location) "venv\Scripts\python.exe"
  if (-not (Test-Path $pythonExe)) { $pythonExe = "python" }

  Write-Host "Starting backend (Python) on http://${HostAddress}:${apiPortToUse} ..." -ForegroundColor Yellow
  Start-Process -FilePath pwsh -WorkingDirectory (Get-Location) -ArgumentList @(
    "-NoExit",
    "-Command",
    "$pythonExe -m web.home_server"
  ) | Out-Null

  if (-not (Wait-HttpOk "http://${HostAddress}:${apiPortToUse}/api/status" 15)) {
    Write-Host "Backend didn't respond on port $apiPortToUse yet. It may still be starting." -ForegroundColor DarkYellow
  }

  $webDir = Join-Path (Get-Location) "webapp"
  if (-not (Test-Path (Join-Path $webDir "node_modules"))) {
    Write-Host "Installing webapp dependencies (npm install)..." -ForegroundColor Yellow
    Push-Location $webDir
    try {
      & npm install
    } finally {
      Pop-Location
    }
  }

  Write-Host "Starting frontend (Vite) on http://${HostAddress}:${webPortToUse} ..." -ForegroundColor Yellow
  Start-Process -FilePath pwsh -WorkingDirectory $webDir -ArgumentList @(
    "-NoExit",
    "-Command",
    "npm run dev -- --host $HostAddress --port $webPortToUse"
  ) | Out-Null

  Write-Host "" 
  Write-Host "Open:" -ForegroundColor Green
  Write-Host "- Frontend: http://${HostAddress}:${webPortToUse}" -ForegroundColor Green
  Write-Host "- Backend:  http://${HostAddress}:${apiPortToUse}" -ForegroundColor Green
  Write-Host "- API:      http://${HostAddress}:${apiPortToUse}/api/stocks" -ForegroundColor Green
} finally {
  Pop-Location
}

param(
  [switch]$SetupOnly,
  [switch]$JobsOnly,
  [switch]$HomeOnly
)

$ErrorActionPreference = "Stop"

Push-Location (Split-Path $PSScriptRoot -Parent)
try {
  # 1) Ensure .env.local is present and valid
  $needsSetup = $false
  if (-not (Test-Path ".env.local")) {
    $needsSetup = $true
  } else {
    $content = Get-Content ".env.local" -Raw
    if ($content -match "SUPABASE_URL=\s*$" -or $content -match "SUPABASE_URL=\p{Cc}") { $needsSetup = $true }
    if ($content -match "SUPABASE_ANON_KEY=\p{Cc}" -or $content -match "SUPABASE_SERVICE_ROLE_KEY=\p{Cc}") { $needsSetup = $true }
  }

  if ($needsSetup) {
    Write-Host "Configuring .env.local..." -ForegroundColor Yellow
    & "$PSScriptRoot\setup_env.ps1"
  }

  if ($SetupOnly) {
    Write-Host "Setup completed." -ForegroundColor Green
    return
  }

  # 2) Run jobs
  if (-not $HomeOnly) {
    Write-Host "Running jobs..." -ForegroundColor Yellow
    .\venv\Scripts\python.exe -m jobs.sync_prices
    .\venv\Scripts\python.exe -m jobs.sync_dividends
    .\venv\Scripts\python.exe -m jobs.compute_signals
  }

  if ($JobsOnly) {
    Write-Host "Jobs completed." -ForegroundColor Green
    return
  }

  # 3) Start Home
  if (-not $JobsOnly) {
    Write-Host "Starting Home on http://127.0.0.1:8000" -ForegroundColor Yellow
    .\venv\Scripts\python.exe -m web.home_server
  }
}
finally {
  Pop-Location
}

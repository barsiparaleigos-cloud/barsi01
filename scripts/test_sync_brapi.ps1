# Script para testar sincronização Brapi → Supabase
# Execute: .\scripts\test_sync_brapi.ps1

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  TESTE: BRAPI → SUPABASE" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se .env.local existe
if (-not (Test-Path ".env.local")) {
    Write-Error "ERRO: Arquivo .env.local nao encontrado"
    Write-Host "Configure suas credenciais do Supabase:" -ForegroundColor Yellow
    Write-Host "  1. Copie .env.example para .env.local" -ForegroundColor Gray
    Write-Host "  2. Adicione SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY" -ForegroundColor Gray
    Write-Host "  3. Execute: .\scripts\setup_env.ps1" -ForegroundColor Gray
    exit 1
}

Write-Host "OK: Credenciais do Supabase encontradas" -ForegroundColor Green
Write-Host ""

# Verificar se venv existe
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Warning "AVISO: Virtual environment nao encontrado"
    Write-Host "Criando venv..." -ForegroundColor Cyan
    python -m venv venv
    
    Write-Host "Instalando dependências..." -ForegroundColor Cyan
    .\venv\Scripts\pip.exe install -r requirements.txt
}

Write-Host "Executando job: sync_precos_brapi" -ForegroundColor Cyan
Write-Host ""

# Executar job
.\venv\Scripts\python.exe -m jobs.sync_precos_brapi

if ($LASTEXITCODE -ne 0) {
    Write-Error "ERRO: Job falhou (exit code: $LASTEXITCODE)"
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "OK: Teste concluido com sucesso" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "Verificar dados no Supabase:" -ForegroundColor Cyan
Write-Host "  SELECT * FROM precos ORDER BY data DESC LIMIT 10;" -ForegroundColor Gray
Write-Host ""

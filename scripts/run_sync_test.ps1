# Script Autônomo: Testar Sincronização Brapi → Supabase
# Executa tudo automaticamente sem interação do usuário

$ErrorActionPreference = "Stop"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  TESTE AUTONOMO: BRAPI -> SUPABASE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Navegar para o diretório do projeto
$projectPath = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $projectPath
Write-Host "Diretorio: $projectPath" -ForegroundColor Gray

# 1. Verificar Python
Write-Host "`n[1/5] Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = & python --version 2>&1
    Write-Host "   OK: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   ERRO: Python nao encontrado!" -ForegroundColor Red
    exit 1
}

# 2. Verificar/Criar Virtual Environment
Write-Host "`n[2/5] Verificando virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "   venv nao encontrado, criando..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "   OK: venv criado" -ForegroundColor Green
} else {
    Write-Host "   OK: venv encontrado" -ForegroundColor Green
}

# 3. Instalar dependências
Write-Host "`n[3/5] Instalando dependencias..." -ForegroundColor Yellow
& .\venv\Scripts\pip.exe install --quiet --upgrade pip
& .\venv\Scripts\pip.exe install --quiet python-dotenv requests
Write-Host "   OK: Dependencias instaladas" -ForegroundColor Green

# 4. Verificar credenciais Supabase
Write-Host "`n[4/5] Verificando credenciais..." -ForegroundColor Yellow
if (-not (Test-Path ".env.local")) {
    Write-Host "   ERRO: .env.local nao encontrado!" -ForegroundColor Red
    Write-Host "`n   Configure suas credenciais:" -ForegroundColor Yellow
    Write-Host "      1. Crie arquivo .env.local" -ForegroundColor Gray
    Write-Host "      2. Adicione:" -ForegroundColor Gray
    Write-Host "         SUPABASE_URL=https://seu-projeto.supabase.co" -ForegroundColor Gray
    Write-Host "         SUPABASE_SERVICE_ROLE_KEY=seu_service_role_key" -ForegroundColor Gray
    exit 1
}

# Verificar se tem as variáveis necessárias
$envContent = Get-Content .env.local -Raw
if ($envContent -notmatch "SUPABASE_URL" -or $envContent -notmatch "SUPABASE_SERVICE_ROLE_KEY") {
    Write-Host "   ERRO: Credenciais incompletas em .env.local!" -ForegroundColor Red
    exit 1
}
Write-Host "   OK: Credenciais encontradas" -ForegroundColor Green

# 5. Executar Job de Sincronização
Write-Host "`n[5/5] Executando sincronizacao..." -ForegroundColor Yellow
Write-Host "========================================`n" -ForegroundColor Cyan

$result = & .\venv\Scripts\python.exe -m jobs.sync_precos_brapi 2>&1

# Mostrar output
Write-Host $result

# Verificar se teve sucesso
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "OK: SINCRONIZACAO CONCLUIDA COM SUCESSO!" -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Green
    
    Write-Host "Proximos comandos uteis:" -ForegroundColor Cyan
    Write-Host "   • Ver no Supabase SQL Editor:" -ForegroundColor Gray
    Write-Host "     SELECT * FROM precos ORDER BY data DESC LIMIT 10;" -ForegroundColor White
    Write-Host "`n   • Ver tickers:" -ForegroundColor Gray
    Write-Host "     SELECT * FROM ticker_mapping WHERE ativo = true;" -ForegroundColor White
    Write-Host "`n   • Ver logs:" -ForegroundColor Gray
    Write-Host "     SELECT * FROM job_runs ORDER BY started_at DESC LIMIT 5;" -ForegroundColor White
    Write-Host ""
    
    exit 0
} else {
    Write-Host "`n========================================" -ForegroundColor Red
    Write-Host "ERRO: FALHA NA SINCRONIZACAO!" -ForegroundColor Red
    Write-Host "========================================`n" -ForegroundColor Red
    
    Write-Host "Possiveis solucoes:" -ForegroundColor Yellow
    Write-Host "   1. Verifique se a migração 003 foi aplicada" -ForegroundColor Gray
    Write-Host "   2. Verifique as credenciais em .env.local" -ForegroundColor Gray
    Write-Host "   3. Verifique se há tickers em ticker_mapping" -ForegroundColor Gray
    Write-Host ""
    
    exit 1
}

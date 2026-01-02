# Script Master: Sincronização Completa de Dados
# Executa todas as sincronizações necessárias para metodologia Barsi
# Ordem: CVM -> Preços -> Dividendos -> Enriquecimento

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================================================"
Write-Host "SINCRONIZACAO MASTER - METODOLOGIA BARSI"
Write-Host "========================================================================"
Write-Host ""

# Navegar para diretório raiz
$PROJECT_ROOT = "c:\Users\rafae\OneDrive\Desktop\Barsi Para Leigos\barsi01"
Set-Location $PROJECT_ROOT

Write-Host "[INFO] Diretorio: $PROJECT_ROOT"
Write-Host ""

# Verificar Python
Write-Host "[1/6] Verificando Python..."
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  [OK] $pythonVersion"
} catch {
    Write-Host "  [ERRO] Python nao encontrado!"
    Write-Host "  Instale Python 3.10+ de https://python.org"
    exit 1
}

# Verificar venv
Write-Host ""
Write-Host "[2/6] Verificando ambiente virtual..."
$venvPath = Join-Path $PROJECT_ROOT "venv"

if (Test-Path "$venvPath\Scripts\python.exe") {
    Write-Host "  [OK] venv encontrado"
} else {
    Write-Host "  [AVISO] venv nao encontrado, criando..."
    python -m venv venv
    Write-Host "  [OK] venv criado"
}

$python = "$venvPath\Scripts\python.exe"

# Instalar dependências
Write-Host ""
Write-Host "[3/6] Verificando dependencias..."
& $python -m pip install --quiet --upgrade pip
& $python -m pip install --quiet python-dotenv requests pandas
Write-Host "  [OK] Dependencias instaladas"

# Verificar .env.local
Write-Host ""
Write-Host "[4/6] Verificando credenciais Supabase..."
$envFile = Join-Path $PROJECT_ROOT ".env.local"

if (-not (Test-Path $envFile)) {
    Write-Host "  [ERRO] Arquivo .env.local nao encontrado!"
    Write-Host "  Crie o arquivo com:"
    Write-Host "    SUPABASE_URL=https://seu-projeto.supabase.co"
    Write-Host "    SERVICE_ROLE_KEY=sua-chave-service-role"
    exit 1
}

$envContent = Get-Content $envFile -Raw
if ($envContent -match "SUPABASE_URL" -and $envContent -match "SERVICE_ROLE_KEY") {
    Write-Host "  [OK] Credenciais encontradas"
} else {
    Write-Host "  [ERRO] Credenciais incompletas no .env.local"
    exit 1
}

Write-Host ""
Write-Host "========================================================================"
Write-Host "INICIANDO SINCRONIZACOES"
Write-Host "========================================================================"

# Job 1: Fundamentalistas CVM
Write-Host ""
Write-Host "[5/6] JOB 1: Sincronizar Fundamentalistas CVM..."
Write-Host "------------------------------------------------------------------------"
try {
    & $python -m jobs.sync_fundamentals_cvm
    Write-Host ""
    Write-Host "  [OK] Fundamentalistas CVM sincronizados"
} catch {
    Write-Host ""
    Write-Host "  [ERRO] Falha no job de fundamentalistas CVM"
    Write-Host "  $_"
    exit 1
}

# Job 2: Preços Brapi
Write-Host ""
Write-Host "[6/6] JOB 2: Sincronizar Precos Brapi..."
Write-Host "------------------------------------------------------------------------"
try {
    & $python -m jobs.sync_precos_brapi
    Write-Host ""
    Write-Host "  [OK] Precos sincronizados"
} catch {
    Write-Host ""
    Write-Host "  [ERRO] Falha no job de precos"
    Write-Host "  $_"
    exit 1
}

# Job 3: Dividendos Brapi
Write-Host ""
Write-Host "JOB 3: Sincronizar Dividendos Brapi..."
Write-Host "------------------------------------------------------------------------"
try {
    & $python -m jobs.sync_dividendos_brapi
    Write-Host ""
    Write-Host "  [OK] Dividendos sincronizados"
} catch {
    Write-Host ""
    Write-Host "  [AVISO] Job de dividendos falhou (alguns tickers podem nao ter assets)"
    Write-Host "  $_"
}

# Job 4: Enriquecimento (opcional)
Write-Host ""
Write-Host "JOB 4: Enriquecer Ticker Mapping (opcional)..."
Write-Host "------------------------------------------------------------------------"
try {
    & $python -m jobs.enrich_ticker_mapping
    Write-Host ""
    Write-Host "  [OK] Ticker mapping enriquecido"
} catch {
    Write-Host ""
    Write-Host "  [AVISO] Enriquecimento falhou (tabela companies_cvm pode nao existir)"
    Write-Host "  $_"
}

Write-Host ""
Write-Host "========================================================================"
Write-Host "SINCRONIZACAO MASTER CONCLUIDA"
Write-Host "========================================================================"
Write-Host ""
Write-Host "[INFO] Proximos passos:"
Write-Host "  1. Verificar dados no Supabase Dashboard"
Write-Host "  2. Executar calculos de Dividend Yield"
Write-Host "  3. Gerar ranking de empresas Barsi"
Write-Host ""
Write-Host "Para re-executar: .\scripts\run_master_sync.ps1"
Write-Host ""

# Script para aplicar migração 003 no Supabase
# Execute: .\scripts\apply_migration_003.ps1

param(
    [string]$ProjectRef = $env:SUPABASE_PROJECT_REF
)

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  APLICAR MIGRAÇÃO 003 NO SUPABASE" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se Supabase CLI está instalado
if (-not (Get-Command supabase -ErrorAction SilentlyContinue)) {
    Write-Error "ERRO: Supabase CLI nao encontrado"
    Write-Host "Instale com: npm install -g supabase" -ForegroundColor Yellow
    exit 1
}

# Verificar se está linkado ao projeto
if (-not (Test-Path ".\.git\supabase-link")) {
    Write-Warning "AVISO: Projeto nao linkado ao Supabase"
    Write-Host "Execute primeiro: .\scripts\supabase_link.ps1" -ForegroundColor Yellow
    
    if ($ProjectRef) {
        Write-Host "Tentando linkar automaticamente com project-ref: $ProjectRef" -ForegroundColor Cyan
        & supabase link --project-ref $ProjectRef
        
        if ($LASTEXITCODE -ne 0) {
            Write-Error "ERRO: Falha ao linkar projeto"
            exit 1
        }
    } else {
        exit 1
    }
}

Write-Host "Migracoes disponiveis:" -ForegroundColor Cyan
Write-Host "  001_init.sql" -ForegroundColor Gray
Write-Host "  002_align_schema.sql" -ForegroundColor Gray
Write-Host "  003_add_precos_and_ticker_mapping.sql" -ForegroundColor Green
Write-Host ""

# Perguntar confirmação
$confirm = Read-Host "Aplicar migração 003 no Supabase? (S/n)"
if ($confirm -eq "n" -or $confirm -eq "N") {
    Write-Host "Cancelado pelo usuario" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Aplicando migracao 003..." -ForegroundColor Cyan

# Aplicar migração via Supabase CLI
$sqlFile = ".\sql\003_add_precos_and_ticker_mapping.sql"

if (-not (Test-Path $sqlFile)) {
    Write-Error "ERRO: Arquivo nao encontrado: $sqlFile"
    exit 1
}

Write-Host "Executando: $sqlFile" -ForegroundColor Gray

# Executar SQL no Supabase
& supabase db push

if ($LASTEXITCODE -ne 0) {
    Write-Error "ERRO: Falha ao aplicar migracao (exit code: $LASTEXITCODE)"
    Write-Host ""
    Write-Host "Alternativa: Aplique manualmente no dashboard" -ForegroundColor Yellow
    Write-Host "   1. Acesse: https://supabase.com/dashboard/project/$ProjectRef/sql" -ForegroundColor Gray
    Write-Host "   2. Cole o conteúdo de: $sqlFile" -ForegroundColor Gray
    Write-Host "   3. Execute (RUN)" -ForegroundColor Gray
    exit 1
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "OK: Migracao 003 aplicada com sucesso" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "Tabelas criadas:" -ForegroundColor Cyan
Write-Host "  • precos (cotações diárias)" -ForegroundColor Gray
Write-Host "  • ticker_mapping (CNPJ → Ticker)" -ForegroundColor Gray
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Cyan
Write-Host "  1. Testar sync de preços: python jobs\sync_precos.py --test" -ForegroundColor Gray
Write-Host "  2. Popular ticker_mapping com mais empresas" -ForegroundColor Gray
Write-Host "  3. Calcular Dividend Yield" -ForegroundColor Gray
Write-Host ""

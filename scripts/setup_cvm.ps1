# Script de setup rápido para integração CVM
# Execute: .\scripts\setup_cvm.ps1

Write-Host ""
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "  SETUP - INTEGRAÇÃO CVM (Dados Abertos)" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Python
Write-Host "1. Verificando Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Python instalado: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "   ❌ Python não encontrado!" -ForegroundColor Red
    Write-Host "   Instale Python 3.8+ antes de continuar" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 2. Instalar dependências
Write-Host "2. Instalando dependências CVM..." -ForegroundColor Yellow
Write-Host "   (requests, pandas)" -ForegroundColor Gray

pip install -q requests pandas

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Dependências instaladas" -ForegroundColor Green
} else {
    Write-Host "   ❌ Erro ao instalar dependências" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 3. Criar diretórios
Write-Host "3. Criando estrutura de diretórios..." -ForegroundColor Yellow

$dirs = @(
    "data/cvm",
    "data/processed",
    "data/integrations"
)

foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -Path $dir -ItemType Directory -Force | Out-Null
        Write-Host "   ✅ Criado: $dir" -ForegroundColor Green
    } else {
        Write-Host "   ℹ️  Já existe: $dir" -ForegroundColor Gray
    }
}

Write-Host ""

# 4. Testar conexão
Write-Host "4. Testando conexão com CVM..." -ForegroundColor Yellow

$testUrl = "https://dados.cvm.gov.br/"
try {
    $response = Invoke-WebRequest -Uri $testUrl -TimeoutSec 10 -UseBasicParsing
    Write-Host "   ✅ Portal CVM acessível" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Não foi possível acessar portal CVM" -ForegroundColor Yellow
    Write-Host "   Verifique sua conexão com internet" -ForegroundColor Yellow
}

Write-Host ""

# 5. Resumo
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "  SETUP CONCLUÍDO!" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor White
Write-Host ""
Write-Host "   1. Testar integração:" -ForegroundColor White
Write-Host "      python scripts/test_cvm.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "   2. Sincronizar dados:" -ForegroundColor White
Write-Host "      python -m jobs.sync_cvm" -ForegroundColor Cyan
Write-Host ""
Write-Host "   3. Ver documentação:" -ForegroundColor White
Write-Host "      docs/robo-cvm-guia.md" -ForegroundColor Cyan
Write-Host "      docs/integracao-cvm.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 LEMBRE-SE:" -ForegroundColor Yellow
Write-Host "   • Dados CVM são GRATUITOS e PÚBLICOS" -ForegroundColor White
Write-Host "   • NÃO precisa de login ou API key" -ForegroundColor White
Write-Host "   • Atualização automática semanal" -ForegroundColor White
Write-Host ""
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

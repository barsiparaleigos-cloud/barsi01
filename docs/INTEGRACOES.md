# Sistema de Integrações - Metodologia Barsi

## Visão Geral

Sistema completo de sincronização de dados para análise de ações via metodologia Barsi, com 4 fontes de dados integradas e sistema de fallback automático.

## APIs Integradas

### 1. Brapi (Principal)
**Status:** ✅ Online | **Prioridade:** 1 para preços e dividendos

- **URL:** https://brapi.dev/api
- **Dados:** Preços tempo real, dividendos, fundamentalistas, logos
- **Quota:** 4 ações gratuitas (PETR4, VALE3, ITUB4, MGLU3)
- **Update:** Tempo real (15min delay plano gratuito)
- **Job:** `jobs/sync_precos_brapi.py`, `jobs/sync_dividendos_brapi.py`

**Teste:**
```python
from integrations.brapi_integration import BrapiIntegration
brapi = BrapiIntegration()
brapi.test_connection()
```

### 2. CVM - Comissão de Valores Mobiliários (Oficial)
**Status:** ✅ Online | **Prioridade:** 1 para fundamentalistas

- **URL:** https://dados.cvm.gov.br/dados
- **Dados:** Cadastro empresas, ITR, DFP, dividendos declarados
- **Quota:** Ilimitada (dados abertos)
- **Update:** Diário (cadastro), Trimestral (ITR), Anual (DFP)
- **Job:** `jobs/sync_fundamentals_cvm.py`

**Dados Disponíveis:**
- **Cadastro:** CNPJ, razão social, código CVM, setor, município
- **ITR (Trimestral):** DRE, Balanço, Fluxo de Caixa
- **DFP (Anual):** Demonstrações completas
- **Dividendos:** Proventos declarados oficialmente

**Teste:**
```python
from integrations.cvm_integration import CVMIntegration
cvm = CVMIntegration()
empresas = cvm.get_empresas_ativas()
print(f"Total empresas ativas: {len(empresas)}")
```

### 3. B3 - Bolsa de Valores (Corporativo)
**Status:** ✅ Online | **Prioridade:** 1 para dados corporativos

- **URL:** https://sistemaswebb3-listados.b3.com.br/
- **Dados:** Empresas listadas, setores, classificação, calendário eventos
- **Quota:** Ilimitada (site público)
- **Update:** Diário
- **Job:** (a criar) `jobs/sync_companies_b3.py`

**Dados Disponíveis:**
- Empresas listadas (Bovespa, B3)
- Classificação setorial GICS
- Calendário de eventos corporativos
- Composição de índices (IBOV, IBRX, etc.)

### 4. Yahoo Finance (Backup)
**Status:** ✅ Online | **Prioridade:** 2 para preços (fallback)

- **URL:** https://query1.finance.yahoo.com/
- **Dados:** Preços históricos, cotações, volume
- **Quota:** Ilimitada (API pública)
- **Update:** Tempo real (15min delay)
- **Job:** (a criar) `jobs/sync_backup_yahoo.py`

**Uso:** Fallback caso Brapi falhe ou atinja limite

## Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                      MASTER INTEGRATOR                          │
│                 (integrations/master_integrator.py)             │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ test_all_connections()  - Testa 4 APIs                  │  │
│  │ get_available_sources() - Lista fontes online           │  │
│  │ get_data_priority()     - Define prioridade por tipo    │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
    ┌─────────┐          ┌─────────┐          ┌─────────┐
    │  BRAPI  │          │   CVM   │          │   B3    │
    │         │          │         │          │         │
    │ Preços  │          │ Fundamt │          │ Empres. │
    │ Divid.  │          │ Oficial │          │ Setores │
    └─────────┘          └─────────┘          └─────────┘
          │                    │                    │
          └────────────────────┴────────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   SUPABASE DB     │
                    ├───────────────────┤
                    │ precos            │
                    │ dividends         │
                    │ companies_cvm     │
                    │ ticker_mapping    │
                    │ assets            │
                    └───────────────────┘
```

## Prioridades por Tipo de Dado

Sistema define automaticamente qual API usar primeiro:

| Tipo de Dado   | Ordem de Prioridade        | Motivo                         |
|----------------|----------------------------|--------------------------------|
| **prices**     | brapi → yahoo → b3         | Brapi mais completo            |
| **dividends**  | brapi → cvm → b3           | Brapi histórico + CVM oficial  |
| **fundamentals** | cvm → brapi              | CVM é fonte oficial            |
| **corporate**  | b3 → cvm                   | B3 tem dados corporativos      |
| **indicators** | brapi → cvm                | Brapi calcula automaticamente  |

## Jobs de Sincronização

### 1. sync_precos_brapi.py
**Status:** ✅ Funcional (100%)

```bash
python -m jobs.sync_precos_brapi
```

**Resultado esperado:**
```
[OK] 4 ticker(s) para processar
- ITUB4: R$ 39.23 (+0.64%)
- MGLU3: R$ 8.94 (+0.40%)
- PETR4: R$ 30.82 (+0.29%)
- VALE3: R$ 71.96 (-0.22%)
[OK] 4 preco(s) salvos no Supabase
Taxa de sucesso: 100.0%
```

### 2. sync_dividendos_brapi.py
**Status:** ⚠️ Funcional (25% - aguarda migração 005)

```bash
python -m jobs.sync_dividendos_brapi
```

**Resultado esperado (pós migração 005):**
```
[OK] 4 ticker(s) para processar
- ITUB4: 69 dividendo(s) salvos ✅
- MGLU3: XX dividendo(s) salvos ✅
- PETR4: XX dividendo(s) salvos ✅
- VALE3: XX dividendo(s) salvos ✅
Taxa de sucesso: 100.0%
```

### 3. sync_fundamentals_cvm.py
**Status:** ✅ Pronto (aguarda migração 006)

```bash
python -m jobs.sync_fundamentals_cvm
```

**Resultado esperado:**
```
[INFO] Total empresas CVM: 500+
[INFO] Empresas ativas: 300+
[OK] Sincronizadas: 300+
```

### 4. enrich_ticker_mapping.py
**Status:** ✅ Pronto (aguarda job 3)

```bash
python -m jobs.enrich_ticker_mapping
```

**Função:** Enriquece ticker_mapping com dados oficiais da CVM (setor, denominação social)

## Script Master

Execute **todas** as sincronizações em ordem:

```powershell
.\scripts\run_master_sync.ps1
```

**Ordem de execução:**
1. ✅ Verificar Python e venv
2. ✅ Instalar dependências
3. ✅ Validar credenciais Supabase
4. 🔄 Sincronizar fundamentalistas CVM
5. 🔄 Sincronizar preços Brapi
6. 🔄 Sincronizar dividendos Brapi
7. 🔄 Enriquecer ticker_mapping

## Migrações Supabase

### Aplicadas ✅

- **003_add_precos_and_ticker_mapping.sql** - Tabelas preços e mapeamento
- **004_fix_dividends_constraint.sql** - Corrigir constraint único dividends
- **005_sync_assets.sql** - Sincronizar assets ← ticker_mapping

### Pendentes ⏳

- **006_add_companies_cvm.sql** - Tabela cadastro CVM (APLICAR ANTES DO JOB 3)

**Aplicar migração 006:**
```sql
-- Copie todo o conteúdo de sql/006_add_companies_cvm.sql
-- Cole no Supabase Dashboard → SQL Editor → Run
```

## Estrutura de Dados

### ticker_mapping (Mapeamento CNPJ → Ticker)
```sql
ticker         TEXT    PRIMARY KEY  -- Ex: PETR4
cnpj           TEXT                 -- 33.000.167/0001-01
nome           TEXT                 -- Petrobras
tipo_acao      TEXT                 -- PN, ON, UNIT
ativo          BOOLEAN DEFAULT true
cvm_code       TEXT                 -- Enriquecido via CVM
setor_atividade TEXT                -- Enriquecido via CVM
```

### precos (Cotações diárias)
```sql
ticker          TEXT    -- PETR4
data            DATE    -- 2026-01-02
fechamento      NUMERIC -- 30.82
abertura        NUMERIC -- 30.50
maxima          NUMERIC -- 31.00
minima          NUMERIC -- 30.40
volume          BIGINT  -- 12345678
market_cap      NUMERIC -- 400000000000
variacao_percentual NUMERIC -- 0.29
fonte           TEXT    -- brapi, yahoo
```

**Índice único:** (ticker, data, fonte) para UPSERT

### dividends (Dividendos históricos)
```sql
ticker            TEXT    -- ITUB4
ex_date           DATE    -- 2026-04-30 (data COM)
pay_date          DATE    -- 2026-04-30 (data pagamento)
amount_per_share  NUMERIC -- 0.36975
type              TEXT    -- dividend, jcp, special
```

**Índice único:** (ticker, ex_date, type, amount_per_share)

### companies_cvm (Cadastro oficial CVM)
```sql
cnpj                    TEXT UNIQUE -- 33.000.167/0001-01
cvm_code                TEXT        -- 23264
denominacao_social      TEXT        -- Petróleo Brasileiro S.A.
denominacao_comercial   TEXT        -- Petrobras
setor_atividade         TEXT        -- Petróleo e Gás
uf                      TEXT        -- RJ
situacao_cvm            TEXT        -- ATIVO
```

## Teste de Conectividade

Teste todas as APIs:

```bash
python -m integrations.master_integrator
```

**Resultado esperado:**
```
TESTE DE CONECTIVIDADE - TODAS AS APIS
======================================================================

[1/4] Testando Brapi...
  [OK] Brapi conectada

[2/4] Testando CVM API...
  [OK] CVM API acessivel

[3/4] Testando B3...
  [OK] B3 API acessivel

[4/4] Testando Yahoo Finance...
  [OK] Yahoo Finance acessivel

4/4 APIs online
```

## Próximos Passos

### Imediato (hoje)
1. ✅ Aplicar migração 005 no Supabase (sync assets)
2. ✅ Re-executar sync_dividendos_brapi (espera 100%)
3. ✅ Aplicar migração 006 no Supabase (companies_cvm)
4. ✅ Executar sync_fundamentals_cvm (popular tabela CVM)

### Curto prazo (esta semana)
5. ⏳ Implementar jobs B3 (empresas listadas, setores)
6. ⏳ Implementar job Yahoo (backup de preços)
7. ⏳ Criar job de cálculo de Dividend Yield
8. ⏳ Popular ticker_mapping com mais empresas BESST

### Médio prazo (próximas semanas)
9. ⏳ Implementar agendamento automático (daily sync)
10. ⏳ Criar job de ranking Barsi (DY + consistência)
11. ⏳ Implementar análise fundamentalista (P/L, ROE, etc.)
12. ⏳ UI para visualização de dados

## Troubleshooting

### "HTTP 404" da CVM
- **Causa:** Ano não disponível ou URL incorreta
- **Solução:** Verificar anos disponíveis em https://dados.cvm.gov.br/

### "Foreign Key Error" em dividends
- **Causa:** Ticker não existe em `assets`
- **Solução:** Aplicar migração 005 (sync assets)

### "UnicodeEncodeError" no Windows
- **Causa:** Emojis UTF-8 em terminal CP1252
- **Solução:** Já corrigido (emojis → ASCII)

### "Brapi quota exceeded"
- **Causa:** Limite de 4 ações no plano gratuito
- **Solução:** Usar Yahoo Finance como fallback ou upgrade Brapi

## Monitoramento

Todos os jobs registram execução em `job_runs`:

```sql
SELECT 
    job_name,
    status,
    rows_processed,
    started_at,
    finished_at,
    error_message
FROM job_runs
ORDER BY started_at DESC
LIMIT 10;
```

## Suporte

- **Docs Brapi:** https://brapi.dev/docs
- **Docs CVM:** https://dados.cvm.gov.br/
- **Docs B3:** https://www.b3.com.br/data/
- **Supabase:** https://supabase.com/docs

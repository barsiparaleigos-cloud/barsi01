# Changelog

Todas as mudanças relevantes do projeto.

O foco é o backend de jobs + integrações (Brapi / Fintz / HG Brasil / CVM), o padrão de ingestão `raw -> materialização`, e os utilitários/scripts de suporte.

## 
## 2026-01-02

### Fundamentals (padrão raw -> daily)
- Adicionada ingestão de payload bruto em `fundamentals_raw` (Supabase) para manter flexibilidade de fontes.
- Adicionada materialização diária em `fundamentals_daily` a partir de `fundamentals_raw`.
- Novo job de materialização: [barsi01/jobs/compute_fundamentals_daily.py](barsi01/jobs/compute_fundamentals_daily.py).

### Integrações: Brapi / HG Brasil / Fintz
- Brapi: job para sincronizar fundamentos e salvar payload bruto.
- HG Brasil: cápsula + job para sincronizar `stock_price` e salvar payload bruto com `source="hgbrasil"`.
  - Compute: fallback de moeda para `BRL` quando ausente.
- Fintz: cápsula atualizada para autenticação por header `X-API-Key` e endpoints oficiais de Bolsa B3.
  - Novo job: [barsi01/jobs/sync_fundamentals_fintz.py](barsi01/jobs/sync_fundamentals_fintz.py) (indicadores + itens contábeis por ticker).
  - Compute: suporte a `source="fintz"` extraindo `ValorDeMercado`, `P_L` e `LPA` do snapshot.

### CVM (oficial)
- Job de sincronização do cadastro (companies_cvm) com dedupe defensivo por CNPJ e logging em `job_runs`.
- Novo job: [barsi01/jobs/sync_fundamentals_cvm_dfp.py](barsi01/jobs/sync_fundamentals_cvm_dfp.py)
  - Baixa DFP (ZIP anual), filtra por CNPJ (via `ticker_mapping`) e salva snapshot por ticker em `fundamentals_raw` com `source="cvm"`.

### Schema / SQL (Supabase)
- Adicionadas migrações SQL para suportar os novos fluxos:
  - [barsi01/sql/007_add_fundamentals_raw.sql](barsi01/sql/007_add_fundamentals_raw.sql)
  - [barsi01/sql/008_add_fundamentals_daily.sql](barsi01/sql/008_add_fundamentals_daily.sql)

### Orquestração, scripts e admin
- Master integrator atualizado para incluir novas cápsulas e health-checks.
- Scripts adicionados para inspeção/validação de payloads de fundamentos.
- UI/Admin: ajustes e evoluções nos painéis e integração de fontes.

### Configuração
- Variáveis de ambiente documentadas/atualizadas em [barsi01/.env.example](barsi01/.env.example) (inclui `FINTZ_API_KEY`).

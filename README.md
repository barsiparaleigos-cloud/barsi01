# Dividendos para leigos

MVP de jobs diários para alimentar tabelas no Supabase (preços, dividendos, sinais).

## Estrutura
- `sql/001_init.sql`: cria as tabelas no Supabase
- `jobs/sync_prices.py`: insere preços do dia
- `jobs/sync_dividends.py`: insere dividendos (mock inicial)
- `jobs/compute_signals.py`: calcula preço-teto e sinal
- `.github/workflows/daily.yml`: executa os jobs diariamente via GitHub Actions

## Setup (local)
1. Crie `.env.local` na raiz (não é commitado)
   - Use como base o `.env.example`
2. Crie e ative o venv
   - Windows (PowerShell):
     - `python -m venv venv`
     - `venv\Scripts\Activate.ps1`
3. Instale dependências
   - `pip install --upgrade pip`
   - `pip install -r requirements.txt`
4. Crie as tabelas no Supabase
   - Abra o SQL Editor do Supabase e execute `sql/001_init.sql`
5. Rode os jobs
   - `python -m jobs.sync_prices`
   - `python -m jobs.sync_dividends`
   - `python -m jobs.compute_signals`

## Setup (GitHub Actions)
Em Settings → Secrets and variables → Actions, crie:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`

O workflow executa diariamente e também permite rodar manualmente.

## Nota sobre dependências
Os scripts usam a API REST do Supabase (PostgREST) via `requests` para manter a instalação leve.

## Home (UI mínima)
Para visualizar o ranking em uma tela simples (mock-first), rode:

 `python -m web.home_server`

Depois abra:

- `http://127.0.0.1:8000/`

Quando os jobs popularem `signals_daily`, a Home passa a mostrar dados do Supabase automaticamente.

## Webapp (React/Vite)
O design do Figma foi incorporado como um frontend React em `webapp/`. Ele consome a API do backend Python via proxy (`/api` → `http://127.0.0.1:8000`).

1. Suba o backend (API)
   - `python -m web.home_server`

2. Suba o frontend (em outro terminal)
   - `cd webapp`
   - `npm install`
   - `npm run dev`

O frontend vai buscar os dados em `GET /api/stocks`.

### Atalho (Windows)
Para subir backend + webapp em 1 comando (abre dois terminais):

- `powershell -ExecutionPolicy Bypass -File .\scripts\dev.ps1`

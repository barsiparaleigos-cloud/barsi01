-- 002_align_schema.sql
-- Alinha o schema do Supabase para o MVP rodar com UPSERT (PostgREST on_conflict)
-- Seguro para rodar várias vezes.

-- prices_daily: UPSERT por (ticker, date)
create unique index if not exists prices_daily_ticker_date_uidx
  on public.prices_daily (ticker, date);

-- signals_daily: UPSERT por (ticker, date)
create unique index if not exists signals_daily_ticker_date_uidx
  on public.signals_daily (ticker, date);

-- dividends: UPSERT por (ticker, ex_date, type, amount_per_share)
-- (para o mock não duplicar dados a cada execução)
create unique index if not exists dividends_unique_mock_uidx
  on public.dividends (ticker, ex_date, type, amount_per_share);

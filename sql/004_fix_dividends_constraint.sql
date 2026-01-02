-- 004_fix_dividends_constraint.sql
-- Corrige constraint único da tabela dividends
-- Remover constraint antigo e usar apenas o correto

-- Remover constraint antigo (se existir)
alter table if exists public.dividends 
  drop constraint if exists dividends_ticker_ex_date_type_key;

-- Garantir que o constraint correto existe
-- (ticker, ex_date, type, amount_per_share) conforme 001_init.sql
create unique index if not exists dividends_unique_mock_uidx
  on public.dividends (ticker, ex_date, type, amount_per_share);

-- Limpar dividendos duplicados antes (opcional)
-- Se quiser fazer cleanup, descomente:
-- delete from public.dividends
-- where id not in (
--   select min(id)
--   from public.dividends
--   group by ticker, ex_date, type, amount_per_share
-- );

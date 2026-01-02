-- 005_sync_assets_from_ticker_mapping.sql
-- Sincroniza tabela assets com dados de ticker_mapping
-- Remove FK constraint se necessário para flexibilidade

-- Inserir tickers de ticker_mapping em assets
INSERT INTO public.assets (ticker, name, sector, is_active)
SELECT 
  tm.ticker,
  tm.nome as name,
  'Financeiro' as sector,  -- Default, atualizar depois
  tm.ativo as is_active
FROM public.ticker_mapping tm
WHERE tm.ticker NOT IN (SELECT ticker FROM public.assets)
ON CONFLICT (ticker) DO UPDATE SET
  name = EXCLUDED.name,
  is_active = EXCLUDED.is_active;

-- Opcional: Remover FK constraint se causar problemas
-- ALTER TABLE public.dividends DROP CONSTRAINT IF EXISTS dividends_ticker_fkey;

-- Comentário
COMMENT ON TABLE public.assets IS 'Lista de ativos negociados (sincronizado com ticker_mapping)';

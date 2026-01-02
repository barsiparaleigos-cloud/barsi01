-- Migração 008: Tabela fundamentals_daily (normalizada)
-- Objetivo: materializar campos básicos (preço, market cap, EPS, P/L) por ticker/dia
-- Fonte primária inicial: fundamentals_raw (brapi)
-- Data: 2026-01-02

CREATE TABLE IF NOT EXISTS public.fundamentals_daily (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  ticker TEXT NOT NULL,
  date DATE NOT NULL,
  source TEXT NOT NULL,

  currency TEXT,
  price_current NUMERIC,
  market_cap NUMERIC,
  eps NUMERIC,
  pe NUMERIC,

  fundamentals_raw_id BIGINT,

  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS fundamentals_daily_ticker_date_source_uidx
  ON public.fundamentals_daily (ticker, date, source);

ALTER TABLE public.fundamentals_daily ENABLE ROW LEVEL SECURITY;

-- Policies (idempotentes)
DROP POLICY IF EXISTS "Leitura publica de fundamentals_daily" ON public.fundamentals_daily;
DROP POLICY IF EXISTS "fundamentals_daily_insert_service_role" ON public.fundamentals_daily;
DROP POLICY IF EXISTS "fundamentals_daily_update_service_role" ON public.fundamentals_daily;
DROP POLICY IF EXISTS "fundamentals_daily_delete_service_role" ON public.fundamentals_daily;

CREATE POLICY "Leitura publica de fundamentals_daily"
ON public.fundamentals_daily FOR SELECT
USING (true);

CREATE POLICY "fundamentals_daily_insert_service_role"
ON public.fundamentals_daily FOR INSERT
WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "fundamentals_daily_update_service_role"
ON public.fundamentals_daily FOR UPDATE
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "fundamentals_daily_delete_service_role"
ON public.fundamentals_daily FOR DELETE
USING (auth.role() = 'service_role');

COMMENT ON TABLE public.fundamentals_daily IS
'Tabela normalizada de fundamentos (por ticker/dia). Preenchida por jobs de compute a partir de fundamentals_raw.';

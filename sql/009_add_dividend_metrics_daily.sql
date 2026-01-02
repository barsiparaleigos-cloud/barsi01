-- Migração 009: Tabela dividend_metrics_daily
-- Objetivo: materializar DY 12m e consistência (5 anos) por ticker/dia
-- Data: 2026-01-02

CREATE TABLE IF NOT EXISTS public.dividend_metrics_daily (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  ticker TEXT NOT NULL,
  date DATE NOT NULL,

  price_current NUMERIC,
  price_source TEXT,

  dividends_sum_12m NUMERIC,
  dividend_yield_12m NUMERIC,

  years_with_dividends_5y INTEGER,
  consistency_score_5y NUMERIC,

  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS dividend_metrics_daily_ticker_date_uidx
  ON public.dividend_metrics_daily (ticker, date);

ALTER TABLE public.dividend_metrics_daily ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Leitura publica de dividend_metrics_daily" ON public.dividend_metrics_daily;
DROP POLICY IF EXISTS "dividend_metrics_daily_insert_service_role" ON public.dividend_metrics_daily;
DROP POLICY IF EXISTS "dividend_metrics_daily_update_service_role" ON public.dividend_metrics_daily;
DROP POLICY IF EXISTS "dividend_metrics_daily_delete_service_role" ON public.dividend_metrics_daily;

CREATE POLICY "Leitura publica de dividend_metrics_daily"
ON public.dividend_metrics_daily FOR SELECT
USING (true);

CREATE POLICY "dividend_metrics_daily_insert_service_role"
ON public.dividend_metrics_daily FOR INSERT
WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "dividend_metrics_daily_update_service_role"
ON public.dividend_metrics_daily FOR UPDATE
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "dividend_metrics_daily_delete_service_role"
ON public.dividend_metrics_daily FOR DELETE
USING (auth.role() = 'service_role');

COMMENT ON TABLE public.dividend_metrics_daily IS
'Tabela diária com métricas de dividendos (DY 12m e consistência 5 anos) por ticker.';

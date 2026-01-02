-- Migração 011: Tabela cvm_dfp_metrics_daily (normalizada)
-- Objetivo: materializar métricas extraídas do DFP (CVM) por ticker/data fiscal
-- Fonte: fundamentals_raw (source=cvm)
-- Data: 2026-01-02

CREATE TABLE IF NOT EXISTS public.cvm_dfp_metrics_daily (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  ticker TEXT NOT NULL,
  as_of_date DATE NOT NULL,
  source TEXT NOT NULL DEFAULT 'cvm',

  fiscal_year INT,
  cnpj TEXT,

  patrimonio_liquido NUMERIC,
  proventos_total_keywords NUMERIC,

  dre_rows_count INT,
  bpp_rows_count INT,

  fundamentals_raw_id BIGINT,

  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS cvm_dfp_metrics_daily_ticker_date_source_uidx
  ON public.cvm_dfp_metrics_daily (ticker, as_of_date, source);

ALTER TABLE public.cvm_dfp_metrics_daily ENABLE ROW LEVEL SECURITY;

-- Policies (idempotentes)
DROP POLICY IF EXISTS "Leitura publica de cvm_dfp_metrics_daily" ON public.cvm_dfp_metrics_daily;
DROP POLICY IF EXISTS "cvm_dfp_metrics_daily_insert_service_role" ON public.cvm_dfp_metrics_daily;
DROP POLICY IF EXISTS "cvm_dfp_metrics_daily_update_service_role" ON public.cvm_dfp_metrics_daily;
DROP POLICY IF EXISTS "cvm_dfp_metrics_daily_delete_service_role" ON public.cvm_dfp_metrics_daily;

CREATE POLICY "Leitura publica de cvm_dfp_metrics_daily"
ON public.cvm_dfp_metrics_daily FOR SELECT
USING (true);

CREATE POLICY "cvm_dfp_metrics_daily_insert_service_role"
ON public.cvm_dfp_metrics_daily FOR INSERT
WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "cvm_dfp_metrics_daily_update_service_role"
ON public.cvm_dfp_metrics_daily FOR UPDATE
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "cvm_dfp_metrics_daily_delete_service_role"
ON public.cvm_dfp_metrics_daily FOR DELETE
USING (auth.role() = 'service_role');

COMMENT ON TABLE public.cvm_dfp_metrics_daily IS
'Métricas normalizadas do DFP (CVM) por ticker/data fiscal. Preenchida por jobs de compute a partir de fundamentals_raw(source=cvm).';

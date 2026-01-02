-- Migração 007: Tabela fundamentals_raw (payload bruto de fundamentos)
-- Objetivo: armazenar fundamentos por ticker/data, com schema flexível (JSONB)
-- Fonte: Brapi (e futuras fontes como Fintz)
-- Data: 2026-01-02

CREATE TABLE IF NOT EXISTS public.fundamentals_raw (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  ticker TEXT NOT NULL,
  as_of_date DATE NOT NULL DEFAULT CURRENT_DATE,
  source TEXT NOT NULL,
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS fundamentals_raw_ticker_date_source_uidx
  ON public.fundamentals_raw (ticker, as_of_date, source);

ALTER TABLE public.fundamentals_raw ENABLE ROW LEVEL SECURITY;

-- Recriar policies de forma idempotente
DROP POLICY IF EXISTS "Leitura publica de fundamentals_raw" ON public.fundamentals_raw;
DROP POLICY IF EXISTS "fundamentals_raw_insert_service_role" ON public.fundamentals_raw;
DROP POLICY IF EXISTS "fundamentals_raw_update_service_role" ON public.fundamentals_raw;
DROP POLICY IF EXISTS "fundamentals_raw_delete_service_role" ON public.fundamentals_raw;

-- Leitura pública (os dados aqui são derivados de fontes públicas/market-data)
CREATE POLICY "Leitura publica de fundamentals_raw"
ON public.fundamentals_raw FOR SELECT
USING (true);

-- Escrita: apenas service_role (via jobs)
CREATE POLICY "fundamentals_raw_insert_service_role"
ON public.fundamentals_raw FOR INSERT
WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "fundamentals_raw_update_service_role"
ON public.fundamentals_raw FOR UPDATE
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "fundamentals_raw_delete_service_role"
ON public.fundamentals_raw FOR DELETE
USING (auth.role() = 'service_role');

COMMENT ON TABLE public.fundamentals_raw IS
'Payload bruto (JSONB) de fundamentos por ticker/data. Preenchido por jobs de sincronização (ex.: sync_fundamentals_brapi).';

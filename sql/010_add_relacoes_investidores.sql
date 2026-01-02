-- Migração 010: Tabela relacoes_investidores (RI) via CVM (FCA/FRE)
-- Objetivo: persistir contatos e canais oficiais de RI por CNPJ/data
-- Data: 2026-01-02

CREATE TABLE IF NOT EXISTS public.relacoes_investidores (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

  cnpj TEXT NOT NULL,
  as_of_date DATE NOT NULL,
  source TEXT NOT NULL,

  -- Campos extraídos (mínimo viável)
  canal_divulgacao TEXT,

  dri_nome TEXT,
  dri_email TEXT,
  dri_telefone TEXT,

  dept_acionistas_contato TEXT,
  dept_acionistas_email TEXT,
  dept_acionistas_telefone TEXT,

  endereco_logradouro TEXT,
  endereco_complemento TEXT,
  endereco_bairro TEXT,
  endereco_cidade TEXT,
  endereco_uf TEXT,
  endereco_pais TEXT,
  endereco_cep TEXT,

  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS relacoes_investidores_cnpj_date_source_uidx
  ON public.relacoes_investidores (cnpj, as_of_date, source);

CREATE INDEX IF NOT EXISTS idx_relacoes_investidores_cnpj
  ON public.relacoes_investidores (cnpj);

ALTER TABLE public.relacoes_investidores ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Leitura publica de relacoes_investidores" ON public.relacoes_investidores;
DROP POLICY IF EXISTS "relacoes_investidores_insert_service_role" ON public.relacoes_investidores;
DROP POLICY IF EXISTS "relacoes_investidores_update_service_role" ON public.relacoes_investidores;
DROP POLICY IF EXISTS "relacoes_investidores_delete_service_role" ON public.relacoes_investidores;

CREATE POLICY "Leitura publica de relacoes_investidores"
ON public.relacoes_investidores FOR SELECT
USING (true);

CREATE POLICY "relacoes_investidores_insert_service_role"
ON public.relacoes_investidores FOR INSERT
WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "relacoes_investidores_update_service_role"
ON public.relacoes_investidores FOR UPDATE
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "relacoes_investidores_delete_service_role"
ON public.relacoes_investidores FOR DELETE
USING (auth.role() = 'service_role');

COMMENT ON TABLE public.relacoes_investidores IS
'Contatos e canais oficiais de Relações com Investidores (RI) extraídos de documentos CVM (FCA/FRE).';

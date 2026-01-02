-- Migração 012: Extensão de cvm_dfp_metrics_daily (dívida/caixa)
-- Objetivo: habilitar análise Patrimônio x Dívida (método Barsi)
-- Data: 2026-01-02

ALTER TABLE public.cvm_dfp_metrics_daily
  ADD COLUMN IF NOT EXISTS divida_bruta NUMERIC,
  ADD COLUMN IF NOT EXISTS caixa_equivalentes NUMERIC,
  ADD COLUMN IF NOT EXISTS divida_liquida NUMERIC;

COMMENT ON COLUMN public.cvm_dfp_metrics_daily.divida_bruta IS
'Dívida bruta (heurística) extraída do BPP consolidado do DFP CVM.';

COMMENT ON COLUMN public.cvm_dfp_metrics_daily.caixa_equivalentes IS
'Caixa e equivalentes (heurística) extraída do BPA consolidado do DFP CVM.';

COMMENT ON COLUMN public.cvm_dfp_metrics_daily.divida_liquida IS
'Dívida líquida = dívida bruta - caixa e equivalentes (quando ambos disponíveis).';

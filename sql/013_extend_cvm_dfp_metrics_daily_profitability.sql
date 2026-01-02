-- Migração 013: Extensão de cvm_dfp_metrics_daily (lucro/ROE/payout)
-- Objetivo: completar critérios centrais do método (qualidade + sustentabilidade)
-- Data: 2026-01-02

ALTER TABLE public.cvm_dfp_metrics_daily
  ADD COLUMN IF NOT EXISTS lucro_liquido NUMERIC,
  ADD COLUMN IF NOT EXISTS roe_percent NUMERIC,
  ADD COLUMN IF NOT EXISTS payout_percent_keywords NUMERIC,
  ADD COLUMN IF NOT EXISTS divida_liquida_pl NUMERIC;

COMMENT ON COLUMN public.cvm_dfp_metrics_daily.lucro_liquido IS
'Lucro líquido (heurística) extraído da DRE consolidada do DFP CVM.';

COMMENT ON COLUMN public.cvm_dfp_metrics_daily.roe_percent IS
'ROE% = (lucro_liquido / patrimonio_liquido) * 100 quando ambos disponíveis.';

COMMENT ON COLUMN public.cvm_dfp_metrics_daily.payout_percent_keywords IS
'Payout% (proxy) = (proventos_total_keywords / lucro_liquido) * 100 quando ambos disponíveis.';

COMMENT ON COLUMN public.cvm_dfp_metrics_daily.divida_liquida_pl IS
'Alavancagem (proxy) = divida_liquida / patrimonio_liquido quando ambos disponíveis.';

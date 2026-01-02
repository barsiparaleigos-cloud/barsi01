-- 003_add_precos_and_ticker_mapping.sql
-- Adiciona tabelas para sincronização de preços via Brapi e mapeamento de tickers
-- Seguro para rodar várias vezes.

-- =============================================================================
-- TABELA: precos
-- Armazena histórico de cotações das ações brasileiras (fonte: Brapi)
-- =============================================================================
create table if not exists public.precos (
  id bigserial primary key,
  ticker text not null,
  data date not null,
  abertura numeric,
  maxima numeric,
  minima numeric,
  fechamento numeric not null,
  volume bigint,
  market_cap bigint,
  variacao_percentual numeric,
  moeda text default 'BRL',
  fonte text default 'brapi',
  created_at timestamptz default now()
);

-- Índice único para evitar duplicatas (UPSERT por ticker, data, fonte)
create unique index if not exists precos_ticker_data_fonte_uidx
  on public.precos (ticker, data, fonte);

-- Índices de performance
create index if not exists idx_precos_ticker on public.precos(ticker);
create index if not exists idx_precos_data on public.precos(data desc);
create index if not exists idx_precos_ticker_data on public.precos(ticker, data desc);

-- Comentários (documentação)
comment on table public.precos is 'Histórico de cotações diárias das ações (sincronizado via Brapi)';
comment on column public.precos.ticker is 'Código da ação na B3 (ex: PETR4, VALE3)';
comment on column public.precos.fechamento is 'Preço de fechamento (campo obrigatório)';
comment on column public.precos.fonte is 'Fonte dos dados (brapi, yahoo, manual)';


-- =============================================================================
-- TABELA: ticker_mapping
-- Mapeia CNPJ (CVM) → Ticker (B3) para empresas
-- =============================================================================
create table if not exists public.ticker_mapping (
  id bigserial primary key,
  empresa_id bigint,  -- FK para tabela empresas (se existir)
  cnpj text,
  ticker text not null,
  nome text,
  tipo_acao text,  -- PN, ON, UNIT
  ativo boolean default true,
  verificado boolean default false,  -- se o mapeamento foi verificado manualmente
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Índice único para ticker (não pode ter duplicatas)
create unique index if not exists ticker_mapping_ticker_uidx
  on public.ticker_mapping (ticker);

-- Índices de busca
create index if not exists idx_ticker_mapping_cnpj on public.ticker_mapping(cnpj);
create index if not exists idx_ticker_mapping_ticker on public.ticker_mapping(ticker);
create index if not exists idx_ticker_mapping_empresa_id on public.ticker_mapping(empresa_id);
create index if not exists idx_ticker_mapping_ativo on public.ticker_mapping(ativo) where ativo = true;

-- Comentários
comment on table public.ticker_mapping is 'Mapeamento CNPJ → Ticker para integrar dados CVM + B3';
comment on column public.ticker_mapping.cnpj is 'CNPJ da empresa (14 dígitos, pode ter pontuação)';
comment on column public.ticker_mapping.ticker is 'Código da ação na B3 (ex: PETR4)';
comment on column public.ticker_mapping.verificado is 'TRUE se o mapeamento foi verificado manualmente';


-- =============================================================================
-- TRIGGER: Atualizar updated_at automaticamente
-- =============================================================================
create or replace function public.update_updated_at_column()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

-- Aplicar trigger na tabela ticker_mapping
drop trigger if exists ticker_mapping_updated_at on public.ticker_mapping;
create trigger ticker_mapping_updated_at
  before update on public.ticker_mapping
  for each row
  execute function public.update_updated_at_column();


-- =============================================================================
-- DADOS INICIAIS: Tickers de teste (4 ações gratuitas Brapi)
-- =============================================================================
insert into public.ticker_mapping (ticker, nome, ativo, verificado)
values
  ('PETR4', 'Petrobras PN', true, true),
  ('VALE3', 'Vale ON', true, true),
  ('ITUB4', 'Itaú Unibanco PN', true, true),
  ('MGLU3', 'Magazine Luiza ON', true, true)
on conflict (ticker) do update set
  nome = excluded.nome,
  ativo = excluded.ativo,
  verificado = excluded.verificado,
  updated_at = now();


-- =============================================================================
-- RLS (Row Level Security) - Opcional
-- =============================================================================
-- Se você quiser proteger as tabelas com RLS, descomente abaixo:

-- alter table public.precos enable row level security;
-- alter table public.ticker_mapping enable row level security;

-- Política: qualquer um pode LER (para app público)
-- create policy "Permitir leitura pública de precos"
--   on public.precos for select
--   using (true);

-- create policy "Permitir leitura pública de ticker_mapping"
--   on public.ticker_mapping for select
--   using (true);

-- Política: apenas service_role pode ESCREVER (jobs)
-- create policy "Apenas service_role pode escrever em precos"
--   on public.precos for all
--   using (auth.role() = 'service_role');

-- create policy "Apenas service_role pode escrever em ticker_mapping"
--   on public.ticker_mapping for all
--   using (auth.role() = 'service_role');

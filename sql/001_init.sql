-- 001_init.sql
-- Cria tabelas base para o MVP

create table if not exists public.assets (
  ticker text primary key,
  name text,
  sector text,
  is_active boolean default true,
  created_at timestamptz default now()
);

create table if not exists public.job_runs (
  id bigserial primary key,
  job_name text not null,
  status text not null, -- success | error
  rows_processed integer,
  message text,
  started_at timestamptz not null default now(),
  finished_at timestamptz not null default now()
);

create index if not exists idx_job_runs_name_time on public.job_runs(job_name, finished_at desc);

create table if not exists public.prices_daily (
  id bigserial primary key,
  ticker text not null,
  date date not null,
  close numeric not null,
  volume bigint,
  created_at timestamptz default now()
);

create unique index if not exists prices_daily_ticker_date_uidx
  on public.prices_daily (ticker, date);

create table if not exists public.dividends (
  id bigserial primary key,
  ticker text not null,
  ex_date date not null,
  pay_date date,
  amount_per_share numeric not null,
  type text check (type = any (array['dividend'::text, 'jcp'::text, 'special'::text])),
  created_at timestamptz default now()
);

create unique index if not exists dividends_unique_mock_uidx
  on public.dividends (ticker, ex_date, type, amount_per_share);

create table if not exists public.signals_daily (
  id bigserial primary key,
  ticker text not null,
  date date not null,
  price_current numeric,
  dpa_avg_5y numeric,
  dy_target numeric default 0.06,
  price_teto numeric,
  below_teto boolean,
  margin_to_teto numeric,
  created_at timestamptz default now()
);

create unique index if not exists signals_daily_ticker_date_uidx
  on public.signals_daily (ticker, date);

insert into public.assets (ticker, name, sector)
values
  ('ITUB4', 'Itaú Unibanco', 'Bancos'),
  ('BBAS3', 'Banco do Brasil', 'Bancos'),
  ('BBDC4', 'Bradesco', 'Bancos'),
  ('TAEE11', 'Taesa', 'Energia'),
  ('WEGE3', 'WEG', 'Industrial'),
  ('EGIE3', 'Engie Brasil', 'Energia'),
  ('ABEV3', 'Ambev', 'Consumo')
on conflict (ticker) do nothing;

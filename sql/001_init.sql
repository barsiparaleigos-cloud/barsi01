-- 001_init.sql
-- Cria tabelas base para o MVP

create table if not exists public.prices_daily (
  date date not null,
  ticker text not null,
  price numeric not null,
  created_at timestamptz not null default now(),
  primary key (date, ticker)
);

create table if not exists public.dividends (
  ex_date date not null,
  pay_date date,
  ticker text not null,
  amount numeric not null,
  created_at timestamptz not null default now(),
  primary key (ex_date, ticker, amount)
);

create table if not exists public.signals_daily (
  date date not null,
  ticker text not null,
  price_current numeric not null,
  price_teto numeric,
  below_teto boolean,
  margin_to_teto numeric,
  created_at timestamptz not null default now(),
  primary key (date, ticker)
);

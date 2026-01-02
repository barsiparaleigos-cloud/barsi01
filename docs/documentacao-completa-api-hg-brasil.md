# Documentação Completa API HG Brasil (resumo técnico)

> Fonte do conteúdo: texto fornecido pelo usuário a partir de https://hgbrasil.com/docs/guide.
> 
> Objetivo: registrar, de forma prática, **como autenticar**, **como formatar respostas**, e **quais endpoints principais** (Mercado Financeiro) são úteis para o projeto.

## Autenticação (Chave de Integração)

- A chave é informada no parâmetro `key` na URL.
- Todas as respostas incluem um campo de validação (ex.: `valid_key` ou `metadata.key_status`, dependendo do endpoint/versão).

Exemplo:

- `GET https://api.hgbrasil.com/weather?key=SUACHAVE`

Validação:
- Se `valid_key` vier `false`, revisar:
  - chave digitada corretamente;
  - domínio configurado (no caso de **chaves expostas**);
  - chave desativada/removida.

### Tipos de chave (conceito)
- **Chave para uso exposto (client-side)**: deve ter domínio configurado.
- **Chave para uso interno (server/mobile)**: não precisa de domínio (inclui testes em `localhost` e `127.0.0.1`).

## CORS

Para requisições feitas diretamente do navegador (JS), usar `format=json-cors`.

Exemplo:
- `GET https://api.hgbrasil.com/finance?format=json-cors&key=SUACHAVE`

Observação (dev local): `localhost` e `127.0.0.1` já são permitidos.

## Respostas formatadas e filtros

### `format`
- `json` (padrão)
- `json-cors` (habilita CORS)
- `php-serialize`
- `debug` (para testes; evitar em produção)

### `fields` e `array_limit`
- `fields`: permite reduzir payload, ex.: `only_results` e campos específicos.
- `array_limit`: limita tamanho de arrays (compatível apenas com JSON).

Exemplos:
- Finance:
  - `GET https://api.hgbrasil.com/finance?fields=only_results,currencies,stocks,bitcoin,taxes&array_limit=2&key=SUACHAVE`
- Weather:
  - `GET https://api.hgbrasil.com/weather?fields=only_results,temp,humidity,wind_speedy,forecast&woeid=455827&array_limit=3&key=SUACHAVE`
- Geo:
  - `GET https://api.hgbrasil.com/geoip?fields=only_results,city,region,country_name,continent&address=remote&key=SUACHAVE`

## Boas práticas (resumo)

- Evitar excesso de requisições (economiza limite e reduz latência).
- Implementar cache (cliente/servidor) com TTL.
- Validar dados e usar seleção de campos (`fields`) para reduzir tráfego.

---

# Mercado Financeiro

## Finance (visão geral)

Endpoint base:
- `GET https://api.hgbrasil.com/finance?key=SUACHAVE`

Notas:
- Atualização típica das cotações: ~15 a 45 minutos durante pregão.
- Estrutura geral citada no texto:
  - `results.currencies`
  - `results.stocks`
  - `results.bitcoin`
  - `results.taxes`

### Moedas

Para retornar apenas moedas:
- `GET https://api.hgbrasil.com/finance?fields=currencies&key=SUACHAVE`

Principais campos (exemplo):
- `results.currencies.source`
- `results.currencies.USD.buy/sell/variation` (e demais ISO)

### Bolsa de Valores (ações/FIIs)

Ação específica via `symbol`:
- `GET https://api.hgbrasil.com/finance/stock_price?symbol=PETR4&key=SUACHAVE`

No texto, o payload do ativo inclui (exemplos):
- Identificação: `symbol`, `name`, `company_name`, `document` (CNPJ)
- Setor/descrição: `sector`, `description`, `website`
- Logos: `logo.small`, `logo.big`
- Financeiros: `financials.equity`, `financials.price_to_book_ratio`, `financials.dividends.yield_12m`
- Mercado: `price`, `change_percent`, `volume`, `updated_at`

Maiores altas/baixas:
- `GET https://api.hgbrasil.com/finance/stock_price?symbol=get-high&key=SUACHAVE`
- `GET https://api.hgbrasil.com/finance/stock_price?symbol=get-low&key=SUACHAVE`

Ibovespa (diário/último pregão):
- `GET https://api.hgbrasil.com/finance/ibovespa?key=SUACHAVE`

### Dividendos e Proventos (v2)

Endpoint:
- `GET https://api.hgbrasil.com/v2/finance/dividends?tickers=B3:PETR4&key=SUACHAVE`

Parâmetros citados:
- `tickers` (obrigatório): `{fonte}:{símbolo}`; múltiplos separados por vírgula.
- filtros de data: `start_date`, `end_date`, `date`, `days_ago`.

Resposta (resumo do que aparece no texto):
- `metadata.key_status`, `metadata.cached`, `metadata.response_time_ms`
- `results[]` com:
  - `ticker`, `symbol`, `name`, `full_name`
  - `summary.yield_12m_percent`, `summary.yield_12m_cash`
  - `series[]` eventos (ex.: `dividend`, `interest_on_equity`) com:
    - `amount`, `approval_date`, `com_date`, `payment_date`, `status`

Tipos de proventos citados:
- `dividend`, `interest_on_equity`, `income`, `bonus_issue`, `amortization`, etc.

### Indicadores Econômicos (v2)

Endpoint:
- `GET https://api.hgbrasil.com/v2/finance/indicators?tickers=IBGE:IPCA&key=SUACHAVE`

Parâmetros citados:
- `tickers` (obrigatório): `{fonte}:{símbolo}`; múltiplos separados por vírgula.
- filtros de data: `start_date`, `end_date`, `date`, `days_ago`.

Resposta (resumo):
- `metadata.*`
- `results[]` com:
  - `ticker`, `unit`, `periodicity`
  - `name`, `full_name`, `description`, `category`
  - `summary.ytd`, `summary.last_12m`
  - `series[]` com pares período/valor
  - `source.*`

Fontes citadas:
- `BCB` (Banco Central), `IBGE`, `FGV`.

### Taxas de Juros

Endpoint:
- `GET https://api.hgbrasil.com/finance/taxes?key=SUACHAVE`

Campos citados (exemplo):
- `results[].date`, `results[].cdi`, `results[].selic`, `results[].daily_factor`, `selic_daily`, `cdi_daily`

### Histórico (v2)

Endpoint:
- `GET https://api.hgbrasil.com/v2/finance/historical?...&key=SUACHAVE`

Parâmetros citados:
- `symbols` (obrigatório): tickers separados por vírgula
  - ativos (ações/FIIs/BDRs/ETFs), moedas (ex.: `USDBRL`), índices (ex.: `BVSP`)
- `sample_by`: `1m`, `5m`, `15m`, `30m`, `1h`, `2h`, `1d`, `1M`
- filtros (apenas 1 por requisição):
  - intervalo: `start_date` + `end_date`
  - data específica: `date`
  - dias atrás: `days_ago`

Exemplos:
- `GET https://api.hgbrasil.com/v2/finance/historical?symbols=embr3,hglg11,usdbrl,bvsp&days_ago=3&sample_by=1d&key=SUACHAVE`

---

# Como isso ajuda o projeto

- Complementa o CVM DFP com:
  - proventos (para payout real, por evento);
  - indicadores macro (SELIC/CDI/IPCA) para análise de juros/inflação;
  - histórico de preços/câmbio/índices para contexto de mercado.
- Para front-end no navegador, já padroniza o uso de `format=json-cors`.
- Para reduzir custo e evitar rate-limit, incentiva `fields`/`array_limit` + cache.

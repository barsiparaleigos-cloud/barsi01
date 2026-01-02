# Toda documentação Fintz API (resumo técnico)

> Fonte do conteúdo: texto fornecido pelo usuário (documentação Fintz).
> 
> Objetivo: registrar de forma prática **como autenticar**, **quais endpoints existem**, **parâmetros**, **formatos de resposta** e **como isso ajuda o projeto**.

## Visão geral

A Fintz fornece dados padronizados do mercado financeiro (bolsa, fundos, tesouro, índices/taxas/câmbio) e também um conjunto muito relevante para **backtests point-in-time** (evita look-ahead e survivorship bias).

### Base URL e autenticação

- `URL_BASE = https://api.fintz.com.br`
- Header obrigatório em todas as chamadas:
  - `X-API-Key: {sua-chave}`
- Existe uma chave pública de teste **bem limitada** para testes iniciais:
  - `chave-de-testes-api-fintz`

Contato citado:
- email: `contato@fintz.com.br`
- whatsapp: `(41) 99187-5540`

---

# Endpoints

## Bolsa (B3)

Notas gerais:
- Dados disponíveis desde `2010-01-01`.
- Existe coleção Postman (download e import no Postman).

### Busca e lista de ativos

- `GET /bolsa/b3/avista/busca`

Uso típico:
- autocomplete/barra de busca por ticker;
- filtrar classe (ações, FIIs, BDRs, etc.) e/ou apenas ativos negociados.

Parâmetros:
- `q` (string, opcional): exemplo `BBAS` retorna `BBAS3`
- `classe` (string, opcional): `BDRS`, `ACOES`, `FUNDOS`, `FIIS`, `TODOS`
- `ativo` (boolean, opcional): `true|false`

Resposta (exemplo conceitual):
- lista de itens com `ticker`, `nome`, `ativo`.

### Cotação histórica OHLC (JSON)

- `GET /bolsa/b3/avista/cotacoes/historico`

Parâmetros:
- `ticker` (string, obrigatório)
- `dataInicio` (string `yyyy-mm-dd`, obrigatório)
- `dataFim` (string `yyyy-mm-dd`, opcional)

Campos esperados (ex.: por dia):
- preços OHLC (abertura/máxima/mínima/fechamento)
- `precoFechamentoAjustado` (ajustado por eventos)
- volume/quantidades (`quantidadeNegociada`, `volumeNegociado`, etc.)

### Cotação histórica OHLC (arquivo parquet)

- `GET /bolsa/b3/avista/cotacoes/historico/arquivos`

Retorna:
- link para download de parquet com OHLC de **todos os tickers**.

Parâmetro:
- `preencher` (boolean, opcional): preenche dias sem negociação com cotação anterior.

### Eventos corporativos (JSON)

#### Proventos (dividendos/JCP etc.)
- `GET /bolsa/b3/avista/proventos`

Parâmetros:
- `ticker` (obrigatório)
- `dataInicio` (obrigatório)
- `dataFim` (opcional)

Resposta típica inclui:
- datas (`dataCom`, `dataPagamento`, `dataAprovacao`)
- `valor`
- `tipo` (ex.: dividendos / juros sobre capital próprio)

Observação fornecida:
- inicialmente cobre proventos de ações; FIIs seriam incluídos depois (pela nota do texto).

#### Bonificações
- `GET /bolsa/b3/avista/bonificacoes`

Parâmetros:
- `ticker` (obrigatório)
- `dataInicio` (obrigatório)
- `dataFim` (opcional)

Campos típicos:
- `proporcao`, `dataCom`, `dataAnuncio`, `dataIncorporacao`, `valorBase`

#### Desdobramentos / grupamentos
- `GET /bolsa/b3/avista/desdobramentos`

Parâmetros:
- `ticker` (obrigatório)
- `dataInicio` (obrigatório)
- `dataFim` (opcional)

Campos típicos:
- `valorAntes`, `valorDepois`, `dataCom`, `dataAnuncio`, `tipo`

### Itens contábeis (padronizados)

A documentação lista itens contábeis com suporte por periodicidade:
- `TRIMESTRAL`, `ANUAL` (via DFP) e, para alguns itens, `12M`.

**Observação conceitual importante (do texto):**
- Itens de balanço (ex.: `AtivoTotal`) não fazem sentido em `12M`.
- Itens de DRE (ex.: `ReceitaLiquida`) podem ser acumulados em `12M`.

#### Histórico por item e ticker
- `GET /bolsa/b3/avista/itens-contabeis/historico`

Parâmetros:
- `item` (obrigatório)
- `ticker` (obrigatório)
- `tipoPeriodo` (obrigatório): `12M`, `TRIMESTRAL`, `ANUAL`
- `tipoDemonstracao` (opcional): `CONSOLIDADO` | `INDIVIDUAL` | vazio

Regra recomendada no texto:
- na dúvida, **não informar** `tipoDemonstracao` (usa consolidado quando existir).

#### Valor mais recente de um item (todos os tickers)
- `GET /bolsa/b3/avista/itens-contabeis`

Parâmetros:
- `item` (obrigatório)
- `tipoPeriodo` (opcional; padrão citado: `12M`)
- `tipoDemonstracao` (opcional)

#### Itens contábeis mais recentes por ticker
- `GET /bolsa/b3/avista/itens-contabeis/por-ticker`

Parâmetros:
- `ticker` (obrigatório)
- `tipoPeriodo` (opcional)
- `tipoDemonstracao` (opcional)

Regra do texto:
- se `tipoPeriodo` não for informado, a resposta prioriza `12M`, depois `TRIMESTRAL` por item.

### Indicadores

Há lista de indicadores para ações e FIIs (no texto, os FIIs foram adicionados em updates e usam os mesmos endpoints).

#### Histórico de indicador por ticker
- `GET /bolsa/b3/avista/indicadores/historico`

Parâmetros:
- `indicador` (obrigatório)
- `ticker` (obrigatório)

Nota importante:
- a data do indicador é a **data de referência do documento de origem**.

#### Valor mais recente de um indicador (todos os tickers)
- `GET /bolsa/b3/avista/indicadores`

Parâmetros:
- `indicador` (obrigatório)
- `classe` (opcional): `ACOES` (padrão) ou `FIIS`

#### Indicadores mais recentes por ticker
- `GET /bolsa/b3/avista/indicadores/por-ticker`

Parâmetros:
- `ticker` (obrigatório)

Observação:
- alguns indicadores não se aplicam a empresas financeiras (podem não aparecer na resposta).

### Logos e ícones

- Este é o único caso citado que usa **outra URL** (não é `api.fintz.com.br`).

Base:
- `https://raw.githubusercontent.com/thefintz/icones-b3/main/icones/`

Exemplo:
- `.../TSLA34.png`

---

## Fundos (beta)

No texto: endpoints disponíveis em beta sob requisição:
- `/busca`
- `/historico/diario`
- `/historico/mensal`
- `/historico/anual`

Uso descrito:
- `/busca`: lista/cadastro + filtros;
- `/historico/*`: série diária/mensal/anual (cota, PL, cotistas, etc.).

---

## Tesouro Direto

Notas:
- dados disponíveis desde `2003-01-01`
- atualização diária

### Lista de títulos
- `GET /titulos-publicos/tesouro`

Parâmetros (paginação):
- `pagina` (opcional; padrão 1)
- `tamanho` (opcional; padrão 10)

Resposta típica:
- paginação (`pagina`, `tamanho`, `total`) + `dados[]` com `codigo`, `nome`, `dataVencimento`, flags de vencido/investir/resgatar.

### Informações de um título
- `GET /titulos-publicos/tesouro/{codigo}/informacoes`

Resposta típica:
- `indice` (ex.: IPCA), `descricao`, `estrategia`, `jurosSemestrais`, etc.

### Histórico de preços e taxas
- `GET /titulos-publicos/tesouro/{codigo}/precos/historico`

Parâmetros:
- `pagina`, `tamanho` (opcionais)
- `dataInicio`, `dataFim` (opcionais; `yyyy-mm-dd`)

Campos típicos:
- taxas compra/venda, PU compra/venda, `puBase`.

### Preços e taxas atuais
- `GET /titulos-publicos/tesouro/{codigo}/precos/atual`

Campos típicos:
- taxas compra/venda, PU compra/venda, mínimos, `dataUltAtualizacao`.

### Cupons
- `GET /titulos-publicos/tesouro/{codigo}/cupons`

Parâmetros:
- `pagina`, `tamanho` (opcionais)

Campos típicos:
- `dataResgate`, `valor`, `qtdTotal`, `valorTotal`, etc.

---

## Índices, taxas e câmbio

Notas:
- índices com dados desde `2000-01-01`

### Índices

#### Histórico
- `GET /indices/historico`

Parâmetros:
- `indice` (obrigatório; ex.: `IBOV`)
- `dataInicio` (obrigatório)
- `dataFim` (opcional)
- `ordem` (opcional): `ASC|DESC`

#### Composição
- `GET /indices/composicao`

Parâmetros:
- `indice` (obrigatório)
- `ordem` (opcional): `ASC|DESC` (ordenar por participação)

### Taxas

#### Busca (lista de taxas)
- `GET /taxas/busca`

Parâmetros:
- `q` (opcional; ex.: `cdi`)

Retorna itens com:
- `nome`, `codigo`, `unidade`, `descricao`.

#### Histórico
- `GET /taxas/historico`

Parâmetros:
- `codigo` (obrigatório; ex.: CDI = `12`)
- `dataInicio` (obrigatório)
- `dataFim` (opcional)
- `ordem` (opcional)

### Câmbio (PTAX)

#### Busca
- `GET /cambio/ptax/busca`

Parâmetros:
- `q` (opcional; ex.: “dólar”)

#### Histórico
- `GET /cambio/ptax/historico`

Parâmetros:
- `codigo` (obrigatório; ex.: `USD`)
- `dataInicio` (obrigatório)
- `dataFim` (opcional)
- `boletim` (opcional): `FECHAMENTO|ABERTURA`
- `ordem` (opcional)

Campos típicos:
- `cotacaoCompra`, `cotacaoVenda`, `paridadeCompra`, `paridadeVenda`, `tipoBoletim`, `tipoMoeda`.

---

## Point in Time (backtest)

Conceitos (do texto):
- evita **look-ahead bias** (usar dados só quando ficaram públicos)
- inclui empresas delistadas (mitiga **survivorship bias**)
- melhora confiabilidade (preço ajustado e dados versionados no tempo)

Atualização:
- arquivos atualizados diariamente (~22h Brasília), incluindo preços e releases (ITRs/DFPs).

Endpoints citados:
- Arquivo (itens contábeis, todos tickers, 1 item):
  - `GET /bolsa/b3/avista/itens-contabeis/point-in-time/arquivos`
  - parâmetros: `item` (obrigatório), `tipoPeriodo` (`12M` ou `TRIMESTRAL`)
- JSON (itens contábeis, 1 ticker + 1 item):
  - `GET /bolsa/b3/avista/itens-contabeis/point-in-time`
  - parâmetros: `item`, `ticker`, `tipoPeriodo`, `tipoDemonstracao` (opcional)

Indicadores point-in-time (citados como “em breve” no texto):
- `GET /bolsa/b3/avista/indicadores/point-in-time/arquivos`
- `GET /bolsa/b3/avista/indicadores/point-in-time`

Endpoints antigos (planejados para descontinuação no texto):
- `GET /bolsa/b3/tm/indicadores/arquivos`
- `GET /bolsa/b3/tm/demonstracoes/arquivos`
- `GET /bolsa/b3/tm/demonstracoes`
- `GET /bolsa/b3/tm/indicadores`

---

# Postman

A documentação menciona coleção Postman disponibilizada via link para facilitar testes.

---

# Updates (notas)

O texto lista releases importantes, incluindo:
- indicadores de FIIs
- proventos de FIIs no mesmo endpoint
- expansão do catálogo de indicadores/itens contábeis
- separação de endpoints point-in-time vs comuns
- adição de taxas e câmbio
- índices B3

---

# Como isso ajuda o projeto

- **Proventos (ações/FIIs)**: base para payout real (por evento).
- **Itens contábeis e indicadores padronizados**: reduz heurísticas e melhora qualidade dos cálculos (ROE, dívida, margens, etc.).
- **Point-in-time**: viabiliza backtests sem viés de look-ahead, útil para ranking/estratégias do “método Barsi” com consistência histórica.
- **Índices/taxas/câmbio/tesouro**: contexto macro e comparativos (CDI/SELIC, PTAX, etc.).

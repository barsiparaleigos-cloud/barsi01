# Metodologia (Fórmula Completa) - Dividendos para leigos

Este documento é a **fonte de verdade** (source of truth) para:
- quais empresas entram no universo,
- quais critérios definem “elegível pela metodologia”,
- como calculamos preço-teto / margem,
- como o ranking e o card vão afirmar: **“ação dentro de todos os nossos critérios em conjunto”**.

> Nota: o sistema deve comunicar sempre como “**critérios da metodologia**” (não como recomendação personalizada).

---

## 1) Conceitos e definições

### 1.1 Universo de empresas
Uma empresa entra no universo analisável se:
- está no cadastro CVM (companhia aberta) e
- tem status operacional compatível (ex.: `ATIVO`) e
- conseguimos ligar **empresa (CNPJ)** ↔ **ticker** (para cruzar com preço e dividendos).

### 1.2 BESST (setores perenes)
Filtro de foco setorial:
- **B**: Bancos / instituições financeiras
- **E**: Energia (ênfase em transmissão/receitas previsíveis)
- **S**: Saneamento e/ou Seguros
- **T**: Telecom

No projeto isso já existe como classificação de “no radar” (BESST) para reduzir ruído.

### 1.3 Proventos e termos
- **Dividendos/JCP**: proventos distribuídos por ação.
- **DPA**: dividendos por ação (o que interessa para renda por ação).
- **DY**: dividend yield.

---

## 2) A regra central: disciplina de preço (Preço-Teto)

### 2.1 Parâmetro principal: DY alvo
No projeto, o DY alvo padrão é **6% a.a.**:

- Em código: `DESIRED_YIELD = 0.06` em [jobs/compute_signals.py](../jobs/compute_signals.py)

### 2.2 Fórmula do Preço-Teto
Definição:

$$
P_{teto} = \frac{DPA_{médio}}{DY_{alvo}}
$$

- $P_{teto}$: preço máximo aceitável para manter o DY alvo.
- $DPA_{médio}$: média anual de proventos por ação (idealmente média de múltiplos anos).
- $DY_{alvo}$: alvo de rendimento (padrão 0,06).

### 2.3 Margem até o teto
Usada para ordenar ranking:

$$
Margem\_\% = \frac{P_{teto}-P_{atual}}{P_{teto}} \times 100
$$

No projeto (tabela `signals_daily`) isso aparece como `margin_to_teto`.

### 2.4 Implementação atual (MVP)
Hoje o `compute_signals` está em modo MVP:
- `price_current` vem de `prices_daily.close`.
- `DPA_médio` ainda é um **proxy**: soma de proventos dos últimos 12 meses.
  - Em código: `dpa_avg_5y = div_sum if div_sum > 0 else None`.

Alvo (próximas iterações):
- trocar o proxy por uma métrica real, por exemplo:
  - média anual de proventos por ação dos últimos 5 anos.

---

## 3) Critérios (o que significa “dentro da metodologia”)

A “aprovação” deve ser composta por critérios em conjunto. Separar em:
- **Hard filters** (se falhar, não entra como indicação completa)
- **Soft checks** (mostram risco/qualidade do dado; podem virar hard depois)

### 3.1 Hard filters (mínimo para afirmar “passou tudo”)
1) **BESST**
- Empresa está em setor BESST (no radar).

2) **Ativa**
- Empresa/ativo em situação operacional ativa.

3) **Mapeamento CNPJ ↔ ticker**
- Conseguimos associar a empresa a um ticker negociado.

4) **Tem base para cálculo de renda**
- Temos proventos suficientes para estimar DPA (no MVP: proventos 12m > 0).

5) **Preço abaixo do preço-teto**
- $P_{atual} < P_{teto}$ (ou `below_teto = true`).

> Resultado: se TODOS os itens acima forem verdadeiros, então:
> **Ação dentro de todos os critérios em conjunto**.

### 3.2 Soft checks (qualidade/robustez)
Estes não precisam bloquear o ranking agora, mas devem ser visíveis:
- **Consistência de dividendos (5 anos)**
  - Roadmap define score 0–100 e sugere corte mínimo 80.
- **Dados frescos**
  - preço do dia (ou do último pregão), dividendos atualizados.
- **Normalização de eventos**
  - desdobramentos/grupamentos podem distorcer DPA se não ajustados.

---

## 4) Ranking: como ordenar as ações

### 4.1 Regra de ordenação (atual)
Ordenar por `margin_to_teto` (maior primeiro):
- quanto maior a margem, “mais abaixo do teto” está o preço atual.

### 4.2 Regras de inclusão no ranking
- só entram ações com `price_teto` calculável (não nulo e > 0)
- e `margin_to_teto` não nulo.

---

## 5) Estrelas no card do ranking (UX: ticks + tooltip)

Objetivo:
- o card deve mostrar de forma imediata **quantos critérios foram cumpridos**;
- se houver falha(s), ao passar o mouse, exibir tooltip com **quais critérios falharam e por quê**.

### 5.1 Quantidade e significado das estrelas
Recomendação (5 estrelas, uma por critério hard):

1) **BESST**
- Check: empresa pertence a setor BESST.
- Falha tooltip: "Não está em setor BESST (fora do radar)".

2) **Ativa**
- Check: empresa/ativo está ativo.
- Falha tooltip: "Empresa/ativo não está ativo".

3) **Dados de dividendos (base DPA)**
- Check: existe base para estimar DPA (MVP: soma 12m > 0).
- Falha tooltip: "Sem dividendos/JCP suficientes para estimar DPA".

4) **Preço-teto calculável**
- Check: `price_teto` não nulo e > 0.
- Falha tooltip: "Não foi possível calcular preço-teto (dados insuficientes)".

5) **Abaixo do teto**
- Check: `below_teto = true`.
- Falha tooltip: "Preço atual acima do preço-teto".

### 5.2 Regra de “aprovado”
- `aprovado_metodologia = (estrela1 && estrela2 && estrela3 && estrela4 && estrela5)`

Quando `aprovado_metodologia = true`, o card pode afirmar:
- “Dentro dos critérios da metodologia (completo)”.

Quando for `false`:
- mostrar as estrelas com as faltas,
- tooltip listando os critérios não atendidos.

### 5.3 Tooltips (padrão)
- Tooltip deve listar **somente as falhas** (para ser rápido de ler).
- Texto sempre no formato: `Não cumpriu: <critério> — <motivo>`.

Exemplo:
- Não cumpriu: Base de dividendos — sem proventos 12m suficientes
- Não cumpriu: Abaixo do teto — preço atual acima do teto

---

## 6) Campos/dados (o que cada critério usa)

### 6.1 Dados já existentes (Supabase jobs)
- `prices_daily` (usado pelo cálculo): `ticker`, `date`, `close`
- `dividends` (usado pelo cálculo): `ticker`, `ex_date`, `amount_per_share`, `type`
- `signals_daily` (resultado): `ticker`, `date`, `price_current`, `dpa_avg_5y` (proxy), `dy_target`, `price_teto`, `below_teto`, `margin_to_teto`

### 6.2 Dados do BESST (SQLite hoje)
- Classificação BESST está implementada no banco SQLite (`empresas.setor_besst`, `monitorar`).

Alvo:
- consolidar uma fonte única para o card do ranking (ou sincronizar BESST para Supabase).

---

## 7) Checklist para afirmar “passou tudo”

Uma ação só é “indicação completa” se:
- BESST ok
- Ativa ok
- Dividendos ok (base DPA)
- Preço-teto calculável
- Preço atual abaixo do teto

E o card deve refletir isso com 5/5 estrelas.

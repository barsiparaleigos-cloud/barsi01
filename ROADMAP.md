# 🎯 ROADMAP - Dividendos para leigos

**Projeto:** Sistema de Recomendação de Ações - Metodologia de dividendos  
**Iniciado:** Janeiro 2026  
**Status:** 🟢 Em Desenvolvimento Ativo

---

## ✅ Definição do MVP (Jan/2026) — decisão tomada

**Objetivo do MVP:** ensinar (leigos/crianças) e dar uma lista pequena e confiável de “PODE COMPRAR / ESPERE” com explicação simples.

**Escopo do MVP (o que entra):**
- Universo: **30–50 tickers BESST** (curados/verificados)
- Preço: **diário**
- Dividendos/proventos: histórico suficiente para **DPA médio 5 anos**
- Sinal principal: **Preço-teto + Regra dos 6%**
- Transparência: sempre guardar **fonte + data de coleta** (raw)

**Fora do MVP (depois):** backtest point-in-time, ajuste completo por eventos corporativos, IA em PDFs/RI.

**Critérios de aceite do MVP:**
- Para cada ticker do universo: `preco_atual`, `dpa_5y` (ou equivalente), `preco_teto`, `status` (comprar/esperar/sem dados) e **motivo**
- Execução diária sem depender de APIs pagas por “ticker a ticker”
- Dados rastreáveis (source-of-truth em DB) e reprocessamento possível

---

## 📊 Progresso Geral

**Fase 1 (Fundação):** ████████░░ 80% ✅  
**Fase 2 (Core Features):** ██░░░░░░░░ 20% 🔄  
**Fase 3 (Avançado):** ░░░░░░░░░░ 0% ⏳

---

## 📌 Fonte de verdade (metodologia)

- 📄 **Metodologia + Fórmula + Critérios + Estrelas do ranking:** [docs/METODOLOGIA-FORMULA-COMPLETA.md](docs/METODOLOGIA-FORMULA-COMPLETA.md)

---

## 🧭 ROADMAP (Supabase / Método Barsi “na íntegra”)

> Esta seção espelha o estado real do pipeline em Supabase (ingestão + materializações).

### A) Dados base (persistência + automação)
- [x] Persistência real no Supabase (contagens + amostras)
- [x] `job_runs` (observabilidade)
- [x] Ingestão diária Brapi (preços/dividendos/fundamentos) com fallback sem `BRAPI_API_KEY`
- [x] Ingestão CVM: cadastro + DFP (raw)

### B) Conectores e normalização (CNPJ ↔ ticker)
- [x] `ticker_mapping` populado via Brapi `quote/list`
- [x] Sugestão automática de CNPJ por matching de nomes (CVM cadastro)
- [ ] Curadoria (MVP): definir universo BESST (30–50) e marcar `verificado=true` (lista “golden”)

### C) Métricas essenciais do método (camada de dados)
- [x] Dividendos 12m + consistência (materializado em `dividend_metrics_daily`)
- [x] DFP CVM normalizado básico (materializado em `cvm_dfp_metrics_daily`)
- [x] Solvência: patrimônio vs dívida/caixa (migração 012 + compute)
- [ ] Qualidade: lucro líquido (DFP) + ROE (Lucro/PL) (validar extração e preencher 2024)
- [ ] Sustentabilidade: payout (Proventos/Lucro) (definir fonte de proventos do MVP)
- [ ] Caixa/FCF: ingestão e métricas via DFC (fluxo de caixa) para cobertura de dividendos
- [ ] Ajustes corporativos: normalização de proventos por ação (desdobramentos/grupamentos)

### C1) Pacote mínimo para o MVP (destrava UI + ranking)
- [ ] `dpa_5y` (ou dpa_medio) por ticker
- [ ] `preco_teto` por ticker/dia
- [ ] `status_mvp` por ticker/dia: COMPRAR | ESPERAR | SEM_DADOS (com `motivo_mvp`)
- [ ] “Gates” de qualidade: ticker só entra em ranking se tiver dados mínimos

### F) Caminho próprio (dados brutos) para reduzir custo de APIs pagas 🔴 ALTA
> Objetivo: não depender de Fintz/HG Brasil para operar o MVP e evoluir para um método “investível”.

**Estratégia do MVP (curta):**
- Preço: começar com **Brapi** para destravar (já integrado), mas **migrar para batch B3** como caminho definitivo.
- Proventos: manter um **conector opcional** (HG Brasil v2, limitado ao universo MVP) com cache + persistência raw.

**F1) Preços históricos via B3 (batch, sem API por ticker)**
- [ ] Ingestão B3 COTAHIST (download + parser) para popular OHLC/volume
- [ ] Materialização `prices_daily` a partir do arquivo consolidado (1 arquivo/dia)
- [ ] Ajustes corporativos de preço (split/inplit/bonificação) para preço ajustado (se disponível)

**F2) Macro oficial (BCB/IBGE) para contexto e filtros**
- [ ] Ingestão BCB (Selic/CDI/SGS) + PTAX (câmbio) + IPCA (IBGE)
- [ ] Tabela `macro_series_daily` (ex.: selic, cdi, ipca, usdbrl)

**F3) Proventos/eventos corporativos (principal gargalo vs fontes pagas)**
- [ ] Definir “fonte de proventos” MVP (pode ser limitada): brapi/hgbrasil ou base oficial alternativa
- [ ] Persistir proventos com campos mínimos: `ticker`, `ex_date`, `pay_date`, `amount_per_share`, `type`, `source`
- [ ] Regras de normalização: deduplicação + padronização de tipos (dividend/jcp/etc.)

**F4) Qualidade e rastreabilidade do dado (para ficar próximo de 100%)**
- [ ] Data Quality Gates: flags por ticker/dia (ex.: `has_price`, `has_dividends`, `has_profit`, `has_equity`)
- [ ] Cross-check de fontes (quando houver 2 fontes): divergência de preço/dividendo acima de threshold gera alerta
- [ ] Log de origem por métrica (ex.: lucro veio de DRE linha X / provento veio da fonte Y)

**F5) Backtest “sem look-ahead” (point-in-time) – evolução pós-MVP**
- [ ] Armazenar data de referência vs data de publicação do documento CVM
- [ ] Queries “as-of” para ranking histórico (evitar usar dado que não existia na época)

### D) Regras por setor (evitar falso positivo)
- [ ] Separar “financeiras” (bancos/seguradoras) vs “não-financeiras” no score
- [ ] Thresholds por setor (ex.: dívida/PL não é comparável entre bancos e utilities)

### E) RI e documentos (camada de evidência)
- [x] RI (FCA): contatos/canal oficial em `relacoes_investidores`
- [ ] Índice de documentos (metadados + links): DFP/ITR/FRE/FR/Comunicados (CVM)
- [ ] Persistir documentos: download + hash + versionamento (mudanças)
- [ ] (Opcional) IA: sumarização e extração de riscos/temas a partir de PDFs/HTML

---

## ✅ FASE 1: FUNDAÇÃO DO SISTEMA (80% Concluído)

### 1.1 Infraestrutura Base ✅
- [x] Setup do projeto (Python + React + Vite)
- [x] Estrutura de diretórios
- [x] Scripts de desenvolvimento (dev.ps1)
- [x] Configuração de ambiente
- [x] README com instruções

### 1.2 Backend Base ✅
- [x] Servidor HTTP Python (web/home_server.py)
- [x] Roteamento de endpoints
- [x] CORS configurado
- [x] Servir arquivos estáticos

### 1.3 Frontend Base ✅
- [x] React 18 + TypeScript
- [x] Tailwind CSS 4
- [x] Componentes base (Card, Button, Input, etc.)
- [x] Sidebar responsivo e escalável
- [x] Roteamento interno (tabs/views)

### 1.4 Banco de Dados SQLite ✅
- [x] database/models.py implementado
- [x] 6 tabelas criadas:
  - [x] empresas
  - [x] acoes
  - [x] dividendos
  - [x] patrimonio
  - [x] relacoes_investidores
  - [x] sync_log
- [x] Índices para performance
- [x] Singleton pattern (get_db())

### 1.5 Integração CVM ✅
- [x] integrations/cvm_integration.py
- [x] Download de cadastro de empresas (diário)
- [x] Download de DFP (Demonstrações Financeiras)
- [x] Extração de dividendos (DRE)
- [x] Extração de patrimônio líquido (BPP)
- [x] Job de sincronização (jobs/sync_cvm.py)
- [x] Script de teste (scripts/test_cvm.py)
- [x] Primeira sincronização executada: **2.650 empresas cadastradas** ✅

### 1.6 API REST - Empresas ✅
- [x] GET /api/empresas (listagem com filtros)
- [x] GET /api/empresas/{cnpj} (detalhes)
- [x] GET /api/acoes (tickers)
- [x] GET /api/stats (estatísticas do banco)
- [x] web/companies.py implementado

### 1.7 UI - Listagem de Empresas ✅
- [x] CompanyList.tsx criado
- [x] Cards de estatísticas (total, ativas, dividendos, DB size)
- [x] Busca por razão social/CNPJ/nome fantasia
- [x] Filtros: Ativas / Todas / Canceladas
- [x] Item "Empresas" no sidebar
- [x] Exibição de última sincronização

### 1.8 Documentação ✅
- [x] docs/METODOLOGIA-FORMULA-COMPLETA.md
- [x] docs/integracao-cvm.md
- [x] docs/robo-cvm-guia.md
- [x] docs/plano-historico-e-ri.md
- [x] TODO.md

---

## 🔄 FASE 2: CORE FEATURES (35% Concluído)

### 2.1 Filtro de Empresas BESST ✅ CONCLUÍDO
**Objetivo:** Focar apenas em empresas da metodologia

- [x] **2.1.1** Criar classificador BESSTClassifier em database/besst_classifier.py
- [x] **2.1.2** Sistema de migrações atômicas (database/migrations.py)
- [x] **2.1.3** Adicionar colunas na tabela empresas:
  ```sql
  ALTER TABLE empresas ADD COLUMN setor_besst TEXT;
  ALTER TABLE empresas ADD COLUMN elegivel_barsi BOOLEAN DEFAULT FALSE;
  ALTER TABLE empresas ADD COLUMN dividend_yield_atual REAL;
  ALTER TABLE empresas ADD COLUMN consistencia_dividendos REAL;
  ALTER TABLE empresas ADD COLUMN monitorar BOOLEAN DEFAULT FALSE;
  ALTER TABLE empresas ADD COLUMN ultima_analise TIMESTAMP;
  ALTER TABLE empresas ADD COLUMN motivo_exclusao TEXT;
  
  CREATE INDEX idx_empresas_setor_besst ON empresas(setor_besst);
  CREATE INDEX idx_empresas_elegivel ON empresas(elegivel_barsi);
  CREATE INDEX idx_empresas_monitorar ON empresas(monitorar);
  ```
- [x] **2.1.4** Script para classificar todas as empresas (scripts/migrate_and_classify.py)
- [x] **2.1.5** Classificação automática de novas empresas (integrado em sync_cvm.py)
- [x] **2.1.6** Backend: GET /api/empresas?apenas_monitoradas=true
- [x] **2.1.7** Backend: GET /api/empresas/besst (endpoint dedicado)
- [x] **2.1.8** UI: Toggle "🎯 Apenas empresas BESST (no radar)"
- [x] **2.1.9** UI: Badges coloridos por setor (🏦 Bancos, ⚡ Energia, 💧 Saneamento, 📡 Telecom)
- [x] **2.1.10** UI: Card de estatísticas BESST destacado
- [x] **2.1.11** UI: Alerta informativo quando filtro ativo

**Resultados:**
- ✅ **677 empresas BESST** classificadas (26,9% do total)
- ✅ **261 empresas BESST ATIVAS** (10,4% do total)
- ✅ Distribuição: 228 Bancos | 163 Energia | 100 Saneamento/Seguros | 186 Telecom

**Tempo Real:** 1 dia  
**Impacto:** 🚀 ALTO - Sistema focado, 73% de ruído eliminado

📄 **Documentação:** [docs/FILTRO-BESST-IMPLEMENTADO.md](docs/FILTRO-BESST-IMPLEMENTADO.md)

---

### 2.2 Cálculo de Dividend Yield (DY) 🔴 ALTA
**Objetivo:** Calcular DY projetado para ranquear empresas

- [ ] **2.2.1** Implementar integração de preços (Brapi ou Yahoo Finance)
- [ ] **2.2.2** Criar job sync_precos.py (execução diária)
- [ ] **2.2.3** Criar função `calcular_dy_projetado()` em database/models.py
  ```python
  # Fórmula: DY = (Soma Dividendos Últimos 12M / Preço Atual) * 100
  ```
- [ ] **2.2.4** Atualizar coluna `dividend_yield_atual` na tabela empresas
- [ ] **2.2.5** Job automático para recalcular DY diariamente
- [ ] **2.2.6** UI: Exibir DY em destaque no card de empresa

**Tempo Estimado:** 2 dias  
**Impacto:** 🚀 ALTO - Métrica fundamental da metodologia

---

### 2.3 Consistência de Dividendos 🔴 ALTA
**Objetivo:** Score de confiabilidade de pagamento

- [ ] **2.3.1** Criar função `avaliar_consistencia_dividendos()` em database/models.py
  ```python
  # Score 0-100:
  # - 100: Pagou dividendos todos os anos (últimos 5 anos)
  # - 80: Pagou 4 de 5 anos
  # - <80: Inconsistente (não elegível)
  ```
- [ ] **2.3.2** Atualizar coluna `consistencia_dividendos` na tabela empresas
- [ ] **2.3.3** Job automático para recalcular consistência (mensal)
- [ ] **2.3.4** UI: Badge de consistência no card
  - 🟢 100%: "Excelente"
  - 🟡 80-99%: "Boa"
  - 🔴 <80%: "Inconsistente"

**Tempo Estimado:** 1 dia  
**Impacto:** 🚀 ALTO - Filtra empresas confiáveis

---

### 2.4 Mapeamento CNPJ → Ticker 🟡 MÉDIA
**Objetivo:** Cruzar dados CVM com cotações da B3

- [ ] **2.4.1** Pesquisar fonte de mapeamento:
  - Opção A: Tabela manual (top 100 empresas)
  - Opção B: API Brapi (buscar ticker por nome)
  - Opção C: Scraping B3
- [ ] **2.4.2** Adicionar coluna `ticker_principal` na tabela empresas
- [ ] **2.4.3** Popular tabela acoes automaticamente
- [ ] **2.4.4** Função `mapear_cnpj_para_ticker(cnpj)` em cvm_integration.py

**Tempo Estimado:** 3 dias  
**Impacto:** 🚀 ALTO - Necessário para preços e análises

**Desafio:** CVM usa CNPJ, B3 usa Ticker. Não há API oficial de mapeamento.

---

### 2.5 Sistema de Histórico (Versionamento) 🟡 MÉDIA
**Objetivo:** Tracking de mudanças ao longo do tempo

- [ ] **2.5.1** Criar tabelas de histórico:
  ```sql
  CREATE TABLE empresas_historico (
    id, empresa_id, razao_social, cnpj, situacao, setor,
    versao, valido_de, valido_ate, alterado_por, created_at
  );
  
  CREATE TABLE dividendos_historico (
    id, empresa_id, ano_fiscal, trimestre, tipo,
    valor_por_acao, valor_total, data_aprovacao, data_pagamento,
    fonte, created_at
  );
  
  CREATE TABLE precos_historico (
    id, acao_id, data, abertura, maxima, minima, fechamento,
    volume, fechamento_ajustado, fonte, created_at
  );
  ```
- [ ] **2.5.2** Modificar sync_cvm.py para salvar snapshots
- [ ] **2.5.3** Implementar lógica de diff (detectar mudanças)
- [ ] **2.5.4** Endpoint GET /api/empresas/{cnpj}/historico
- [ ] **2.5.5** UI: Timeline de histórico na tab "Histórico CVM"

**Tempo Estimado:** 5 dias  
**Impacto:** 🔥 MÉDIO - Base para análises temporais

---

### 2.6 UI - Card Detalhado com Tabs 🟡 MÉDIA
**Objetivo:** Interface completa para análise de empresa

- [ ] **2.6.1** Criar componente CompanyDetail.tsx
- [ ] **2.6.2** Implementar sistema de tabs:
  - [ ] Tab "Visão Geral" (dados cadastrais + métricas principais)
  - [ ] Tab "Histórico CVM" (timeline de mudanças)
  - [ ] Tab "Dividendos" (gráfico de barras + tabela)
  - [ ] Tab "Preços" (gráfico candlestick)
  - [ ] Tab "RI" (Relações com Investidores)
  - [ ] Tab "Análise" (score + critérios)
- [ ] **2.6.3** Navegação: clicar em empresa → abrir modal ou página
- [ ] **2.6.4** Integrar com Chart.js ou Recharts
- [ ] **2.6.5** Responsividade mobile

**Tempo Estimado:** 3 dias  
**Impacto:** 🚀 ALTO - UX profissional

---

### 2.7 Dados de RI via CVM (FRE/FCA) 🟡 MÉDIA
**Objetivo:** Capturar contatos oficiais de Relações com Investidores

- [ ] **2.7.1** Criar integrations/cvm_fre_integration.py
- [ ] **2.7.2** Implementar download de FRE (Formulário de Referência)
  - URL: https://dados.cvm.gov.br/dataset/cia_aberta-doc-fre
- [ ] **2.7.3** Implementar download de FCA (Formulário Cadastral)
  - URL: https://dados.cvm.gov.br/dataset/cia_aberta-doc-fca
- [ ] **2.7.4** Extrair seção "Comunicação com Investidores" do FRE:
  - Website de RI
  - Email de RI
  - Telefone de RI
  - Nome do diretor de RI
- [ ] **2.7.5** Salvar em tabela relacoes_investidores
- [ ] **2.7.6** Criar job sync_cvm_ri.py (execução mensal)
- [ ] **2.7.7** UI: Exibir dados de RI na tab "RI"

**Tempo Estimado:** 3 dias  
**Impacto:** 🔥 MÉDIO - Dados oficiais e confiáveis

---

## ⏳ FASE 3: FEATURES AVANÇADAS (0% Concluído)

### 3.1 Robô de Monitoramento de RI (Solução Híbrida) 🟢 BAIXA
**Estratégia Aprovada pelo Usuário:** ✅
> "CVM (mensal): Dados oficiais de contato  
> Scraping (diário): Detectar mudanças via hash do HTML  
> Se hash mudou → notificar + salvar no histórico"

**Implementação:**

#### Parte 1: CVM (Mensal) - Fonte Primária
- [ ] **3.1.1** Job sync_cvm_ri.py já planejado na Fase 2
- [ ] **3.1.2** Frequência: Mensal (toda primeira segunda-feira do mês)
- [ ] **3.1.3** Garante dados oficiais e atualizados

#### Parte 2: Scraping (Diário) - Detecção de Mudanças
- [ ] **3.1.4** Criar integrations/ri_scraper.py
- [ ] **3.1.5** Implementar função `detect_changes(url, last_hash)`
  ```python
  # 1. Fetch página de RI
  # 2. Calcular hash SHA256 do HTML
  # 3. Comparar com hash anterior
  # 4. Se diferente: notificar + salvar histórico
  ```
- [ ] **3.1.6** Criar tabela ri_mudancas:
  ```sql
  CREATE TABLE ri_mudancas (
    id, empresa_id, url, hash_anterior, hash_atual,
    tipo_mudanca, descricao, created_at
  );
  ```
- [ ] **3.1.7** Job monitor_ri.py (execução diária às 00:00)
- [ ] **3.1.8** Respeitar robots.txt e rate limiting (1 req/seg por domínio)
- [ ] **3.1.9** User-Agent identificado: `DividendosParaLeigos/1.0`
- [ ] **3.1.10** Fallback: Se site bloquear, usar apenas dados CVM

**Tipos de Mudanças a Detectar:**
- Novo comunicado ao mercado
- Novo fato relevante
- Atualização de calendário de dividendos
- Nova apresentação institucional
- Mudança de contato (email/telefone)

**Tempo Estimado:** 5 dias  
**Impacto:** 🔥 MÉDIO - Útil mas não essencial  
**Complexidade:** 🔴 ALTA (manutenção constante)

---

### 3.2 Sistema de Notificações 🟢 BAIXA
**Objetivo:** Alertar usuários sobre mudanças importantes

- [ ] **3.2.1** Criar tabela notificacoes:
  ```sql
  CREATE TABLE notificacoes (
    id, empresa_id, tipo, titulo, descricao,
    gravidade, lida, link, created_at
  );
  ```
- [ ] **3.2.2** Tipos de notificação:
  - CADASTRO (mudança de razão social, situação)
  - RI_DADOS (novo email/telefone de RI)
  - RI_COMUNICADO (novo comunicado no site)
  - DIVIDENDO_NOVO (aprovação de dividendos)
- [ ] **3.2.3** Endpoint GET /api/notificacoes
- [ ] **3.2.4** Endpoint POST /api/notificacoes/{id}/marcar-lida
- [ ] **3.2.5** UI: Bell icon no header com badge
- [ ] **3.2.6** UI: Dropdown de notificações
- [ ] **3.2.7** UI: Filtros (tipo, gravidade, lidas/não lidas)

**Tempo Estimado:** 2 dias  
**Impacto:** 🔥 MÉDIO - Engajamento do usuário

---

### 3.3 Gráficos de Preços (Candlestick) 🟢 BAIXA
**Objetivo:** Visualizar histórico de preços

- [ ] **3.3.1** Integração já planejada em 2.2 (sync_precos.py)
- [ ] **3.3.2** Salvar em precos_historico
- [ ] **3.3.3** Implementar gráfico candlestick na tab "Preços"
- [ ] **3.3.4** Biblioteca: Chart.js com plugin Financial ou Recharts
- [ ] **3.3.5** Opções de período: 1M, 3M, 6M, 1A, 5A, Tudo
- [ ] **3.3.6** Indicadores: Média móvel 50/200 dias

**Tempo Estimado:** 2 dias  
**Impacto:** 🔥 MÉDIO - Visualização útil

---

### 3.4 Ranking Dinâmico de Ações 🟢 BAIXA
**Objetivo:** Lista ordenada por melhor DY e consistência

- [ ] **3.4.1** Endpoint GET /api/ranking
  - Parâmetros: setor_besst, dy_minimo, consistencia_minima
- [ ] **3.4.2** Ordenação: DY DESC, Consistência DESC
- [ ] **3.4.3** UI: Página de Ranking (já existe estrutura no sidebar)
- [ ] **3.4.4** Cards com top 10 empresas por setor BESST
- [ ] **3.4.5** Filtros avançados: capitalização, liquidez

**Tempo Estimado:** 2 dias  
**Impacto:** 🚀 ALTO - Feature core do produto

---

### 3.5 Simulador de Renda Passiva 🟢 BAIXA
**Objetivo:** Calcular renda mensal com base em investimento

- [ ] **3.5.1** UI: Formulário de simulação
  - Input: Valor a investir
  - Input: Prazo (anos)
  - Seleção: Empresas da carteira
- [ ] **3.5.2** Lógica de cálculo:
  ```python
  # 1. Distribuir valor entre empresas selecionadas
  # 2. Calcular quantidade de ações de cada
  # 3. Projetar dividendos mensais (baseado em histórico)
  # 4. Considerar reinvestimento
  ```
- [ ] **3.5.3** Gráfico: Evolução de renda ao longo do tempo
- [ ] **3.5.4** Comparação: Com vs sem reinvestimento

**Tempo Estimado:** 3 dias  
**Impacto:** 🚀 ALTO - Feature diferenciada

---

## 📅 CRONOGRAMA SUGERIDO

### Mês 1 (Janeiro 2026)
- ✅ Semana 1-2: Fase 1 (Fundação) - **CONCLUÍDO**
- 🔄 Semana 3: Filtro BESST + Cálculo DY + Consistência (2.1, 2.2, 2.3)
- ⏳ Semana 4: Mapeamento CNPJ→Ticker + Histórico (2.4, 2.5)

### Mês 2 (Fevereiro 2026)
- ⏳ Semana 1: UI Card Detalhado (2.6)
- ⏳ Semana 2: Dados de RI via CVM (2.7)
- ⏳ Semana 3: Ranking Dinâmico (3.4)
- ⏳ Semana 4: Simulador de Renda (3.5)

### Mês 3 (Março 2026)
- ⏳ Semana 1-2: Robô de Monitoramento RI (3.1)
- ⏳ Semana 3: Sistema de Notificações (3.2)
- ⏳ Semana 4: Gráficos de Preços (3.3)

---

## 🎯 PRÓXIMAS AÇÕES IMEDIATAS

### 🔴 HOJE (Próximas 2 horas)
1. **Implementar Filtro BESST** (2.1.1, 2.1.2, 2.1.3)
   - Criar função classificar_setor_besst()
   - Adicionar colunas no banco
   - Rodar script de classificação

2. **UI: Toggle de Filtro** (2.1.5)
   - Adicionar switch no CompanyList.tsx
   - Filtrar empresas na listagem

### 🟡 ESTA SEMANA
1. **Integração de Preços** (2.2.1, 2.2.2)
   - Pesquisar melhor API (Brapi vs Yahoo)
   - Implementar sync_precos.py

2. **Cálculo de DY** (2.2.3, 2.2.4)
   - Implementar fórmula
   - Atualizar banco

3. **Consistência de Dividendos** (2.3.1, 2.3.2)
   - Implementar cálculo
   - Exibir na UI

---

## 📊 MÉTRICAS DE SUCESSO

### KPIs Técnicos
- [x] Banco de dados populado: **2.650 empresas** ✅
- [ ] Empresas classificadas BESST: 0 / ~300 empresas (meta)
- [ ] Empresas elegíveis: 0 / ~50 empresas (meta)
- [ ] Preços atualizados diariamente: 0 / 50 empresas
- [ ] Uptime do sistema: Meta 99%

### KPIs de Produto
- [ ] Tempo de carregamento de listagem: <500ms
- [ ] Tempo de sync CVM: <60s
- [ ] Cobertura de setores BESST: 100%
- [ ] Dados de RI capturados: 0 / 50 empresas (meta)

---

## 🚨 RISCOS E MITIGAÇÕES

### Risco 1: Mapeamento CNPJ → Ticker
**Problema:** Não há API oficial  
**Mitigação:** Criar tabela manual para top 100 empresas + busca por nome na Brapi

### Risco 2: Scraping de Sites de RI
**Problema:** Bloqueios, CAPTCHAs, estruturas heterogêneas  
**Mitigação:** 
- Respeitar robots.txt
- Rate limiting (1 req/seg)
- Fallback para CVM (fonte oficial)
- Implementar apenas depois que core features estiverem prontas

### Risco 3: Qualidade de Dados da CVM
**Problema:** Empresas podem demorar a atualizar formulários  
**Mitigação:** 
- Validação de dados antes de salvar
- Flag de "última atualização"
- Exibir data de referência dos dados

---

## 📝 NOTAS DE DESENVOLVIMENTO

### Convenções de Código
- Python: PEP 8
- TypeScript: ESLint + Prettier
- Commits: Conventional Commits (feat:, fix:, docs:, etc.)

### Testes
- [ ] Implementar testes unitários (pytest)
- [ ] Testes de integração (API endpoints)
- [ ] Testes E2E (Playwright)

### Deploy (Futuro)
- [ ] Dockerizar aplicação
- [ ] CI/CD com GitHub Actions
- [ ] Hosting: Render ou Railway (backend) + Vercel (frontend)

---

## 🔗 REFERÊNCIAS
- [Metodologia - Fórmula Completa](docs/METODOLOGIA-FORMULA-COMPLETA.md)
- [Integração CVM](docs/integracao-cvm.md)
- [Robô CVM - Guia](docs/robo-cvm-guia.md)
- [Plano Histórico & RI](docs/plano-historico-e-ri.md)
- [TODO Detalhado](TODO.md)

---

**Última Atualização:** 02/01/2026 - 00:30  
**Próxima Revisão:** Semanal (toda segunda-feira)  
**Responsável:** Time Dividendos para leigos

---

## ✅ COMO USAR ESTE ROADMAP

1. **Semanal:** Revisar progresso e ajustar prioridades
2. **Diário:** Marcar [x] nas tarefas concluídas
3. **Bloqueios:** Anotar na seção "Riscos e Mitigações"
4. **Ideias:** Adicionar na Fase 3 ou criar nova fase

**Lembre-se:** ✅ Feito é melhor que perfeito. Implementar features incrementalmente.

# 📋 TODO - Projeto Barsi Para Leigos

**Última Atualização:** 02/01/2026

---

## 🔴 PRIORIDADE ALTA (Implementar Agora)

### 1. Filtro de Empresas BESST ⏰ 1 hora
**Status:** 🔴 Não Iniciado  
**Objetivo:** Classificar e filtrar empresas por setores da metodologia Barsi

- [ ] Criar função `classificar_setor_besst()` em `database/models.py`
- [ ] Adicionar coluna `setor_besst` na tabela `empresas`
- [ ] Rodar script de classificação em massa
- [ ] Criar endpoint `/api/empresas/elegiveis`
- [ ] Adicionar toggle "Apenas empresas Barsi" no CompanyList.tsx
- [ ] Badge visual "✅ Elegível Barsi" nas empresas que atendem critérios

**Critérios:**
- Setor BESST (Bancos, Energia, Saneamento, Seguros, Telecomunicações)
- DY ≥ 6%
- Consistência de dividendos ≥ 80% (últimos 5 anos)

**Impacto:** 🚀 Alto - Foco imediato nas empresas certas  
**Complexidade:** 🟢 Baixa

---

### 2. Sistema de Histórico de Dados ⏰ 5 dias
**Status:** 🔴 Não Iniciado  
**Objetivo:** Versionamento temporal de todos os dados críticos

- [ ] Criar tabela `empresas_historico` (versionamento de cadastro)
- [ ] Criar tabela `dividendos_historico` (já existe parcialmente)
- [ ] Criar tabela `precos_historico` (integração futura)
- [ ] Modificar `sync_cvm.py` para salvar snapshots a cada sync
- [ ] Implementar lógica de diff (detectar o que mudou)
- [ ] Criar endpoint `/api/empresas/{cnpj}/historico`
- [ ] UI: Timeline de histórico na tab "Histórico CVM"

**Tabelas:**
```sql
empresas_historico:
  - id, empresa_id, razao_social, cnpj, situacao, setor
  - versao, valido_de, valido_ate, alterado_por
  - created_at

dividendos_historico:
  - id, empresa_id, ano_fiscal, trimestre, tipo
  - valor_por_acao, valor_total, data_aprovacao, data_pagamento
  - fonte, created_at

precos_historico:
  - id, acao_id, data, abertura, maxima, minima, fechamento
  - volume, fechamento_ajustado, fonte, created_at
```

**Impacto:** 🚀 Alto - Base para análises temporais  
**Complexidade:** 🟡 Média

---

### 3. Dados de RI via CVM (FRE/FCA) ⏰ 3 dias
**Status:** 🔴 Não Iniciado  
**Objetivo:** Capturar dados oficiais de Relações com Investidores

- [ ] Criar `integrations/cvm_fre_integration.py`
- [ ] Implementar download de FRE (Formulário de Referência)
- [ ] Implementar download de FCA (Formulário Cadastral)
- [ ] Extrair seção "Comunicação com Investidores" do FRE
- [ ] Extrair contatos corporativos do FCA
- [ ] Salvar em tabela `relacoes_investidores`
- [ ] Criar job `sync_cvm_ri.py` (execução mensal)

**Dados a Capturar:**
- Website de RI
- Email de RI
- Telefone de RI
- Nome do diretor de RI
- Endereço completo da sede

**Fonte:** https://dados.cvm.gov.br/dataset/cia_aberta-doc-fre  
**Impacto:** 🚀 Alto - Dados oficiais e confiáveis  
**Complexidade:** 🟡 Média

---

## 🟡 PRIORIDADE MÉDIA (Próximas Sprints)

### 4. UI - Card com Tabs por Empresa ⏰ 3 dias
**Status:** 🔴 Não Iniciado  
**Objetivo:** Interface completa com abas para cada tipo de dado

- [ ] Criar componente `CompanyDetail.tsx`
- [ ] Implementar tabs:
  - [ ] Visão Geral (dados cadastrais + métricas)
  - [ ] Histórico CVM (timeline de mudanças)
  - [ ] Dividendos (gráfico + tabela)
  - [ ] Preços (gráfico candlestick)
  - [ ] RI (contatos + histórico de mudanças)
  - [ ] Análise Barsi (score + critérios)
- [ ] Navegação: clicar em empresa → modal ou página detalhada
- [ ] Gráficos: Chart.js ou Recharts

**Impacto:** 🚀 Alto - UX profissional  
**Complexidade:** 🟡 Média

---

### 5. Cálculo de Dividend Yield (DY) ⏰ 2 dias
**Status:** 🔴 Não Iniciado  
**Objetivo:** Calcular DY projetado baseado nos últimos 12 meses

- [ ] Criar função `calcular_dy_projetado()` em `database/models.py`
- [ ] Integrar com dados de dividendos (já temos)
- [ ] Integrar com preços atuais (precisa implementar sync de preços)
- [ ] Adicionar coluna `dividend_yield_atual` na tabela `empresas`
- [ ] Atualizar DY a cada sync de preços (diário)
- [ ] Exibir DY no card de empresa

**Fórmula:**
```
DY = (Soma Dividendos Últimos 12 Meses / Preço Atual) * 100
```

**Impacto:** 🚀 Alto - Critério essencial da metodologia  
**Complexidade:** 🟡 Média (depende de preços atualizados)

---

### 6. Consistência de Dividendos ⏰ 1 dia
**Status:** 🔴 Não Iniciado  
**Objetivo:** Calcular score de consistência de pagamento

- [ ] Criar função `avaliar_consistencia_dividendos()` em `database/models.py`
- [ ] Analisar histórico de 5 anos
- [ ] Calcular score (0-100): % de anos com dividendos
- [ ] Adicionar coluna `consistencia_dividendos` na tabela `empresas`
- [ ] Exibir badge de consistência no card

**Critério:**
- 100: Pagou dividendos todos os anos
- 80-99: Pagou na maioria dos anos
- <80: Inconsistente (não elegível)

**Impacto:** 🔥 Médio - Filtra empresas confiáveis  
**Complexidade:** 🟢 Baixa

---

## 🟢 PRIORIDADE BAIXA (Backlog)

### 7. Robô de Monitoramento de RI (Scraping) ⏰ 5 dias
**Status:** 🔴 Não Iniciado  
**Objetivo:** Detectar mudanças diárias em sites de RI

- [ ] Criar `integrations/ri_scraper.py`
- [ ] Implementar detecção de mudanças via hash de conteúdo
- [ ] Criar job `monitor_ri.py` (execução diária)
- [ ] Criar tabela `ri_mudancas` (log de alterações)
- [ ] Respeitar robots.txt e rate limiting
- [ ] Fallback: se site bloquear, usar apenas dados CVM

**Tipos de Mudanças:**
- Novo comunicado ao mercado
- Novo fato relevante
- Atualização de calendário de dividendos
- Nova apresentação institucional

**Impacto:** 🔥 Médio - Útil mas não essencial  
**Complexidade:** 🔴 Alta (manutenção constante, sites heterogêneos)

---

### 8. Sistema de Notificações ⏰ 2 dias
**Status:** 🔴 Não Iniciado  
**Objetivo:** Alertas de mudanças importantes

- [ ] Criar tabela `notificacoes`
- [ ] Criar endpoint `/api/notificacoes`
- [ ] Criar endpoint `/api/notificacoes/{id}/marcar-lida`
- [ ] UI: Bell icon no header
- [ ] UI: Badge com contador de não lidas
- [ ] UI: Dropdown de notificações
- [ ] Tipos: CADASTRO, RI_DADOS, RI_COMUNICADO, DIVIDENDO_NOVO

**Impacto:** 🔥 Médio - Engajamento do usuário  
**Complexidade:** 🟡 Média

---

### 9. Gráfico de Preços (Candlestick) ⏰ 2 dias
**Status:** 🔴 Não Iniciado  
**Objetivo:** Visualizar histórico de preços

- [ ] Criar integração para baixar preços históricos (Yahoo Finance ou Brapi)
- [ ] Criar job `sync_precos.py` (diário)
- [ ] Salvar em tabela `precos_historico`
- [ ] Implementar gráfico candlestick na tab "Preços"
- [ ] Opções: 1M, 3M, 6M, 1A, 5A, Tudo

**Impacto:** 🔥 Médio - Visualização útil mas não essencial  
**Complexidade:** 🟡 Média

---

### 10. Mapeamento CNPJ → Ticker ⏰ 3 dias
**Status:** 🔴 Não Iniciado  
**Objetivo:** Cruzar dados CVM com cotações da bolsa

- [ ] Criar tabela manual de CNPJs principais (top 100 empresas)
- [ ] Ou: integrar com Brapi (buscar ticker por nome de empresa)
- [ ] Adicionar coluna `ticker_principal` na tabela `empresas`
- [ ] Criar função `mapear_cnpj_para_ticker()`
- [ ] Popular tabela `acoes` automaticamente

**Desafio:**
- CVM usa CNPJ
- B3 usa Ticker (PETR4, VALE3, etc.)
- Não há API oficial de mapeamento

**Impacto:** 🚀 Alto - Necessário para preços e DY  
**Complexidade:** 🟡 Média (trabalho manual)

---

## ✅ CONCLUÍDO

### ✅ Integração CVM - Cadastro e DFP
- [x] Criar `integrations/cvm_integration.py`
- [x] Baixar cadastro de empresas (2.650 empresas)
- [x] Baixar DFP (Demonstrações Financeiras)
- [x] Extrair dividendos da DRE
- [x] Extrair patrimônio líquido do BPP
- [x] Criar job `sync_cvm.py`
- [x] Executar primeira sincronização

### ✅ Banco de Dados SQLite
- [x] Criar `database/models.py`
- [x] Tabelas: empresas, acoes, dividendos, patrimonio, relacoes_investidores, sync_log
- [x] Índices para performance
- [x] Singleton pattern

### ✅ Backend API
- [x] Endpoints REST para consulta de empresas
- [x] GET `/api/empresas` (listagem)
- [x] GET `/api/empresas/{cnpj}` (detalhes)
- [x] GET `/api/acoes` (tickers)
- [x] GET `/api/stats` (estatísticas)

### ✅ Frontend - Listagem de Empresas
- [x] Criar `CompanyList.tsx`
- [x] Cards de estatísticas
- [x] Busca por razão social/CNPJ
- [x] Filtros: Ativas/Todas/Canceladas
- [x] Adicionar item "Empresas" no sidebar

### ✅ Script de Teste com Flag Auto-Yes
- [x] Adicionar flag `--auto-yes` em `test_cvm.py`
- [x] Pular inputs manuais em modo automático

---

## 📊 PROGRESSO GERAL

**Total de Tarefas:** 10  
**Concluídas:** 5 ✅  
**Em Andamento:** 0 🔄  
**Não Iniciadas:** 5 🔴

**Progresso:** 50% 🎯

---

## 🎯 PRÓXIMAS AÇÕES IMEDIATAS

1. **Implementar Filtro BESST** (1h) - Quick win, alto impacto
2. **Calcular DY e Consistência** (1 dia) - Essencial para metodologia
3. **Sistema de Histórico** (5 dias) - Base para todas as análises

**Próxima Sprint:** Histórico + RI via CVM (8 dias)

---

**Criado em:** 02/01/2026  
**Próxima Revisão:** Semanal (toda segunda-feira)

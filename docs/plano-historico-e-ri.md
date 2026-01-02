# 📋 Plano de Implementação: Histórico & Relações com Investidores (RI)

**Data de Criação:** 02/01/2026  
**Status:** 📝 Planejamento  
**Prioridade:** 🔴 ALTA

---

## 🎯 Objetivos

### 1. Sistema de Histórico de Dados
Implementar versionamento temporal de todos os dados críticos das empresas:
- ✅ Histórico CVM (cadastro, situação, setor)
- ✅ Histórico de dividendos distribuídos
- ✅ Histórico de preços de ações
- ✅ Histórico de patrimônio líquido
- ⏳ Histórico de mudanças no RI

### 2. Monitoramento de Relações com Investidores (RI)
- ⏳ Capturar dados de RI da CVM
- ⏳ Robô de monitoramento diário
- ⏳ Sistema de notificações de mudanças
- ⏳ Histórico de alterações no RI

### 3. Filtro Metodologia Barsi (BESST)
- ⏳ Classificar empresas por setor BESST
- ⏳ Filtro automático (apenas empresas dentro do range)
- ⏳ Dashboard focado em empresas elegíveis

---

## 📊 PARTE 1: Dados de RI na CVM

### ✅ O que a CVM Oferece

#### A) Formulário Cadastral (FCA)
**Dataset:** `cia_aberta-doc-fca`  
**URL:** https://dados.cvm.gov.br/dataset/cia_aberta-doc-fca  
**Contém:**
- ✅ Site da empresa
- ✅ Endereço completo
- ✅ Telefone
- ❌ NÃO contém: email específico do RI

**Estrutura do arquivo:**
```
fca_cia_aberta_{year}.zip
  └── fca_cia_aberta_geral_{year}.csv
      ├── CNPJ_CIA
      ├── DENOM_SOCIAL (razão social)
      ├── DENOM_COMERC (nome comercial)
      ├── SIT (situação)
      ├── DT_REG (data de registro)
      ├── DT_CONST (data de constituição)
      ├── DT_CANCEL (data de cancelamento)
      ├── MOTIVO_CANCEL
      ├── PAIS
      ├── UF
      └── MUNICIPIO
```

**Arquivo de Contato:**
```
fca_cia_aberta_geral_{year}.csv
Campos específicos:
  - LOGRADOURO
  - COMPL
  - BAIRRO
  - MUNICIPIO
  - UF
  - CEP
  - DDD_TEL
  - TEL
  - DDD_FAX
  - FAX
  - EMAIL (email corporativo geral, não necessariamente do RI)
  - TP_ENDER (tipo: sede, filial, etc)
```

#### B) Formulário de Referência (FRE)
**Dataset:** `cia_aberta-doc-fre`  
**URL:** https://dados.cvm.gov.br/dataset/cia_aberta-doc-fre  
**Contém:**
- ✅ Estrutura acionária
- ✅ Administração e governança
- ✅ Negócios e riscos
- ✅ **Informações importantes sobre RI**

**Estrutura do arquivo:**
```
fre_cia_aberta_{year}.zip
  └── Múltiplos CSVs por seção do formulário:
      ├── fre_cia_aberta_geral_{year}.csv
      ├── fre_cia_aberta_valor_mobiliario_{year}.csv
      └── ... (20+ arquivos)
```

**📌 IMPORTANTE:** O FRE contém uma seção específica sobre **"Comunicação com Investidores"** que pode incluir:
- Website de RI
- Email de RI
- Telefone de RI
- Nome do diretor de RI

---

## 🤖 PARTE 2: Robô de Monitoramento de RI

### Estratégia de Implementação

#### Opção 1: Monitoramento via CVM (RECOMENDADO)
**Vantagens:**
- ✅ Fonte oficial e confiável
- ✅ Estruturado (CSV/JSON)
- ✅ Atualizado periodicamente pela CVM
- ✅ Sem bloqueios ou CAPTCHAs

**Desvantagens:**
- ⚠️ Atualização não é diária (semanal/mensal dependendo do formulário)
- ⚠️ Empresas podem demorar a atualizar

**Implementação:**
```python
# integrations/cvm_fre_integration.py
class CVMFREIntegration:
    """
    Captura dados de RI do Formulário de Referência da CVM
    """
    
    def download_fre(self, year: int) -> Dict[str, pd.DataFrame]:
        """Baixa FRE completo de um ano"""
        url = f"https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/DADOS/fre_cia_aberta_{year}.zip"
        # ...
    
    def extrair_dados_ri(self, fre_data: Dict) -> pd.DataFrame:
        """
        Extrai informações de Relações com Investidores
        
        Retorna:
            DataFrame com:
            - CNPJ_CIA
            - website_ri
            - email_ri
            - telefone_ri
            - diretor_ri_nome
            - ultima_atualizacao
        """
        # Processar seção específica do FRE
```

**Frequência:**
- FCA: Mensal (quando há mudanças cadastrais)
- FRE: Anual (prazo: até 31/05)

**Solução para Atualização Diária:**
- Combinar CVM (fonte primária) + scraping sites de RI (fonte secundária)
- CVM garante dados oficiais
- Scraping detecta mudanças rápidas (novo comunicado, FAQ, etc.)

---

#### Opção 2: Scraping de Sites de RI (COMPLEMENTAR)
**Vantagens:**
- ✅ Detecta mudanças em tempo real
- ✅ Captura novos comunicados, fatos relevantes

**Desvantagens:**
- ⚠️ Sites heterogêneos (cada empresa tem estrutura diferente)
- ⚠️ Risco de bloqueios
- ⚠️ Necessita manutenção constante

**Implementação:**
```python
# integrations/ri_scraper.py
class RIScraper:
    """
    Scraper genérico para sites de RI
    """
    
    def detect_changes(self, url: str, last_hash: str) -> bool:
        """
        Detecta mudanças no site através de hash do conteúdo
        """
        current_content = self.fetch_page(url)
        current_hash = hashlib.sha256(current_content.encode()).hexdigest()
        
        return current_hash != last_hash
    
    def extract_latest_comunicado(self, url: str) -> Dict:
        """
        Extrai último comunicado/fato relevante
        """
        # Usar Beautiful Soup ou Playwright
```

**Frequência:**
- Execução: Diária (00:00)
- Checagem rápida: hash do HTML
- Se mudança detectada: notificar + salvar histórico

---

### 🔔 Sistema de Notificações

#### Tipos de Mudanças a Monitorar

1. **Mudanças Cadastrais (CVM)**
   - Troca de razão social
   - Mudança de endereço/telefone
   - Mudança de situação (ativa → cancelada)

2. **Mudanças no RI (FRE)**
   - Novo email de RI
   - Novo telefone de RI
   - Mudança de diretor de RI
   - Novo website de RI

3. **Mudanças no Site de RI (Scraping)**
   - Novo comunicado ao mercado
   - Novo fato relevante
   - Atualização de calendário de dividendos
   - Nova apresentação institucional

#### Implementação de Notificações

```python
# Estrutura da tabela
CREATE TABLE notificacoes (
    id INTEGER PRIMARY KEY,
    empresa_id INTEGER,
    tipo TEXT, -- 'CADASTRO', 'RI_DADOS', 'RI_COMUNICADO'
    titulo TEXT,
    descricao TEXT,
    gravidade TEXT, -- 'INFO', 'WARNING', 'CRITICAL'
    lida BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP
);

# Exemplo de notificação
{
    "tipo": "RI_COMUNICADO",
    "empresa": "PETROBRAS",
    "titulo": "Novo comunicado sobre dividendos",
    "descricao": "Aprovação de dividendos extraordinários de R$ 2,50 por ação",
    "gravidade": "CRITICAL",
    "link": "https://ri.petrobras.com.br/comunicado-123",
    "data": "2026-01-02T10:30:00"
}
```

---

## 📈 PARTE 3: Sistema de Histórico (Versionamento)

### Estrutura de Banco de Dados

#### Tabela: `empresas_historico`
```sql
CREATE TABLE empresas_historico (
    id INTEGER PRIMARY KEY,
    empresa_id INTEGER,
    
    -- Snapshot dos dados
    razao_social TEXT,
    nome_fantasia TEXT,
    cnpj TEXT,
    codigo_cvm TEXT,
    situacao TEXT,
    setor TEXT,
    
    -- Dados de RI
    website_ri TEXT,
    email_ri TEXT,
    telefone_ri TEXT,
    diretor_ri TEXT,
    
    -- Metadados de versionamento
    versao INTEGER,
    valido_de TIMESTAMP,
    valido_ate TIMESTAMP,
    alterado_por TEXT, -- 'SYNC_CVM', 'SYNC_FRE', 'SCRAPER_RI'
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (empresa_id) REFERENCES empresas(id)
);

CREATE INDEX idx_empresas_historico_empresa ON empresas_historico(empresa_id);
CREATE INDEX idx_empresas_historico_validade ON empresas_historico(valido_de, valido_ate);
```

#### Tabela: `dividendos_historico`
```sql
CREATE TABLE dividendos_historico (
    id INTEGER PRIMARY KEY,
    empresa_id INTEGER,
    
    -- Dados do dividendo
    ano_fiscal INTEGER,
    trimestre INTEGER,
    tipo TEXT, -- 'DIVIDENDO', 'JCP'
    valor_por_acao REAL,
    valor_total REAL,
    data_aprovacao DATE,
    data_pagamento DATE,
    
    -- Metadados
    fonte TEXT, -- 'CVM_DRE', 'CVM_DMPL', 'BRAPI'
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (empresa_id) REFERENCES empresas(id)
);

CREATE INDEX idx_dividendos_empresa_ano ON dividendos_historico(empresa_id, ano_fiscal);
```

#### Tabela: `precos_historico`
```sql
CREATE TABLE precos_historico (
    id INTEGER PRIMARY KEY,
    acao_id INTEGER,
    
    -- Dados do preço
    data DATE,
    abertura REAL,
    maxima REAL,
    minima REAL,
    fechamento REAL,
    volume INTEGER,
    
    -- Ajustes
    fechamento_ajustado REAL,
    
    -- Metadados
    fonte TEXT, -- 'BRAPI', 'YAHOO', 'B3'
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (acao_id) REFERENCES acoes(id)
);

CREATE INDEX idx_precos_acao_data ON precos_historico(acao_id, data);
```

---

## 🎨 PARTE 4: UI - Card com Tabs por Empresa

### Estrutura do Card

```tsx
// components/CompanyDetail.tsx
<Card className="max-w-4xl">
  {/* Header */}
  <CardHeader>
    <div className="flex items-center justify-between">
      <div>
        <h2 className="text-2xl font-bold">{empresa.razao_social}</h2>
        <p className="text-muted-foreground">{empresa.ticker} • {empresa.setor}</p>
      </div>
      <Badge variant={empresa.situacao === 'ATIVO' ? 'success' : 'warning'}>
        {empresa.situacao}
      </Badge>
    </div>
  </CardHeader>

  {/* Tabs */}
  <Tabs defaultValue="visao-geral">
    <TabsList>
      <TabsTrigger value="visao-geral">Visão Geral</TabsTrigger>
      <TabsTrigger value="historico-cvm">Histórico CVM</TabsTrigger>
      <TabsTrigger value="dividendos">Dividendos</TabsTrigger>
      <TabsTrigger value="precos">Preços</TabsTrigger>
      <TabsTrigger value="ri">Relações com Investidores</TabsTrigger>
      <TabsTrigger value="analise">Análise Barsi</TabsTrigger>
    </TabsList>

    {/* Tab: Visão Geral */}
    <TabsContent value="visao-geral">
      <div className="grid grid-cols-2 gap-4">
        <InfoCard label="CNPJ" value={empresa.cnpj} />
        <InfoCard label="Código CVM" value={empresa.codigo_cvm} />
        <InfoCard label="Setor" value={empresa.setor} />
        <InfoCard label="Dividend Yield" value={`${empresa.dy}%`} />
      </div>
    </TabsContent>

    {/* Tab: Histórico CVM */}
    <TabsContent value="historico-cvm">
      <Timeline>
        {historicoCVM.map(item => (
          <TimelineItem 
            key={item.id}
            date={item.data}
            title={item.campo_alterado}
            description={`${item.valor_antigo} → ${item.valor_novo}`}
          />
        ))}
      </Timeline>
    </TabsContent>

    {/* Tab: Dividendos */}
    <TabsContent value="dividendos">
      <Chart type="bar" data={dividendosPorAno} />
      <Table data={dividendosDetalhados} />
    </TabsContent>

    {/* Tab: Preços */}
    <TabsContent value="precos">
      <Chart type="candlestick" data={precosHistoricos} />
    </TabsContent>

    {/* Tab: RI */}
    <TabsContent value="ri">
      <div className="space-y-4">
        <ContactCard 
          title="Website de RI"
          value={empresa.website_ri}
          icon={Globe}
        />
        <ContactCard 
          title="Email de RI"
          value={empresa.email_ri}
          icon={Mail}
        />
        <ContactCard 
          title="Telefone de RI"
          value={empresa.telefone_ri}
          icon={Phone}
        />
        
        {/* Histórico de mudanças no RI */}
        <Accordion>
          <AccordionItem title="Histórico de Alterações">
            <Timeline data={historicoRI} />
          </AccordionItem>
        </Accordion>

        {/* Últimos comunicados (se scraping ativo) */}
        <div>
          <h3>Últimos Comunicados</h3>
          {comunicados.map(c => (
            <Card key={c.id}>
              <CardTitle>{c.titulo}</CardTitle>
              <CardDescription>{c.data}</CardDescription>
              <Link href={c.url}>Ver comunicado</Link>
            </Card>
          ))}
        </div>
      </div>
    </TabsContent>

    {/* Tab: Análise Barsi */}
    <TabsContent value="analise">
      <ScoreCard 
        score={empresa.barsi_score}
        criterios={[
          { nome: 'Setor BESST', atende: true },
          { nome: 'DY > 6%', atende: empresa.dy >= 6 },
          { nome: 'Consistência Dividendos', atende: empresa.consistencia >= 80 },
        ]}
      />
    </TabsContent>
  </Tabs>
</Card>
```

---

## 🎯 PARTE 5: Filtro de Empresas (Metodologia Barsi)

### Critérios de Elegibilidade

#### 1. Setor BESST
```python
SETORES_BESST = {
    'B': ['Bancos', 'Instituições Financeiras'],
    'E': ['Energia Elétrica', 'Utilities'],
    'S': ['Saneamento', 'Água e Esgoto'],
    'S': ['Seguros', 'Seguradoras', 'Resseguradoras'],
    'T': ['Telecomunicações', 'Telefonia'],
}

def classificar_setor_besst(setor: str) -> Optional[str]:
    """
    Classifica empresa em setor BESST
    
    Retorna: 'B', 'E', 'S', 'T' ou None (se não se enquadra)
    """
    setor_lower = setor.lower()
    
    for letra, setores in SETORES_BESST.items():
        for setor_besst in setores:
            if setor_besst.lower() in setor_lower:
                return letra
    
    return None
```

#### 2. Dividend Yield > 6%
```python
def calcular_dy_projetado(empresa: dict) -> float:
    """
    Calcula DY projetado com base nos últimos 12 meses
    
    DY = (Soma Dividendos Últimos 12 Meses / Preço Atual) * 100
    """
    dividendos_12m = sum_dividendos_ultimos_12_meses(empresa['id'])
    preco_atual = get_preco_atual(empresa['ticker'])
    
    if preco_atual <= 0:
        return 0
    
    return (dividendos_12m / preco_atual) * 100
```

#### 3. Consistência de Dividendos
```python
def avaliar_consistencia_dividendos(empresa_id: int, anos: int = 5) -> float:
    """
    Avalia consistência de pagamento de dividendos
    
    Retorna: Score de 0 a 100
    - 100: Pagou dividendos todos os anos
    - 0: Nunca pagou dividendos
    """
    historico = get_dividendos_por_ano(empresa_id, anos)
    
    anos_com_dividendos = sum(1 for ano in historico if ano['valor_total'] > 0)
    
    return (anos_com_dividendos / anos) * 100
```

### Implementação do Filtro

```python
# database/models.py - adicionar método
class Database:
    
    def get_empresas_elegiveis_barsi(
        self,
        dy_minimo: float = 6.0,
        consistencia_minima: float = 80.0
    ) -> List[dict]:
        """
        Retorna apenas empresas elegíveis pela metodologia Barsi
        """
        query = """
            SELECT 
                e.*,
                e.setor_besst,
                e.dividend_yield_atual,
                e.consistencia_dividendos
            FROM empresas e
            WHERE 
                e.situacao = 'ATIVO'
                AND e.setor_besst IS NOT NULL  -- Apenas setores BESST
                AND e.dividend_yield_atual >= ?
                AND e.consistencia_dividendos >= ?
            ORDER BY e.dividend_yield_atual DESC
        """
        
        self.cursor.execute(query, (dy_minimo, consistencia_minima))
        return self.cursor.fetchall()
```

### Endpoint de API

```python
# web/companies.py
def handle_empresas_elegiveis(self) -> dict:
    """
    GET /api/empresas/elegiveis
    
    Retorna apenas empresas que atendem critérios Barsi
    """
    db = get_db()
    
    # Parâmetros de filtro (opcional)
    dy_minimo = float(self.params.get('dy_minimo', 6.0))
    consistencia = float(self.params.get('consistencia', 80.0))
    
    empresas = db.get_empresas_elegiveis_barsi(dy_minimo, consistencia)
    
    return {
        'total': len(empresas),
        'filtros': {
            'dy_minimo': dy_minimo,
            'consistencia_minima': consistencia
        },
        'empresas': empresas
    }
```

### UI - Toggle de Filtro

```tsx
// components/CompanyList.tsx
<div className="flex items-center gap-2">
  <Switch 
    id="filtro-barsi"
    checked={filtroBarsiAtivo}
    onCheckedChange={setFiltroBarsiAtivo}
  />
  <Label htmlFor="filtro-barsi">
    Mostrar apenas empresas elegíveis Barsi
  </Label>
</div>

{filtroBarsiAtivo && (
  <Alert>
    <Info className="size-4" />
    <AlertTitle>Filtro Ativo</AlertTitle>
    <AlertDescription>
      Exibindo apenas empresas dos setores BESST com DY ≥ 6% e 
      consistência de dividendos ≥ 80% nos últimos 5 anos.
    </AlertDescription>
  </Alert>
)}
```

---

## 📅 CRONOGRAMA DE IMPLEMENTAÇÃO

### Sprint 1: Sistema de Histórico (5 dias)
- [ ] Criar tabelas de histórico no SQLite
- [ ] Implementar versionamento automático (trigger ou lógica de app)
- [ ] Modificar sync_cvm.py para salvar snapshots
- [ ] Criar endpoint GET /api/empresas/{cnpj}/historico
- [ ] UI: Timeline de histórico na tab "Histórico CVM"

### Sprint 2: Dados de RI via CVM (3 dias)
- [ ] Criar `integrations/cvm_fre_integration.py`
- [ ] Baixar e processar FRE (Formulário de Referência)
- [ ] Baixar e processar FCA (Formulário Cadastral)
- [ ] Extrair dados de RI (website, email, telefone, diretor)
- [ ] Salvar em tabela `relacoes_investidores`
- [ ] Criar job `sync_cvm_ri.py` (mensal)

### Sprint 3: Filtro Metodologia Barsi (2 dias)
- [ ] Implementar classificação de setores BESST
- [ ] Calcular DY projetado de cada empresa
- [ ] Calcular consistência de dividendos (5 anos)
- [ ] Adicionar campos na tabela empresas (setor_besst, dy_atual, consistencia)
- [ ] Criar endpoint GET /api/empresas/elegiveis
- [ ] UI: Toggle de filtro + badge "Elegível Barsi"

### Sprint 4: UI - Card com Tabs (3 dias)
- [ ] Criar componente CompanyDetail.tsx
- [ ] Implementar tabs (Visão Geral, Histórico CVM, Dividendos, Preços, RI, Análise)
- [ ] Gráficos de dividendos por ano (Chart.js ou Recharts)
- [ ] Timeline de histórico CVM
- [ ] Card de contato de RI
- [ ] Navegação: clicar em empresa → abrir card detalhado

### Sprint 5: Robô de Monitoramento de RI (5 dias)
- [ ] Criar `integrations/ri_scraper.py`
- [ ] Implementar detecção de mudanças (hash de conteúdo)
- [ ] Criar job `monitor_ri.py` (diário)
- [ ] Criar tabela `ri_mudancas` (log de alterações)
- [ ] Sistema de notificações (tabela + endpoint)
- [ ] UI: Bell icon com contador de notificações não lidas

### Sprint 6: Notificações (2 dias)
- [ ] Criar tabela `notificacoes`
- [ ] Endpoint GET /api/notificacoes
- [ ] Endpoint POST /api/notificacoes/{id}/marcar-lida
- [ ] UI: Dropdown de notificações no header
- [ ] UI: Badge com contador de não lidas
- [ ] UI: Filtros (tipo, gravidade, lidas/não lidas)

---

## 🚀 QUICK WINS (Implementar Primeiro)

### 1. Filtro BESST (1 hora)
**Impacto:** Alto - foco imediato nas empresas certas  
**Complexidade:** Baixa - apenas classificação de strings

```python
# Adicionar função no database/models.py
def classificar_besst_todas_empresas():
    """Roda uma vez para classificar todas as empresas"""
    empresas = db.get_all_empresas()
    
    for emp in empresas:
        setor_besst = classificar_setor_besst(emp['setor'])
        db.update_empresa(emp['id'], {'setor_besst': setor_besst})
```

### 2. Histórico de Dividendos (2 horas)
**Impacto:** Alto - visualização essencial  
**Complexidade:** Média - já temos os dados, só falta a UI

```tsx
// Gráfico simples de dividendos por ano
<BarChart data={dividendosPorAno} />
```

### 3. Badge "Elegível Barsi" (30 min)
**Impacto:** Médio - destaque visual  
**Complexidade:** Baixa - apenas condicional na UI

```tsx
{empresa.elegivel_barsi && (
  <Badge variant="success">✅ Elegível Barsi</Badge>
)}
```

---

## 📝 NOTAS IMPORTANTES

### ⚠️ Sobre o Scraping de RI
- **Legalidade:** Respeitar robots.txt e termos de uso
- **Rate Limiting:** Não fazer mais de 1 requisição por segundo por domínio
- **User-Agent:** Identificar claramente: `BarsiParaLeigos/1.0 (contato@barsi.com)`
- **Fallback:** Se site bloquear, continuar usando apenas dados da CVM

### 💡 Otimizações
- Cache de 24h para dados de RI (evitar requisições desnecessárias)
- Índices no banco para queries rápidas de histórico
- Paginação em históricos longos (>100 registros)

### 🔒 Segurança
- Nunca armazenar senhas ou dados sensíveis de RI
- Apenas URLs públicas e dados já disponíveis na CVM
- Log de todas as requisições de scraping (auditoria)

---

## 📚 REFERÊNCIAS

- [Portal de Dados Abertos da CVM](https://dados.cvm.gov.br/)
- [Documentação CKAN API](https://docs.ckan.org/en/2.9/api/)
- [Metodologia Barsi - Consolidação](./consolidacao-projeto-metodologia-barsi.md)
- [Integração CVM - Documentação](./integracao-cvm.md)
- [Robô CVM - Guia](./robo-cvm-guia.md)

---

**Última Atualização:** 02/01/2026  
**Próxima Revisão:** Após Sprint 1

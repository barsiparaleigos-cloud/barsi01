# Consolidação do Projeto: Metodologia Luiz Barsi e Viabilidade de Software

> **Nota de segurança (importante):** este documento foi gerado a partir do histórico de conversa e, por isso, qualquer **token, chave ou segredo** que apareceu no texto original foi **removido/mascarado** (ex.: `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_ANON_KEY`, tokens `sbp_...`).
> 
> - **Nunca** registre segredos em repositório Git (mesmo privado).
> - Use `.env.local` (ignorado pelo Git) e **GitHub Secrets**.
> - Se algum segredo foi colado em chat, considere **rotacionar/revogar**.

Este documento consolida toda a análise realizada, desde a compreensão da metodologia de investimento de Luiz Barsi Filho até a avaliação da viabilidade técnica para o desenvolvimento de um software de recomendação de ações para investidores leigos.

---

## 1. Pesquisa Inicial: A Metodologia de Luiz Barsi

### Pergunta do Usuário

> vc consegue fazer uma pesquisa na internet, e entender a base da metodologia de compra de açoes do Luis barsi brasileiro?

### Resposta Consolidada (Manus AI)

A metodologia de Luiz Barsi Filho, conhecida como "Carteira Previdenciária", é uma abordagem de Value Investing com foco absoluto na geração de renda passiva através de dividendos.

#### Fundamentos da Filosofia de Investimento

- **Visão de Sócio:** O investidor deve se comportar como um proprietário da empresa, interessado na sua lucratividade e sustentabilidade ao longo de décadas.
- **Foco em Dividendos:** O objetivo primordial é o recebimento de proventos, que são utilizados para adquirir mais ações, criando um efeito de "bola de neve" (reinvestimento).
- **Buy and Hold:** A estratégia consiste em comprar boas empresas e mantê-las indefinidamente, vendendo apenas se os fundamentos do negócio se deteriorarem irreversivelmente.

#### O Acrônimo BESST: Setores Perenes

Barsi concentra seus investimentos em setores que considera "à prova de balas", caracterizados por demanda constante, previsibilidade de caixa e barreiras de entrada.

| Letra | Setor             | Justificativa |
|------:|-------------------|---------------|
| B     | Bancos            | Instituições essenciais com alta rentabilidade e histórico de distribuição de lucros. |
| E     | Energia           | Especialmente o segmento de transmissão, com receitas reguladas e contratos de longuíssimo prazo. |
| S     | Saneamento        | Serviços básicos indispensáveis com baixa concorrência e fluxos de caixa estáveis. |
| S     | Seguros           | Modelo de negócio baseado em "float" (receber prêmios antes de pagar sinistros) e alta recorrência. |
| T     | Telecomunicações  | Setor de infraestrutura crítica na sociedade moderna, com demanda resiliente. |

#### A Regra dos 6% e o Preço-Teto

O aspecto mais prático da metodologia é a disciplina quanto ao preço pago. Barsi estabelece que uma ação só deve ser adquirida se projetar um Dividend Yield (DY) mínimo de 6% ao ano.

O **Preço-Teto** é o valor máximo que se deve pagar por uma ação para garantir esse retorno mínimo:

$$
\text{Preço-Teto} = \frac{\text{Média de Dividendos por Ação (DPA)}}{0{,}06}
$$

---

## 2. Fontes de Dados e Métodos de Pesquisa

### Pergunta do Usuário

> considerando isso, como ele pesquisa essas empresas? aonde estão as fontes desses dados?

### Resposta Consolidada (Manus AI)

A pesquisa de Barsi é um processo de análise fundamentalista pura, baseada em fontes oficiais e públicas, com foco na capacidade da empresa de gerar lucros e distribuí-los de forma consistente.

#### As Fontes Primárias de Dados

As fontes de dados são os documentos que as empresas de capital aberto são obrigadas a divulgar:

- **CVM (Comissão de Valores Mobiliários):** Principal fonte para o Formulário de Demonstrações Financeiras Padronizadas (DFP) e Informes Trimestrais (ITR).
- **B3 (Brasil, Bolsa, Balcão):** Fonte de dados de negociação e cotações.
- **Relações com Investidores (RI) das Empresas:** Sites oficiais para acesso a Fatos Relevantes e relatórios gerenciais.

#### Ferramentas de Consolidação (AGF)

A equipe de Barsi, notadamente através da plataforma AGF (Ações Garantem o Futuro), desenvolveu ferramentas para consolidar e aplicar a metodologia:

| Ferramenta | Função | Relevância para a Metodologia |
|-----------|--------|-------------------------------|
| MDI (Mapa do Dividendo Inteligente) | Estima a probabilidade e a data de anúncio de dividendos, baseado no histórico. | Permite ao investidor se antecipar aos anúncios de proventos, comprando antes da alta de preço. |
| Raio-X | Consolida todos os indicadores de Barsi (DY, DPA, Preço-Teto) em uma única tela. | Simplifica a análise fundamentalista para verificar se a ação atende aos critérios de compra. |

---

## 3. Viabilidade e Desafios do Software para Leigos

### Pergunta do Usuário

> quero desenvolver um software para leigos absolutos. qual o objetivo, acessar todas as fontes de dados via api, ou consulta em browser via i.a , e ter indices em tempo real, para nos indicar qual ação comprar segundo esse metodologia. imagine o seguinte, temos uma fonte primaria onde acompanhamos indices e numeros, que nos indicam uma boa possibilidade, mas ao inves de interpretar isso leigamente, o software de leitura de dados, vai buscar inumeras fontes, cruzar, submeter ao metodo que ele montou, e nos dizer essas empresas vale a pena comprar. consegui explicar ? me diga a viabilidade, e os desafios técnicos para montar isso. e tambem pesquise as principais fonte de dados do mercado financeiro, que são abertos a integração via api automático.

### Resposta Consolidada (Manus AI)

A construção de um "Cérebro Digital de Investimentos" que automatiza a metodologia Barsi é altamente viável. O maior valor do software será retirar a carga cognitiva do usuário, traduzindo números complexos em recomendações simples.

#### Viabilidade Técnica

O projeto é viável por se basear em regras algorítmicas claras (BESST e Preço-Teto) e pela existência de APIs de dados no mercado brasileiro.

#### Desafios Técnicos e Soluções

| Desafio Técnico | Solução Proposta |
|----------------|------------------|
| Normalização de Dados | Utilizar APIs intermediárias (como Fintz) que já fazem a limpeza e estruturação dos dados contábeis da CVM. |
| Latência dos Dados | Arquitetura híbrida: APIs de Market Data para preços em tempo real e Data Lake para histórico de proventos. |
| Interpretação da IA | Aplicar o modelo RAG (Retrieval-Augmented Generation): a IA apenas interpreta os resultados calculados pelo motor lógico, garantindo fidelidade à metodologia. |

#### Mapeamento de Fontes de Dados (APIs)

| Fonte de Dados | Tipo de Informação | Integração Recomendada |
|---------------|--------------------|------------------------|
| CVM (Dados Abertos) | Balanços Oficiais (DFP/ITR) | Download de arquivos CSV/XML (exige processamento) ou APIs intermediárias. |
| Brapi (brapi.dev) | Cotações em tempo real, Histórico de preços, Dividendos. | API REST (Fácil integração, bom plano gratuito). |
| Fintz (fintz.com.br) | Dados contábeis normalizados, Histórico de Proventos. | API REST (Ideal para dados limpos e prontos para o cálculo do Preço-Teto). |
| HG Brasil Finance | Cotações, Índices, Moedas. | API REST (Estável, mas com limites de requisição no plano gratuito). |

---

## 4. Insights Adicionais para o Desenvolvimento

Para garantir o sucesso do software para "leigos absolutos", sugiro as seguintes considerações estratégicas:

### A. Foco na Experiência do Usuário (UX)

O software deve ser mais do que uma calculadora; deve ser um educador.

- **Gamificação da Disciplina:** Incluir um sistema de pontuação ou badges para incentivar o reinvestimento de dividendos e a manutenção da carteira no longo prazo, combatendo a tentação de vender por pânico ou euforia.
- **Simulação de Renda:** Apresentar visualmente ao usuário o quanto a carteira atual gera de renda mensal projetada e o quanto essa renda aumentaria ao reinvestir os dividendos recebidos. Isso tangibiliza o conceito de "Carteira Previdenciária".

### B. Otimização da Camada de IA

A camada de IA deve ser treinada com um vocabulário específico para evitar jargões do mercado.

- **Exemplo de Output Leigo:** Em vez de dizer: "O P/L está em 8x e o Preço-Teto é R$ 40,00", a IA deve dizer: "A empresa X está barata. Você está comprando R$ 1,00 de lucro por apenas R$ 8,00, e o preço atual é R$ 30,00, bem abaixo do máximo que você deveria pagar (R$ 40,00) para garantir sua aposentadoria."

### C. Estratégia de Dados

Recomenda-se fortemente a criação de um Data Lake próprio. Embora as APIs sejam ótimas para começar, a dependência de terceiros para dados históricos de dividendos pode ser um risco a longo prazo. Coletar e armazenar o histórico de proventos e balanços em uma base de dados própria garante a perenidade e a precisão dos cálculos do Preço-Teto, que é o coração da metodologia Barsi.

Com uma metodologia clara, fontes de dados mapeadas e uma estratégia de comunicação focada no leigo, o projeto tem todas as condições para ser um sucesso.

---

## 5. Continuação da conversa (Copilot)

> **Observação:** a partir daqui o texto reflete a consolidação da conversa com foco em viabilidade, arquitetura e MVP.

### Leitura crítica e arquitetura recomendada

Li o material e a ideia está bem formulada: você quer um software que “traduza” a metodologia Barsi (renda/dividendos + disciplina de preço via preço-teto/DY mínimo + preferência por setores perenes) em decisões acionáveis para um leigo, automatizando coleta de dados, cálculo e explicação.

Abaixo vai uma leitura crítica da viabilidade, dos principais desafios técnicos e um desenho de arquitetura recomendada (com alertas importantes).

#### 1) Viabilidade (é possível? sim, mas com recortes claros)

Tecnicamente é viável porque a metodologia se apoia em regras e métricas calculáveis:

- filtro de universo (setores “BESST” ou critérios equivalentes)
- histórico e consistência de proventos
- lucro/geração de caixa (capacidade de pagar dividendos)
- preço-teto (derivado de DPA médio e DY-alvo)
- preço atual (market data)

O ponto “sensível” não é a matemática; é dados confiáveis + padronização + atualização + governança.

Viabilidade prática depende do escopo do MVP:

- Se você começar com recomendação “segundo regras” + explicação, usando 1–2 provedores de dados, dá para lançar.
- Se o objetivo for “buscar inúmeras fontes via IA no browser e cruzar tudo em tempo real”, isso vira caro, frágil e difícil de auditar (e pode dar problema regulatório e de responsabilidade).

#### 2) Desafios técnicos reais (onde a maioria falha)

**A) Qualidade/normalização de dados (o maior)**

- CVM publica dados, mas eles vêm em formatos e taxonomias que exigem ETL.
- Dividendos/JCP têm eventos corporativos (desdobramento, grupamento, reorganizações) que quebram séries históricas se você não ajustar.
- Empresas mudam ticker, fazem incorporação, spin-off.

Consequência: seu “preço-teto” pode ficar errado se o DPA histórico não estiver ajustado corretamente.

**B) “Tempo real” é mais difícil do que parece**

- “Índices em tempo real” (cotações) exigem provider com SLA, limites e, muitas vezes, licença.
- Para metodologia Barsi, você não precisa de tick-a-tick. Normalmente:
  - preço com atraso de minutos já resolve
  - atualização diária é suficiente para preço-teto e ranking

**C) IA não pode ser o “motor de decisão”**

A IA “lendo sites” e decidindo compra é:

- pouco reprodutível (hoje diz A, amanhã diz B com os mesmos dados)
- difícil de auditar (“por que recomendou isso?”)
- suscetível a fonte ruim / dado desatualizado

Padrão correto: IA como camada de explicação (RAG), e motor lógico determinístico como decisor.

**D) Regulação/risco jurídico (mesmo que você não queira)**

No Brasil, “recomendar compra” pode ser entendido como recomendação de investimento dependendo de como você comunica (linguagem, personalização, promessa de retorno, perfil do usuário etc.).

Na prática, o app deve tender a:

- “sinalizar oportunidades segundo critérios públicos e pré-definidos”
- mostrar “não é recomendação; é ferramenta educacional”
- registrar premissas e permitir o usuário alterar parâmetros (DY alvo, janelas etc.)

**E) Anti-fragilidade contra dependência de terceiros**

Se você depender só de uma API (ou scraping), você fica vulnerável a:

- mudança de endpoint/termos
- limites de requisição
- dados inconsistentes

Por isso o insight do seu texto é correto: Data Lake próprio (ao menos de proventos e balanços) vira um diferencial e reduz risco.

#### 3) Arquitetura recomendada (simples, auditável, escalável)

**Camadas**

1. **Ingestão de dados**
   - market data (preço)
   - fundamentals/proventos (DPA, histórico de dividendos/JCP)
   - eventos corporativos (splits etc.)
2. **Padronização/ETL**
   - converte tudo para um “modelo canônico” interno:
     - empresa_id
     - ticker(s) ao longo do tempo
     - datas de pagamento/declaração
     - provento por ação ajustado
     - demonstrativos por período
3. **Motor Barsi (regras determinísticas)**
   - filtros: setores, liquidez mínima, histórico mínimo
   - métricas: DY atual/projetado, DPA médio (ex: 5 anos), payout, estabilidade
   - calcula preço-teto: $\text{Preço-Teto} = \frac{\text{DPA médio}}{\text{DY alvo}}$
   - gera ranking e status:
     - “Abaixo do preço-teto: SIM/NÃO”
     - “margem até o teto”
     - “qualidade de histórico de proventos”
4. **Camada de explicação (IA)**
   - recebe somente resultados + fontes + trechos
   - produz texto leigo (“por que entrou”, “quais riscos”, “o que observar”)
   - RAG: linka de volta para CVM/RI quando citar fatos
5. **Produto/UX**
   - 1 clique: “ver empresas abaixo do preço-teto hoje”
   - simulação de renda (reinvestimento)
   - alertas: “entrou abaixo do teto”, “subiu acima do teto”

#### 4) Fontes de dados: como pensar

Separar em:

- **Fonte oficial (verdade contábil):** CVM + RI (para auditoria e confiança)
- **Agregadores (praticidade):** para acelerar MVP com dados “limpos”
- **Market data (preço):** provedor com estabilidade/limites claros

Estratégia recomendada para MVP:

- Usar 1 agregador para fundamentos/proventos (para não construir ETL pesado no dia 1)
- Usar 1 API para preço
- Paralelamente, começar a montar seu Data Lake com o que for crítico (proventos + ajustes)

#### 5) Recorte de MVP (o que fazer primeiro)

Para lançar rápido e correto para “leigo absoluto”:

- Universo: ~50–100 ativos (ex: setores “perenes” + liquidez mínima).
- Parâmetros fixos e transparentes:
  - DY alvo = 6% (editável)
  - DPA médio = 5 anos (editável)
- Tela ranking:
  - preço atual
  - preço-teto
  - % abaixo/acima do teto
  - “consistência de dividendos” (score simples)
- Explicação em português simples + links de fonte.

---

## 6. Setup prático e estado atual do repo

**Estado atual (no repositório local):**

- O repositório `barsiparaleigos-cloud/barsi01` está conectado ao Supabase via Supabase CLI.
- Existe workflow de GitHub Actions para execução diária.
- Os scripts de jobs são um MVP inicial e podem começar com dados mock e evoluir para uma fonte real.
- O frontend do produto está em `webapp/` (React + Vite) baseado no design do Figma.
- O backend local expõe uma API simples em Python (ex.: `GET /api/stocks`) para o `webapp/` consumir via proxy.

> **Nota:** Qualquer passo que envolva segredos deve ser feito via `.env.local` (local) e GitHub Secrets (CI).

### Execução local (mínimo para ver o produto funcionando)

1) Rodar jobs (popular dados no Supabase)

- `python -m jobs.sync_prices`
- `python -m jobs.sync_dividends`
- `python -m jobs.compute_signals`

2) Subir backend (API)

- `python -m web.home_server`

3) Subir frontend (webapp)

- `cd webapp`
- `npm install`
- `npm run dev`

---

## 7. Próximos passos (plano direto e sustentável)

### A) Dados (confiabilidade)

- **Normalizar dividendos/JCP e ajustes (splits/grupamentos)**: sem isso, o DPA histórico pode ficar errado.
- **Garantir consistência do universo (assets)**: definir quais tickers entram e por quê (BESST + liquidez mínima).
- **Separar “fonte de preço” e “fonte de proventos”**: preço pode ser diário; proventos/fundamentos podem ser atualizados em lote.

### B) Motor (determinístico e auditável)

- Consolidar o cálculo do preço-teto como regra central e deixar parâmetros explícitos (DY alvo, janela de DPA, etc.).
- Gerar ranking e “vereditos” com regras claras e reproduzíveis (sem IA tomando decisão).

### C) Produto/UX (leigo absoluto)

- Manter a recomendação em linguagem simples ("PODE COMPRAR / ESPERE / SEM DADOS") e sempre mostrar o “por quê”.
- Evoluir a tela de detalhes para usar dados reais (histórico de preço/dividendos hoje ainda é mock no modal).

### D) Deploy (sem dor)

- **Dev**: Vite com proxy `/api` → backend Python local.
- **Prod** (opção simples): build do `webapp/` (estático) + API Python rodando separada (ex.: container/VM). Alternativas (Vercel/Cloudflare) dependem de onde a API vai rodar.

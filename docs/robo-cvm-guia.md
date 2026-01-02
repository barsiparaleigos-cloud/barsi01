# 🤖 Robô de Integração CVM - Guia Rápido

## 🎯 O que é?

Robô automatizado que baixa e processa dados oficiais da **CVM (Comissão de Valores Mobiliários)** para o projeto Dividendos para leigos.

## 🔓 Dados Abertos - Sem Login!

- ✅ **Totalmente gratuito** - sem custo algum
- ✅ **Sem API key** - não precisa cadastro
- ✅ **Sem autenticação** - acesso direto via HTTP
- ✅ **Dados oficiais** - fonte reguladora do mercado
- ✅ **Atualizações automáticas** - CVM atualiza semanalmente

## 📦 O que o robô baixa?

### 1. Cadastro de Empresas (Diário)
- CNPJ, razão social, código CVM
- Setor de atividade
- Situação do registro

### 2. Demonstrações Financeiras (Semanal)
- **DFP** (Demonstração Financeira Padronizada - Anual)
- **ITR** (Informações Trimestrais)
- DRE, BPP, BPA, Fluxo de Caixa, etc.

### 3. Dados para Metodologia de Dividendos
- 💰 **Dividendos pagos** (da DRE)
- 📊 **Patrimônio Líquido** (do BPP)
- 📈 **Lucros** (da DRE)
- 🏢 **Setores BESST** (do Formulário de Referência)

## 🚀 Como usar?

### 1️⃣ Testar a integração (primeira vez)

```powershell
# Instalar dependências (se necessário)
pip install requests pandas

# Executar teste
python scripts/test_cvm.py
```

O teste vai:
- ✅ Verificar conexão com CVM
- ✅ Baixar cadastro de empresas (~500KB)
- ✅ Perguntar se quer baixar DFP completo (~50-200MB)
- ✅ Processar dividendos e patrimônio líquido
- ✅ Mostrar top 5 pagadoras de dividendos

### 2️⃣ Executar sincronização completa

```powershell
# Baixar todos os dados e salvar localmente
python -m jobs.sync_cvm
```

Isso vai:
1. Baixar cadastro atualizado
2. Baixar DFP do último ano disponível
3. Extrair dividendos de todas as empresas
4. Extrair patrimônio líquido
5. Salvar tudo em `data/processed/`

### 3️⃣ Automatizar (executar periodicamente)

**Opção A: Manualmente quando quiser**
```powershell
python -m jobs.sync_cvm
```

**Opção B: Agendar no Windows (Task Scheduler)**
```powershell
# Criar tarefa que executa toda segunda-feira às 9h
$action = New-ScheduledTaskAction -Execute "python" -Argument "-m jobs.sync_cvm" -WorkingDirectory "C:\caminho\do\projeto"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 9am
Register-ScheduledTask -TaskName "SyncCVM" -Action $action -Trigger $trigger
```

**Opção C: Via cron (Linux/Mac)**
```bash
# Toda segunda às 9h
0 9 * * 1 cd /caminho/projeto && python -m jobs.sync_cvm
```

## 📁 Onde ficam os dados?

```
barsi01/
├── data/
│   ├── cvm/                    # Cache dos arquivos brutos
│   │   ├── cadastro_20260102.csv
│   │   └── dfp_2024.zip
│   │
│   └── processed/              # Dados processados (JSON)
│       ├── cvm_cadastro.json
│       ├── cvm_dividendos_2024.json
│       ├── cvm_patrimonio_2024.json
│       └── cvm_sync_report.json
```

## 🔧 Configuração no painel

No frontend (Admin → Integrações → CVM):

```json
{
  "enabled": true,
  "baseUrl": "https://dados.cvm.gov.br/dados",
  "autoSync": true,
  "syncSchedule": "weekly",
  "lastSync": "2026-01-02T10:30:00Z"
}
```

## 📊 Exemplo de dados extraídos

### Dividendos (cvm_dividendos_2024.json)
```json
[
  {
    "CNPJ_CIA": "33000118000179",
    "DENOM_CIA": "PETROBRAS",
    "DT_REFER": "2024-12-31",
    "PROVENTOS_TOTAL": 54321000
  }
]
```

### Patrimônio (cvm_patrimonio_2024.json)
```json
[
  {
    "CNPJ_CIA": "33000118000179",
    "DENOM_CIA": "PETROBRAS",
    "DT_REFER": "2024-12-31",
    "PATRIMONIO_LIQUIDO": 456789000
  }
]
```

## ⚙️ Personalização

### Baixar outro ano
```python
from integrations.cvm_integration import CVMIntegration

cvm = CVMIntegration()
demonstracoes = cvm.download_dfp(2023)  # Ano específico
```

### Extrair apenas dividendos
```python
df_dre = demonstracoes['DRE']
dividendos = cvm.extrair_dividendos(df_dre)
```

### Processar ITR (trimestral) ao invés de DFP
```python
# Modificar URL em cvm_integration.py
url = f"{self.BASE_URL}/CIA_ABERTA/DOC/ITR/DADOS/itr_cia_aberta_{year}.zip"
```

## 🎯 Métricas disponíveis

Com os dados da CVM, você pode calcular:

### 1. Dividend Yield Real
```python
DY = (Dividendos Pagos / Preço da Ação) × 100
```

### 2. Preço Teto
```python
VPA = Patrimônio Líquido / Número de Ações
Preço Teto = 1.5 × VPA
```

### 3. Payout Ratio
```python
Payout = (Dividendos / Lucro Líquido) × 100
```

### 4. ROE (Return on Equity)
```python
ROE = (Lucro Líquido / Patrimônio Líquido) × 100
```

## ⚠️ Limitações conhecidas

1. **Não tem cotações**: Precisa combinar com Brapi/B3 para preços atuais
2. **CNPJ ≠ Ticker**: Precisa mapear CNPJ → ticker manualmente ou via API
3. **Arquivos grandes**: DFP completo pode ter 200MB
4. **Prazo de entrega**: DFP só disponível após 31/03 do ano seguinte
5. **Encoding**: Arquivos CSV em Latin1, separador `;`

## 🔗 Links úteis

- **Portal CVM**: https://dados.cvm.gov.br/
- **Documentação**: Ver `docs/integracao-cvm.md`
- **API Docs**: http://docs.ckan.org/en/2.11/api/
- **Novidades**: https://dados.cvm.gov.br/pages/novidades

## 🐛 Troubleshooting

### Erro: "Arquivo ZIP corrompido"
```powershell
# Limpar cache e tentar novamente
Remove-Item data/cvm/*.zip
python -m jobs.sync_cvm
```

### Erro: "DFP não disponível"
```
# DFP do ano atual pode não estar disponível ainda
# Prazo: até 31/03 do ano seguinte
# O robô tentará automaticamente o ano anterior
```

### Erro: "Connection timeout"
```powershell
# Arquivo muito grande, aumentar timeout
# Editar cvm_integration.py linha 100:
response = requests.get(url, timeout=600)  # 10 min
```

### Erro de memória
```powershell
# Processar demonstrações individualmente
# Ao invés de carregar todas de uma vez
```

## 📝 TODO / Melhorias futuras

- [ ] Mapear CNPJ → Ticker automaticamente (via Brapi)
- [ ] Baixar ITR (trimestral) além de DFP
- [ ] Cache inteligente (não baixar se já atualizado)
- [ ] Processar em streaming (arquivos muito grandes)
- [ ] API local para consultar dados processados
- [ ] Dashboard de monitoramento de sync
- [ ] Alertas quando novos dados disponíveis

## 💡 Dicas

1. **Primeira execução**: Execute fora de horário de pico (arquivos grandes)
2. **Frequência**: Semanal é suficiente (CVM atualiza semanalmente)
3. **Storage**: Reserve ~500MB para cache completo
4. **Performance**: Use SSD se possível (processamento intensivo)

---

**Criado em**: Janeiro 2026  
**Versão**: 1.0  
**Licença dos dados**: ODbL (CVM)  
**Status**: ✅ Totalmente funcional

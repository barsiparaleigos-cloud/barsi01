# Integração CVM - Documentação Completa

## 📌 Visão Geral

A CVM (Comissão de Valores Mobiliários) oferece um **Portal de Dados Abertos** completo com acesso gratuito a informações de companhias abertas, fundos, dividendos e demonstrações financeiras.

- **URL Base**: https://dados.cvm.gov.br/
- **Licença**: ODbL (Open Database License) - Dados Abertos
- **Formato**: CSV, TXT, ZIP
- **Atualização**: Diária (cadastros) e Semanal (documentos)
- **API**: CKAN API v3 disponível

## 🔗 Principais Endpoints

### 1. Cadastro de Companhias Abertas
**Dataset**: `cia_aberta-cad`
- **URL**: https://dados.cvm.gov.br/dataset/cia_aberta-cad
- **Formato**: CSV
- **Atualização**: Diária
- **Dados**: CNPJ, razão social, data de registro, situação, setor

**Arquivo direto**:
```
https://dados.cvm.gov.br/dataset/cia_aberta-cad/resource/2391143f-1423-48a5-9f6a-423245aca362
```

**Repositório de arquivos**:
```
https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/
```

### 2. Demonstrações Financeiras Padronizadas (DFP)
**Dataset**: `cia_aberta-doc-dfp`
- **URL**: https://dados.cvm.gov.br/dataset/cia_aberta-doc-dfp
- **Formato**: ZIP (contém CSVs)
- **Atualização**: Semanal
- **Período**: Últimos 5 anos + histórico desde 2010

**Demonstrações incluídas**:
- ✅ Balanço Patrimonial Ativo (BPA)
- ✅ Balanço Patrimonial Passivo (BPP)
- ✅ Demonstração de Resultado (DRE) - **IMPORTANTE PARA DIVIDENDOS**
- ✅ Demonstração de Fluxo de Caixa (DFC)
- ✅ Demonstração das Mutações do Patrimônio Líquido (DMPL)
- ✅ Demonstração de Resultado Abrangente (DRA)
- ✅ Demonstração de Valor Adicionado (DVA)

**Repositório de arquivos**:
```
https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/
```

### 3. Informações Trimestrais (ITR)
**Dataset**: `cia_aberta-doc-itr`
- **URL**: https://dados.cvm.gov.br/dataset/cia_aberta-doc-itr
- **Formato**: ZIP (contém CSVs)
- **Periodicidade**: Trimestral
- **Mesmas demonstrações do DFP**

**Repositório de arquivos**:
```
https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/DADOS/
```

### 4. Formulário de Referência (FRE)
**Dataset**: `cia_aberta-doc-fre`
- **URL**: https://dados.cvm.gov.br/dataset/cia_aberta-doc-fre
- **Informações**: Estrutura acionária, administração, negócios, fatores de risco
- **Útil para**: Identificar setores BESST, governança corporativa

### 5. Formulário Cadastral (FCA)
**Dataset**: `cia_aberta-doc-fca`
- **URL**: https://dados.cvm.gov.br/dataset/cia_aberta-doc-fca
- **Informações**: Dados cadastrais detalhados, valores mobiliários emitidos

## 📊 Como Obter Dados de Dividendos

### Opção 1: Demonstração de Resultado (DRE)
A DRE contém a linha **"Dividendos e JCP"** que mostra os proventos distribuídos:

```
Arquivo: dfp_cia_aberta_DRE_con_YYYY.csv
Campos relevantes:
- CNPJ_CIA
- DT_REFER (data de referência)
- CD_CONTA (código da conta contábil)
- DS_CONTA (descrição - procurar "Dividendos" ou "JCP")
- VL_CONTA (valor distribuído)
```

### Opção 2: Demonstração das Mutações do PL (DMPL)
A DMPL mostra a movimentação de dividendos e JCP:

```
Arquivo: dfp_cia_aberta_DMPL_con_YYYY.csv
Campos relevantes:
- CNPJ_CIA
- DT_REFER
- CD_CONTA
- DS_CONTA (procurar "Dividendos" ou "Juros sobre Capital Próprio")
- COLUNA_DF (tipo de coluna)
- VL_CONTA
```

## 🔧 Estrutura dos Arquivos

### Padrão de Nomenclatura
```
{tipo_doc}_cia_aberta_{demonstracao}_{consolidacao}_{ano}.csv

Exemplos:
- dfp_cia_aberta_DRE_con_2024.csv  (DFP, DRE, Consolidado, 2024)
- itr_cia_aberta_BPA_ind_2024.csv  (ITR, BPA, Individual, 2024)
```

### Campos Comuns
```csv
CNPJ_CIA,DT_REFER,VERSAO,DENOM_CIA,CD_CVM,GRUPO_DFP,MOEDA,ESCALA_MOEDA,
ORDEM_EXERC,DT_FIM_EXERC,CD_CONTA,DS_CONTA,VL_CONTA
```

## 🚀 Implementação Sugerida

### 1. Download Inicial
```python
import requests
import zipfile
import pandas as pd
from io import BytesIO

def download_cvm_data(year: int):
    """
    Baixa dados DFP do ano especificado
    """
    url = f"https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_{year}.zip"
    
    response = requests.get(url)
    response.raise_for_status()
    
    # Extrair ZIP em memória
    with zipfile.ZipFile(BytesIO(response.content)) as z:
        # Ler DRE (para dividendos)
        with z.open(f'dfp_cia_aberta_DRE_con_{year}.csv', encoding='latin1') as f:
            df_dre = pd.read_csv(f, sep=';', decimal=',')
        
        return df_dre

# Uso
df = download_cvm_data(2024)
```

### 2. Extrair Dividendos
```python
def extract_dividends(df_dre):
    """
    Extrai informações de dividendos da DRE
    """
    # Filtrar contas relacionadas a dividendos
    dividends = df_dre[
        df_dre['DS_CONTA'].str.contains('Dividendo|JCP|Juros sobre', case=False, na=False)
    ]
    
    # Agrupar por empresa
    result = dividends.groupby(['CNPJ_CIA', 'DENOM_CIA']).agg({
        'VL_CONTA': 'sum',
        'DT_REFER': 'first'
    }).reset_index()
    
    return result
```

### 3. Relacionar com Cotações
```python
def map_cnpj_to_ticker():
    """
    Relaciona CNPJ da CVM com ticker da B3
    Pode usar API Brapi para crosscheck
    """
    # Download cadastro
    url = "https://dados.cvm.gov.br/dataset/cia_aberta-cad/resource/2391143f-1423-48a5-9f6a-423245aca362/download/cad_cia_aberta.csv"
    df = pd.read_csv(url, sep=';', encoding='latin1')
    
    # Retornar mapeamento
    return df[['CNPJ_CIA', 'DENOM_SOCIAL', 'CD_CVM']]
```

## 📋 Campos Importantes

### Cadastro de Companhias
```
CNPJ_CIA: CNPJ da empresa
DENOM_SOCIAL: Razão social
DENOM_COMERC: Nome fantasia
CD_CVM: Código CVM
DT_REG: Data de registro
DT_CANCEL: Data de cancelamento (se aplicável)
SIT: Situação (ATIVO, CANCELADA, etc)
DT_INI_SIT: Data início situação
SETOR_ATIV: Setor de atividade
```

### Demonstrações Financeiras
```
CNPJ_CIA: CNPJ da empresa
DT_REFER: Data de referência (31/12/YYYY para DFP)
VERSAO: Versão do documento (1, 2, 3...)
CD_CONTA: Código da conta contábil
DS_CONTA: Descrição da conta
VL_CONTA: Valor (em milhares, geralmente)
ESCALA_MOEDA: MIL, MILHAO, etc
ST_CONTA_FIXA: S/N (se é conta do elenco fixo)
```

## 🎯 Dados Específicos para Metodologia de Dividendos

### Dividend Yield
1. **Dividendos pagos**: DRE → Conta "Dividendos e JCP"
2. **Lucro líquido**: DRE → Conta "Lucro/Prejuízo do Período"
3. **Patrimônio líquido**: BPP → Conta "Patrimônio Líquido"
4. **Número de ações**: FCA → Valores Mobiliários

### Preço Teto (P/VPA)
1. **Valor Patrimonial**: BPP → Patrimônio Líquido
2. **Número de ações**: FCA
3. **VPA = PL / Número de ações**
4. **Preço teto = 1.5 × VPA** (metodologia de dividendos)

### Setores BESST
**Formulário de Referência (FRE)** → Seção "Descrição das Atividades":
- Bancos
- Energia
- Saneamento
- Seguros
- Telecomunicações

## 🔄 Periodicidade de Atualização

| Tipo de Dado | Frequência | Prazo de Entrega |
|--------------|------------|------------------|
| Cadastro | Diária | Tempo real |
| DFP (anual) | Anual | Até 31/03 do ano seguinte |
| ITR (trimestral) | Trimestral | Até 45 dias após trimestre |
| FRE | Anual | Até 31/05 do ano seguinte |
| FCA | Eventual | Quando há mudanças |

## ⚠️ Considerações Importantes

### Qualidade dos Dados
- ✅ **Oficial**: Dados oficiais enviados pelas empresas à CVM
- ✅ **Auditado**: Demonstrações financeiras são auditadas
- ⚠️ **Reapresentações**: Empresas podem reenviar (campo VERSAO)
- ⚠️ **Formato**: Encoding Latin1, separador `;`, decimal `,`

### Limitações
- ❌ **Não tem cotações**: Precisa complementar com Brapi/B3
- ❌ **Não tem histórico de dividendos individual**: Só valor total anual
- ❌ **CNPJ ≠ Ticker**: Precisa mapear manualmente ou via outra API
- ⚠️ **Tamanho dos arquivos**: ZIPs podem ter 50-200MB

### Vantagens
- ✅ **Gratuito e aberto**: Sem limitação de chamadas
- ✅ **Confiável**: Fonte oficial do regulador
- ✅ **Completo**: Todas as companhias abertas
- ✅ **Histórico**: Dados desde 2010

## 🔗 Links Úteis

- **Portal**: https://dados.cvm.gov.br/
- **API Docs**: http://docs.ckan.org/en/2.11/api/
- **Repositório FTP**: https://dados.cvm.gov.br/dados/
- **Novidades**: https://dados.cvm.gov.br/pages/novidades
- **Gov.br/CVM**: https://www.gov.br/cvm/

## 💡 Próximos Passos

1. ✅ Implementar download de cadastro de empresas
2. ✅ Implementar download de DFP (DRE + BPP)
3. ✅ Extrair dividendos e patrimônio líquido
4. ✅ Mapear CNPJ → Ticker (via Brapi)
5. ✅ Calcular Dividend Yield e Preço Teto
6. ✅ Armazenar no banco local (SQLite/JSON)
7. ✅ Sincronizar periodicamente

## 📝 Exemplo de Integração Completa

```python
# 1. Baixar cadastro
cadastro_url = "https://dados.cvm.gov.br/dataset/cia_aberta-cad/resource/2391143f-1423-48a5-9f6a-423245aca362/download/cad_cia_aberta.csv"

# 2. Baixar DFP do ano
dfp_url = f"https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_{year}.zip"

# 3. Extrair arquivos do ZIP:
#    - dfp_cia_aberta_DRE_con_{year}.csv (dividendos)
#    - dfp_cia_aberta_BPP_con_{year}.csv (patrimônio)
#    - dfp_cia_aberta_DFP_{year}.csv (geral)

# 4. Processar dividendos
# 5. Mapear para tickers via Brapi
# 6. Calcular métricas da metodologia
# 7. Salvar localmente
```

---

**Data**: Janeiro 2026  
**Fonte**: Portal Dados Abertos CVM  
**Licença dos dados**: ODbL (Open Database License)

"""
Integração CVM - Dados Abertos
Baixa e processa dados oficiais da Comissão de Valores Mobiliários
Sem necessidade de API key - dados públicos via HTTP
"""

import requests
import zipfile
import pandas as pd
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class CVMIntegration:
    """
    Integração com Portal de Dados Abertos da CVM
    Documentação: https://dados.cvm.gov.br/
    """
    
    BASE_URL = "https://dados.cvm.gov.br/dados"
    CADASTRO_URL = "https://dados.cvm.gov.br/dataset/cia_aberta-cad/resource/2391143f-1423-48a5-9f6a-423245aca362/download/cad_cia_aberta.csv"
    
    def __init__(self, cache_dir: str = "data/cvm"):
        """
        Inicializa integração CVM
        
        Args:
            cache_dir: Diretório para cache local dos dados
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def download_cadastro_empresas(self) -> pd.DataFrame:
        """
        Baixa cadastro atualizado de companhias abertas
        Atualização: Diária
        
        Returns:
            DataFrame com dados cadastrais (CNPJ, razão social, código CVM, setor)
        """
        logger.info("Baixando cadastro de companhias abertas da CVM...")
        
        try:
            # Baixar CSV diretamente
            df = pd.read_csv(
                self.CADASTRO_URL,
                sep=';',
                encoding='latin1',
                dtype=str  # Manter CNPJ como string
            )
            
            logger.info(f"✅ Cadastro baixado: {len(df)} empresas")
            
            # Salvar cache local
            cache_file = self.cache_dir / f"cadastro_{datetime.now().strftime('%Y%m%d')}.csv"
            df.to_csv(cache_file, index=False, sep=';', encoding='utf-8')
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Erro ao baixar cadastro: {e}")
            raise
    
    def download_dfp(self, year: int) -> Dict[str, pd.DataFrame]:
        """
        Baixa Demonstrações Financeiras Padronizadas (DFP) de um ano
        Atualização: Anual (prazo: até 31/03 do ano seguinte)
        
        Args:
            year: Ano fiscal (ex: 2024)
            
        Returns:
            Dicionário com DataFrames das demonstrações:
            - 'DRE': Demonstração de Resultado (dividendos)
            - 'BPP': Balanço Patrimonial Passivo (patrimônio líquido)
            - 'BPA': Balanço Patrimonial Ativo
            - 'DFC_MD': Demonstração Fluxo Caixa - Método Direto
            - 'DFC_MI': Demonstração Fluxo Caixa - Método Indireto
            - 'DMPL': Demonstração Mutações PL
            - 'DVA': Demonstração Valor Adicionado
        """
        logger.info(f"Baixando DFP {year} da CVM...")
        
        # URL do arquivo ZIP
        url = f"{self.BASE_URL}/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_{year}.zip"

        # Cache local (DFP é anual e não muda frequentemente)
        cache_file = self.cache_dir / f"dfp_{year}.zip"
        
        try:
            content: bytes
            if cache_file.exists() and cache_file.stat().st_size > 0:
                logger.info(f"Usando cache local do DFP: {cache_file}")
                content = cache_file.read_bytes()
            else:
                # Download do ZIP
                response = requests.get(url, timeout=300)  # 5 min timeout (arquivo grande)
                response.raise_for_status()
                content = response.content
                logger.info(f"✅ ZIP baixado: {len(content) / 1024 / 1024:.1f} MB")
            
            # Extrair arquivos do ZIP em memória
            demonstracoes = {}
            
            with zipfile.ZipFile(BytesIO(content)) as z:
                # Listar arquivos disponíveis
                available_files = z.namelist()
                logger.info(f"Arquivos no ZIP: {len(available_files)}")
                
                # Demonstrações que queremos extrair
                docs = {
                    'DRE': 'DRE_con',  # Consolidado
                    'BPP': 'BPP_con',
                    'BPA': 'BPA_con',
                    'DFC_MD': 'DFC_MD_con',
                    'DFC_MI': 'DFC_MI_con',
                    'DMPL': 'DMPL_con',
                    'DVA': 'DVA_con'
                }
                
                for doc_name, file_prefix in docs.items():
                    filename = f'dfp_cia_aberta_{file_prefix}_{year}.csv'
                    
                    if filename in available_files:
                        try:
                            logger.info(f"Extraindo {filename}...")
                            with z.open(filename) as f:
                                df = pd.read_csv(
                                    f,
                                    sep=';',
                                    encoding='latin1',
                                    decimal=',',
                                    thousands='.',
                                    dtype={'CNPJ_CIA': str}  # CNPJ como string
                                )
                                demonstracoes[doc_name] = df
                                logger.info(f"  ✅ {doc_name}: {len(df)} linhas")
                                
                        except Exception as e:
                            logger.warning(f"  ⚠️ Erro ao extrair {doc_name}: {e}")
                    else:
                        logger.warning(f"  ⚠️ {filename} não encontrado no ZIP")
            
            # Salvar cache local
            if not (cache_file.exists() and cache_file.stat().st_size > 0):
                with open(cache_file, 'wb') as f:
                    f.write(content)
            
            logger.info(f"✅ DFP {year} processado: {len(demonstracoes)} demonstrações")
            return demonstracoes
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erro ao baixar DFP {year}: {e}")
            raise
        except zipfile.BadZipFile as e:
            logger.error(f"❌ Arquivo ZIP corrompido: {e}")
            raise
    
    def extrair_dividendos(self, df_dre: pd.DataFrame) -> pd.DataFrame:
        """
        Extrai informações de dividendos da DRE
        
        Args:
            df_dre: DataFrame da Demonstração de Resultado
            
        Returns:
            DataFrame com colunas:
            - CNPJ_CIA
            - DENOM_CIA (razão social)
            - DT_REFER (data referência)
            - DIVIDENDOS (valor total)
            - JCP (juros sobre capital próprio)
            - PROVENTOS_TOTAL (dividendos + JCP)
        """
        logger.info("Extraindo dividendos da DRE...")
        
        # Filtrar contas relacionadas a dividendos e JCP
        keywords = ['dividendo', 'jcp', 'juros sobre capital']
        
        mask = df_dre['DS_CONTA'].str.lower().str.contains(
            '|'.join(keywords),
            case=False,
            na=False
        )
        
        df_prov = df_dre[mask].copy()
        
        logger.info(f"Linhas com proventos encontradas: {len(df_prov)}")
        
        # Agrupar por empresa e somar valores
        result = df_prov.groupby(['CNPJ_CIA', 'DENOM_CIA', 'DT_REFER']).agg({
            'VL_CONTA': 'sum'
        }).reset_index()
        
        result.rename(columns={'VL_CONTA': 'PROVENTOS_TOTAL'}, inplace=True)
        
        # Converter valores (geralmente em milhares)
        result['PROVENTOS_TOTAL'] = pd.to_numeric(result['PROVENTOS_TOTAL'], errors='coerce')
        
        logger.info(f"✅ Dividendos extraídos para {len(result)} empresas")
        
        return result
    
    def extrair_patrimonio_liquido(self, df_bpp: pd.DataFrame) -> pd.DataFrame:
        """
        Extrai Patrimônio Líquido do Balanço Patrimonial Passivo
        
        Args:
            df_bpp: DataFrame do BPP
            
        Returns:
            DataFrame com colunas:
            - CNPJ_CIA
            - DENOM_CIA
            - DT_REFER
            - PATRIMONIO_LIQUIDO
        """
        logger.info("Extraindo Patrimônio Líquido do BPP...")
        
        # Procurar conta "Patrimônio Líquido"
        mask = df_bpp['DS_CONTA'].str.contains(
            'patrimônio líquido',
            case=False,
            na=False
        )
        
        df_pl = df_bpp[mask].copy()
        
        logger.info(f"Linhas de PL encontradas: {len(df_pl)}")
        
        # Pegar o valor consolidado (última versão)
        result = df_pl.sort_values('VERSAO', ascending=False).groupby(
            ['CNPJ_CIA', 'DENOM_CIA', 'DT_REFER']
        ).first().reset_index()
        
        result = result[['CNPJ_CIA', 'DENOM_CIA', 'DT_REFER', 'VL_CONTA']]
        result.rename(columns={'VL_CONTA': 'PATRIMONIO_LIQUIDO'}, inplace=True)
        
        # Converter valores
        result['PATRIMONIO_LIQUIDO'] = pd.to_numeric(result['PATRIMONIO_LIQUIDO'], errors='coerce')
        
        logger.info(f"✅ PL extraído para {len(result)} empresas")
        
        return result

    def _extrair_conta_por_keywords(
        self,
        df: pd.DataFrame,
        *,
        keywords: List[str],
        output_col: str,
    ) -> pd.DataFrame:
        """Extrai um valor consolidado por DT_REFER a partir de keywords em DS_CONTA.

        Heurística para evitar dupla contagem:
        - filtra por DS_CONTA via keywords
        - converte VL_CONTA para numérico
        - mantém somente o(s) nível(is) mais agregados via menor profundidade de CD_CONTA
          (menos subníveis separados por '.')
        - soma os valores desse nível agregado por empresa/data
        """

        if df is None or len(df) == 0:
            return pd.DataFrame(columns=["CNPJ_CIA", "DENOM_CIA", "DT_REFER", output_col])

        pattern = "|".join(re.escape(k) for k in keywords if k)
        if not pattern:
            return pd.DataFrame(columns=["CNPJ_CIA", "DENOM_CIA", "DT_REFER", output_col])

        mask = df["DS_CONTA"].astype(str).str.lower().str.contains(pattern, case=False, na=False)
        d = df[mask].copy()
        if len(d) == 0:
            return pd.DataFrame(columns=["CNPJ_CIA", "DENOM_CIA", "DT_REFER", output_col])

        d["VL_CONTA"] = pd.to_numeric(d["VL_CONTA"], errors="coerce")
        d = d.dropna(subset=["VL_CONTA"])
        if len(d) == 0:
            return pd.DataFrame(columns=["CNPJ_CIA", "DENOM_CIA", "DT_REFER", output_col])

        # Profundidade de CD_CONTA (quanto menor, mais agregado)
        cd = d.get("CD_CONTA")
        if cd is not None:
            d["CD_CONTA"] = d["CD_CONTA"].astype(str)
            d["__depth"] = d["CD_CONTA"].str.count(r"\.")
            min_depth = d.groupby(["CNPJ_CIA", "DT_REFER"])["__depth"].transform("min")
            d = d[d["__depth"] == min_depth]

        result = (
            d.groupby(["CNPJ_CIA", "DENOM_CIA", "DT_REFER"], as_index=False)["VL_CONTA"]
            .sum()
            .rename(columns={"VL_CONTA": output_col})
        )
        result[output_col] = pd.to_numeric(result[output_col], errors="coerce")
        return result

    def extrair_divida_bruta(self, df_bpp: pd.DataFrame) -> pd.DataFrame:
        """Extrai dívida bruta (heurística) do BPP consolidado.

        Retorna colunas:
        - CNPJ_CIA, DENOM_CIA, DT_REFER, DIVIDA_BRUTA
        """
        logger.info("Extraindo Dívida Bruta (heurística) do BPP...")

        # Cobertura ampla (Português). A heurística tenta pegar linhas agregadas.
        keywords = [
            "emprést",
            "emprest",
            "financi",
            "debênt",
            "debent",
            "arrend",
            "leasing",
            "capta",
        ]

        result = self._extrair_conta_por_keywords(
            df_bpp,
            keywords=keywords,
            output_col="DIVIDA_BRUTA",
        )

        logger.info(f"✅ Dívida bruta extraída para {len(result)} empresas")
        return result

    def extrair_caixa_equivalentes(self, df_bpa: pd.DataFrame) -> pd.DataFrame:
        """Extrai Caixa e Equivalentes (heurística) do BPA consolidado.

        Retorna colunas:
        - CNPJ_CIA, DENOM_CIA, DT_REFER, CAIXA_EQUIVALENTES
        """
        logger.info("Extraindo Caixa e Equivalentes (heurística) do BPA...")

        keywords = [
            "caixa",
            "equivalentes",
            "equivalente",
        ]

        result = self._extrair_conta_por_keywords(
            df_bpa,
            keywords=keywords,
            output_col="CAIXA_EQUIVALENTES",
        )

        logger.info(f"✅ Caixa/equivalentes extraídos para {len(result)} empresas")
        return result
    
    def calcular_metricas_dividendos(
        self,
        dividendos: pd.DataFrame,
        patrimonio: pd.DataFrame,
        cotacoes: Dict[str, float],
        acoes_em_circulacao: Dict[str, int]
    ) -> pd.DataFrame:
        """
        Calcula métricas da metodologia de dividendos
        
        Args:
            dividendos: DataFrame com dividendos
            patrimonio: DataFrame com patrimônio líquido
            cotacoes: Dict {ticker: preço_atual}
            acoes_em_circulacao: Dict {ticker: quantidade_acoes}
            
        Returns:
            DataFrame com métricas:
            - DIVIDEND_YIELD
            - VPA (Valor Patrimonial por Ação)
            - PRECO_TETO (1.5 × VPA)
            - ABAIXO_DO_TETO (bool)
            - MARGEM_SEGURANCA (%)
        """
        logger.info("Calculando métricas da metodologia...")
        
        # Merge dividendos + patrimônio
        df = dividendos.merge(
            patrimonio,
            on=['CNPJ_CIA', 'DENOM_CIA', 'DT_REFER'],
            how='inner'
        )
        
        # TODO: Mapear CNPJ → Ticker (via Brapi ou tabela local)
        # Por enquanto, retornar com CNPJ
        
        logger.info(f"✅ Métricas calculadas para {len(df)} empresas")
        
        return df
    
    def mapear_cnpj_para_ticker(self, cnpj: str) -> Optional[str]:
        """
        Mapeia CNPJ da CVM para ticker da B3
        
        Args:
            cnpj: CNPJ da empresa (com ou sem formatação)
            
        Returns:
            Ticker da B3 (ex: 'PETR4') ou None se não encontrado
        """
        # TODO: Implementar mapeamento
        # Opções:
        # 1. Tabela local manual (principais empresas)
        # 2. Crosscheck com API Brapi (buscar por nome)
        # 3. API B3 (se disponível)
        
        return None
    
    def test_connection(self) -> Dict[str, any]:
        """
        Testa conexão com portal CVM
        
        Returns:
            Dict com status e informações
        """
        try:
            # Testar download do cadastro (arquivo pequeno)
            response = requests.head(self.CADASTRO_URL, timeout=10)
            response.raise_for_status()
            
            return {
                'status': 'success',
                'message': 'Conexão com CVM OK',
                'base_url': self.BASE_URL,
                'data_source': 'Portal Dados Abertos CVM',
                'requires_auth': False,
                'cost': 'Gratuito',
                'update_frequency': 'Diária (cadastro) / Semanal (demonstrações)'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Erro ao conectar com CVM: {str(e)}'
            }


def main():
    """
    Teste da integração CVM
    """
    logging.basicConfig(level=logging.INFO)
    
    cvm = CVMIntegration()
    
    # 1. Testar conexão
    print("\n=== Testando Conexão CVM ===")
    status = cvm.test_connection()
    print(f"Status: {status['status']}")
    print(f"Message: {status['message']}")
    
    # 2. Baixar cadastro
    print("\n=== Baixando Cadastro ===")
    df_cadastro = cvm.download_cadastro_empresas()
    print(f"Total de empresas: {len(df_cadastro)}")
    print(f"Colunas: {list(df_cadastro.columns)}")
    print(f"\nAmostra:")
    print(df_cadastro.head())
    
    # 3. Baixar DFP (ano mais recente disponível)
    print("\n=== Baixando DFP 2024 ===")
    demonstracoes = cvm.download_dfp(2024)
    
    # 4. Extrair dividendos
    if 'DRE' in demonstracoes:
        print("\n=== Extraindo Dividendos ===")
        dividendos = cvm.extrair_dividendos(demonstracoes['DRE'])
        print(f"Empresas com dividendos: {len(dividendos)}")
        print(dividendos.head())
    
    # 5. Extrair PL
    if 'BPP' in demonstracoes:
        print("\n=== Extraindo Patrimônio Líquido ===")
        pl = cvm.extrair_patrimonio_liquido(demonstracoes['BPP'])
        print(f"Empresas com PL: {len(pl)}")
        print(pl.head())


if __name__ == '__main__':
    main()

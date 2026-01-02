"""
Integração Brapi - API Brasileira de Cotações B3
Documentação: https://brapi.dev/docs

Features:
- Cotações em tempo real
- Histórico de preços
- Dados fundamentalistas
- Dividendos
- Sem autenticação para ações de teste (PETR4, MGLU3, VALE3, ITUB4)
- Com token: acesso a +4.000 ações
"""

import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class BrapiIntegration:
    """
    Cliente para API Brapi
    
    Plano Gratuito:
    - 10.000 requests/mês
    - Acesso a +4.000 ações
    - Dados em tempo real
    """
    
    BASE_URL = "https://brapi.dev/api"
    
    # Ações gratuitas (sem token necessário)
    FREE_TICKERS = ['PETR4', 'MGLU3', 'VALE3', 'ITUB4']
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa cliente Brapi
        
        Args:
            api_key: Token de autenticação (opcional para ações de teste)
        """
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}'
            })
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Testa conexão com a API usando ação gratuita
        
        Returns:
            Dict com status da conexão
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/quote/PETR4",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'status': 'success',
                    'message': 'Conexão OK com Brapi',
                    'sample_data': data['results'][0] if data.get('results') else None
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Erro HTTP {response.status_code}',
                    'details': response.text
                }
        
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Erro na conexão: {str(e)}'
            }
    
    def get_quote(
        self, 
        tickers: str | List[str],
        fundamental: bool = False,
        dividends: bool = False,
        modules: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Busca cotações de uma ou mais ações
        
        Args:
            tickers: Ticker único ou lista de tickers (ex: 'PETR4' ou ['PETR4', 'VALE3'])
            fundamental: Incluir dados fundamentalistas
            dividends: Incluir histórico de dividendos
            modules: Módulos adicionais (ex: 'summaryProfile,balanceSheetHistory')
        
        Returns:
            Dict com dados das cotações
        
        Example:
            >>> brapi = BrapiIntegration()
            >>> data = brapi.get_quote('PETR4')
            >>> print(data['results'][0]['regularMarketPrice'])
            38.50
        """
        if isinstance(tickers, list):
            tickers = ','.join(tickers)
        
        params = {}
        if fundamental:
            params['fundamental'] = 'true'
        if dividends:
            params['dividends'] = 'true'
        if modules:
            params['modules'] = modules
        
        try:
            logger.info(f"Buscando cotação: {tickers}")
            
            response = self.session.get(
                f"{self.BASE_URL}/quote/{tickers}",
                params=params,
                timeout=15
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"✅ {len(data.get('results', []))} cotações recebidas")
            return data
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.error("❌ Erro de autenticação. Verifique seu token.")
            elif e.response.status_code == 429:
                logger.error("❌ Limite de requisições excedido. Aguarde ou upgrade seu plano.")
            raise
        
        except Exception as e:
            logger.error(f"❌ Erro ao buscar cotação: {e}")
            raise
    
    def get_quote_list(self, limit: int = 100, sortBy: str = 'name', sortOrder: str = 'asc') -> Dict[str, Any]:
        """
        Lista todas as ações disponíveis
        
        Args:
            limit: Número máximo de resultados (1-200)
            sortBy: Campo de ordenação (name, close, change, volume, market_cap)
            sortOrder: Ordem (asc ou desc)
        
        Returns:
            Dict com lista de ações
        """
        try:
            logger.info(f"Listando ações (limit={limit})")
            
            response = self.session.get(
                f"{self.BASE_URL}/quote/list",
                params={
                    'limit': limit,
                    'sortBy': sortBy,
                    'sortOrder': sortOrder
                },
                timeout=15
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"✅ {len(data.get('stocks', []))} ações listadas")
            return data
        
        except Exception as e:
            logger.error(f"❌ Erro ao listar ações: {e}")
            raise
    
    def get_historical_data(
        self,
        ticker: str,
        range_period: str = '1mo',
        interval: str = '1d'
    ) -> Dict[str, Any]:
        """
        Busca histórico de preços
        
        Args:
            ticker: Ticker da ação (ex: 'PETR4')
            range_period: Período (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Intervalo (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
        Returns:
            Dict com dados históricos
        
        Example:
            >>> brapi = BrapiIntegration()
            >>> data = brapi.get_historical_data('PETR4', range_period='1mo', interval='1d')
            >>> print(len(data['results'][0]['historicalDataPrice']))
            22  # ~22 dias úteis no mês
        """
        try:
            logger.info(f"Buscando histórico: {ticker} ({range_period}, {interval})")
            
            response = self.session.get(
                f"{self.BASE_URL}/quote/{ticker}",
                params={
                    'range': range_period,
                    'interval': interval
                },
                timeout=20
            )
            
            response.raise_for_status()
            data = response.json()
            
            historical = data['results'][0].get('historicalDataPrice', [])
            logger.info(f"✅ {len(historical)} pontos históricos recebidos")
            
            return data
        
        except Exception as e:
            logger.error(f"❌ Erro ao buscar histórico: {e}")
            raise
    
    def parse_quote_to_dict(self, quote_data: Dict) -> Dict[str, Any]:
        """
        Converte resposta da API para formato do banco de dados
        
        Args:
            quote_data: Dados de cotação da API
        
        Returns:
            Dict formatado para insert no banco
        """
        return {
            'ticker': quote_data.get('symbol'),
            'nome': quote_data.get('shortName'),
            'nome_completo': quote_data.get('longName'),
            'moeda': quote_data.get('currency', 'BRL'),
            'preco_atual': quote_data.get('regularMarketPrice'),
            'preco_abertura': quote_data.get('regularMarketOpen'),
            'preco_maximo_dia': quote_data.get('regularMarketDayHigh'),
            'preco_minimo_dia': quote_data.get('regularMarketDayLow'),
            'variacao_dia': quote_data.get('regularMarketChange'),
            'variacao_percentual_dia': quote_data.get('regularMarketChangePercent'),
            'volume': quote_data.get('regularMarketVolume'),
            'market_cap': quote_data.get('marketCap'),
            'timestamp': quote_data.get('regularMarketTime'),
            'logo_url': quote_data.get('logourl')
        }
    
    def extract_dividends(self, quote_data: Dict) -> List[Dict[str, Any]]:
        """
        Extrai histórico de dividendos da resposta
        
        Args:
            quote_data: Dados de cotação com dividends=true
        
        Returns:
            Lista de dividendos formatados
        """
        dividends_data = quote_data.get('dividendsData', {})
        cash_dividends = dividends_data.get('cashDividends', [])
        
        result = []
        for div in cash_dividends:
            result.append({
                'ticker': quote_data.get('symbol'),
                'tipo': div.get('type', 'DIVIDEND'),
                'data_aprovacao': div.get('approvedOn'),
                'data_pagamento': div.get('paymentDate'),
                'valor_por_acao': div.get('rate'),
                'moeda': div.get('currency', 'BRL'),
                'fonte': 'brapi'
            })
        
        return result


def main():
    """Teste da integração"""
    print("="*60)
    print("🧪 TESTE DA INTEGRAÇÃO BRAPI")
    print("="*60)
    
    brapi = BrapiIntegration()
    
    # 1. Testar conexão
    print("\n[1/4] Testando conexão...")
    status = brapi.test_connection()
    print(f"Status: {status['status']}")
    print(f"Message: {status['message']}")
    
    if status['status'] != 'success':
        print("\n❌ Falha na conexão. Abortando testes.")
        return
    
    # 2. Buscar cotação simples
    print("\n[2/4] Buscando cotação PETR4...")
    quote = brapi.get_quote('PETR4')
    result = quote['results'][0]
    print(f"  • Ticker: {result['symbol']}")
    print(f"  • Nome: {result['shortName']}")
    print(f"  • Preço: R$ {result['regularMarketPrice']:.2f}")
    print(f"  • Variação: {result['regularMarketChangePercent']:.2f}%")
    
    # 3. Buscar múltiplas ações
    print("\n[3/4] Buscando múltiplas ações (4 gratuitas)...")
    quotes = brapi.get_quote(BrapiIntegration.FREE_TICKERS)
    for stock in quotes['results']:
        print(f"  • {stock['symbol']}: R$ {stock['regularMarketPrice']:.2f}")
    
    # 4. Buscar com dividendos
    print("\n[4/4] Buscando ITUB4 com dividendos...")
    itub = brapi.get_quote('ITUB4', dividends=True)
    result = itub['results'][0]
    dividends = brapi.extract_dividends(result)
    print(f"  • Total de dividendos: {len(dividends)}")
    if dividends:
        last_div = dividends[0]
        print(f"  • Último: R$ {last_div['valor_por_acao']:.4f} em {last_div['data_pagamento']}")
    
    print("\n" + "="*60)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("="*60)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()

"""
Job de Sincronização de Preços
Atualiza cotações diárias das ações brasileiras via Brapi
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import sqlite3
import logging
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from integrations.brapi_integration import BrapiIntegration

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PriceSync:
    """
    Gerenciador de sincronização de preços
    
    Responsabilidades:
    - Buscar cotações atualizadas via Brapi
    - Salvar preços no banco (tabela precos)
    - Atualizar última sincronização
    - Detectar e tratar erros
    """
    
    def __init__(self, db_path: str = "data/barsi.db", api_key: Optional[str] = None):
        self.db_path = Path(db_path)
        self.brapi = BrapiIntegration(api_key)
        self.synced_count = 0
        self.error_count = 0
    
    def get_active_tickers(self) -> List[str]:
        """
        Busca lista de tickers ativos no banco
        
        Returns:
            Lista de tickers (ex: ['PETR4', 'VALE3'])
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT ticker 
            FROM ticker_mapping 
            WHERE ativo = TRUE
            ORDER BY ticker
        """)
        
        tickers = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return tickers
    
    def save_quote(self, ticker: str, quote_data: Dict[str, Any], data: date) -> bool:
        """
        Salva cotação no banco de dados
        
        Args:
            ticker: Código da ação (ex: 'PETR4')
            quote_data: Dados da cotação da Brapi
            data: Data da cotação
        
        Returns:
            True se sucesso, False se erro
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Extrair campos da resposta Brapi
            fechamento = quote_data.get('regularMarketPrice')
            abertura = quote_data.get('regularMarketOpen')
            maxima = quote_data.get('regularMarketDayHigh')
            minima = quote_data.get('regularMarketDayLow')
            volume = quote_data.get('regularMarketVolume')
            market_cap = quote_data.get('marketCap')
            variacao = quote_data.get('regularMarketChangePercent')
            moeda = quote_data.get('currency', 'BRL')
            
            # Validar dados obrigatórios
            if fechamento is None:
                logger.warning(f"⚠️  {ticker}: Preço de fechamento ausente, pulando...")
                return False
            
            # Inserir ou atualizar (UPSERT)
            cursor.execute("""
                INSERT INTO precos (
                    ticker, data, abertura, maxima, minima, 
                    fechamento, volume, market_cap, variacao_percentual, moeda, fonte
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'brapi')
                ON CONFLICT(ticker, data, fonte) DO UPDATE SET
                    abertura = excluded.abertura,
                    maxima = excluded.maxima,
                    minima = excluded.minima,
                    fechamento = excluded.fechamento,
                    volume = excluded.volume,
                    market_cap = excluded.market_cap,
                    variacao_percentual = excluded.variacao_percentual,
                    created_at = CURRENT_TIMESTAMP
            """, (
                ticker, data, abertura, maxima, minima,
                fechamento, volume, market_cap, variacao, moeda
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ {ticker}: R$ {fechamento:.2f} salvo com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar {ticker}: {e}")
            return False
    
    def sync_batch(self, tickers: List[str], data: date) -> Dict[str, int]:
        """
        Sincroniza um lote de tickers
        
        Args:
            tickers: Lista de tickers (máx 10 por batch)
            data: Data da cotação
        
        Returns:
            Dict com estatísticas: {'success': N, 'errors': N}
        """
        if not tickers:
            return {'success': 0, 'errors': 0}
        
        # Brapi aceita múltiplos tickers separados por vírgula
        ticker_list = ','.join(tickers)
        logger.info(f"🔄 Buscando cotações: {ticker_list}")
        
        try:
            # Buscar cotações via Brapi
            response = self.brapi.get_quote(
                tickers=ticker_list,
                fundamental=False,
                dividends=False
            )
            
            if not response or 'results' not in response:
                logger.error(f"❌ Resposta inválida da Brapi: {response}")
                return {'success': 0, 'errors': len(tickers)}
            
            # Processar cada cotação
            success = 0
            errors = 0
            
            for quote in response['results']:
                ticker = quote.get('symbol')
                
                if self.save_quote(ticker, quote, data):
                    success += 1
                else:
                    errors += 1
            
            return {'success': success, 'errors': errors}
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar lote {ticker_list}: {e}")
            return {'success': 0, 'errors': len(tickers)}
    
    def sync_all(self, batch_size: int = 10):
        """
        Sincroniza todos os tickers ativos
        
        Args:
            batch_size: Quantos tickers processar por batch (padrão: 10)
        """
        logger.info("=" * 70)
        logger.info("📈 SINCRONIZAÇÃO DE PREÇOS")
        logger.info("=" * 70)
        
        # Testar conexão com Brapi
        logger.info("🔌 Testando conexão com Brapi...")
        test_result = self.brapi.test_connection()
        
        if test_result.get('status') != 'success':
            logger.error("❌ Falha ao conectar com Brapi, abortando...")
            return
        
        logger.info("✅ Conexão com Brapi OK")
        
        # Buscar tickers ativos
        tickers = self.get_active_tickers()
        
        if not tickers:
            logger.warning("⚠️  Nenhum ticker ativo encontrado no banco")
            logger.info("💡 Dica: Popule a tabela ticker_mapping primeiro")
            return
        
        logger.info(f"📊 {len(tickers)} ticker(s) para sincronizar")
        
        # Data atual
        data_sync = date.today()
        logger.info(f"📅 Data: {data_sync.strftime('%d/%m/%Y')}")
        
        # Processar em batches
        total_success = 0
        total_errors = 0
        
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(tickers) + batch_size - 1) // batch_size
            
            logger.info(f"\n📦 Batch {batch_num}/{total_batches} ({len(batch)} tickers)")
            
            stats = self.sync_batch(batch, data_sync)
            total_success += stats['success']
            total_errors += stats['errors']
        
        # Relatório final
        logger.info("\n" + "=" * 70)
        logger.info("📊 RELATÓRIO FINAL")
        logger.info("=" * 70)
        logger.info(f"✅ Sucesso: {total_success} ticker(s)")
        logger.info(f"❌ Erros: {total_errors} ticker(s)")
        logger.info(f"📈 Taxa de sucesso: {(total_success / len(tickers) * 100):.1f}%")
        logger.info("=" * 70)
        
        self.synced_count = total_success
        self.error_count = total_errors
    
    def sync_test_tickers(self):
        """
        Sincroniza apenas as 4 ações gratuitas (para teste sem API key)
        """
        logger.info("=" * 70)
        logger.info("🧪 TESTE DE SINCRONIZAÇÃO (4 AÇÕES GRATUITAS)")
        logger.info("=" * 70)
        
        # Adicionar tickers de teste ao banco (se não existirem)
        test_tickers = ['PETR4', 'MGLU3', 'VALE3', 'ITUB4']
        self._ensure_test_tickers(test_tickers)
        
        # Sincronizar
        data_sync = date.today()
        stats = self.sync_batch(test_tickers, data_sync)
        
        logger.info("\n" + "=" * 70)
        logger.info("📊 RESULTADO DO TESTE")
        logger.info("=" * 70)
        logger.info(f"✅ Sucesso: {stats['success']}/4")
        logger.info(f"❌ Erros: {stats['errors']}/4")
        logger.info("=" * 70)
    
    def _ensure_test_tickers(self, tickers: List[str]):
        """
        Garante que os tickers de teste existam na tabela ticker_mapping
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for ticker in tickers:
            cursor.execute("""
                INSERT OR IGNORE INTO ticker_mapping (ticker, ativo, verificado)
                VALUES (?, TRUE, TRUE)
            """, (ticker,))
        
        conn.commit()
        conn.close()


def main():
    """Executa sincronização de preços"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sincronização de preços via Brapi')
    parser.add_argument('--test', action='store_true', help='Testar com 4 ações gratuitas')
    parser.add_argument('--api-key', type=str, help='API key da Brapi (opcional)')
    parser.add_argument('--db', type=str, default='data/barsi.db', help='Caminho do banco')
    
    args = parser.parse_args()
    
    # Criar sincronizador
    sync = PriceSync(db_path=args.db, api_key=args.api_key)
    
    # Executar sincronização
    if args.test:
        sync.sync_test_tickers()
    else:
        sync.sync_all()


if __name__ == "__main__":
    main()

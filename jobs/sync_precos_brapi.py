"""
Job: Sincronizar Preços via Brapi → Supabase
Busca cotações da API Brapi e salva na tabela `precos` do Supabase
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime, timezone, date
from typing import List, Dict, Any

# Adicionar diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from jobs.common import get_supabase_admin_client, log_job_run, load_universo_mvp_tickers
import os

from integrations.brapi_integration import BrapiIntegration


def list_active_tickers_from_mapping(sb) -> List[str]:
    """
    Busca tickers ativos da tabela ticker_mapping no Supabase
    
    Returns:
        Lista de tickers (ex: ['PETR4', 'VALE3'])
    """
    try:
        result = sb.select(
            "ticker_mapping",
            "select=ticker&ativo=eq.true&order=ticker.asc"
        )
        
        if not result or not isinstance(result, list):
            print("[AVISO] Nenhum ticker ativo encontrado em ticker_mapping")
            return []
        
        tickers = [row['ticker'] for row in result if 'ticker' in row]
        print(f"[INFO] {len(tickers)} ticker(s) ativos encontrados")
        return tickers
        
    except Exception as e:
        print(f"[ERRO] Erro ao buscar tickers: {e}")
        return []


def convert_quote_to_supabase_row(ticker: str, quote_data: Dict[str, Any], data_sync: date) -> Dict[str, Any]:
    """
    Converte dados da Brapi para formato da tabela `precos` do Supabase
    
    Args:
        ticker: Código da ação
        quote_data: Resposta da API Brapi
        data_sync: Data da sincronização
    
    Returns:
        Dict pronto para inserir no Supabase
    """
    return {
        'ticker': ticker,
        'data': data_sync.isoformat(),
        'fechamento': float(quote_data.get('regularMarketPrice', 0)),
        'abertura': float(quote_data.get('regularMarketOpen', 0)) if quote_data.get('regularMarketOpen') else None,
        'maxima': float(quote_data.get('regularMarketDayHigh', 0)) if quote_data.get('regularMarketDayHigh') else None,
        'minima': float(quote_data.get('regularMarketDayLow', 0)) if quote_data.get('regularMarketDayLow') else None,
        'volume': int(quote_data.get('regularMarketVolume', 0)) if quote_data.get('regularMarketVolume') else None,
        'market_cap': int(quote_data.get('marketCap', 0)) if quote_data.get('marketCap') else None,
        'variacao_percentual': float(quote_data.get('regularMarketChangePercent', 0)) if quote_data.get('regularMarketChangePercent') else None,
        'moeda': quote_data.get('currency', 'BRL'),
        'fonte': 'brapi'
    }


def sync_batch_to_supabase(
    sb,
    brapi: BrapiIntegration,
    tickers: List[str],
    data_sync: date,
    batch_size: int = 10
) -> Dict[str, int]:
    """
    Sincroniza um lote de tickers da Brapi para o Supabase
    
    Args:
        sb: Cliente Supabase
        brapi: Cliente Brapi
        tickers: Lista de tickers para sincronizar
        data_sync: Data da sincronização
        batch_size: Tamanho do lote (padrão: 10)
    
    Returns:
        Dict com estatísticas {'success': N, 'errors': N}
    """
    total_success = 0
    total_errors = 0
    
    # Processar em batches (Brapi aceita múltiplos tickers)
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(tickers) + batch_size - 1) // batch_size
        
        print(f"\n[*] Batch {batch_num}/{total_batches} ({len(batch)} tickers)")
        
        try:
            # Buscar cotações via Brapi
            ticker_list = ','.join(batch)
            response = brapi.get_quote(
                tickers=ticker_list,
                fundamental=False,
                dividends=False
            )
            
            if not response or 'results' not in response:
                print(f"[ERRO] Resposta invalida da Brapi para batch {batch_num}")
                total_errors += len(batch)
                continue
            
            # Converter para formato Supabase
            rows = []
            for quote in response['results']:
                ticker = quote.get('symbol')
                
                # Validar dados obrigatórios
                if not ticker or quote.get('regularMarketPrice') is None:
                    print(f"[AVISO] {ticker or 'UNKNOWN'}: Dados incompletos, pulando...")
                    total_errors += 1
                    continue
                
                row = convert_quote_to_supabase_row(ticker, quote, data_sync)
                rows.append(row)
                
                preco = row['fechamento']
                variacao = row['variacao_percentual'] or 0
                print(f"  - {ticker}: R$ {preco:.2f} ({variacao:+.2f}%)")
            
            if not rows:
                print(f"[AVISO] Nenhum dado valido no batch {batch_num}")
                total_errors += len(batch)
                continue
            
            # Salvar no Supabase (UPSERT)
            try:
                sb.upsert("precos", rows, on_conflict="ticker,data,fonte")
                print(f"[OK] {len(rows)} preco(s) salvos no Supabase")
                total_success += len(rows)
                
            except Exception as e:
                print(f"[ERRO] Erro ao salvar batch {batch_num} no Supabase: {e}")
                total_errors += len(batch)
        
        except Exception as e:
            print(f"[ERRO] Erro ao processar batch {batch_num}: {e}")
            total_errors += len(batch)
    
    return {'success': total_success, 'errors': total_errors}


def main() -> None:
    """Executa sincronização de preços Brapi -> Supabase"""
    print("=" * 70)
    print("SINCRONIZACAO BRAPI -> SUPABASE")
    print("=" * 70)
    
    started_at = datetime.now(timezone.utc)
    data_sync = date.today()
    
    # Conectar ao Supabase
    print("\n[*] Conectando ao Supabase...")
    sb = get_supabase_admin_client()
    print("[OK] Supabase conectado")
    
    # Conectar à Brapi
    print("\n[*] Conectando a Brapi...")
    api_key = (os.getenv("BRAPI_API_KEY") or "").strip() or None
    brapi = BrapiIntegration(api_key=api_key)
    
    # Testar conexão
    test_result = brapi.test_connection()
    if test_result.get('status') != 'success':
        print("[ERRO] Falha ao conectar com Brapi")
        return
    
    print("[OK] Brapi conectada")
    
    # Buscar tickers ativos
    print(f"\n[*] Data: {data_sync.strftime('%d/%m/%Y')}")
    print("\n[*] Buscando tickers ativos...")
    
    tickers = list_active_tickers_from_mapping(sb)

    # Se existir Universo MVP, restringir o processamento a ele.
    universo = load_universo_mvp_tickers()
    if universo:
        tickers = [t for t in tickers if t in set(universo)]
        print(f"[INFO] Universo MVP ativo: {len(tickers)} ticker(s) após filtro")

    # Sem token, manter apenas o universo gratuito para evitar falhas
    if not api_key:
        tickers = [t for t in tickers if t in BrapiIntegration.FREE_TICKERS]
        if not tickers:
            tickers = list(BrapiIntegration.FREE_TICKERS)
        print("[AVISO] BRAPI_API_KEY ausente; usando apenas tickers gratuitos.")
    
    if not tickers:
        print("\n[AVISO] Nenhum ticker ativo para sincronizar")
        print("[DICA] Adicione tickers na tabela ticker_mapping do Supabase")
        return
    
    print(f"[OK] {len(tickers)} ticker(s) para processar: {', '.join(tickers)}")
    
    # Sincronizar
    status = "success"
    message = None
    rows_processed = 0
    
    try:
        stats = sync_batch_to_supabase(sb, brapi, tickers, data_sync, batch_size=10)
        rows_processed = stats['success']
        
        # Relatório final
        print("\n" + "=" * 70)
        print("RELATORIO FINAL")
        print("=" * 70)
        print(f"[OK] Sucesso: {stats['success']} ticker(s)")
        print(f"[ERRO] Erros: {stats['errors']} ticker(s)")
        
        if len(tickers) > 0:
            taxa_sucesso = (stats['success'] / len(tickers)) * 100
            print(f"[INFO] Taxa de sucesso: {taxa_sucesso:.1f}%")
        
        print("=" * 70)
        
        if stats['errors'] > 0:
            status = "error"
            message = f"{stats['errors']} ticker(s) com erro"
    
    except Exception as e:
        status = "error"
        message = str(e)
        print(f"\n[ERRO CRITICO] {e}")
        raise
    
    finally:
        # Registrar execução no Supabase
        finished_at = datetime.now(timezone.utc)
        log_job_run(
            sb,
            job_name="sync_precos_brapi",
            status=status,
            rows_processed=rows_processed,
            message=message,
            started_at=started_at,
            finished_at=finished_at,
        )
        print(f"\n[OK] Job registrado: {status} ({rows_processed} rows)")


if __name__ == "__main__":
    main()

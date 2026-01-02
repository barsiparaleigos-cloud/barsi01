"""
Job: Sincronizar Dividendos via Brapi -> Supabase
Busca histórico de dividendos da API Brapi e salva na tabela `dividends` do Supabase
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any

# Adicionar diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from jobs.common import get_supabase_admin_client, log_job_run, load_universo_mvp_tickers
import os

from integrations.brapi_integration import BrapiIntegration


def list_active_tickers_from_mapping(sb) -> List[str]:
    """Busca tickers ativos da tabela ticker_mapping"""
    try:
        result = sb.select(
            "ticker_mapping",
            "select=ticker&ativo=eq.true&order=ticker.asc"
        )
        
        if not result or not isinstance(result, list):
            return []
        
        return [row['ticker'] for row in result if 'ticker' in row]
        
    except Exception as e:
        print(f"[ERRO] Erro ao buscar tickers: {e}")
        return []


def convert_dividend_to_supabase_row(ticker: str, dividend: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converte dividendo da Brapi para formato da tabela `dividends` do Supabase
    
    Args:
        ticker: Código da ação
        dividend: Dados do dividendo da integração Brapi (já parseado)
    
    Returns:
        Dict pronto para inserir no Supabase
    """
    # Mapear tipo de dividendo
    tipo_map = {
        'DIVIDEND': 'dividend',
        'JCP': 'jcp',
        'JSCP': 'jcp',
        'SPECIAL': 'special',
        'ESPECIAL': 'special'
    }
    
    tipo_original = dividend.get('tipo', 'DIVIDEND').upper()
    tipo_normalizado = tipo_map.get(tipo_original, 'dividend')
    
    # Usar data_pagamento como ex_date (formato da Brapi)
    ex_date_str = dividend.get('data_pagamento')
    pay_date_str = dividend.get('data_pagamento')
    
    # Converter ISO para YYYY-MM-DD
    if ex_date_str and 'T' in ex_date_str:
        ex_date = ex_date_str.split('T')[0]
    else:
        ex_date = ex_date_str
    
    if pay_date_str and 'T' in pay_date_str:
        pay_date = pay_date_str.split('T')[0]
    else:
        pay_date = pay_date_str
    
    return {
        'ticker': ticker,
        'ex_date': ex_date,
        'pay_date': pay_date,
        'amount_per_share': float(dividend.get('valor_por_acao', 0)),
        'type': tipo_normalizado
    }


def sync_dividends_batch(
    sb,
    brapi: BrapiIntegration,
    tickers: List[str],
    batch_size: int = 10
) -> Dict[str, int]:
    """
    Sincroniza dividendos de um lote de tickers
    
    Returns:
        Dict com estatísticas {'success': N, 'errors': N, 'dividends_total': N}
    """
    total_success = 0
    total_errors = 0
    total_dividends = 0
    
    # Processar em batches
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(tickers) + batch_size - 1) // batch_size
        
        print(f"\n[*] Batch {batch_num}/{total_batches} ({len(batch)} tickers)")
        
        try:
            # Buscar cotações COM dividendos via Brapi
            ticker_list = ','.join(batch)
            response = brapi.get_quote(
                tickers=ticker_list,
                fundamental=False,
                dividends=True  # IMPORTANTE: pedir dividendos
            )
            
            if not response or 'results' not in response:
                print(f"[ERRO] Resposta invalida da Brapi para batch {batch_num}")
                total_errors += len(batch)
                continue
            
            # Processar cada ticker
            for quote in response['results']:
                ticker = quote.get('symbol')
                
                if not ticker:
                    total_errors += 1
                    continue
                
                # Extrair dividendos
                dividends_data = brapi.extract_dividends(quote)
                
                if not dividends_data:
                    print(f"  - {ticker}: Sem dividendos")
                    total_success += 1
                    continue
                
                # Converter para formato Supabase
                rows = []
                for div in dividends_data:
                    try:
                        row = convert_dividend_to_supabase_row(ticker, div)
                        if row['ex_date']:  # Só adicionar se tiver data
                            rows.append(row)
                    except Exception as e:
                        print(f"    [AVISO] Erro ao converter dividendo: {e}")
                        continue
                
                if not rows:
                    print(f"  - {ticker}: Dividendos sem data valida")
                    total_success += 1
                    continue
                
                # Salvar no Supabase
                try:
                    # on_conflict precisa ser exatamente o índice único da tabela
                    # dividends_unique_mock_uidx: (ticker, ex_date, type, amount_per_share)
                    sb.upsert(
                        "dividends", 
                        rows, 
                        on_conflict="ticker,ex_date,type,amount_per_share"
                    )
                    print(f"  - {ticker}: {len(rows)} dividendo(s) salvos")
                    total_success += 1
                    total_dividends += len(rows)
                    
                except Exception as e:
                    print(f"  - {ticker}: ERRO ao salvar - {e}")
                    total_errors += 1
        
        except Exception as e:
            print(f"[ERRO] Erro ao processar batch {batch_num}: {e}")
            total_errors += len(batch)
    
    return {
        'success': total_success,
        'errors': total_errors,
        'dividends_total': total_dividends
    }


def main() -> None:
    """Executa sincronização de dividendos Brapi -> Supabase"""
    print("=" * 70)
    print("SINCRONIZACAO DIVIDENDOS: BRAPI -> SUPABASE")
    print("=" * 70)
    
    started_at = datetime.now(timezone.utc)
    
    # Conectar ao Supabase
    print("\n[*] Conectando ao Supabase...")
    sb = get_supabase_admin_client()
    print("[OK] Supabase conectado")
    
    # Conectar à Brapi
    print("\n[*] Conectando a Brapi...")
    api_key = (os.getenv("BRAPI_API_KEY") or "").strip() or None
    brapi = BrapiIntegration(api_key=api_key)
    
    test_result = brapi.test_connection()
    if test_result.get('status') != 'success':
        print("[ERRO] Falha ao conectar com Brapi")
        return
    
    print("[OK] Brapi conectada")
    
    # Buscar tickers ativos
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
        return
    
    print(f"[OK] {len(tickers)} ticker(s) para processar: {', '.join(tickers)}")
    
    # Sincronizar dividendos
    status = "success"
    message = None
    rows_processed = 0
    
    try:
        stats = sync_dividends_batch(sb, brapi, tickers, batch_size=10)
        rows_processed = stats['dividends_total']
        
        # Relatório final
        print("\n" + "=" * 70)
        print("RELATORIO FINAL")
        print("=" * 70)
        print(f"[OK] Tickers processados: {stats['success']}")
        print(f"[ERRO] Erros: {stats['errors']}")
        print(f"[INFO] Total de dividendos salvos: {stats['dividends_total']}")
        
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
            job_name="sync_dividendos_brapi",
            status=status,
            rows_processed=rows_processed,
            message=message,
            started_at=started_at,
            finished_at=finished_at,
        )
        print(f"\n[OK] Job registrado: {status} ({rows_processed} dividends)")


if __name__ == "__main__":
    main()

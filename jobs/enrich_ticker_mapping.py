"""
Job: Enriquecer Ticker Mapping com dados CVM
Busca dados da CVM para empresas no ticker_mapping
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from jobs.common import SupabaseRestClient, get_supabase_admin_client, log_job_run


def normalize_cnpj(cnpj: str) -> str:
    """Remove formatação do CNPJ"""
    return ''.join(c for c in str(cnpj or "") if c.isdigit())


def enrich_ticker_with_cvm(sb: SupabaseRestClient) -> Dict[str, Any]:
    """
    Enriquece ticker_mapping com dados da CVM
    
    Args:
        sb: Cliente Supabase
    
    Returns:
        Dict com estatísticas
    """
    print("\n[*] Buscando tickers ativos no ticker_mapping...")
    
    # Buscar tickers com CNPJ
    tickers = sb.select(
        "ticker_mapping",
        "select=ticker,cnpj,nome,ativo,verificado,tipo_acao,empresa_id&ativo=eq.true&cnpj=not.is.null"
    )
    
    print(f"[OK] {len(tickers)} tickers com CNPJ para enriquecer")
    
    # Para cada ticker, buscar dados na CVM
    enriched_count = 0
    not_found_count = 0
    
    for ticker_data in tickers:
        ticker = ticker_data['ticker']
        cnpj = normalize_cnpj(ticker_data['cnpj'])
        
        print(f"\n[*] {ticker} ({cnpj})...")
        
        # Buscar na tabela companies_cvm
        cvm_data = sb.select(
            "companies_cvm",
            f"select=cnpj,denominacao_social&cnpj=eq.{cnpj}"
        )
        
        if not cvm_data:
            print(f"  [AVISO] Nao encontrado na CVM")
            not_found_count += 1
            continue
        
        # Pegar primeiro resultado
        cvm = cvm_data[0]
        
        # Atualizar ticker_mapping com dados da CVM
        update_row = {
            'ticker': ticker,
            'cnpj': ticker_data.get('cnpj'),
            'nome': cvm.get('denominacao_social') or ticker_data.get('nome'),
            'ativo': ticker_data.get('ativo', True),
            'verificado': ticker_data.get('verificado', False),
            'tipo_acao': ticker_data.get('tipo_acao'),
            'empresa_id': ticker_data.get('empresa_id'),
            'updated_at': datetime.now().isoformat(),
        }

        # UPSERT por ticker (preserva as colunas selecionadas acima)
        try:
            sb.upsert("ticker_mapping", [update_row], on_conflict="ticker")
            
            enriched_count += 1
            print(f"  [OK] Enriquecido: {cvm.get('denominacao_social')}")
        
        except Exception as e:
            print(f"  [ERRO] Falha ao atualizar: {e}")
    
    print(f"\n" + "=" * 70)
    print(f"[OK] Enriquecidos: {enriched_count}")
    print(f"[AVISO] Nao encontrados: {not_found_count}")
    print("=" * 70)
    
    return {
        'total': len(tickers),
        'enriched': enriched_count,
        'not_found': not_found_count
    }


def main():
    """Executa enriquecimento de ticker_mapping com CVM"""
    print("=" * 70)
    print("ENRIQUECIMENTO TICKER_MAPPING COM DADOS CVM")
    print("=" * 70)
    
    sb = get_supabase_admin_client()
    started_at = datetime.now(timezone.utc)
    status = "success"
    message = None

    # Conectar Supabase
    print("\n[*] Conectando ao Supabase...")
    print("[OK] Supabase conectado")
    
    # Enriquecer
    result: Dict[str, Any] = {}
    try:
        result = enrich_ticker_with_cvm(sb)
        
        print("\n" + "=" * 70)
        print("RELATORIO FINAL")
        print("=" * 70)
        print(f"[INFO] Total tickers: {result['total']}")
        print(f"[OK] Enriquecidos: {result['enriched']}")
        print(f"[AVISO] Nao encontrados: {result['not_found']}")
        print("=" * 70)
        
    except Exception as e:
        status = "error"
        message = str(e)
        print("\n" + "=" * 70)
        print("[ERRO] FALHA NO ENRIQUECIMENTO")
        print("=" * 70)
        print(f"[ERRO] {str(e)}")
        print("=" * 70)
        raise
    finally:
        finished_at = datetime.now(timezone.utc)
        rows_processed = int(result.get("enriched") or 0) if status == "success" else 0
        log_job_run(
            sb,
            job_name="enrich_ticker_mapping",
            status=status,
            rows_processed=rows_processed,
            message=message,
            started_at=started_at,
            finished_at=finished_at,
        )

        print(f"\n[OK] Job registrado: {status}")


if __name__ == "__main__":
    main()

"""
Job: Enriquecer Ticker Mapping com dados CVM
Busca dados da CVM para empresas no ticker_mapping
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from jobs.common import SupabaseRestClient, load_settings, log_job_run


def normalize_cnpj(cnpj: str) -> str:
    """Remove formatação do CNPJ"""
    return ''.join(c for c in cnpj if c.isdigit())


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
    result = sb.select(
        "ticker_mapping",
        "select=ticker,cnpj,nome&ativo=eq.true&cnpj=not.is.null"
    )
    
    tickers = result.get('data', [])
    
    print(f"[OK] {len(tickers)} tickers com CNPJ para enriquecer")
    
    # Para cada ticker, buscar dados na CVM
    enriched_count = 0
    not_found_count = 0
    
    for ticker_data in tickers:
        ticker = ticker_data['ticker']
        cnpj = normalize_cnpj(ticker_data['cnpj'])
        
        print(f"\n[*] {ticker} ({cnpj})...")
        
        # Buscar na tabela companies_cvm
        cvm_result = sb.select(
            "companies_cvm",
            f"select=*&cnpj=like.*{cnpj}*"
        )
        
        cvm_data = cvm_result.get('data', [])
        
        if not cvm_data:
            print(f"  [AVISO] Nao encontrado na CVM")
            not_found_count += 1
            continue
        
        # Pegar primeiro resultado
        cvm = cvm_data[0]
        
        # Atualizar ticker_mapping com dados da CVM
        update_data = {
            'nome': cvm.get('denominacao_social', ticker_data['nome']),
            'cvm_code': cvm.get('cvm_code'),
            'setor_atividade': cvm.get('setor_atividade'),
            'updated_at': datetime.now().isoformat()
        }
        
        # Fazer UPDATE
        try:
            sb.update(
                "ticker_mapping",
                update_data,
                f"ticker=eq.{ticker}"
            )
            
            enriched_count += 1
            print(f"  [OK] Enriquecido: {cvm.get('denominacao_social')}")
            print(f"    Setor: {cvm.get('setor_atividade')}")
        
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
    
    # Carregar configuração
    settings = load_settings()
    
    # Conectar Supabase
    print("\n[*] Conectando ao Supabase...")
    sb = SupabaseRestClient(
        url=settings["SUPABASE_URL"],
        key=settings["SERVICE_ROLE_KEY"]
    )
    print("[OK] Supabase conectado")
    
    # Enriquecer
    try:
        result = enrich_ticker_with_cvm(sb)
        
        print("\n" + "=" * 70)
        print("RELATORIO FINAL")
        print("=" * 70)
        print(f"[INFO] Total tickers: {result['total']}")
        print(f"[OK] Enriquecidos: {result['enriched']}")
        print(f"[AVISO] Nao encontrados: {result['not_found']}")
        print("=" * 70)
        
        # Registrar sucesso
        log_job_run(
            sb=sb,
            job_name="enrich_ticker_mapping",
            status="success",
            rows_processed=result['enriched'],
            error_message=None
        )
        
        print("\n[OK] Job registrado: success")
    
    except Exception as e:
        print("\n" + "=" * 70)
        print("[ERRO] FALHA NO ENRIQUECIMENTO")
        print("=" * 70)
        print(f"[ERRO] {str(e)}")
        print("=" * 70)
        
        # Registrar erro
        log_job_run(
            sb=sb,
            job_name="enrich_ticker_mapping",
            status="error",
            rows_processed=0,
            error_message=str(e)
        )
        
        print("\n[OK] Job registrado: error")
        
        raise


if __name__ == "__main__":
    main()

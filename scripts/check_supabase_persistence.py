from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from jobs.common import get_supabase_admin_client


TABLES = [
    "job_runs",
    "assets",
    "ticker_mapping",
    "precos",
    "prices_daily",
    "dividends",
    "signals_daily",
    "fundamentals_raw",
    "fundamentals_daily",
    "cvm_dfp_metrics_daily",
    "dividend_metrics_daily",
    "relacoes_investidores",
]


def main() -> None:
    sb = get_supabase_admin_client()

    print("SUPABASE PERSISTENCE CHECK")
    print("=" * 70)

    for table in TABLES:
        try:
            total = sb.count(table)
            print(f"[OK] {table:<22} rows={total}")
        except Exception as e:
            print(f"[WARN] {table:<22} {e}")

    # Métricas úteis para destravar integrações CVM (DFP/FRE/RI por CNPJ)
    try:
        total = sb.count("ticker_mapping")
        with_cnpj = sb.count("ticker_mapping", "cnpj=not.is.null")
        verified = sb.count("ticker_mapping", "verificado=eq.true")
        print(
            f"\n[INFO] ticker_mapping: total={total}  com_cnpj={with_cnpj}  verificados={verified}"
        )
    except Exception as e:
        print(f"[WARN] ticker_mapping metrics failed: {e}")

    # Cobertura de alavancagem (DFP): colunas podem não existir antes da migração 012
    try:
        total_dfp = sb.count("cvm_dfp_metrics_daily")
        with_debt = sb.count("cvm_dfp_metrics_daily", "divida_bruta=not.is.null")
        with_cash = sb.count("cvm_dfp_metrics_daily", "caixa_equivalentes=not.is.null")
        with_net = sb.count("cvm_dfp_metrics_daily", "divida_liquida=not.is.null")
        print(
            f"[INFO] cvm_dfp_metrics_daily leverage: total={total_dfp}  divida={with_debt}  caixa={with_cash}  divida_liq={with_net}"
        )
    except Exception:
        pass

    print("\nLatest job runs:")
    try:
        rows = sb.select(
            "job_runs",
            "select=job_name,status,rows_processed,finished_at,message&order=finished_at.desc&limit=10",
        )
        for r in rows:
            print(
                f"- {r.get('finished_at')}  {r.get('job_name')}  {r.get('status')}  rows={r.get('rows_processed')}  msg={r.get('message')}"
            )
    except Exception as e:
        print(f"[WARN] job_runs listing failed: {e}")


if __name__ == "__main__":
    main()


"""Job: Sincronizar fundamentos via Brapi -> Supabase

Armazena o payload bruto (JSON) em `fundamentals_raw` para manter flexibilidade
(e permitir evoluir o schema depois, ou adicionar outra fonte como Fintz).

Requer (Supabase): executar `sql/007_add_fundamentals_raw.sql`.
"""

from __future__ import annotations

import os

from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

from jobs.common import get_supabase_admin_client, list_active_tickers, log_job_run
from integrations.brapi_integration import BrapiIntegration


def _env_brapi_key() -> Optional[str]:
    return (os.getenv("BRAPI_API_KEY") or "").strip() or None


def _chunk(items: List[str], size: int) -> List[List[str]]:
    if size <= 0:
        return [items]
    return [items[i : i + size] for i in range(0, len(items), size)]


def _extract_results(resp: Dict[str, Any]) -> List[Dict[str, Any]]:
    results = resp.get("results")
    if isinstance(results, list):
        return [r for r in results if isinstance(r, dict)]
    return []


def main(
    *,
    tickers: Optional[List[str]] = None,
    batch_size: int = 10,
    api_key: Optional[str] = None,
) -> None:
    started_at = datetime.now(timezone.utc)
    sb = get_supabase_admin_client()

    as_of = date.today().isoformat()

    if api_key is None:
        api_key = _env_brapi_key()

    if not tickers:
        tickers = list_active_tickers(sb)

    tickers = [t.strip().upper() for t in tickers if t and str(t).strip()]
    tickers = list(dict.fromkeys(tickers))  # de-dupe preservando ordem

    if not tickers:
        print("[AVISO] Nenhum ticker ativo encontrado.")
        return

    # Sem token, a Brapi pode limitar o universo: manter execução resiliente.
    if not api_key:
        tickers = [t for t in tickers if t in BrapiIntegration.FREE_TICKERS]
        if not tickers:
            tickers = list(BrapiIntegration.FREE_TICKERS)
        print("[AVISO] BRAPI_API_KEY ausente; usando apenas tickers gratuitos.")

    brapi = BrapiIntegration(api_key=api_key)

    status = "success"
    message: Optional[str] = None
    rows_written = 0

    try:
        batches = _chunk(tickers, batch_size)
        for i, batch in enumerate(batches, start=1):
            print(f"[*] Batch {i}/{len(batches)}: {', '.join(batch)}")
            resp = brapi.get_quote(batch, fundamental=True, dividends=False)
            results = _extract_results(resp)

            rows: List[Dict[str, Any]] = []
            for r in results:
                ticker = str(r.get("symbol") or "").strip().upper()
                if not ticker:
                    continue
                rows.append(
                    {
                        "ticker": ticker,
                        "as_of_date": as_of,
                        "source": "brapi",
                        "payload": r,
                    }
                )

            if not rows:
                continue

            sb.upsert("fundamentals_raw", rows, on_conflict="ticker,as_of_date,source")
            rows_written += len(rows)

        print(f"✅ {rows_written} payload(s) de fundamentos salvos em fundamentals_raw para {as_of}")

    except Exception as e:
        status = "error"
        message = str(e)
        print(f"[ERRO] Falha ao sincronizar fundamentos Brapi: {e}")
        raise

    finally:
        finished_at = datetime.now(timezone.utc)
        log_job_run(
            sb,
            job_name="sync_fundamentals_brapi",
            status=status,
            rows_processed=rows_written,
            message=message,
            started_at=started_at,
            finished_at=finished_at,
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sincronizar fundamentos (payload bruto) via Brapi -> Supabase")
    parser.add_argument("--tickers", type=str, help="Lista de tickers separados por vírgula (opcional)")
    parser.add_argument("--batch-size", type=int, default=10, help="Tamanho do batch para chamadas na Brapi")
    parser.add_argument("--api-key", type=str, default=None, help="Token da Brapi (opcional)")

    args = parser.parse_args()

    tickers_arg: Optional[List[str]] = None
    if args.tickers:
        tickers_arg = [t.strip() for t in str(args.tickers).split(",") if t.strip()]

    main(tickers=tickers_arg, batch_size=int(args.batch_size), api_key=args.api_key)

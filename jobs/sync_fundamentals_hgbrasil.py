"""Job: Sincronizar fundamentos via HG Brasil -> Supabase

Armazena o payload bruto (JSON) em `fundamentals_raw`.

Fonte:
- HG Brasil Finance (stock_price)
- Doc: https://hgbrasil.com/docs/finance/stocks

Requer (Supabase): executar `sql/007_add_fundamentals_raw.sql`.
"""

from __future__ import annotations

import os
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

from integrations.hgbrasil_integration import HGBrasilIntegration
from jobs.common import get_supabase_admin_client, list_active_tickers, log_job_run


def _first_env(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "")
        if value and str(value).strip():
            return str(value).strip()
    return ""


def _extract_symbol_payload(resp: Dict[str, Any], ticker: str) -> Optional[Dict[str, Any]]:
    results = resp.get("results")
    if not isinstance(results, dict):
        return None

    # A chave normalmente vem como o próprio ticker em uppercase
    key = ticker.strip().upper()
    payload = results.get(key)
    if isinstance(payload, dict):
        return payload

    # Fallback: primeira entrada dict dentro de results
    for _, v in results.items():
        if isinstance(v, dict):
            return v

    return None


def main(
    *,
    tickers: Optional[List[str]] = None,
    api_key: Optional[str] = None,
) -> None:
    started_at = datetime.now(timezone.utc)
    sb = get_supabase_admin_client()

    as_of = date.today().isoformat()

    if not tickers:
        tickers = list_active_tickers(sb)

    tickers = [t.strip().upper() for t in tickers if t and str(t).strip()]
    tickers = list(dict.fromkeys(tickers))

    if not tickers:
        print("[AVISO] Nenhum ticker ativo encontrado.")
        return

    api_key = api_key or _first_env("HGBRASIL_KEY", "HG_BRASIL_KEY")
    if not api_key:
        print(
            "[AVISO] HGBRASIL_KEY não configurada; pulando sync_fundamentals_hgbrasil. "
            "Defina HGBRASIL_KEY em .env.local (veja .env.example)."
        )
        return

    hg = HGBrasilIntegration(api_key=api_key)

    status = "success"
    message: Optional[str] = None
    rows_written = 0

    try:
        for i, ticker in enumerate(tickers, start=1):
            print(f"[*] {i}/{len(tickers)}: {ticker}")
            resp = hg.get_stock_price(ticker)
            payload = _extract_symbol_payload(resp, ticker)
            if not payload:
                continue

            row: Dict[str, Any] = {
                "ticker": ticker,
                "as_of_date": as_of,
                "source": "hgbrasil",
                "payload": payload,
            }
            sb.upsert("fundamentals_raw", [row], on_conflict="ticker,as_of_date,source")
            rows_written += 1

        print(f"✅ {rows_written} payload(s) de fundamentos salvos em fundamentals_raw para {as_of} (hgbrasil)")

    except Exception as e:
        status = "error"
        message = str(e)
        print(f"[ERRO] Falha ao sincronizar fundamentos HG Brasil: {e}")
        raise

    finally:
        finished_at = datetime.now(timezone.utc)
        log_job_run(
            sb,
            job_name="sync_fundamentals_hgbrasil",
            status=status,
            rows_processed=rows_written,
            message=message,
            started_at=started_at,
            finished_at=finished_at,
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Sincronizar fundamentos (payload bruto) via HG Brasil -> Supabase"
    )
    parser.add_argument("--tickers", type=str, help="Lista de tickers separados por virgula (opcional)")
    parser.add_argument("--api-key", type=str, default=None, help="Chave da HG Brasil (opcional; usa env HGBRASIL_KEY)")

    args = parser.parse_args()

    tickers_arg: Optional[List[str]] = None
    if args.tickers:
        tickers_arg = [t.strip() for t in str(args.tickers).split(",") if t.strip()]

    main(tickers=tickers_arg, api_key=args.api_key)

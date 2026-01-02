"""Job: popular `ticker_mapping` com tickers disponíveis na Brapi.

Esse job serve para aumentar o universo de tickers no Supabase, para que os
demais jobs (preços, dividendos, sinais) tenham o que processar.

Observações:
- Sem `BRAPI_API_KEY`, a cobertura pode ser limitada conforme o plano.
- Esse job NÃO define CNPJ; apenas cria/atualiza `ticker` + `nome`.
"""

from __future__ import annotations

import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from integrations.brapi_integration import BrapiIntegration
from jobs.common import get_supabase_admin_client, log_job_run


_TICKER_RE = re.compile(r"^[A-Z]{4}\d{1,2}$")


def _pick_ticker(row: Dict[str, Any]) -> str:
    for k in ("stock", "ticker", "symbol"):
        v = row.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip().upper()
    return ""


def _pick_name(row: Dict[str, Any]) -> str:
    for k in ("name", "shortName", "longName", "company"):
        v = row.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def main() -> None:
    sb = get_supabase_admin_client()
    started_at = datetime.now(timezone.utc)
    status = "success"
    message = None
    inserted = 0

    api_key = os.getenv("BRAPI_API_KEY") or None
    brapi = BrapiIntegration(api_key=api_key)

    try:
        limit = int(os.getenv("BRAPI_QUOTE_LIST_LIMIT") or "200")
        limit = max(1, min(200, limit))

        print(f"[INFO] Buscando lista de tickers via Brapi (limit={limit})...")
        data = brapi.get_quote_list(limit=limit, sortBy="market_cap", sortOrder="desc")
        stocks: List[Dict[str, Any]] = list(data.get("stocks") or [])
        print(f"[OK] Recebidos: {len(stocks)}")

        rows_to_upsert: List[Dict[str, Any]] = []
        for s in stocks:
            ticker = _pick_ticker(s)
            if not ticker or not _TICKER_RE.match(ticker):
                continue
            nome = _pick_name(s)
            # Não sobrescrever `verificado` (pode ter sido ajustado manualmente).
            # Para inserts novos, o default do banco continua sendo FALSE.
            row = {"ticker": ticker, "ativo": True}
            if nome:
                row["nome"] = nome
            rows_to_upsert.append(row)

        if not rows_to_upsert:
            print("[AVISO] Nenhum ticker válido retornado pelo quote/list.")
        else:
            sb.upsert("ticker_mapping", rows_to_upsert, on_conflict="ticker")
            inserted = len(rows_to_upsert)
            print(f"[OK] Upsert em ticker_mapping: {inserted} tickers")

            # Convenção do projeto: tickers gratuitos do Brapi são considerados verificados.
            try:
                sb.upsert(
                    "ticker_mapping",
                    [{"ticker": t, "verificado": True, "ativo": True} for t in BrapiIntegration.FREE_TICKERS],
                    on_conflict="ticker",
                )
            except Exception:
                pass

    except Exception as e:
        status = "error"
        message = str(e)
        raise
    finally:
        finished_at = datetime.now(timezone.utc)
        log_job_run(
            sb,
            job_name="sync_ticker_mapping_brapi_list",
            status=status,
            rows_processed=inserted if status == "success" else 0,
            message=message,
            started_at=started_at,
            finished_at=finished_at,
        )


if __name__ == "__main__":
    main()

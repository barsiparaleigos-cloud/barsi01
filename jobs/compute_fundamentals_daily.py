"""Job: Materializar fundamentals_daily a partir de fundamentals_raw.

Passo seguinte após `jobs/sync_fundamentals_brapi.py`.

Requer (Supabase): executar `sql/008_add_fundamentals_daily.sql`.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

from jobs.common import get_supabase_admin_client, log_job_run


def _to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def _pick_fintz_indicator_value(indicators: Any, name: str) -> Optional[float]:
    if not isinstance(indicators, list) or not name:
        return None
    best_date = ""
    best_val: Optional[float] = None
    for row in indicators:
        if not isinstance(row, dict):
            continue
        if str(row.get("indicador") or "") != name:
            continue
        v = _to_float(row.get("valor"))
        if v is None:
            continue
        d = str(row.get("data") or "")
        if d >= best_date:
            best_date = d
            best_val = v
    return best_val


def _extract_daily_fields(payload: Dict[str, Any], source: str) -> Dict[str, Any]:
    if source == "brapi":
        return {
            "currency": payload.get("currency"),
            "price_current": _to_float(payload.get("regularMarketPrice")),
            "market_cap": _to_float(payload.get("marketCap")),
            "eps": _to_float(payload.get("earningsPerShare")),
            "pe": _to_float(payload.get("priceEarnings")),
        }

    if source == "hgbrasil":
        # HG Brasil (stock_price)
        currency = payload.get("currency")
        if not currency:
            # A API é focada em ativos BR; manter fallback simples.
            currency = "BRL"
        return {
            "currency": currency,
            "price_current": _to_float(payload.get("price")),
            "market_cap": _to_float(payload.get("market_cap")),
            "eps": None,
            "pe": None,
        }

    if source == "fintz":
        # Snapshot raw: { ticker, indicadores: [...], itens_contabeis: [...], ... }
        indicators = payload.get("indicadores")
        return {
            "currency": "BRL",
            "price_current": None,
            "market_cap": _pick_fintz_indicator_value(indicators, "ValorDeMercado"),
            "eps": _pick_fintz_indicator_value(indicators, "LPA"),
            "pe": _pick_fintz_indicator_value(indicators, "P_L"),
        }

    return {
        "currency": payload.get("currency"),
        "price_current": None,
        "market_cap": None,
        "eps": None,
        "pe": None,
    }


def main(*, as_of: Optional[str] = None, source: str = "brapi") -> None:
    sb = get_supabase_admin_client()
    started_at = datetime.now(timezone.utc)

    day = as_of or date.today().isoformat()

    status = "success"
    message: Optional[str] = None
    rows_written = 0

    try:
        raws = sb.select(
            "fundamentals_raw",
            f"select=id,ticker,as_of_date,source,payload&as_of_date=eq.{day}&source=eq.{source}&order=created_at.desc",
        )

        out: List[Dict[str, Any]] = []
        for r in raws:
            payload = r.get("payload") if isinstance(r, dict) else None
            if not isinstance(payload, dict):
                continue

            ticker = str(r.get("ticker") or "").strip().upper()
            if not ticker:
                continue

            fields = _extract_daily_fields(payload, source)

            out.append(
                {
                    "ticker": ticker,
                    "date": day,
                    "source": source,
                    "currency": fields.get("currency"),
                    "price_current": fields.get("price_current"),
                    "market_cap": fields.get("market_cap"),
                    "eps": fields.get("eps"),
                    "pe": fields.get("pe"),
                    "fundamentals_raw_id": r.get("id"),
                }
            )

        if not out:
            print(f"[AVISO] Nenhum payload em fundamentals_raw para {day} (source={source}).")
            return

        sb.upsert("fundamentals_daily", out, on_conflict="ticker,date,source")
        rows_written = len(out)
        print(f"✅ {rows_written} linha(s) materializadas em fundamentals_daily para {day}")

    except Exception as e:
        status = "error"
        message = str(e)
        print(f"[ERRO] Falha ao materializar fundamentals_daily: {e}")
        if "PGRST205" in message and "fundamentals_daily" in message:
            print("[DICA] Rode a migração no Supabase: sql/008_add_fundamentals_daily.sql")
            return
        raise

    finally:
        finished_at = datetime.now(timezone.utc)
        log_job_run(
            sb,
            job_name="compute_fundamentals_daily",
            status=status,
            rows_processed=rows_written,
            message=message,
            started_at=started_at,
            finished_at=finished_at,
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Materializa fundamentals_daily a partir de fundamentals_raw")
    parser.add_argument("--date", type=str, default=None, help="Data YYYY-MM-DD (default: hoje)")
    parser.add_argument("--source", type=str, default="brapi", help="Fonte (default: brapi)")

    args = parser.parse_args()
    main(as_of=args.date, source=args.source)

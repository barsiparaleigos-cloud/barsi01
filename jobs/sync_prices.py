from __future__ import annotations

from datetime import datetime, timezone
from datetime import date

from jobs.common import get_supabase_admin_client, list_active_tickers, log_job_run


def main() -> None:
    sb = get_supabase_admin_client()
    started_at = datetime.now(timezone.utc)

    today = date.today().isoformat()

    # MVP: preços mock para validar pipeline/supabase. Trocar por integração real quando estiver pronto.
    mock_prices = {
        "ITUB4": 35.50,
        "BBAS3": 55.10,
        "BBDC4": 14.80,
        "TAEE11": 34.20,
        "WEGE3": 36.90,
        "EGIE3": 44.30,
        "ABEV3": 13.20,
    }

    tickers = list_active_tickers(sb)
    # Schema atual (Supabase): prices_daily(close, volume) + unique(ticker, date)
    rows = [
        {
            "date": today,
            "ticker": t,
            "close": float(mock_prices.get(t, 0.0)),
            "volume": None,
        }
        for t in tickers
    ]

    # Upsert por (date, ticker)
    status = "success"
    message = None
    try:
        sb.upsert("prices_daily", rows, on_conflict="ticker,date")
        print(f"✅ {len(rows)} preços atualizados para {today}")
    except Exception as e:
        status = "error"
        message = str(e)
        raise
    finally:
        finished_at = datetime.now(timezone.utc)
        log_job_run(
            sb,
            job_name="sync_prices",
            status=status,
            rows_processed=len(rows),
            message=message,
            started_at=started_at,
            finished_at=finished_at,
        )


if __name__ == "__main__":
    main()

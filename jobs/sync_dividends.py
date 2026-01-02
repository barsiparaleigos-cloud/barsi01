from __future__ import annotations

from datetime import datetime, timezone
from datetime import date, timedelta

from jobs.common import get_supabase_admin_client, list_active_tickers, log_job_run


def main() -> None:
    sb = get_supabase_admin_client()
    started_at = datetime.now(timezone.utc)

    # MVP: dividendos mock (trimestral), só para habilitar compute_signals.
    # Trocar por integração real quando estiver pronto.
    today = date.today()
    ex_dates = [today - timedelta(days=90), today - timedelta(days=180), today - timedelta(days=270), today - timedelta(days=360)]

    tickers = list_active_tickers(sb)

    rows = []
    for ticker in tickers:
        # valor simbólico, diferente por ticker para variar
        base = (sum(map(ord, ticker)) % 50) / 100.0  # 0.00 a 0.49
        amount = round(0.30 + base, 2)
        for ex_date in ex_dates:
            rows.append(
                {
                    "ex_date": ex_date.isoformat(),
                    "pay_date": (ex_date + timedelta(days=30)).isoformat(),
                    "ticker": ticker,
                    # Schema atual (Supabase): dividends(amount_per_share, type)
                    "amount_per_share": float(amount),
                    "type": "dividend",
                }
            )

    status = "success"
    message = None
    try:
        # Requer unique index para on_conflict (ver sql/002_align_schema.sql)
        sb.upsert("dividends", rows, on_conflict="ticker,ex_date,type,amount_per_share")
        print(f"✅ {len(rows)} dividendos sincronizados")
    except Exception as e:
        status = "error"
        message = str(e)
        raise
    finally:
        finished_at = datetime.now(timezone.utc)
        log_job_run(
            sb,
            job_name="sync_dividends",
            status=status,
            rows_processed=len(rows),
            message=message,
            started_at=started_at,
            finished_at=finished_at,
        )


if __name__ == "__main__":
    main()

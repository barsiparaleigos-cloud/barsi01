from __future__ import annotations

from datetime import date, timedelta

from jobs.common import TICKERS, get_supabase_admin_client


def main() -> None:
    sb = get_supabase_admin_client()

    # MVP: dividendos mock (trimestral), só para habilitar compute_signals.
    # Trocar por integração real quando estiver pronto.
    today = date.today()
    ex_dates = [today - timedelta(days=90), today - timedelta(days=180), today - timedelta(days=270), today - timedelta(days=360)]

    rows = []
    for ticker in TICKERS:
        # valor simbólico, diferente por ticker para variar
        base = (sum(map(ord, ticker)) % 50) / 100.0  # 0.00 a 0.49
        amount = round(0.30 + base, 2)
        for ex_date in ex_dates:
            rows.append(
                {
                    "ex_date": ex_date.isoformat(),
                    "pay_date": (ex_date + timedelta(days=30)).isoformat(),
                    "ticker": ticker,
                    "amount": float(amount),
                }
            )

    sb.upsert("dividends", rows)

    print(f"✅ {len(rows)} dividendos sincronizados")


if __name__ == "__main__":
    main()

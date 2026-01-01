from __future__ import annotations

from datetime import date

from jobs.common import TICKERS, get_supabase_admin_client


def main() -> None:
    sb = get_supabase_admin_client()

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

    rows = [{"date": today, "ticker": t, "price": float(mock_prices.get(t, 0.0))} for t in TICKERS]

    # Upsert por (date, ticker)
    sb.upsert("prices_daily", rows, on_conflict="date,ticker")

    print(f"✅ {len(rows)} preços atualizados para {today}")


if __name__ == "__main__":
    main()

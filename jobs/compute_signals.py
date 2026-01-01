from __future__ import annotations

from datetime import date
from datetime import datetime, timedelta

from jobs.common import TICKERS, get_supabase_admin_client


DESIRED_YIELD = 0.06  # 6% a.a.


def main() -> None:
    sb = get_supabase_admin_client()

    today = date.today().isoformat()

    prices = sb.select("prices_daily", f"select=date,ticker,price&date=eq.{today}")
    dividends = sb.select("dividends", "select=ex_date,ticker,amount")

    if not prices:
        raise RuntimeError(
            "Não há preços do dia em prices_daily. Rode jobs/sync_prices.py primeiro."
        )

    # Soma simples de dividendos na janela de 12 meses (em produção, ajustar regra se necessário)
    cutoff = datetime.fromisoformat(today) - timedelta(days=365)
    dividend_sum_by_ticker: dict[str, float] = {t: 0.0 for t in TICKERS}
    for row in dividends:
        try:
            ex_date = datetime.fromisoformat(str(row.get("ex_date")))
        except Exception:
            continue
        if ex_date < cutoff:
            continue
        ticker = str(row.get("ticker", "")).strip()
        if ticker not in dividend_sum_by_ticker:
            continue
        try:
            dividend_sum_by_ticker[ticker] += float(row.get("amount", 0.0) or 0.0)
        except Exception:
            continue

    out_rows: list[dict[str, object]] = []
    for p in prices:
        ticker = str(p.get("ticker", "")).strip()
        if ticker not in TICKERS:
            continue

        price_current = float(p.get("price", 0.0) or 0.0)
        div_sum = float(dividend_sum_by_ticker.get(ticker, 0.0))
        price_teto = (div_sum / DESIRED_YIELD) if div_sum > 0 else None
        below_teto = (price_current < price_teto) if price_teto is not None else None
        margin_to_teto = (
            round(((price_teto - price_current) / price_teto) * 100.0, 2)
            if price_teto not in (None, 0)
            else None
        )

        out_rows.append(
            {
                "date": today,
                "ticker": ticker,
                "price_current": price_current,
                "price_teto": price_teto,
                "below_teto": below_teto,
                "margin_to_teto": margin_to_teto,
            }
        )

    sb.upsert("signals_daily", out_rows, on_conflict="date,ticker")

    print(f"✅ {len(out_rows)} sinais calculados para {today}")

    ranking = [r for r in out_rows if r.get("price_teto") not in (None, 0) and r.get("margin_to_teto") is not None]
    ranking.sort(key=lambda r: float(r.get("margin_to_teto") or 0.0), reverse=True)
    if ranking:
        print("\n📊 RANKING: Ações abaixo do preço-teto")
        for i, r in enumerate(ranking):
            print(
                f"{i}  {r['ticker']:<6}  price_current={r['price_current']:.2f}  "
                f"price_teto={float(r['price_teto']):.2f}  margin_to_teto={float(r['margin_to_teto']):.2f}%"
            )


if __name__ == "__main__":
    main()

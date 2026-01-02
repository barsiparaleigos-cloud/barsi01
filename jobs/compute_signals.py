from __future__ import annotations

from datetime import date
from datetime import datetime, timedelta, timezone

from jobs.common import get_supabase_admin_client, list_active_tickers, log_job_run


DESIRED_YIELD = 0.06  # 6% a.a.


def main() -> None:
    sb = get_supabase_admin_client()
    started_at = datetime.now(timezone.utc)

    today = date.today().isoformat()

    tickers = list_active_tickers(sb)
    # Schema atual (Supabase): prefer `precos.fechamento` (Brapi) e cai para `prices_daily.close` (legado)
    prices: list[dict[str, object]] = []
    try:
        prices = sb.select("precos", f"select=data,ticker,fechamento&data=eq.{today}")
        # Normalizar para o shape usado abaixo
        prices = [
            {"date": r.get("data"), "ticker": r.get("ticker"), "close": r.get("fechamento")}
            for r in prices
        ]
    except Exception:
        prices = []

    if not prices:
        prices = sb.select("prices_daily", f"select=date,ticker,close&date=eq.{today}")
    dividends = sb.select("dividends", "select=ex_date,ticker,amount_per_share,type")

    if not prices:
        raise RuntimeError(
            "Não há preços do dia em prices_daily. Rode jobs/sync_prices.py primeiro."
        )

    # Soma simples de dividendos na janela de 12 meses (em produção, ajustar regra se necessário)
    cutoff = datetime.fromisoformat(today) - timedelta(days=365)
    dividend_sum_by_ticker: dict[str, float] = {t: 0.0 for t in tickers}
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
            dividend_sum_by_ticker[ticker] += float(row.get("amount_per_share", 0.0) or 0.0)
        except Exception:
            continue

    out_rows: list[dict[str, object]] = []
    for p in prices:
        ticker = str(p.get("ticker", "")).strip()
        if ticker not in tickers:
            continue

        price_current = float(p.get("close", 0.0) or 0.0)
        div_sum = float(dividend_sum_by_ticker.get(ticker, 0.0))
        # MVP: usa soma 12m como proxy para dpa_avg_5y (melhorar quando houver dados reais)
        dpa_avg_5y = div_sum if div_sum > 0 else None
        dy_target = DESIRED_YIELD

        price_teto = (float(dpa_avg_5y) / float(dy_target)) if dpa_avg_5y not in (None, 0) else None
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
                "dpa_avg_5y": dpa_avg_5y,
                "dy_target": dy_target,
                "price_teto": price_teto,
                "below_teto": below_teto,
                "margin_to_teto": margin_to_teto,
            }
        )

    status = "success"
    message = None
    try:
        # Requer unique index para on_conflict (ver sql/002_align_schema.sql)
        sb.upsert("signals_daily", out_rows, on_conflict="ticker,date")
        print(f"✅ {len(out_rows)} sinais calculados para {today}")
    except Exception as e:
        status = "error"
        message = str(e)
        raise
    finally:
        finished_at = datetime.now(timezone.utc)
        log_job_run(
            sb,
            job_name="compute_signals",
            status=status,
            rows_processed=len(out_rows),
            message=message,
            started_at=started_at,
            finished_at=finished_at,
        )

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

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

from jobs.common import SupabaseRestClient, get_supabase_admin_client, log_job_run, load_universo_mvp_tickers


@dataclass(frozen=True)
class PricePoint:
    ticker: str
    date: str
    close: float
    source: str


def _safe_float(value: object) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def _list_active_tickers(sb: SupabaseRestClient) -> list[str]:
    # Prefer ticker_mapping (mais alinhado com precos/dividends via Brapi)
    try:
        rows = sb.select("ticker_mapping", "select=ticker&ativo=eq.true&order=ticker.asc")
        tickers = [str(r.get("ticker", "")).strip() for r in rows]
        tickers = [t for t in tickers if t]
        if tickers:
            return tickers
    except Exception:
        pass

    # Fallback: assets
    try:
        rows = sb.select("assets", "select=ticker&is_active=eq.true&order=ticker.asc")
        tickers = [str(r.get("ticker", "")).strip() for r in rows]
        tickers = [t for t in tickers if t]
        if tickers:
            return tickers
    except Exception:
        pass

    return []


def _apply_universe_filter(tickers: list[str]) -> list[str]:
    universo = load_universo_mvp_tickers()
    if not universo:
        return tickers
    universo_set = set(universo)
    return [t for t in tickers if t in universo_set]


def _load_prices_for_day(sb: SupabaseRestClient, day: str) -> dict[str, PricePoint]:
    # Prefer tabela precos (brapi)
    prices: dict[str, PricePoint] = {}

    try:
        rows = sb.select(
            "precos",
            f"select=ticker,data,fechamento,fonte&data=eq.{day}",
        )
        for r in rows:
            ticker = str(r.get("ticker", "")).strip()
            close = _safe_float(r.get("fechamento"))
            if not ticker or close in (None, 0.0):
                continue
            prices[ticker] = PricePoint(ticker=ticker, date=day, close=close, source=str(r.get("fonte") or "precos"))
    except Exception:
        pass

    if prices:
        return prices

    # Fallback: prices_daily (schema antigo)
    try:
        rows = sb.select(
            "prices_daily",
            f"select=ticker,date,close&date=eq.{day}",
        )
        for r in rows:
            ticker = str(r.get("ticker", "")).strip()
            close = _safe_float(r.get("close"))
            if not ticker or close in (None, 0.0):
                continue
            prices[ticker] = PricePoint(ticker=ticker, date=day, close=close, source="prices_daily")
    except Exception:
        pass

    return prices


def main() -> None:
    sb = get_supabase_admin_client()
    started_at = datetime.now(timezone.utc)

    try:
        sb.count("dividend_metrics_daily")
    except Exception as e:
        raise RuntimeError(
            "Tabela dividend_metrics_daily não encontrada ou sem acesso. "
            "Aplique a migração `sql/009_add_dividend_metrics_daily.sql` no Supabase e rode novamente. "
            f"(detalhe: {e})"
        )

    today = date.today().isoformat()
    cutoff_12m = datetime.fromisoformat(today) - timedelta(days=365)
    cutoff_5y = datetime.fromisoformat(today) - timedelta(days=365 * 5)

    tickers = _apply_universe_filter(_list_active_tickers(sb))
    if not tickers:
        raise RuntimeError("Nenhum ticker ativo encontrado (ticker_mapping/assets).")

    prices_by_ticker = _load_prices_for_day(sb, today)
    if not prices_by_ticker:
        raise RuntimeError(
            "Não há preços do dia em precos ou prices_daily. Rode jobs/sync_precos_brapi.py (ou jobs/sync_prices.py)."
        )

    dividends = sb.select("dividends", "select=ex_date,ticker,amount_per_share,type")

    sum_12m: dict[str, float] = defaultdict(float)
    years_paid_5y: dict[str, set[int]] = defaultdict(set)

    for row in dividends:
        ticker = str(row.get("ticker", "")).strip()
        if not ticker:
            continue

        ex_date_raw = row.get("ex_date")
        if not ex_date_raw:
            continue

        try:
            ex_dt = datetime.fromisoformat(str(ex_date_raw))
        except Exception:
            # tenta normalizar 'YYYY-MM-DD'
            try:
                ex_dt = datetime.fromisoformat(str(ex_date_raw).split("T")[0])
            except Exception:
                continue

        amount = _safe_float(row.get("amount_per_share"))
        if amount is None:
            continue

        if ex_dt >= cutoff_12m:
            sum_12m[ticker] += amount

        if ex_dt >= cutoff_5y:
            years_paid_5y[ticker].add(ex_dt.year)

    out_rows: list[dict[str, object]] = []
    for ticker in tickers:
        price = prices_by_ticker.get(ticker)
        if not price:
            continue

        div_sum = float(sum_12m.get(ticker, 0.0))
        dy = (div_sum / price.close) if price.close else None

        years = years_paid_5y.get(ticker, set())
        years_count = int(len(years))
        score = (years_count / 5.0) * 100.0

        out_rows.append(
            {
                "ticker": ticker,
                "date": today,
                "price_current": price.close,
                "price_source": price.source,
                "dividends_sum_12m": round(div_sum, 6),
                "dividend_yield_12m": round(dy, 8) if dy is not None else None,
                "years_with_dividends_5y": years_count,
                "consistency_score_5y": round(score, 2),
            }
        )

    status = "success"
    message = None
    try:
        sb.upsert("dividend_metrics_daily", out_rows, on_conflict="ticker,date")
        print(f"✅ {len(out_rows)} métricas de dividendos calculadas para {today}")
    except Exception as e:
        status = "error"
        message = str(e)
        raise
    finally:
        finished_at = datetime.now(timezone.utc)
        log_job_run(
            sb,
            job_name="compute_dividend_metrics_daily",
            status=status,
            rows_processed=len(out_rows),
            message=message,
            started_at=started_at,
            finished_at=finished_at,
        )


if __name__ == "__main__":
    main()

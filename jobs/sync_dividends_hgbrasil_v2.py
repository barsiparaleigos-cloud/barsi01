"""Job: Sincronizar proventos (HG Brasil v2) -> Supabase.

Objetivo MVP:
- Usar HG Brasil como fonte de proventos (mais barato que Fintz).
- Persistir eventos em `dividends` (schema MVP) e também guardar payload bruto em `fundamentals_raw`.

Notas importantes:
- A tabela `dividends` do MVP aceita apenas types: dividend | jcp | special.
- HG Brasil v2 traz vários tipos (bonus_issue, amortization, etc). Aqui, persistimos apenas os
  tipos em dinheiro que ajudam no DPA/payout:
    - dividend -> dividend
    - interest_on_equity -> jcp
  (os demais são ignorados por enquanto, para não violar a constraint do schema.)

Uso:
  python -m jobs.sync_dividends_hgbrasil_v2

Env:
  HGBRASIL_KEY (obrigatório)
  HGBRASIL_DIVIDENDS_DAYS_AGO (opcional; default=1825 ~ 5 anos)
  UNIVERSE_MVP_PATH (opcional; default=data/universo_mvp.csv)
"""

from __future__ import annotations

import os
from datetime import date, datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

from dotenv import load_dotenv

from integrations.hgbrasil_integration import HGBrasilIntegration
from jobs.common import (
    get_supabase_admin_client,
    load_universo_mvp_tickers,
    log_job_run,
)


def _first_env(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "")
        if value and str(value).strip():
            return str(value).strip()
    return ""


def _normalize_type(hg_type: str) -> Optional[str]:
    t = (hg_type or "").strip().lower()
    if t == "dividend":
        return "dividend"
    if t in ("interest_on_equity", "jcp", "jscp"):
        return "jcp"
    # Outros tipos existem, mas o schema do MVP não suporta ainda.
    return None


def _to_date(value: Any) -> Optional[str]:
    if not value:
        return None
    s = str(value).strip()
    if not s:
        return None
    # HG costuma retornar YYYY-MM-DD ou ISO.
    if "T" in s:
        s = s.split("T")[0]
    return s


def _iter_dividend_rows(result_obj: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    symbol = str(result_obj.get("symbol") or result_obj.get("ticker") or "").strip().upper()
    if not symbol:
        return []

    series = result_obj.get("series")
    if not isinstance(series, list):
        return []

    out: List[Dict[str, Any]] = []
    for ev in series:
        if not isinstance(ev, dict):
            continue

        ev_type = _normalize_type(str(ev.get("type") or ""))
        if not ev_type:
            continue

        # Para o MVP, usamos com_date como ex_date.
        ex_date = _to_date(ev.get("com_date")) or _to_date(ev.get("approval_date"))
        if not ex_date:
            continue

        pay_date = _to_date(ev.get("payment_date"))

        amount = ev.get("amount")
        try:
            amount_per_share = float(amount)
        except Exception:
            continue

        if amount_per_share <= 0:
            continue

        out.append(
            {
                "ticker": symbol,
                "ex_date": ex_date,
                "pay_date": pay_date,
                "amount_per_share": amount_per_share,
                "type": ev_type,
            }
        )

    return out


def main(
    *,
    tickers: Optional[List[str]] = None,
    days_ago: Optional[int] = None,
    api_key: Optional[str] = None,
) -> None:
    started_at = datetime.now(timezone.utc)
    # Carregar .env.local (mesmo padrão dos jobs do projeto)
    load_dotenv(dotenv_path=".env.local", override=False)
    sb = get_supabase_admin_client()

    as_of = date.today().isoformat()

    if tickers is None:
        # Prefer universo MVP (se existir). Se não existir, não “chuta” universo grande.
        tickers = load_universo_mvp_tickers() or []

    tickers = [t.strip().upper() for t in (tickers or []) if t and str(t).strip()]
    tickers = list(dict.fromkeys(tickers))

    if not tickers:
        print("[AVISO] Sem tickers para processar (universo MVP vazio?).")
        return

    api_key = api_key or _first_env("HGBRASIL_KEY", "HG_BRASIL_KEY")
    if not api_key:
        print("[AVISO] HGBRASIL_KEY não configurada; pulando sync_dividends_hgbrasil_v2.")
        return

    if days_ago is None:
        days_ago = int(os.getenv("HGBRASIL_DIVIDENDS_DAYS_AGO") or "1825")

    hg = HGBrasilIntegration(api_key=api_key)

    status = "success"
    message: Optional[str] = None
    rows_written = 0
    events_written = 0

    try:
        # v2 aceita múltiplos tickers
        v2_tickers = ",".join([f"B3:{t}" for t in tickers])
        resp = hg.get_dividends_v2(v2_tickers, days_ago=int(days_ago))

        errors = resp.get("errors")
        if isinstance(errors, list) and errors:
            # Normalmente: [{code: 'UNAUTHORIZED_KEY', message: '...'}]
            first = errors[0] if isinstance(errors[0], dict) else None
            code = first.get("code") if first else None
            msg = first.get("message") if first else None
            raise RuntimeError(f"HG Brasil v2 dividends error ({code}): {msg or errors}")

        results = resp.get("results")
        if not isinstance(results, list):
            raise RuntimeError("Resposta HG Brasil dividends v2 inesperada (results não é list).")

        # Persistir raw por ticker em fundamentals_raw (source específico)
        raw_rows: List[Dict[str, Any]] = []
        dividend_rows: List[Dict[str, Any]] = []

        for r in results:
            if not isinstance(r, dict):
                continue
            symbol = str(r.get("symbol") or "").strip().upper()
            if not symbol:
                continue

            raw_rows.append(
                {
                    "ticker": symbol,
                    "as_of_date": as_of,
                    "source": "hgbrasil_dividends_v2",
                    "payload": {
                        "days_ago": int(days_ago),
                        "result": r,
                        "metadata": resp.get("metadata"),
                    },
                }
            )

            dividend_rows.extend(list(_iter_dividend_rows(r)))

        if raw_rows:
            sb.upsert("fundamentals_raw", raw_rows, on_conflict="ticker,as_of_date,source")
            rows_written = len(raw_rows)

        if dividend_rows:
            sb.upsert("dividends", dividend_rows, on_conflict="ticker,ex_date,type,amount_per_share")
            events_written = len(dividend_rows)

        print(
            f"✅ HG dividends v2: {rows_written} payload(s) raw salvos (fundamentals_raw) e "
            f"{events_written} evento(s) salvos em dividends (days_ago={days_ago})"
        )

    except Exception as e:
        status = "error"
        message = str(e)
        print(f"[ERRO] Falha no sync_dividends_hgbrasil_v2: {e}")
        raise

    finally:
        finished_at = datetime.now(timezone.utc)
        log_job_run(
            sb,
            job_name="sync_dividends_hgbrasil_v2",
            status=status,
            rows_processed=events_written,
            message=message,
            started_at=started_at,
            finished_at=finished_at,
        )


if __name__ == "__main__":
    main()

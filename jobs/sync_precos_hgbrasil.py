"""Job: Sincronizar preços via HG Brasil -> Supabase (tabela `precos`).

Objetivo MVP:
- Ter preço do dia para o universo MVP sem depender de B3/Fintz.
- Persistir em `precos` com `fonte='hgbrasil'`.

Uso:
  python -m jobs.sync_precos_hgbrasil

Env:
  HGBRASIL_KEY (obrigatório)
  UNIVERSE_MVP_PATH (opcional; default=data/universo_mvp.csv)
"""

from __future__ import annotations

import os
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

from integrations.hgbrasil_integration import HGBrasilIntegration
from jobs.common import get_supabase_admin_client, load_universo_mvp_tickers, log_job_run


def _first_env(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "")
        if value and str(value).strip():
            return str(value).strip()
    return ""


def _extract_symbol_payload(resp: Dict[str, Any], ticker: str) -> Optional[Dict[str, Any]]:
    results = resp.get("results")
    if not isinstance(results, dict):
        return None

    key = ticker.strip().upper()
    payload = results.get(key)
    if isinstance(payload, dict):
        return payload

    for _, v in results.items():
        if isinstance(v, dict):
            return v

    return None


def _extract_hg_error(resp: Dict[str, Any]) -> Optional[str]:
    """Extrai mensagens de erro padronizadas do HG Brasil."""
    results = resp.get("results")
    if isinstance(results, dict):
        if results.get("error") is True or results.get("erro") is True:
            msg = results.get("message") or results.get("mensagem")
            return str(msg) if msg else "HG Brasil retornou error=true"
    return None


def _parse_historical_prices(resp: Dict[str, Any], as_of: str) -> list[Dict[str, Any]]:
    """Tenta extrair preços diários do payload do endpoint v2/historical.

    Como a estrutura pode variar por plano/versão, este parser é tolerante.
    """
    out: list[Dict[str, Any]] = []
    results = resp.get("results")
    if not isinstance(results, list):
        return out

    for r in results:
        if not isinstance(r, dict):
            continue
        symbol = str(r.get("symbol") or r.get("ticker") or "").strip().upper()
        if not symbol:
            continue

        series = r.get("series")
        if not isinstance(series, list) or not series:
            continue

        # Pegar o último ponto da série.
        last = series[-1]
        if not isinstance(last, dict):
            continue

        # Campo de data pode vir como date/time/period.
        day = str(last.get("date") or last.get("day") or last.get("time") or "").strip()
        if day and "T" in day:
            day = day.split("T")[0]
        if not day:
            day = as_of

        # Campo de preço pode variar.
        price_value = last.get("close")
        if price_value is None:
            price_value = last.get("price")
        if price_value is None:
            price_value = last.get("value")

        try:
            close = float(price_value)
        except Exception:
            continue

        if close <= 0:
            continue

        out.append(
            {
                "ticker": symbol,
                "data": day,
                "fechamento": close,
                "moeda": "BRL",
                "fonte": "hgbrasil",
            }
        )

    return out


def main(*, tickers: Optional[List[str]] = None, api_key: Optional[str] = None) -> None:
    # Carregar .env.local (mesmo padrão dos jobs do projeto)
    load_dotenv(dotenv_path=".env.local", override=False)

    started_at = datetime.now(timezone.utc)
    sb = get_supabase_admin_client()

    as_of = date.today().isoformat()

    if tickers is None:
        tickers = load_universo_mvp_tickers() or []

    tickers = [t.strip().upper() for t in (tickers or []) if t and str(t).strip()]
    tickers = list(dict.fromkeys(tickers))

    if not tickers:
        print("[AVISO] Sem tickers para processar (universo MVP vazio?).")
        return

    api_key = api_key or _first_env("HGBRASIL_KEY", "HG_BRASIL_KEY")
    if not api_key:
        print("[AVISO] HGBRASIL_KEY não configurada; pulando sync_precos_hgbrasil.")
        return

    hg = HGBrasilIntegration(api_key=api_key)

    status = "success"
    message: Optional[str] = None
    rows_written = 0

    try:
        rows: List[Dict[str, Any]] = []

        # 1) Tentativa barata: 1 chamada para vários símbolos (v2/historical)
        try:
            symbols = ",".join([f"B3:{t}" for t in tickers])
            hist = hg.get_historical_v2(symbols=symbols, days_ago=1, sample_by="1d")
            err = _extract_hg_error(hist)
            if err:
                raise RuntimeError(err)
            rows = _parse_historical_prices(hist, as_of)
            if rows:
                print(f"[OK] Preços obtidos via v2/historical: {len(rows)}")
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"[AVISO] v2/historical falhou; fallback para stock_price. Motivo: {e}")

        # 2) Fallback: 1 chamada por ticker
        if not rows:
            for i, ticker in enumerate(tickers, start=1):
                print(f"[*] {i}/{len(tickers)}: {ticker}")
                resp = hg.get_stock_price(ticker)
                err = _extract_hg_error(resp)
                if err:
                    # Se o plano não permite, não adianta continuar iterando.
                    raise RuntimeError(err)
                payload = _extract_symbol_payload(resp, ticker)
                if not payload:
                    continue

                price = payload.get("price")
                try:
                    fechamento = float(price)
                except Exception:
                    continue

                if fechamento <= 0:
                    continue

                volume = payload.get("volume")
                change_percent = payload.get("change_percent")

                row: Dict[str, Any] = {
                    "ticker": ticker,
                    "data": as_of,
                    "fechamento": fechamento,
                    "volume": int(volume) if volume not in (None, "") else None,
                    "variacao_percentual": float(change_percent) if change_percent not in (None, "") else None,
                    "moeda": "BRL",
                    "fonte": "hgbrasil",
                }
                rows.append(row)

        if rows:
            sb.upsert("precos", rows, on_conflict="ticker,data,fonte")
            rows_written = len(rows)

        print(f"✅ {rows_written} preço(s) salvos em precos para {as_of} (fonte=hgbrasil)")

    except KeyboardInterrupt:
        status = "error"
        message = "interrupted"
        print("[AVISO] Interrompido pelo usuário (Ctrl+C)")
        raise
    except Exception as e:
        status = "error"
        message = str(e)
        print(f"[ERRO] Falha no sync_precos_hgbrasil: {e}")
        raise

    finally:
        finished_at = datetime.now(timezone.utc)
        log_job_run(
            sb,
            job_name="sync_precos_hgbrasil",
            status=status,
            rows_processed=rows_written,
            message=message,
            started_at=started_at,
            finished_at=finished_at,
        )


if __name__ == "__main__":
    main()

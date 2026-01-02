from __future__ import annotations

import json
from datetime import date
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

from jobs.common import TICKERS, get_supabase_admin_client, list_active_tickers, load_settings
from web.admin_integrations import (
    handle_brapi_get,
    handle_brapi_post,
    handle_fintz_get,
    handle_fintz_post,
    handle_hgbrasil_get,
    handle_hgbrasil_post,
    handle_cvm_get,
    handle_cvm_post,
    handle_b3_get,
    handle_b3_post,
)
from web.companies import (
    handle_empresas_list,
    handle_empresa_detail,
    handle_acoes_list,
    handle_stats,
)


def _mock_rows() -> list[dict[str, Any]]:
    today = date.today().isoformat()

    # Mesmos mocks do jobs/sync_prices.py
    mock_prices = {
        "ITUB4": 35.50,
        "BBAS3": 55.10,
        "BBDC4": 14.80,
        "TAEE11": 34.20,
        "WEGE3": 36.90,
        "EGIE3": 44.30,
        "ABEV3": 13.20,
    }

    # Mock simples de "preço teto" só para visual
    desired_yield = 0.06
    mock_dividend_sum_12m = {
        "ITUB4": 2.40,
        "BBAS3": 3.10,
        "BBDC4": 1.20,
        "TAEE11": 2.10,
        "WEGE3": 0.60,
        "EGIE3": 2.70,
        "ABEV3": 0.90,
    }

    rows: list[dict[str, Any]] = []
    for ticker in TICKERS:
        price_current = float(mock_prices.get(ticker, 0.0))
        div_sum = float(mock_dividend_sum_12m.get(ticker, 0.0))
        price_teto = (div_sum / desired_yield) if div_sum > 0 else None
        below_teto = (price_current < price_teto) if price_teto else None
        margin_to_teto = (
            round(((price_teto - price_current) / price_teto) * 100.0, 2)
            if price_teto not in (None, 0)
            else None
        )
        rows.append(
            {
                "date": today,
                "ticker": ticker,
                "price_current": price_current,
                "price_teto": None if price_teto is None else round(float(price_teto), 2),
                "below_teto": below_teto,
                "margin_to_teto": margin_to_teto,
                "source": "mock",
            }
        )

    rows.sort(key=lambda r: (r["margin_to_teto"] is None, -(r["margin_to_teto"] or 0.0)))
    return rows


def _try_load_supabase_rows() -> list[dict[str, Any]] | None:
    try:
        load_settings()
    except Exception:
        return None

    sb = get_supabase_admin_client()

    # Descobre a última data disponível em signals_daily
    try:
        latest = sb.select("signals_daily", "select=date&order=date.desc&limit=1")
    except Exception:
        return None

    if not latest:
        return []

    latest_date = str(latest[0].get("date", "")).strip()
    if not latest_date:
        return []

    rows = sb.select(
        "signals_daily",
        "select=date,ticker,price_current,price_teto,below_teto,margin_to_teto"
        f"&date=eq.{latest_date}&order=margin_to_teto.desc.nullslast",
    )

    for r in rows:
        r["source"] = "supabase"

    return rows


def _try_load_supabase_status() -> dict[str, Any] | None:
    try:
        load_settings()
    except Exception:
        return None

    sb = get_supabase_admin_client()

    status: dict[str, Any] = {
        "supabase": "ok",
        "active_tickers": list_active_tickers(sb),
        "latest_signals_date": None,
        "job_runs": {},
    }

    try:
        latest = sb.select("signals_daily", "select=date&order=date.desc&limit=1")
        if latest:
            status["latest_signals_date"] = str(latest[0].get("date"))
    except Exception:
        status["supabase"] = "error"

    for job in ("sync_prices", "sync_dividends", "compute_signals"):
        try:
            rows = sb.select(
                "job_runs",
                "select=job_name,status,rows_processed,message,finished_at"
                f"&job_name=eq.{job}&order=finished_at.desc&limit=1",
            )
            status["job_runs"][job] = (rows[0] if rows else None)
        except Exception:
            status["job_runs"][job] = None

    return status


def _try_load_supabase_stocks() -> list[dict[str, Any]] | None:
    """Retorna lista de stocks no formato esperado pelo webapp (React)."""
    try:
        load_settings()
    except Exception:
        return None

    sb = get_supabase_admin_client()

    # Última data em signals_daily
    try:
        latest = sb.select("signals_daily", "select=date&order=date.desc&limit=1")
    except Exception:
        return None

    if not latest:
        return []

    latest_date = str(latest[0].get("date", "")).strip()
    if not latest_date:
        return []

    # Puxa sinais + assets embutido (FK ticker -> assets)
    # PostgREST: assets(name,sector)
    rows = sb.select(
        "signals_daily",
        "select=ticker,date,price_current,price_teto,below_teto,margin_to_teto,dpa_avg_5y,dy_target,assets(name,sector)"
        f"&date=eq.{latest_date}",
    )

    out: list[dict[str, Any]] = []
    for r in rows:
        assets = r.get("assets") or {}
        company = (assets.get("name") or r.get("ticker") or "").strip()
        sector = (assets.get("sector") or "").strip() or "-"

        current = float(r.get("price_current") or 0.0)
        teto = float(r.get("price_teto") or 0.0)

        dpa = r.get("dpa_avg_5y")
        div_yield = 0.0
        try:
            dpa_f = float(dpa) if dpa is not None else 0.0
            if current > 0 and dpa_f > 0:
                div_yield = (dpa_f / current) * 100.0
        except Exception:
            div_yield = 0.0

        has_enough = current > 0 and teto > 0
        below = bool(r.get("below_teto") is True) if has_enough else False

        # MVP: consistência é um placeholder até termos dados reais melhores.
        consistency = 90 if div_yield > 0 else 0

        out.append(
            {
                "ticker": str(r.get("ticker") or "").strip(),
                "companyName": company,
                "sector": sector,
                "currentPrice": current,
                "ceilingPrice": teto,
                "dividendYield": round(div_yield, 2),
                "consistency": consistency,
                "belowCeiling": below,
            }
        )

    return out


def load_home_rows() -> list[dict[str, Any]]:
    rows = _try_load_supabase_rows()
    if rows is None:
        return _mock_rows()
    if rows:
        return rows
    return _mock_rows()


def load_home_status() -> dict[str, Any]:
    status = _try_load_supabase_status()
    if status is None:
        return {
            "supabase": "not_configured",
            "active_tickers": list(TICKERS),
            "latest_signals_date": None,
            "job_runs": {"sync_prices": None, "sync_dividends": None, "compute_signals": None},
        }
    return status


def _render_html(rows: list[dict[str, Any]]) -> str:
    today = date.today().isoformat()
    status = load_home_status()
    source = rows[0].get("source") if rows else "mock"

    active_count = len(status.get("active_tickers") or [])
    below_count = sum(1 for r in rows if r.get("below_teto") is True)
    best_margin = None
    margins = [r.get("margin_to_teto") for r in rows if r.get("margin_to_teto") is not None]
    if margins:
        best_margin = max(float(m) for m in margins)

    def fmt(v: Any) -> str:
        if v is None:
            return "-"
        if isinstance(v, bool):
            return "TRUE" if v else "FALSE"
        return str(v)

    def verdict(r: dict[str, Any]) -> tuple[str, str]:
        """Retorna (titulo, explicacao) em linguagem bem simples."""
        if r.get("price_teto") in (None, 0) or r.get("price_current") in (None, 0):
            return ("SEM DADOS", "Ainda não sabemos o preço certo para comparar.")
        if r.get("below_teto") is True:
            m = r.get("margin_to_teto")
            m_txt = "" if m is None else f" Está cerca de {fmt(m)}% abaixo do preço certo."
            return ("PODE COMPRAR", "Pelo nosso método, o preço está bom." + m_txt)
        return ("ESPERE", "Pelo nosso método, está caro agora. Espere baixar.")

    trs = "\n".join(
        "".join(
            [
                "<tr>",
                f"<td>{fmt(r.get('ticker'))}</td>",
                f"<td>{verdict(r)[0]}</td>",
                f"<td>{verdict(r)[1]}</td>",
                f"<td>{fmt(r.get('price_current'))}</td>",
                f"<td>{fmt(r.get('price_teto'))}</td>",
                "</tr>",
            ]
        )
        for r in rows
    )

    def fmt_run(job: str) -> str:
        jr = (status.get("job_runs") or {}).get(job)
        if not jr:
            return "-"
        s = str(jr.get("status", "-"))
        ts = str(jr.get("finished_at", "-"))
        n = jr.get("rows_processed")
        n_str = "-" if n is None else str(n)
        return f"{s} · rows={n_str} · {ts}"

    return f"""<!doctype html>
<html lang=\"pt-BR\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Dividendos para leigos — Home</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 24px; }}
    h1 {{ margin: 0 0 8px 0; }}
    .meta {{ margin: 0 0 16px 0; color: #444; }}
    table {{ border-collapse: collapse; width: 100%; max-width: 900px; }}
    th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
    th {{ background: #f6f6f6; }}
    code {{ background: #f2f2f2; padding: 2px 6px; border-radius: 6px; }}
  </style>
</head>
<body>
    <h1>Home — Motor de Dividendos (MVP)</h1>
        <p class=\"meta\">Data: <code>{today}</code> · Fonte: <code>{source}</code></p>

    <h2>Status</h2>
    <p class=\"meta\">Última data em <code>signals_daily</code>: <code>{fmt(status.get('latest_signals_date'))}</code></p>
    <p class=\"meta\">Ativos monitorados: <code>{active_count}</code> · Abaixo do teto: <code>{below_count}</code> · Melhor margem: <code>{fmt(best_margin)}</code></p>
    <p class=\"meta\">Últimos jobs: <code>sync_prices</code> ({fmt_run('sync_prices')}) · <code>sync_dividends</code> ({fmt_run('sync_dividends')}) · <code>compute_signals</code> ({fmt_run('compute_signals')})</p>

    <h2>Recomendação (bem simples)</h2>
  <table>
    <thead>
      <tr>
        <th>Ticker</th>
                <th>O que fazer</th>
                <th>Por quê</th>
                <th>Preço agora</th>
                <th>Preço certo (método)</th>
      </tr>
    </thead>
    <tbody>
      {trs}
    </tbody>
  </table>

    <p class=\"meta\">Regra: se estiver "PODE COMPRAR", o preço está bom pelo nosso método. Se estiver "ESPERE", espere baixar. Se estiver "SEM DADOS", precisamos de mais informação.</p>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/", "/index.html"):
            rows = load_home_rows()
            html = _render_html(rows)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return

        if self.path == "/api/home":
            rows = load_home_rows()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(rows, ensure_ascii=False).encode("utf-8"))
            return

        if self.path == "/api/status":
            st = load_home_status()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(st, ensure_ascii=False).encode("utf-8"))
            return

        if self.path.startswith("/api/stocks"):
            stocks = _try_load_supabase_stocks()
            if stocks is None:
                stocks = []
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(stocks, ensure_ascii=False).encode("utf-8"))
            return

        # Admin: integrações (GET)
        if self.path == "/api/admin/integrations/brapi":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(handle_brapi_get(), ensure_ascii=False).encode("utf-8"))
            return

        if self.path == "/api/admin/integrations/fintz":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(handle_fintz_get(), ensure_ascii=False).encode("utf-8"))
            return

        if self.path == "/api/admin/integrations/hgbrasil":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(handle_hgbrasil_get(), ensure_ascii=False).encode("utf-8"))
            return

        if self.path == "/api/admin/integrations/cvm":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(handle_cvm_get(), ensure_ascii=False).encode("utf-8"))
            return

        if self.path == "/api/admin/integrations/b3":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(handle_b3_get(), ensure_ascii=False).encode("utf-8"))
            return
        # Empresas: listagem e consulta
        if self.path == "/api/empresas":
            result = handle_empresas_list()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))
            return

        if self.path.startswith("/api/empresas/"):
            cnpj = self.path.split("/")[-1]
            result = handle_empresa_detail(cnpj)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))
            return

        if self.path == "/api/acoes":
            result = handle_acoes_list()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))
            return

        if self.path == "/api/stats":
            result = handle_stats()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))
            return
        self.send_response(404)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Not Found")

    def do_POST(self) -> None:  # noqa: N802
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        data = json.loads(body) if body else {}

        if self.path == "/api/admin/integrations/brapi":
            handle_brapi_post(data)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
            return

        if self.path == "/api/admin/integrations/fintz":
            handle_fintz_post(data)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
            return

        if self.path == "/api/admin/integrations/hgbrasil":
            handle_hgbrasil_post(data)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
            return

        if self.path == "/api/admin/integrations/cvm":
            handle_cvm_post(data)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
            return

        if self.path == "/api/admin/integrations/b3":
            handle_b3_post(data)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
            return

        self.send_response(404)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Not Found")


def main() -> None:
    host = "127.0.0.1"
    port = 8000
    httpd = HTTPServer((host, port), Handler)
    print(f"Home server running: http://{host}:{port}/")
    print(f"API: http://{host}:{port}/api/home")
    httpd.serve_forever()


if __name__ == "__main__":
    main()

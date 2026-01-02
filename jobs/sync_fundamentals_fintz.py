"""Job: Sincronizar fundamentos via Fintz -> Supabase

Armazena um snapshot bruto (JSON) em `fundamentals_raw`.

Nesta versão, usamos dois endpoints estáveis e fáceis de consumir:
- Indicadores mais recentes por ticker
- Itens contábeis mais recentes por ticker

Docs:
- https://docs.fintz.com.br/endpoints/bolsa/

Requer (Supabase): executar `sql/007_add_fundamentals_raw.sql`.
"""

from __future__ import annotations

import os
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

from integrations.fintz_integration import FintzIntegration
from jobs.common import get_supabase_admin_client, list_active_tickers, log_job_run


def _first_env(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "")
        if value and str(value).strip():
            return str(value).strip()
    return ""


def main(
    *,
    tickers: Optional[List[str]] = None,
    api_key: Optional[str] = None,
    tipo_periodo: Optional[str] = None,
    tipo_demonstracao: Optional[str] = None,
) -> None:
    started_at = datetime.now(timezone.utc)
    sb = get_supabase_admin_client()

    as_of = date.today().isoformat()

    if not tickers:
        tickers = list_active_tickers(sb)

    tickers = [t.strip().upper() for t in tickers if t and str(t).strip()]
    tickers = list(dict.fromkeys(tickers))

    if not tickers:
        print("[AVISO] Nenhum ticker ativo encontrado.")
        return

    api_key = api_key or _first_env("FINTZ_API_KEY", "FINTZ_KEY", "X_API_KEY")
    if not api_key:
        print(
            "[AVISO] FINTZ_API_KEY não configurada; pulando sync_fundamentals_fintz. "
            "Defina FINTZ_API_KEY em .env.local (veja .env.example)."
        )
        return

    fintz = FintzIntegration(api_key=api_key)

    status = "success"
    message: Optional[str] = None
    rows_written = 0

    try:
        for i, ticker in enumerate(tickers, start=1):
            print(f"[*] {i}/{len(tickers)}: {ticker}")

            indicadores = fintz.get_indicators_by_ticker(ticker)
            itens = fintz.get_accounting_items_by_ticker(
                ticker,
                tipo_periodo=tipo_periodo,
                tipo_demonstracao=tipo_demonstracao,
            )

            payload: Dict[str, Any] = {
                "ticker": ticker,
                "indicadores": indicadores,
                "itens_contabeis": itens,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "source_meta": {
                    "tipoPeriodo": tipo_periodo,
                    "tipoDemonstracao": tipo_demonstracao,
                },
            }

            row: Dict[str, Any] = {
                "ticker": ticker,
                "as_of_date": as_of,
                "source": "fintz",
                "payload": payload,
            }

            sb.upsert("fundamentals_raw", [row], on_conflict="ticker,as_of_date,source")
            rows_written += 1

        print(f"✅ {rows_written} payload(s) de fundamentos salvos em fundamentals_raw para {as_of} (fintz)")

    except Exception as e:
        status = "error"
        message = str(e)
        print(f"[ERRO] Falha ao sincronizar fundamentos Fintz: {e}")
        raise

    finally:
        finished_at = datetime.now(timezone.utc)
        log_job_run(
            sb,
            job_name="sync_fundamentals_fintz",
            status=status,
            rows_processed=rows_written,
            message=message,
            started_at=started_at,
            finished_at=finished_at,
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sincronizar fundamentos (payload bruto) via Fintz -> Supabase")
    parser.add_argument("--tickers", type=str, help="Lista de tickers separados por vírgula (opcional)")
    parser.add_argument("--api-key", type=str, default=None, help="Chave da Fintz (opcional; usa env FINTZ_API_KEY)")
    parser.add_argument(
        "--tipo-periodo",
        type=str,
        default=None,
        help="tipoPeriodo (12M, TRIMESTRAL, ANUAL) para itens contábeis (opcional)",
    )
    parser.add_argument(
        "--tipo-demonstracao",
        type=str,
        default=None,
        help="tipoDemonstracao (CONSOLIDADO, INDIVIDUAL) para itens contábeis (opcional)",
    )

    args = parser.parse_args()

    tickers_arg: Optional[List[str]] = None
    if args.tickers:
        tickers_arg = [t.strip() for t in str(args.tickers).split(",") if t.strip()]

    main(
        tickers=tickers_arg,
        api_key=args.api_key,
        tipo_periodo=args.tipo_periodo,
        tipo_demonstracao=args.tipo_demonstracao,
    )

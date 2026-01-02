"""Job: aplicar o Universo MVP (30–50 tickers) no Supabase.

Lê `data/universo_mvp.csv` e faz upsert na tabela `ticker_mapping` marcando
os tickers como `ativo=true` e `verificado=true`.

Por padrão:
- Não desativa outros tickers existentes.
- Não tenta inferir CNPJ/empresa_id.

Uso:
  python -m jobs.apply_universo_mvp

Opcional:
  UNIVERSE_MVP_PATH=data/universo_mvp.csv
"""

from __future__ import annotations

import csv
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from jobs.common import get_supabase_admin_client, log_job_run


@dataclass(frozen=True)
class UniversoRow:
    ticker: str
    nome: str | None
    setor_besst: str | None


def _infer_tipo_acao(ticker: str) -> str | None:
    # Heurística simples baseada no sufixo.
    t = ticker.strip().upper()
    if t.endswith("11"):
        return "UNIT"
    if t.endswith("3"):
        return "ON"
    if t.endswith("4"):
        return "PN"
    if t.endswith("5"):
        return "PNA"
    if t.endswith("6"):
        return "PNB"
    return None


def _load_universe_csv(path: Path) -> list[UniversoRow]:
    if not path.exists():
        raise FileNotFoundError(f"Universe file not found: {path}")

    rows: list[UniversoRow] = []

    with path.open("r", encoding="utf-8", newline="") as f:
        # Permite comentários (#...) em qualquer linha.
        raw_lines = [ln for ln in f.read().splitlines() if ln.strip() and not ln.lstrip().startswith("#")]

    reader = csv.DictReader(raw_lines)
    for r in reader:
        ticker = (r.get("ticker") or "").strip().upper()
        if not ticker:
            continue
        nome = (r.get("nome") or "").strip() or None
        setor = (r.get("setor_besst") or "").strip().upper() or None
        rows.append(UniversoRow(ticker=ticker, nome=nome, setor_besst=setor))

    # Dedup preservando ordem
    seen: set[str] = set()
    out: list[UniversoRow] = []
    for r in rows:
        if r.ticker in seen:
            continue
        seen.add(r.ticker)
        out.append(r)
    return out


def main() -> None:
    started_at = datetime.now(timezone.utc)
    status = "success"
    message: str | None = None
    rows_processed = 0

    universe_path = Path(os.getenv("UNIVERSE_MVP_PATH") or "data/universo_mvp.csv")

    sb = get_supabase_admin_client()

    try:
        universo = _load_universe_csv(universe_path)
        if not universo:
            print("[AVISO] Universo MVP vazio. Nada para aplicar.")
            return

        payload: list[dict[str, Any]] = []
        for r in universo:
            row: dict[str, Any] = {
                "ticker": r.ticker,
                "ativo": True,
                "verificado": True,
            }
            if r.nome:
                row["nome"] = r.nome
            tipo = _infer_tipo_acao(r.ticker)
            if tipo:
                row["tipo_acao"] = tipo
            payload.append(row)

        sb.upsert("ticker_mapping", payload, on_conflict="ticker")
        rows_processed = len(payload)
        print(f"[OK] Universo MVP aplicado em ticker_mapping: {rows_processed} tickers")

    except Exception as e:
        status = "error"
        message = str(e)
        raise

    finally:
        finished_at = datetime.now(timezone.utc)
        log_job_run(
            sb,
            job_name="apply_universo_mvp",
            status=status,
            rows_processed=rows_processed if status == "success" else 0,
            message=message,
            started_at=started_at,
            finished_at=finished_at,
        )


if __name__ == "__main__":
    main()

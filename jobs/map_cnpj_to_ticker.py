"""Job: mapear CNPJ (CVM) para ticker (B3).

Objetivo: preencher `ticker_mapping.cnpj` quando estiver nulo, usando heurística
de matching entre o nome retornado pela Brapi (longName/shortName) e a
`denominacao_social` da tabela `companies_cvm`.

Importante:
- Não marca `verificado=true` (apenas sugere o CNPJ).
- Não sobrescreve mapeamentos já existentes.
- Se BRAPI_API_KEY não estiver configurada, só funciona para tickers gratuitos
  (PETR4, MGLU3, VALE3, ITUB4).
"""

from __future__ import annotations

import os
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from integrations.brapi_integration import BrapiIntegration
from jobs.common import SupabaseRestClient, get_supabase_admin_client, log_job_run


STOPWORDS = {
    "sa",
    "s",
    "a",
    "s/a",
    "s.a",
    "s.a.",
    "cia",
    "companhia",
    "comp",
    "ltda",
    "holding",
    "do",
    "da",
    "das",
    "de",
    "dos",
    "e",
    "em",
    "no",
    "na",
    "nos",
    "nas",
    "brasil",
}


def _strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


_NON_ALNUM_RE = re.compile(r"[^a-z0-9 ]+")


def normalize_text(text: str) -> str:
    text = _strip_accents(text).lower().strip()
    text = text.replace("&", " e ")
    text = _NON_ALNUM_RE.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> list[str]:
    norm = normalize_text(text)
    tokens = [t for t in norm.split(" ") if t and len(t) >= 3]
    tokens = [t for t in tokens if t not in STOPWORDS]
    return tokens


def normalize_cnpj(cnpj: str) -> str:
    return "".join(ch for ch in str(cnpj or "") if ch.isdigit())


@dataclass(frozen=True)
class Company:
    cnpj: str
    name: str
    name_norm: str
    tokens: frozenset[str]


def _paged_select(sb: SupabaseRestClient, table: str, select: str, extra_filters: str = "") -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    limit = 1000
    offset = 0
    extra_filters = (extra_filters or "").lstrip("&")
    while True:
        query = f"select={select}&limit={limit}&offset={offset}"
        if extra_filters:
            query += "&" + extra_filters
        batch = sb.select(table, query)
        if not batch:
            break
        rows.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
    return rows


def load_companies(sb: SupabaseRestClient) -> tuple[list[Company], dict[str, list[int]]]:
    rows = _paged_select(sb, "companies_cvm", "cnpj,denominacao_social")
    companies: list[Company] = []
    token_index: dict[str, list[int]] = {}

    for r in rows:
        cnpj = normalize_cnpj(r.get("cnpj") or "")
        name = str(r.get("denominacao_social") or "").strip()
        if not cnpj or not name:
            continue
        name_norm = normalize_text(name)
        tokens = frozenset(tokenize(name))
        company = Company(cnpj=cnpj, name=name, name_norm=name_norm, tokens=tokens)
        idx = len(companies)
        companies.append(company)
        for tok in tokens:
            token_index.setdefault(tok, []).append(idx)

    return companies, token_index


def _candidate_indices(query_tokens: list[str], token_index: dict[str, list[int]]) -> list[int]:
    if not query_tokens:
        return []

    counts: Counter[int] = Counter()
    for tok in query_tokens:
        for idx in token_index.get(tok, []):
            counts[idx] += 1

    if not counts:
        return []

    # pega os melhores candidatos por overlap de tokens (barato)
    most_common = counts.most_common(400)
    return [idx for idx, _ in most_common]


def _score(query_norm: str, query_tokens: set[str], company: Company) -> float:
    if not query_norm or not company.name_norm:
        return 0.0
    if not query_tokens:
        return 0.0

    inter = query_tokens.intersection(company.tokens)
    token_overlap = len(inter) / max(1, len(query_tokens))
    seq = SequenceMatcher(None, query_norm, company.name_norm).ratio()
    return 0.6 * token_overlap + 0.4 * seq


def best_match(
    companies: list[Company],
    token_index: dict[str, list[int]],
    query_name: str,
) -> tuple[Company | None, float, float]:
    query_norm = normalize_text(query_name)
    qtokens = tokenize(query_name)
    qset = set(qtokens)
    cand_idxs = _candidate_indices(qtokens, token_index)
    if not cand_idxs:
        return None, 0.0, 0.0

    best: tuple[int, float] | None = None
    second: float = 0.0

    for idx in cand_idxs:
        c = companies[idx]
        sc = _score(query_norm, qset, c)
        if best is None or sc > best[1]:
            if best is not None:
                second = max(second, best[1])
            best = (idx, sc)
        else:
            second = max(second, sc)

    if best is None:
        return None, 0.0, 0.0
    return companies[best[0]], best[1], second


def _pick_company_name(quote: dict[str, Any] | None, fallback: str | None) -> str:
    if quote:
        for k in ("longName", "shortName", "name"):
            v = quote.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
    return (fallback or "").strip()


def run_job(sb: SupabaseRestClient) -> dict[str, int]:
    print("[INFO] Carregando companies_cvm...")
    companies, token_index = load_companies(sb)
    print(f"[OK] companies_cvm carregadas: {len(companies)}")

    print("[INFO] Buscando tickers sem CNPJ em ticker_mapping...")
    tickers = _paged_select(
        sb,
        "ticker_mapping",
        "ticker,nome,cnpj,verificado,ativo",
        "ativo=eq.true&cnpj=is.null",
    )

    limit_env = os.getenv("MAP_CNPJ_LIMIT")
    if limit_env:
        try:
            lim = int(limit_env)
            if lim > 0:
                tickers = tickers[:lim]
        except Exception:
            pass

    print(f"[OK] tickers candidatos: {len(tickers)}")

    api_key = os.getenv("BRAPI_API_KEY") or None
    brapi = BrapiIntegration(api_key=api_key)

    matched = 0
    no_brapi_quote = 0
    skipped_no_name = 0
    skipped_low_score = 0
    skipped_ambiguous = 0

    rows_to_upsert: list[dict[str, Any]] = []

    for t in tickers:
        ticker = str(t.get("ticker") or "").strip()
        if not ticker:
            continue

        # safety: não mexer em mapeamentos verificados
        if bool(t.get("verificado")):
            continue

        can_query = api_key is not None or ticker in BrapiIntegration.FREE_TICKERS
        quote: dict[str, Any] | None = None
        if can_query:
            try:
                data = brapi.get_quote(ticker)
                results = data.get("results") or []
                if results and isinstance(results[0], dict):
                    quote = results[0]
            except Exception:
                quote = None
        else:
            # Sem token (e não é um ticker gratuito): ainda dá para tentar pelo
            # nome já armazenado em ticker_mapping (ex.: vindo do quote/list).
            no_brapi_quote += 1

        company_name = _pick_company_name(quote, t.get("nome"))
        if not company_name:
            skipped_no_name += 1
            continue

        best, best_score, second_score = best_match(companies, token_index, company_name)
        if not best:
            skipped_low_score += 1
            continue

        # thresholds simples: score alto + não muito ambíguo
        if best_score < 0.78:
            skipped_low_score += 1
            continue
        if second_score and (best_score - second_score) < 0.04:
            skipped_ambiguous += 1
            continue

        rows_to_upsert.append({"ticker": ticker, "cnpj": best.cnpj})
        matched += 1
        print(f"[OK] {ticker}: {best.cnpj}  ({company_name} -> {best.name})")

        if len(rows_to_upsert) >= 200:
            try:
                sb.upsert("ticker_mapping", rows_to_upsert, on_conflict="ticker")
                rows_to_upsert.clear()
            except Exception as e:
                print(f"[ERRO] Falha no batch upsert: {e}")
                rows_to_upsert.clear()

    if rows_to_upsert:
        try:
            sb.upsert("ticker_mapping", rows_to_upsert, on_conflict="ticker")
        except Exception as e:
            print(f"[ERRO] Falha no batch upsert final: {e}")

    stats = {
        "candidates": len(tickers),
        "matched": matched,
        "no_brapi_quote": no_brapi_quote,
        "skipped_no_name": skipped_no_name,
        "skipped_low_score": skipped_low_score,
        "skipped_ambiguous": skipped_ambiguous,
    }
    return stats


def main() -> None:
    sb = get_supabase_admin_client()
    started_at = datetime.now(timezone.utc)
    status = "success"
    message = None
    stats: dict[str, int] = {}

    try:
        stats = run_job(sb)
        print("=" * 70)
        print("RELATORIO FINAL")
        for k, v in stats.items():
            print(f"- {k}: {v}")
        print("=" * 70)
    except Exception as e:
        status = "error"
        message = str(e)
        raise
    finally:
        finished_at = datetime.now(timezone.utc)
        log_job_run(
            sb,
            job_name="map_cnpj_to_ticker",
            status=status,
            rows_processed=int(stats.get("matched") or 0) if status == "success" else 0,
            message=message,
            started_at=started_at,
            finished_at=finished_at,
        )


if __name__ == "__main__":
    main()

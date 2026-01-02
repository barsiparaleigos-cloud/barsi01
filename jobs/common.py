from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from pathlib import Path
import csv

from dotenv import load_dotenv
import requests


@dataclass(frozen=True)
class Settings:
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str


def _first_env(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "")
        value = _sanitize_env_value(value)
        if value:
            return value
    return ""


def _sanitize_env_value(value: str) -> str:
    # Remove caracteres de controle (ex.: \x16) que podem aparecer por colagens/encoding.
    if not value:
        return ""
    cleaned = "".join(ch for ch in str(value) if ord(ch) >= 32)
    return cleaned.strip()


def _url_from_project_ref(project_ref: str) -> str:
    project_ref = _sanitize_env_value(project_ref)
    if not project_ref:
        return ""
    # Supabase URL padrão: https://<project_ref>.supabase.co
    return f"https://{project_ref}.supabase.co"


def load_settings() -> Settings:
    # Local dev: allow .env.local; CI: environment variables take precedence
    load_dotenv(dotenv_path=".env.local", override=False)

    supabase_url = _first_env(
        "SUPABASE_URL",
        "NEXT_PUBLIC_SUPABASE_URL",
        "PUBLIC_SUPABASE_URL",
    )

    if not supabase_url:
        supabase_project_ref = _first_env("SUPABASE_PROJECT_REF", "SUPABASE_PROJECT_ID")
        supabase_url = _url_from_project_ref(supabase_project_ref)

    # Validação mínima do formato da URL
    if supabase_url and not (supabase_url.startswith("https://") or supabase_url.startswith("http://")):
        raise RuntimeError(
            "SUPABASE_URL inválida (precisa começar com https://). "
            "Abra .env.local e corrija o valor."
        )

    supabase_anon_key = _first_env(
        "SUPABASE_ANON_KEY",
        "NEXT_PUBLIC_SUPABASE_ANON_KEY",
        "PUBLIC_SUPABASE_ANON_KEY",
    )

    supabase_service_role_key = _first_env(
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_SERVICE_KEY",
        "SUPABASE_SERVICE_ROLE",
        "SERVICE_ROLE_KEY",
    )

    missing: list[str] = []
    if not supabase_url:
        missing.append("SUPABASE_URL (or SUPABASE_PROJECT_REF)")
    if not supabase_anon_key and not supabase_service_role_key:
        missing.append("SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_ANON_KEY)")

    if missing:
        raise RuntimeError(
            "Missing env vars: "
            + ", ".join(missing)
            + ". Create .env.local from .env.example (local) or set GitHub Secrets (CI)."
        )

    return Settings(
        supabase_url=supabase_url,
        supabase_anon_key=supabase_anon_key,
        supabase_service_role_key=supabase_service_role_key,
    )


class SupabaseRestClient:
    def __init__(self, settings: Settings) -> None:
        self._base_rest = settings.supabase_url.rstrip("/") + "/rest/v1"

        # Reuse HTTP session (important on Windows to avoid repeated TLS/CA overhead)
        self._session = requests.Session()

        # Prefer service role for writes; fall back to anon (works if RLS is disabled
        # or policies allow the operation).
        auth_key = settings.supabase_service_role_key or settings.supabase_anon_key
        self._headers = {
            "apikey": auth_key,
            "Authorization": f"Bearer {auth_key}",
            "Content-Type": "application/json",
        }

    def select(self, table: str, query: str) -> list[dict[str, Any]]:
        # query exemplo: "select=date,ticker,price&date=eq.2026-01-01"
        url = f"{self._base_rest}/{table}?{query}"
        resp = self._session.get(url, headers=self._headers, timeout=30)
        if not resp.ok:
            raise RuntimeError(
                f"Supabase select failed ({resp.status_code}) {table}: {resp.text}"
            )
        data = resp.json()
        if not isinstance(data, list):
            raise RuntimeError(f"Unexpected response type from {table}: {type(data)}")
        return data

    def count(self, table: str, filters: str = "") -> int:
        """Retorna contagem exata de linhas via PostgREST.

        Usa `Prefer: count=exact` e interpreta o header `Content-Range`.
        `filters` deve ser um pedaço de querystring, ex.: "ticker=eq.ITUB4&date=gte.2026-01-01".
        """
        filters = (filters or "").lstrip("&").strip()
        query = "select=*&limit=1"
        if filters:
            query += "&" + filters
        url = f"{self._base_rest}/{table}?{query}"

        headers = dict(self._headers)
        headers["Prefer"] = "count=exact"

        def _parse_count(resp: requests.Response) -> int:
            content_range = resp.headers.get("Content-Range", "")
            # Ex.: "0-0/123" ou "*/123"
            if "/" in content_range:
                try:
                    return int(content_range.split("/")[-1])
                except Exception:
                    pass
            raise RuntimeError(f"Supabase count failed for {table}: missing/invalid Content-Range")

        # Prefer HEAD (mais leve). Se não suportado, cai para GET.
        resp = self._session.head(url, headers=headers, timeout=30)
        if resp.ok:
            return _parse_count(resp)

        resp = self._session.get(url, headers=headers, timeout=30)
        if not resp.ok:
            raise RuntimeError(
                f"Supabase count failed ({resp.status_code}) {table}: {resp.text}"
            )
        return _parse_count(resp)

    def upsert(self, table: str, rows: list[dict[str, Any]], on_conflict: str | None = None) -> None:
        url = f"{self._base_rest}/{table}"
        if on_conflict:
            url += f"?on_conflict={on_conflict}"

        headers = dict(self._headers)
        headers["Prefer"] = "resolution=merge-duplicates"

        resp = self._session.post(url, headers=headers, json=rows, timeout=60)
        if not resp.ok:
            raise RuntimeError(
                f"Supabase upsert failed ({resp.status_code}) {table}: {resp.text}"
            )


def get_supabase_admin_client() -> SupabaseRestClient:
    settings = load_settings()
    return SupabaseRestClient(settings)


TICKERS = ["ITUB4", "BBAS3", "BBDC4", "TAEE11", "WEGE3", "EGIE3", "ABEV3"]


def list_active_tickers(sb: SupabaseRestClient) -> list[str]:
    """Retorna tickers ativos para os jobs (MVP).

    Ordem de preferência:
    1) `ticker_mapping` (mais alinhado com precos/dividends)
    2) `assets` (legacy)
    3) fallback local `TICKERS`

    Se existir `data/universo_mvp.csv`, aplica filtro ao resultado.
    """
    # Prefer ticker_mapping
    try:
        rows = sb.select("ticker_mapping", "select=ticker&ativo=eq.true&order=ticker.asc")
        tickers = [str(r.get("ticker", "")).strip().upper() for r in rows]
        tickers = [t for t in tickers if t]
        if tickers:
            universo = load_universo_mvp_tickers()
            if universo:
                universo_set = set(universo)
                tickers = [t for t in tickers if t in universo_set]
            return tickers
    except Exception:
        pass

    # Fallback: assets
    try:
        rows = sb.select("assets", "select=ticker&is_active=eq.true&order=ticker.asc")
        tickers = [str(r.get("ticker", "")).strip().upper() for r in rows]
        tickers = [t for t in tickers if t]
        if tickers:
            universo = load_universo_mvp_tickers()
            if universo:
                universo_set = set(universo)
                tickers = [t for t in tickers if t in universo_set]
            return tickers
    except Exception:
        pass

    universo = load_universo_mvp_tickers()
    return universo or list(TICKERS)


def log_job_run(
    sb: SupabaseRestClient,
    *,
    job_name: str,
    status: str,
    rows_processed: int | None,
    message: str | None,
    started_at: datetime,
    finished_at: datetime,
) -> None:
    """Registra uma execução em job_runs.

    Observação: usamos insert via POST (upsert sem on_conflict) para manter simples.
    """
    payload = {
        "job_name": job_name,
        "status": status,
        "rows_processed": rows_processed,
        "message": message,
        "started_at": started_at.astimezone(timezone.utc).isoformat(),
        "finished_at": finished_at.astimezone(timezone.utc).isoformat(),
    }
    try:
        sb.upsert("job_runs", [payload])
    except BaseException:
        # Logging de jobs não pode quebrar o job principal
        return


def load_universo_mvp_tickers(path: str | None = None) -> list[str]:
    """Carrega tickers do universo MVP a partir de CSV.

    Formato esperado:
      ticker,nome,setor_besst

    Linhas começando com "#" são ignoradas.
    Se o arquivo não existir, retorna [].
    """
    csv_path = Path(path or os.getenv("UNIVERSE_MVP_PATH") or "data/universo_mvp.csv")
    if not csv_path.exists():
        return []

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        lines = [ln for ln in f.read().splitlines() if ln.strip() and not ln.lstrip().startswith("#")]

    reader = csv.DictReader(lines)
    tickers: list[str] = []
    seen: set[str] = set()
    for row in reader:
        t = str(row.get("ticker") or "").strip().upper()
        if not t or t in seen:
            continue
        seen.add(t)
        tickers.append(t)
    return tickers

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv
import requests


@dataclass(frozen=True)
class Settings:
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str


def load_settings() -> Settings:
    # Local dev: allow .env.local; CI: environment variables take precedence
    load_dotenv(dotenv_path=".env.local", override=False)

    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_anon_key = os.getenv("SUPABASE_ANON_KEY", "").strip()
    supabase_service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()

    missing = [
        name
        for name, value in [
            ("SUPABASE_URL", supabase_url),
            ("SUPABASE_ANON_KEY", supabase_anon_key),
            ("SUPABASE_SERVICE_ROLE_KEY", supabase_service_role_key),
        ]
        if not value
    ]
    if missing:
        raise RuntimeError(
            "Missing env vars: " + ", ".join(missing) + ". "
            "Create .env.local from .env.example (local) or set GitHub Secrets (CI)."
        )

    return Settings(
        supabase_url=supabase_url,
        supabase_anon_key=supabase_anon_key,
        supabase_service_role_key=supabase_service_role_key,
    )


def get_supabase_admin_client() -> Client:
class SupabaseRestClient:
    def __init__(self, settings: Settings) -> None:
        self._base_rest = settings.supabase_url.rstrip("/") + "/rest/v1"
        self._headers = {
            "apikey": settings.supabase_service_role_key,
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
            "Content-Type": "application/json",
        }

    def select(self, table: str, query: str) -> list[dict[str, Any]]:
        # query exemplo: "select=date,ticker,price&date=eq.2026-01-01"
        url = f"{self._base_rest}/{table}?{query}"
        resp = requests.get(url, headers=self._headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, list):
            raise RuntimeError(f"Unexpected response type from {table}: {type(data)}")
        return data

    def upsert(self, table: str, rows: list[dict[str, Any]], on_conflict: str | None = None) -> None:
        url = f"{self._base_rest}/{table}"
        if on_conflict:
            url += f"?on_conflict={on_conflict}"

        headers = dict(self._headers)
        headers["Prefer"] = "resolution=merge-duplicates"

        resp = requests.post(url, headers=headers, json=rows, timeout=60)
        resp.raise_for_status()


def get_supabase_admin_client() -> SupabaseRestClient:
    settings = load_settings()
    return SupabaseRestClient(settings)


TICKERS = ["ITUB4", "BBAS3", "BBDC4", "TAEE11", "WEGE3", "EGIE3", "ABEV3"]

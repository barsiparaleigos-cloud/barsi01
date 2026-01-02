from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter

try:
    # requests bundles urllib3; this import is stable in practice
    from urllib3.util.retry import Retry
except Exception:  # pragma: no cover
    Retry = None  # type: ignore


@dataclass(frozen=True)
class HttpConfig:
    timeout_seconds: int = 20
    retries_total: int = 5
    backoff_factor: float = 0.6
    pool_connections: int = 10
    pool_maxsize: int = 10


def build_retry_session(*, headers: Optional[dict[str, str]] = None, config: Optional[HttpConfig] = None) -> requests.Session:
    cfg = config or HttpConfig()

    session = requests.Session()
    if headers:
        session.headers.update(headers)

    if Retry is None:
        return session

    retry = Retry(
        total=cfg.retries_total,
        connect=cfg.retries_total,
        read=cfg.retries_total,
        status=cfg.retries_total,
        backoff_factor=cfg.backoff_factor,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "POST"}),
        raise_on_status=False,
        respect_retry_after_header=True,
    )

    adapter = HTTPAdapter(
        max_retries=retry,
        pool_connections=cfg.pool_connections,
        pool_maxsize=cfg.pool_maxsize,
    )
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def request_json(
    session: requests.Session,
    method: str,
    url: str,
    *,
    params: Optional[dict[str, Any]] = None,
    headers: Optional[dict[str, str]] = None,
    timeout_seconds: int = 20,
) -> Any:
    """HTTP request returning parsed JSON.

    Notes:
    - Adds a small manual sleep for 429 when Retry isn't available, or server ignores Retry-After.
    - Avoids echoing full URL (which may contain secrets) in error messages.
    """

    resp = session.request(method, url, params=params or {}, headers=headers, timeout=timeout_seconds)

    if resp.status_code == 429:
        retry_after = resp.headers.get("Retry-After")
        try:
            wait_s = int(retry_after) if retry_after else 0
        except Exception:
            wait_s = 0
        if wait_s > 0:
            time.sleep(min(wait_s, 10))

    if not resp.ok:
        # Try to extract structured error without leaking secrets.
        body_preview = (resp.text or "").strip()
        body_preview = body_preview[:500]  # keep logs small
        raise RuntimeError(f"HTTP {resp.status_code} {method} (response: {body_preview})")

    try:
        return resp.json()
    except json.JSONDecodeError as e:
        body_preview = (resp.text or "").strip()[:500]
        raise RuntimeError(f"Invalid JSON response ({e}): {body_preview}") from e

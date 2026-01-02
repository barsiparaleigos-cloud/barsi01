"""Integração Fintz (fintz.com.br)

Nesta fase, usamos endpoints estáveis de Bolsa B3 (Indicadores e Itens contábeis)
para montar um snapshot de fundamentos por ticker.

Docs:
- Autenticação: https://docs.fintz.com.br/autenticacao/
- Bolsa B3: https://docs.fintz.com.br/endpoints/bolsa/
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class FintzIntegration:
    BASE_URL = "https://api.fintz.com.br"

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None) -> None:
        self.api_key = api_key
        self.base_url = (base_url or self.BASE_URL).rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0"})
        if api_key:
            # Conforme docs: header X-API-Key (case-insensitive)
            self.session.headers.update({"X-API-Key": api_key})

    def _get(self, path: str, *, params: Optional[dict[str, Any]] = None, timeout: int = 20) -> Any:
        url = f"{self.base_url}{path}"
        resp = self.session.get(url, params=params or {}, timeout=timeout)
        if not resp.ok:
            raise RuntimeError(f"Fintz HTTP {resp.status_code} {path}: {resp.text}")
        return resp.json()

    def test_connection(self) -> Dict[str, Any]:
        # Probe simples em endpoint público da própria API (exige key; sem key retornará 401/403).
        try:
            endpoint = "/bolsa/b3/avista/busca"
            resp = self.session.get(f"{self.base_url}{endpoint}", params={"q": "ITUB"}, timeout=10)
            if resp.status_code in (200, 401, 403):
                return {
                    "status": "success" if resp.status_code == 200 else "partial",
                    "message": f"Reachable (HTTP {resp.status_code})",
                    "base_url": self.base_url,
                    "auth_configured": bool(self.api_key),
                }
            return {"status": "error", "message": f"HTTP {resp.status_code}", "base_url": self.base_url}
        except Exception as e:
            return {"status": "error", "message": f"Erro ao conectar com Fintz: {e}"}

    def search_assets(self, *, q: Optional[str] = None, classe: Optional[str] = None, ativo: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Busca/lista ativos negociados no mercado à vista da B3."""
        params: dict[str, Any] = {}
        if q:
            params["q"] = q
        if classe:
            params["classe"] = classe
        if ativo is not None:
            params["ativo"] = bool(ativo)

        data = self._get("/bolsa/b3/avista/busca", params=params)
        return data if isinstance(data, list) else []

    def get_indicators_by_ticker(self, ticker: str) -> List[Dict[str, Any]]:
        """Retorna todos os indicadores mais recentes por ticker."""
        ticker = str(ticker or "").strip().upper()
        if not ticker:
            return []
        data = self._get("/bolsa/b3/avista/indicadores/por-ticker", params={"ticker": ticker})
        return data if isinstance(data, list) else []

    def get_accounting_items_by_ticker(
        self,
        ticker: str,
        *,
        tipo_periodo: Optional[str] = None,
        tipo_demonstracao: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retorna os itens contábeis mais recentes por ticker."""
        ticker = str(ticker or "").strip().upper()
        if not ticker:
            return []

        params: dict[str, Any] = {"ticker": ticker}
        if tipo_periodo:
            params["tipoPeriodo"] = tipo_periodo
        if tipo_demonstracao:
            params["tipoDemonstracao"] = tipo_demonstracao

        data = self._get("/bolsa/b3/avista/itens-contabeis/por-ticker", params=params)
        return data if isinstance(data, list) else []

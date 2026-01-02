"""
Integração HG Brasil (cotações/mercado)

Objetivo (MVP):
- Testar conectividade com endpoint público.

Observação:
- A API suporta key via querystring; aqui é health-check simples.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)


class HGBrasilIntegration:
    BASE_URL = "https://api.hgbrasil.com/finance"
    STOCK_PRICE_PATH = "/stock_price"

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None) -> None:
        self.api_key = api_key
        self.base_url = (base_url or self.BASE_URL).rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0"})

    def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """Consulta dados de uma ação/FII via HG Brasil.

        Doc: GET https://api.hgbrasil.com/finance/stock_price?symbol=petr4&key=suachave
        """
        symbol = (symbol or "").strip()
        if not symbol:
            raise ValueError("symbol é obrigatório")
        if not self.api_key:
            raise RuntimeError("HG Brasil api_key não configurada")

        url = f"{self.base_url}{self.STOCK_PRICE_PATH}"
        params = {
            "symbol": symbol,
            "key": self.api_key,
        }

        resp = self.session.get(url, params=params, timeout=20)
        if resp.status_code != 200:
            raise RuntimeError(f"HG Brasil stock_price HTTP {resp.status_code}: {resp.text}")
        data = resp.json()
        if not isinstance(data, dict):
            raise RuntimeError(f"Resposta inesperada HG Brasil: {type(data)}")
        return data

    def test_connection(self) -> Dict[str, Any]:
        try:
            params = {"format": "json"}
            if self.api_key:
                params["key"] = self.api_key

            resp = self.session.get(self.base_url, params=params, timeout=10)
            if resp.status_code != 200:
                return {"status": "error", "message": f"HTTP {resp.status_code}", "base_url": self.base_url}

            try:
                _ = resp.json()
            except Exception:
                return {"status": "partial", "message": "Resposta OK, mas JSON inválido", "base_url": self.base_url}

            return {
                "status": "success",
                "message": "Conexão OK com HG Brasil",
                "base_url": self.base_url,
                "auth_configured": bool(self.api_key),
            }
        except Exception as e:
            return {"status": "error", "message": f"Erro ao conectar com HG Brasil: {e}"}

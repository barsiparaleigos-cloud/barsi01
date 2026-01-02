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

from integrations.http_utils import HttpConfig, build_retry_session, request_json

logger = logging.getLogger(__name__)


class HGBrasilIntegration:
    BASE_URL = "https://api.hgbrasil.com/finance"
    ROOT_URL = "https://api.hgbrasil.com"

    STOCK_PRICE_PATH = "/stock_price"
    TAXES_PATH = "/taxes"  # under /finance

    V2_DIVIDENDS_PATH = "/v2/finance/dividends"
    V2_INDICATORS_PATH = "/v2/finance/indicators"
    V2_HISTORICAL_PATH = "/v2/finance/historical"

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None) -> None:
        self.api_key = api_key
        self.base_url = (base_url or self.BASE_URL).rstrip("/")

        # Derive root URL for v2 endpoints.
        root = self.ROOT_URL
        if "/finance" in self.base_url:
            root = self.base_url.split("/finance")[0]
        self.root_url = root.rstrip("/")

        self._http_cfg = HttpConfig(timeout_seconds=20)
        self.session = build_retry_session(headers={"User-Agent": "Mozilla/5.0"}, config=self._http_cfg)

    def _get(self, url: str, *, params: Dict[str, Any], timeout: int = 20) -> Dict[str, Any]:
        data = request_json(self.session, "GET", url, params=params, timeout_seconds=timeout)
        if not isinstance(data, dict):
            raise RuntimeError(f"Resposta inesperada HG Brasil: {type(data)}")
        return data

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

        return self._get(url, params=params, timeout=20)

    def get_taxes(self) -> Dict[str, Any]:
        """Consulta taxas (CDI/SELIC etc.).

        Doc: GET https://api.hgbrasil.com/finance/taxes?key=SUACHAVE
        """
        if not self.api_key:
            raise RuntimeError("HG Brasil api_key não configurada")

        url = f"{self.base_url}{self.TAXES_PATH}"
        params = {"key": self.api_key}
        return self._get(url, params=params, timeout=20)

    def get_dividends_v2(
        self,
        tickers: str,
        *,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        date: Optional[str] = None,
        days_ago: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Consulta proventos (v2).

        Endpoint: GET /v2/finance/dividends?tickers=B3:PETR4&key=...
        """
        if not self.api_key:
            raise RuntimeError("HG Brasil api_key não configurada")
        tickers = (tickers or "").strip()
        if not tickers:
            raise ValueError("tickers é obrigatório")

        url = f"{self.root_url}{self.V2_DIVIDENDS_PATH}"
        params: Dict[str, Any] = {"tickers": tickers, "key": self.api_key}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if date:
            params["date"] = date
        if days_ago is not None:
            params["days_ago"] = int(days_ago)
        return self._get(url, params=params, timeout=30)

    def get_indicators_v2(
        self,
        tickers: str,
        *,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        date: Optional[str] = None,
        days_ago: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Consulta indicadores econômicos (v2)."""
        if not self.api_key:
            raise RuntimeError("HG Brasil api_key não configurada")
        tickers = (tickers or "").strip()
        if not tickers:
            raise ValueError("tickers é obrigatório")

        url = f"{self.root_url}{self.V2_INDICATORS_PATH}"
        params: Dict[str, Any] = {"tickers": tickers, "key": self.api_key}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if date:
            params["date"] = date
        if days_ago is not None:
            params["days_ago"] = int(days_ago)
        return self._get(url, params=params, timeout=30)

    def get_historical_v2(
        self,
        symbols: str,
        *,
        sample_by: str = "1d",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        date: Optional[str] = None,
        days_ago: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Consulta histórico (v2)."""
        if not self.api_key:
            raise RuntimeError("HG Brasil api_key não configurada")
        symbols = (symbols or "").strip()
        if not symbols:
            raise ValueError("symbols é obrigatório")

        url = f"{self.root_url}{self.V2_HISTORICAL_PATH}"
        params: Dict[str, Any] = {"symbols": symbols, "sample_by": sample_by, "key": self.api_key}

        # A API documenta que apenas UM filtro deve ser usado.
        if start_date and end_date:
            params["start_date"] = start_date
            params["end_date"] = end_date
        elif date:
            params["date"] = date
        elif days_ago is not None:
            params["days_ago"] = int(days_ago)

        return self._get(url, params=params, timeout=30)

    def test_connection(self) -> Dict[str, Any]:
        try:
            params = {"format": "json"}
            if self.api_key:
                params["key"] = self.api_key

            try:
                _ = self._get(self.base_url, params=params, timeout=10)
            except Exception as e:
                return {"status": "error", "message": f"HTTP error: {e}", "base_url": self.base_url}

            return {
                "status": "success",
                "message": "Conexão OK com HG Brasil",
                "base_url": self.base_url,
                "auth_configured": bool(self.api_key),
            }
        except Exception as e:
            return {"status": "error", "message": f"Erro ao conectar com HG Brasil: {e}"}

"""
Integração Yahoo Finance (backup/complemento)

Objetivo (MVP):
- Testar conectividade com o endpoint público de chart.

Observação:
- Yahoo muda detalhes com frequência; aqui é um health-check simples.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

import requests

logger = logging.getLogger(__name__)


class YahooIntegration:
    """Cliente mínimo para validação de conectividade com Yahoo Finance."""

    BASE_URL = "https://query1.finance.yahoo.com"

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0"})

    def test_connection(self, symbol: str = "ITUB4.SA") -> Dict[str, Any]:
        try:
            url = f"{self.BASE_URL}/v8/finance/chart/{symbol}"
            resp = self.session.get(url, timeout=10)
            if resp.status_code != 200:
                return {"status": "error", "message": f"HTTP {resp.status_code}"}

            try:
                _ = resp.json()
            except Exception:
                return {"status": "partial", "message": "Resposta OK, mas JSON inválido"}

            return {
                "status": "success",
                "message": "Conexão OK com Yahoo Finance",
                "base_url": self.BASE_URL,
                "sample_symbol": symbol,
            }
        except Exception as e:
            return {"status": "error", "message": f"Erro ao conectar com Yahoo: {e}"}

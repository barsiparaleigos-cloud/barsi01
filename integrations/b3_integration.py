"""
Integração B3 (fontes públicas / institucionais)

Objetivo (MVP):
- Testar conectividade com endpoint público usado no frontend/infra.

Observação:
- A B3 possui ofertas oficiais via API/FTP que exigem credenciais.
- Aqui usamos um endpoint público amplamente acessível para health-check.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

import requests

logger = logging.getLogger(__name__)


class B3Integration:
    """Cliente mínimo para validação de conectividade com a B3."""

    PUBLIC_LISTED_COMPANIES_URL = (
        "https://sistemaswebb3-listados.b3.com.br/"
        "listedCompaniesProxy/CompanyCall/GetInitialCompanies/"
        "eyJsYW5ndWFnZSI6InB0LWJyIn0="
    )

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0"})

    def test_connection(self) -> Dict[str, Any]:
        try:
            resp = self.session.get(self.PUBLIC_LISTED_COMPANIES_URL, timeout=10)
            if resp.status_code != 200:
                return {
                    "status": "error",
                    "message": f"HTTP {resp.status_code}",
                }

            # Algumas respostas vêm como JSON (dict). Apenas validar parse.
            try:
                _ = resp.json()
            except Exception:
                return {
                    "status": "partial",
                    "message": "Resposta OK, mas JSON inválido",
                }

            return {
                "status": "success",
                "message": "Conexão OK com endpoint público B3",
                "base_url": "https://sistemaswebb3-listados.b3.com.br",
            }
        except Exception as e:
            return {"status": "error", "message": f"Erro ao conectar com B3: {e}"}

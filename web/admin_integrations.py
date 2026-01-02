"""
Backend: Endpoints para gerenciar integrações (cápsulas isoladas).

Cada API tem seu próprio endpoint POST/GET:
- /api/admin/integrations/brapi
- /api/admin/integrations/fintz
- /api/admin/integrations/hgbrasil
- /api/admin/integrations/cvm

Armazenamento: JSON local (pode evoluir para Supabase depois).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Diretório onde ficam as configs (gitignored)
INTEGRATIONS_DIR = Path(__file__).parent.parent / "data" / "integrations"
INTEGRATIONS_DIR.mkdir(parents=True, exist_ok=True)


def _config_path(integration_name: str) -> Path:
    return INTEGRATIONS_DIR / f"{integration_name}.json"


def load_integration_config(integration_name: str) -> dict[str, Any] | None:
    """Carrega configuração de uma integração (cápsula isolada)."""
    path = _config_path(integration_name)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def save_integration_config(integration_name: str, config: dict[str, Any]) -> None:
    """Salva configuração de uma integração (cápsula isolada)."""
    path = _config_path(integration_name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


# Handlers para cada integração (modular, não monolítico)

def handle_brapi_get() -> dict[str, Any]:
    config = load_integration_config("brapi")
    if config is None:
        return {
            "enabled": False,
            "baseUrl": "https://brapi.dev/api",
            "endpoints": {
                "quote": "/quote",
                "dividends": "/dividends",
                "history": "/quote/{ticker}/history",
            },
            "rateLimit": {"requestsPerMinute": 60},
        }
    return config


def handle_brapi_post(config: dict[str, Any]) -> None:
    save_integration_config("brapi", config)


def handle_fintz_get() -> dict[str, Any]:
    config = load_integration_config("fintz")
    if config is None:
        return {
            "enabled": False,
            "baseUrl": "https://api.fintz.com.br/v1",
            "endpoints": {
                "fundamentals": "/stocks/{ticker}/fundamentals",
                "dividends": "/stocks/{ticker}/dividends",
                "balanceSheet": "/stocks/{ticker}/balance-sheet",
            },
            "rateLimit": {"requestsPerMinute": 30},
        }
    return config


def handle_fintz_post(config: dict[str, Any]) -> None:
    save_integration_config("fintz", config)


def handle_hgbrasil_get() -> dict[str, Any]:
    config = load_integration_config("hgbrasil")
    if config is None:
        return {
            "enabled": False,
            "baseUrl": "https://api.hgbrasil.com/finance",
            "endpoints": {
                "stocks": "/stock_price",
                "indexes": "/market_status",
                "currencies": "/currency",
            },
            "rateLimit": {"requestsPerMinute": 60},
        }
    return config


def handle_hgbrasil_post(config: dict[str, Any]) -> None:
    save_integration_config("hgbrasil", config)


def handle_cvm_get() -> dict[str, Any]:
    config = load_integration_config("cvm")
    if config is None:
        return {
            "enabled": False,
            "baseUrl": "https://dados.cvm.gov.br/dados",
            "endpoints": {
                "companies": "/CIA_ABERTA/CAD/DADOS",
                "dfp": "/CIA_ABERTA/DOC/DFP",
                "itr": "/CIA_ABERTA/DOC/ITR",
            },
            "requiresAuth": False,
            "cost": "Gratuito",
            "updateFrequency": "Diária (cadastro) / Semanal (demonstrações)",
            "dataFormat": "CSV em ZIP",
            "lastSync": None,
            "autoSync": True,
            "syncSchedule": "weekly",
            "notes": "Dados oficiais da CVM - Portal de Dados Abertos. Sem necessidade de API key ou autenticação.",
        }
    return config


def handle_cvm_post(config: dict[str, Any]) -> None:
    save_integration_config("cvm", config)


def handle_b3_get() -> dict[str, Any]:
    config = load_integration_config("b3")
    if config is None:
        return {
            "enabled": False,
            "apiKey": "",
            "apiSecret": "",
            "environment": "sandbox",
            "ftpEnabled": False,
            "ftpHost": "ftp.b3.com.br",
            "ftpUser": "",
            "ftpPassword": "",
            "dataSource": "api",
            "notes": "B3 oferece dados via API (requer credenciais) e FTP público (histórico).",
        }
    return config


def handle_b3_post(config: dict[str, Any]) -> None:
    save_integration_config("b3", config)


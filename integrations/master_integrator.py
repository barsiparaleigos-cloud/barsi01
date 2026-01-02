"""Integrador Master de APIs

Gerencia todas as fontes de dados para a metodologia de dividendos.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from integrations.brapi_integration import BrapiIntegration
from integrations.cvm_integration import CVMIntegration
from integrations.b3_integration import B3Integration
from integrations.yahoo_integration import YahooIntegration
from integrations.fintz_integration import FintzIntegration
from integrations.hgbrasil_integration import HGBrasilIntegration


class MasterIntegrator:
    """
    Integrador master que orquestra fontes de dados (cápsulas isoladas):
    - Brapi: preços/dividendos
    - CVM: dados oficiais (cadastro/demonstrações)
    - B3: dados corporativos (health-check público; API oficial exige credenciais)
    - Yahoo Finance: backup/complemento
    - Fintz: fundamentos (placeholder/health-check)
    - HG Brasil: cotações/mercado (health-check)
    """
    
    def __init__(
        self,
        brapi_key: Optional[str] = None,
        fintz_key: Optional[str] = None,
        hgbrasil_key: Optional[str] = None,
    ):
        self.brapi = BrapiIntegration(brapi_key)
        self.cvm = CVMIntegration()
        self.b3 = B3Integration()
        self.yahoo = YahooIntegration()
        self.fintz = FintzIntegration(api_key=fintz_key)
        self.hgbrasil = HGBrasilIntegration(api_key=hgbrasil_key)
        self.sources_status = {}

    @staticmethod
    def _normalize_test_result(test: Dict[str, Any]) -> Dict[str, Any]:
        raw = (test or {}).get("status")
        if raw == "success":
            return {"status": "online", "message": "OK"}
        if raw == "partial":
            return {"status": "partial", "message": test.get("message", "Partial")}
        if raw == "error":
            return {"status": "error", "message": test.get("message", "Error")}
        return {"status": "error", "message": str(test) if test else "Unknown"}
    
    def test_all_connections(self) -> Dict[str, Any]:
        """
        Testa conectividade com todas as APIs
        
        Returns:
            Dict com status de cada fonte
        """
        print("\n" + "=" * 70)
        print("TESTE DE CONECTIVIDADE - TODAS AS APIS")
        print("=" * 70)
        
        results: Dict[str, Any] = {}

        checks = [
            ("brapi", "Brapi", self.brapi.test_connection),
            ("cvm", "CVM", self.cvm.test_connection),
            ("b3", "B3", self.b3.test_connection),
            ("yahoo", "Yahoo", self.yahoo.test_connection),
            ("fintz", "Fintz", self.fintz.test_connection),
            ("hgbrasil", "HG Brasil", self.hgbrasil.test_connection),
        ]

        for idx, (key, label, fn) in enumerate(checks, start=1):
            print(f"\n[{idx}/{len(checks)}] Testando {label}...")
            try:
                test = fn()
                normalized = self._normalize_test_result(test)
                results[key] = normalized
                icon = {
                    "online": "[OK]",
                    "partial": "[AVISO]",
                    "error": "[ERRO]",
                }.get(normalized["status"], "[?]")
                print(f"  {icon} {label}: {normalized['message']}")
            except Exception as e:
                print(f"  [ERRO] {label}: {e}")
                results[key] = {"status": "error", "message": str(e)}
        
        # Resumo
        print("\n" + "=" * 70)
        print("RESUMO DE CONECTIVIDADE")
        print("=" * 70)
        
        online_count = sum(1 for r in results.values() if r['status'] == 'online')
        total_count = len(results)
        
        for source, result in results.items():
            status_icon = {
                'online': '[OK]',
                'offline': '[ERRO]',
                'partial': '[AVISO]',
                'error': '[ERRO]'
            }.get(result['status'], '[?]')
            
            print(f"{status_icon} {source.upper()}: {result['message']}")
        
        print(f"\n{online_count}/{total_count} APIs online")
        print("=" * 70)
        
        self.sources_status = results
        return results
    
    def get_available_sources(self) -> List[str]:
        """Retorna lista de fontes disponíveis"""
        if not self.sources_status:
            self.test_all_connections()
        
        return [
            source for source, status in self.sources_status.items()
            if status['status'] == 'online'
        ]
    
    def get_data_priority(self, data_type: str) -> List[str]:
        """
        Define prioridade de fontes por tipo de dado
        
        Args:
            data_type: 'prices', 'dividends', 'fundamentals', 'corporate'
        
        Returns:
            Lista ordenada de fontes (prioridade decrescente)
        """
        priorities = {
            'prices': ['brapi', 'yahoo', 'b3'],
            'dividends': ['brapi', 'cvm', 'b3'],
            'fundamentals': ['cvm', 'brapi'],
            'corporate': ['b3', 'cvm'],
            'indicators': ['brapi', 'cvm']
        }
        
        return priorities.get(data_type, ['brapi'])


def main():
    """Testa conectividade com todas as APIs"""
    integrator = MasterIntegrator()
    results = integrator.test_all_connections()
    
    print("\n[INFO] Fontes disponiveis:")
    available = integrator.get_available_sources()
    for source in available:
        print(f"  - {source.upper()}")
    
    print("\n[INFO] Prioridades por tipo de dado:")
    for data_type in ['prices', 'dividends', 'fundamentals', 'corporate']:
        priority = integrator.get_data_priority(data_type)
        print(f"  - {data_type}: {' > '.join(priority)}")


if __name__ == "__main__":
    main()

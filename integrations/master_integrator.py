"""
Integrador Master de APIs
Gerencia todas as fontes de dados para a metodologia Barsi
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from integrations.brapi_integration import BrapiIntegration


class MasterIntegrator:
    """
    Integrador master que orquestra todas as fontes de dados:
    - Brapi: Precos e dividendos (tempo real)
    - CVM: Dados fundamentalistas oficiais
    - B3: Dados corporativos
    - Yahoo Finance: Backup/complemento
    """
    
    def __init__(self, brapi_key: Optional[str] = None):
        self.brapi = BrapiIntegration(brapi_key)
        self.sources_status = {}
    
    def test_all_connections(self) -> Dict[str, Any]:
        """
        Testa conectividade com todas as APIs
        
        Returns:
            Dict com status de cada fonte
        """
        print("\n" + "=" * 70)
        print("TESTE DE CONECTIVIDADE - TODAS AS APIS")
        print("=" * 70)
        
        results = {}
        
        # 1. Brapi
        print("\n[1/4] Testando Brapi...")
        try:
            test = self.brapi.test_connection()
            if test.get('status') == 'success':
                print("  [OK] Brapi conectada")
                results['brapi'] = {'status': 'online', 'message': 'OK'}
            else:
                print("  [ERRO] Brapi falhou")
                results['brapi'] = {'status': 'offline', 'message': 'Falha na conexao'}
        except Exception as e:
            print(f"  [ERRO] Brapi: {e}")
            results['brapi'] = {'status': 'error', 'message': str(e)}
        
        # 2. CVM (API Dados Abertos)
        print("\n[2/4] Testando CVM API...")
        try:
            import requests
            resp = requests.get(
                "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/DADOS/itr_cia_aberta_2024.zip",
                timeout=10,
                stream=True
            )
            if resp.status_code == 200:
                print("  [OK] CVM API acessivel")
                results['cvm'] = {'status': 'online', 'message': 'OK'}
            else:
                print(f"  [AVISO] CVM retornou {resp.status_code}")
                results['cvm'] = {'status': 'partial', 'message': f'HTTP {resp.status_code}'}
        except Exception as e:
            print(f"  [ERRO] CVM: {e}")
            results['cvm'] = {'status': 'error', 'message': str(e)}
        
        # 3. B3 (Site institucional)
        print("\n[3/4] Testando B3...")
        try:
            resp = requests.get(
                "https://sistemaswebb3-listados.b3.com.br/listedCompaniesProxy/CompanyCall/GetInitialCompanies/eyJsYW5ndWFnZSI6InB0LWJyIn0=",
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=10
            )
            if resp.status_code == 200:
                print("  [OK] B3 API acessivel")
                results['b3'] = {'status': 'online', 'message': 'OK'}
            else:
                print(f"  [AVISO] B3 retornou {resp.status_code}")
                results['b3'] = {'status': 'partial', 'message': f'HTTP {resp.status_code}'}
        except Exception as e:
            print(f"  [ERRO] B3: {e}")
            results['b3'] = {'status': 'error', 'message': str(e)}
        
        # 4. Yahoo Finance (backup)
        print("\n[4/4] Testando Yahoo Finance...")
        try:
            resp = requests.get(
                "https://query1.finance.yahoo.com/v8/finance/chart/ITUB4.SA",
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=10
            )
            if resp.status_code == 200:
                print("  [OK] Yahoo Finance acessivel")
                results['yahoo'] = {'status': 'online', 'message': 'OK'}
            else:
                print(f"  [AVISO] Yahoo retornou {resp.status_code}")
                results['yahoo'] = {'status': 'partial', 'message': f'HTTP {resp.status_code}'}
        except Exception as e:
            print(f"  [ERRO] Yahoo: {e}")
            results['yahoo'] = {'status': 'error', 'message': str(e)}
        
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

"""Script de debug para verificar estrutura dos dividendos da Brapi"""
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from integrations.brapi_integration import BrapiIntegration
import json

brapi = BrapiIntegration()

print("Buscando ITUB4 com dividendos...")
response = brapi.get_quote(tickers='ITUB4', dividends=True)

if response and 'results' in response:
    quote = response['results'][0]
    
    print("\n=== ESTRUTURA COMPLETA ===")
    print(json.dumps(quote, indent=2, default=str))
    
    print("\n=== CAMPO dividendsData ===")
    dividends_data = quote.get('dividendsData', {})
    print(json.dumps(dividends_data, indent=2, default=str))
    
    print("\n=== EXTRAINDO DIVIDENDOS ===")
    extracted = brapi.extract_dividends(quote)
    print(f"Total extraído: {len(extracted)}")
    
    if extracted:
        print("\n=== PRIMEIROS 3 DIVIDENDOS ===")
        for i, div in enumerate(extracted[:3]):
            print(f"\nDividendo {i+1}:")
            print(json.dumps(div, indent=2, default=str))

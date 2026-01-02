"""
Debug script: inspeciona DRE do ITUB4 para entender por que lucro_liquido está null
"""
from jobs.common import get_supabase_admin_client

sb = get_supabase_admin_client()
rows = sb.select(
    'fundamentals_raw',
    'select=payload&ticker=eq.ITUB4&source=eq.cvm&order=as_of_date.desc&limit=1'
)

if not rows:
    print("❌ Nenhum DFP encontrado para ITUB4")
    exit(1)

payload = rows[0]['payload']
statements = payload.get('statements', {})
dre = statements.get('DRE', [])

print(f"✅ DRE do ITUB4 tem {len(dre)} linhas\n")
print("📋 Primeiras 20 contas da DRE:")
print("="*80)
for i, row in enumerate(dre[:20], 1):
    ds_conta = row.get('DS_CONTA', '')
    vl_conta = row.get('VL_CONTA', 0)
    print(f"{i:2d}. {ds_conta[:70]:<70} | {vl_conta:>15,.0f}")

print("\n🔍 Buscando contas com 'lucro' ou 'resultado':")
print("="*80)
for row in dre:
    ds_conta = row.get('DS_CONTA', '').lower()
    if 'lucro' in ds_conta or 'resultado' in ds_conta:
        vl_conta = row.get('VL_CONTA', 0)
        print(f"   {row.get('DS_CONTA')[:70]:<70} | {vl_conta:>15,.0f}")

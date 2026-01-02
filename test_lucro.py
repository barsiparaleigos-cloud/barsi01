import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from jobs.common import get_supabase_admin_client

sb = get_supabase_admin_client()

# Query ITUB4 latest DFP
print("🔍 Buscando DFP do ITUB4...")
result = sb.select(
    'fundamentals_raw',
    'select=payload&ticker=eq.ITUB4&source=eq.cvm&order=as_of_date.desc&limit=1'
)

if not result:
    print("❌ Nenhum DFP para ITUB4")
    sys.exit(1)

payload = result[0]['payload']
statements = payload.get('statements', {})
dre_rows = statements.get('DRE', [])

print(f"✅ Encontrei {len(dre_rows)} linhas na DRE\n")

# Mostra as primeiras 15 contas
print("=" * 100)
print("PRIMEIRAS 15 CONTAS DA DRE:")
print("=" * 100)
for i, row in enumerate(dre_rows[:15], 1):
    ds_conta = row.get('DS_CONTA', '')
    vl_conta = row.get('VL_CONTA', 0)
    cd_conta = str(row.get('CD_CONTA', ''))
    print(f"{i:2d}. [{cd_conta:15s}] {ds_conta[:65]:<65} | {vl_conta:>15,.0f}")

# Busca contas com 'lucro' ou 'resultado'
print("\n" + "=" * 100)
print("CONTAS COM 'LUCRO' OU 'RESULTADO':")
print("=" * 100)
count = 0
for row in dre_rows:
    ds_conta = row.get('DS_CONTA', '')
    ds_lower = ds_conta.lower()
    if 'lucro' in ds_lower or 'resultado' in ds_lower:
        vl_conta = row.get('VL_CONTA', 0)
        cd_conta = str(row.get('CD_CONTA', ''))
        print(f"[{cd_conta:15s}] {ds_conta[:65]:<65} | {vl_conta:>15,.0f}")
        count += 1

print(f"\n✅ Total: {count} contas encontradas")

import sys
sys.path.insert(0, "C:\\Users\\rafae\\OneDrive\\Desktop\\Barsi Para Leigos\\barsi01")

from jobs.common import get_supabase_admin_client

sb = get_supabase_admin_client()

print("="*100)
print("VALIDAÇÃO: Métricas de Lucro/ROE/Payout no Supabase")
print("="*100)

# Query ITUB4
rows = sb.select(
    'cvm_dfp_metrics_daily',
    'select=ticker,fiscal_year,patrimonio_liquido,lucro_liquido,roe_percent,payout_percent_keywords,divida_bruta,caixa_equivalentes,divida_liquida,divida_liquida_pl&ticker=eq.ITUB4&order=as_of_date.desc&limit=1'
)

if not rows:
    print("❌ Nenhuma linha para ITUB4")
    sys.exit(1)

row = rows[0]
print(f"\n✅ ITUB4 ({row['fiscal_year']}):")
print(f"   Patrimônio Líquido: {row.get('patrimonio_liquido'):,.0f}" if row.get('patrimonio_liquido') else "   Patrimônio Líquido: NULL")
print(f"   Dívida Bruta:       {row.get('divida_bruta'):,.0f}" if row.get('divida_bruta') else "   Dívida Bruta: NULL")
print(f"   Caixa/Equiv:        {row.get('caixa_equivalentes'):,.0f}" if row.get('caixa_equivalentes') else "   Caixa/Equiv: NULL")
print(f"   Dívida Líquida:     {row.get('divida_liquida'):,.0f}" if row.get('divida_liquida') else "   Dívida Líquida: NULL")
print(f"   Dívida Líq/PL:      {row.get('divida_liquida_pl'):.2f}" if row.get('divida_liquida_pl') else "   Dívida Líq/PL: NULL")
print(f"   Lucro Líquido:      {row.get('lucro_liquido'):,.0f}" if row.get('lucro_liquido') else "   Lucro Líquido: NULL ⚠️")
print(f"   ROE:                {row.get('roe_percent'):.2f}%" if row.get('roe_percent') else "   ROE: NULL ⚠️")
print(f"   Payout:             {row.get('payout_percent_keywords'):.2f}%" if row.get('payout_percent_keywords') else "   Payout: NULL ⚠️")

# Summary
metrics_ok = []
metrics_null = []

for k in ['patrimonio_liquido', 'divida_bruta', 'caixa_equivalentes', 'divida_liquida', 'divida_liquida_pl', 'lucro_liquido', 'roe_percent', 'payout_percent_keywords']:
    if row.get(k) is not None:
        metrics_ok.append(k)
    else:
        metrics_null.append(k)

print("\n" + "="*100)
print(f"RESUMO: {len(metrics_ok)}/8 métricas OK")
print("="*100)
if metrics_ok:
    print("✅ Métricas populadas:")
    for m in metrics_ok:
        print(f"   - {m}")
if metrics_null:
    print("\n⚠️  Métricas NULL:")
    for m in metrics_null:
        print(f"   - {m}")

if row.get('lucro_liquido') is not None:
    print("\n🎉 SUCESSO! Lucro líquido agora está populado!")
else:
    print("\n❌ PROBLEMA: Lucro líquido ainda NULL - keywords precisam ser revistos")

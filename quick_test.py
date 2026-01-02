import sys
import os
sys.path.insert(0, "C:\\Users\\rafae\\OneDrive\\Desktop\\Barsi Para Leigos\\barsi01")

from jobs.common import get_supabase_admin_client

sb = get_supabase_admin_client()
r = sb.select('fundamentals_raw', 'select=payload&ticker=eq.ITUB4&source=eq.cvm&order=as_of_date.desc&limit=1')
if r:
    p = r[0]['payload']
    dre = p.get('statements', {}).get('DRE', [])
    print(f"Total DRE rows: {len(dre)}")
    print("\nPrimeiras 10 contas:")
    for i, row in enumerate(dre[:10], 1):
        print(f"{i}. {row.get('DS_CONTA', 'N/A')}")
    print("\nContas com 'lucro':")
    for row in dre:
        ds = row.get('DS_CONTA', '')
        if 'lucro' in ds.lower():
            print(f"  - {ds}")

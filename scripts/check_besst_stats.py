#!/usr/bin/env python
"""
Script para verificar estatísticas das empresas BESST
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.models import Database

def main():
    print("\n" + "="*60)
    print("📊 ESTATÍSTICAS EMPRESAS BESST")
    print("="*60 + "\n")
    
    db = Database()
    
    # Total de empresas
    todas = db.get_all_empresas()
    print(f"✅ Total de empresas no banco: {len(todas)}")
    
    # Empresas BESST
    besst = db.get_empresas_besst()
    print(f"✅ Empresas BESST (monitoradas): {len(besst)}")
    print(f"   Percentual: {len(besst)/len(todas)*100:.1f}%\n")
    
    # Distribuição por setor
    print("📋 Distribuição por setor BESST:")
    cursor = db.connection.cursor()
    
    setores = {
        'B': 'Bancos',
        'E': 'Energia', 
        'S': 'Saneamento/Seguros',
        'T': 'Telecomunicações'
    }
    
    for letra, nome in setores.items():
        cursor.execute(
            "SELECT COUNT(*) FROM empresas WHERE setor_besst = ?",
            (letra,)
        )
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"  • {letra} ({nome}): {count} empresas")
    
    # Situação das empresas BESST
    print("\n📊 Situação das empresas BESST:")
    cursor.execute("""
        SELECT situacao, COUNT(*) as total
        FROM empresas 
        WHERE monitorar = TRUE
        GROUP BY situacao
        ORDER BY total DESC
    """)
    
    for row in cursor.fetchall():
        situacao, total = row
        print(f"  • {situacao}: {total} empresas")
    
    # Exemplos de empresas BESST
    print("\n📌 Exemplos de empresas BESST (primeiras 10):")
    besst_sample = db.get_empresas_besst()[:10]
    for emp in besst_sample:
        print(f"  • [{emp['setor_besst']}] {emp['razao_social']}")
    
    print("\n" + "="*60)
    print("✅ Análise concluída!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

"""
Job: Sincronizar Dados Fundamentalistas da CVM
Busca cadastro de empresas e dados fundamentalistas oficiais da CVM
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from integrations.cvm_integration import CVMIntegration
from jobs.common import SupabaseRestClient, load_settings, log_job_run


def sync_cadastro_to_supabase(sb: SupabaseRestClient, cvm: CVMIntegration) -> Dict[str, Any]:
    """
    Sincroniza cadastro de empresas CVM -> Supabase
    
    Args:
        sb: Cliente Supabase
        cvm: Cliente CVM
    
    Returns:
        Dict com estatísticas
    """
    print("\n[*] Baixando cadastro de empresas da CVM...")
    
    try:
        # Baixar cadastro
        df_cadastro = cvm.download_cadastro_empresas()
        
        print(f"[OK] {len(df_cadastro)} empresas no cadastro CVM")
        
        # Buscar empresas ativas
        empresas_ativas = df_cadastro[df_cadastro['SIT'] == 'ATIVO']
        
        print(f"[INFO] {len(empresas_ativas)} empresas ativas")
        
        # Preparar dados para Supabase
        rows_to_upsert = []
        
        for _, row in empresas_ativas.iterrows():
            cnpj = row.get('CNPJ_CIA', '').strip()
            
            if not cnpj:
                continue
            
            # Mapear campos CVM -> Supabase
            supabase_row = {
                'cnpj': cnpj,
                'cvm_code': row.get('CD_CVM', '').strip(),
                'denominacao_social': row.get('DENOM_SOCIAL', '').strip(),
                'denominacao_comercial': row.get('DENOM_COMERC', '').strip(),
                'setor_atividade': row.get('SETOR_ATIV', '').strip(),
                'uf': row.get('UF', '').strip(),
                'municipio': row.get('MUNIC', '').strip(),
                'data_registro_cvm': row.get('DT_REG', None),
                'data_constituicao': row.get('DT_CONST', None),
                'situacao_cvm': row.get('SIT', '').strip(),
                'updated_at': datetime.now().isoformat()
            }
            
            rows_to_upsert.append(supabase_row)
        
        print(f"\n[*] Preparados {len(rows_to_upsert)} registros para sync...")
        
        # UPSERT no Supabase (batch de 100)
        batch_size = 100
        total_saved = 0
        
        for i in range(0, len(rows_to_upsert), batch_size):
            batch = rows_to_upsert[i:i + batch_size]
            
            try:
                # Criar tabela companies_cvm se não existir
                sb.upsert(
                    "companies_cvm",
                    batch,
                    on_conflict="cnpj"
                )
                
                total_saved += len(batch)
                
                print(f"  Batch {i // batch_size + 1}: {len(batch)} registros salvos")
            
            except Exception as e:
                print(f"  [ERRO] Batch {i // batch_size + 1}: {e}")
        
        print(f"\n[OK] {total_saved} empresas sincronizadas no Supabase")
        
        return {
            'total_empresas': len(df_cadastro),
            'empresas_ativas': len(empresas_ativas),
            'sincronizadas': total_saved
        }
    
    except Exception as e:
        print(f"[ERRO] Falha ao sincronizar cadastro: {e}")
        raise


def main():
    """Executa sincronização de fundamentalistas CVM"""
    print("=" * 70)
    print("SINCRONIZACAO FUNDAMENTALISTAS: CVM -> SUPABASE")
    print("=" * 70)
    
    # Carregar configuração
    settings = load_settings()
    
    # Conectar Supabase
    print("\n[*] Conectando ao Supabase...")
    sb = SupabaseRestClient(
        url=settings["SUPABASE_URL"],
        key=settings["SERVICE_ROLE_KEY"]
    )
    print("[OK] Supabase conectado")
    
    # Conectar CVM
    print("\n[*] Inicializando CVM Integration...")
    cvm = CVMIntegration()
    print("[OK] CVM pronta")
    
    # Sincronizar cadastro
    try:
        result = sync_cadastro_to_supabase(sb, cvm)
        
        print("\n" + "=" * 70)
        print("RELATORIO FINAL")
        print("=" * 70)
        print(f"[INFO] Total empresas CVM: {result['total_empresas']}")
        print(f"[INFO] Empresas ativas: {result['empresas_ativas']}")
        print(f"[OK] Sincronizadas: {result['sincronizadas']}")
        print("=" * 70)
        
        # Registrar sucesso
        log_job_run(
            sb=sb,
            job_name="sync_fundamentals_cvm",
            status="success",
            rows_processed=result['sincronizadas'],
            error_message=None
        )
        
        print("\n[OK] Job registrado: success")
    
    except Exception as e:
        print("\n" + "=" * 70)
        print("[ERRO] FALHA NA SINCRONIZACAO")
        print("=" * 70)
        print(f"[ERRO] {str(e)}")
        print("=" * 70)
        
        # Registrar erro
        log_job_run(
            sb=sb,
            job_name="sync_fundamentals_cvm",
            status="error",
            rows_processed=0,
            error_message=str(e)
        )
        
        print("\n[OK] Job registrado: error")
        
        raise


if __name__ == "__main__":
    main()

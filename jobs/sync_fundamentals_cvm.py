"""
Job: Sincronizar Dados Fundamentalistas da CVM
Busca cadastro de empresas e dados fundamentalistas oficiais da CVM
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from integrations.cvm_integration import CVMIntegration
from jobs.common import SupabaseRestClient, get_supabase_admin_client, log_job_run


def _normalize_cnpj(cnpj: str) -> str:
    return "".join(c for c in str(cnpj or "") if c.isdigit())


def _json_safe(value: Any) -> str | None:
    if value is None:
        return None

    # pandas Timestamp / datetime / date
    if hasattr(value, "isoformat"):
        out = value.isoformat()
        return out if out not in ("NaT", "nan", "NaN") else None

    text = str(value).strip()
    if not text or text in ("NaT", "nan", "NaN", "None"):
        return None
    return text


def _safe_text(value: Any) -> str:
    if value is None:
        return ""
    # pandas NaN costuma virar float('nan')
    try:
        import math

        if isinstance(value, float) and math.isnan(value):
            return ""
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
    except Exception:
        pass

    text = str(value).strip()
    return "" if text in ("nan", "NaN", "None") else text


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
        
        # Preparar dados para Supabase (dedupe por CNPJ)
        rows_to_upsert = []
        seen_cnpjs: set[str] = set()
        duplicates_skipped = 0
        
        for _, row in empresas_ativas.iterrows():
            cnpj = _normalize_cnpj(row.get('CNPJ_CIA', ''))
            
            if not cnpj:
                continue

            if cnpj in seen_cnpjs:
                duplicates_skipped += 1
                continue
            seen_cnpjs.add(cnpj)
            
            # Mapear campos CVM -> Supabase
            supabase_row = {
                'cnpj': cnpj,
                'cvm_code': _safe_text(row.get('CD_CVM', '')),
                'denominacao_social': _safe_text(row.get('DENOM_SOCIAL', '')),
                'denominacao_comercial': _safe_text(row.get('DENOM_COMERC', '')),
                'setor_atividade': _safe_text(row.get('SETOR_ATIV', '')),
                'uf': _safe_text(row.get('UF', '')),
                'municipio': _safe_text(row.get('MUNIC', '')),
                'data_registro_cvm': _json_safe(row.get('DT_REG', None)),
                'data_constituicao': _json_safe(row.get('DT_CONST', None)),
                'situacao_cvm': _safe_text(row.get('SIT', '')),
                'updated_at': datetime.now().isoformat()
            }
            
            rows_to_upsert.append(supabase_row)
        
        # Defesa extra: garantir unicidade por CNPJ no payload final.
        # (Evita erro Postgres 21000 quando o mesmo CNPJ aparece duas vezes no mesmo upsert.)
        unique_by_cnpj: dict[str, dict[str, Any]] = {}
        for r in rows_to_upsert:
            cnpj = str(r.get("cnpj") or "")
            if not cnpj:
                continue
            unique_by_cnpj[cnpj] = r

        if len(unique_by_cnpj) != len(rows_to_upsert):
            duplicates_skipped += len(rows_to_upsert) - len(unique_by_cnpj)
            rows_to_upsert = list(unique_by_cnpj.values())

        print(f"\n[*] Preparados {len(rows_to_upsert)} registros para sync...")
        
        # UPSERT no Supabase (batch de 100)
        batch_size = 100
        total_saved = 0
        batch_errors = 0
        
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
                batch_errors += 1
        
        print(f"\n[OK] {total_saved} empresas sincronizadas no Supabase")
        if duplicates_skipped:
            print(f"[INFO] Duplicatas ignoradas (CNPJ repetido): {duplicates_skipped}")
        if batch_errors:
            print(f"[AVISO] Batches com erro: {batch_errors}")
        
        return {
            'total_empresas': len(df_cadastro),
            'empresas_ativas': len(empresas_ativas),
            'sincronizadas': total_saved,
            'duplicates_skipped': duplicates_skipped,
            'batch_errors': batch_errors,
        }
    
    except Exception as e:
        print(f"[ERRO] Falha ao sincronizar cadastro: {e}")
        raise


def main():
    """Executa sincronização de fundamentalistas CVM"""
    print("=" * 70)
    print("SINCRONIZACAO FUNDAMENTALISTAS: CVM -> SUPABASE")
    print("=" * 70)
    
    sb = get_supabase_admin_client()
    started_at = datetime.now(timezone.utc)
    status = "success"
    message = None
    result: Dict[str, Any] = {}

    # Conectar Supabase
    print("\n[*] Conectando ao Supabase...")
    print("[OK] Supabase conectado")
    
    # Conectar CVM
    print("\n[*] Inicializando CVM Integration...")
    cvm = CVMIntegration()
    print("[OK] CVM pronta")
    
    # Sincronizar cadastro
    try:
        result = sync_cadastro_to_supabase(sb, cvm)

        batch_errors = int(result.get("batch_errors") or 0)
        empresas_ativas = int(result.get("empresas_ativas") or 0)
        sincronizadas = int(result.get("sincronizadas") or 0)

        if batch_errors > 0:
            status = "error"
            message = f"{batch_errors} batch(es) falharam no upsert"
        elif empresas_ativas > 0 and sincronizadas == 0:
            status = "error"
            message = "Nenhuma empresa salva apesar de haver empresas ativas (verifique credenciais/RLS)"
        
        print("\n" + "=" * 70)
        print("RELATORIO FINAL")
        print("=" * 70)
        print(f"[INFO] Total empresas CVM: {result['total_empresas']}")
        print(f"[INFO] Empresas ativas: {result['empresas_ativas']}")
        print(f"[OK] Sincronizadas: {result['sincronizadas']}")
        print("=" * 70)
        
    except Exception as e:
        status = "error"
        message = str(e)
        print("\n" + "=" * 70)
        print("[ERRO] FALHA NA SINCRONIZACAO")
        print("=" * 70)
        print(f"[ERRO] {str(e)}")
        print("=" * 70)
        raise
    finally:
        finished_at = datetime.now(timezone.utc)
        log_job_run(
            sb,
            job_name="sync_fundamentals_cvm",
            status=status,
            rows_processed=int(result.get("sincronizadas") or 0),
            message=message,
            started_at=started_at,
            finished_at=finished_at,
        )

        print(f"\n[OK] Job registrado: {status}")


if __name__ == "__main__":
    main()

"""Job: Sincronizar dados de RI via CVM (FCA) -> Supabase

Objetivo (MVP): persistir contatos/canais oficiais de Relações com Investidores,
extraídos do Formulário Cadastral (FCA).

Fonte oficial:
- https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FCA/DADOS/

Requer (Supabase): executar `sql/010_add_relacoes_investidores.sql`.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Optional

from integrations.cvm_ri_integration import CVMRiIntegration
from jobs.common import get_supabase_admin_client, log_job_run


def main(*, year: int, limit: Optional[int] = None) -> None:
    sb = get_supabase_admin_client()
    started_at = datetime.now(timezone.utc)

    status = "success"
    message: Optional[str] = None
    rows_written = 0

    try:
        # Preflight: tabela existe e temos acesso
        try:
            sb.count("relacoes_investidores")
        except Exception as e:
            raise RuntimeError(
                "Tabela relacoes_investidores não encontrada ou sem acesso. "
                "Aplique `sql/010_add_relacoes_investidores.sql` no Supabase. "
                f"(detalhe: {e})"
            )

        cvm = CVMRiIntegration(timeout_seconds=180)

        print(f"[*] Baixando e parseando FCA {year} (CVM)...")
        snapshots = cvm.load_fca_snapshots(int(year))

        if limit is not None:
            snapshots = snapshots[: int(limit)]

        if not snapshots:
            print("[AVISO] Nenhum snapshot encontrado.")
            return

        batch_size = 100
        for i in range(0, len(snapshots), batch_size):
            batch = snapshots[i : i + batch_size]

            rows = []
            for s in batch:
                e = s.extracted
                rows.append(
                    {
                        "cnpj": s.cnpj,
                        "as_of_date": s.as_of_date,
                        "source": s.source,
                        "canal_divulgacao": e.get("canal_divulgacao"),
                        "dri_nome": e.get("dri_nome"),
                        "dri_email": e.get("dri_email"),
                        "dri_telefone": e.get("dri_telefone"),
                        "dept_acionistas_contato": e.get("dept_acionistas_contato"),
                        "dept_acionistas_email": e.get("dept_acionistas_email"),
                        "dept_acionistas_telefone": e.get("dept_acionistas_telefone"),
                        "endereco_logradouro": e.get("endereco_logradouro"),
                        "endereco_complemento": e.get("endereco_complemento"),
                        "endereco_bairro": e.get("endereco_bairro"),
                        "endereco_cidade": e.get("endereco_cidade"),
                        "endereco_uf": e.get("endereco_uf"),
                        "endereco_pais": e.get("endereco_pais"),
                        "endereco_cep": e.get("endereco_cep"),
                        "payload": s.payload,
                    }
                )

            sb.upsert("relacoes_investidores", rows, on_conflict="cnpj,as_of_date,source")
            rows_written += len(rows)
            print(f"  Batch {i // batch_size + 1}: {len(rows)} salvos")

        print(f"✅ {rows_written} registro(s) de RI salvos em relacoes_investidores")

    except Exception as e:
        status = "error"
        message = str(e)
        print(f"[ERRO] Falha no sync de RI CVM: {e}")
        raise

    finally:
        finished_at = datetime.now(timezone.utc)
        log_job_run(
            sb,
            job_name="sync_cvm_ri",
            status=status,
            rows_processed=rows_written,
            message=message,
            started_at=started_at,
            finished_at=finished_at,
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sincronizar RI (FCA) via CVM -> Supabase")
    parser.add_argument(
        "--year",
        type=int,
        default=(date.today().year - 1),
        help="Ano do FCA (default: ano anterior)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limita quantidade de CNPJs para teste (opcional)",
    )

    args = parser.parse_args()
    main(year=int(args.year), limit=args.limit)

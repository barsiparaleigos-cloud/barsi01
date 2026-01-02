"""Job: Materializar cvm_dfp_metrics_daily a partir de fundamentals_raw (source=cvm).

Esse job transforma o payload DFP (CVM) em colunas normalizadas para consumo
fácil (API/UI/ranking) sem precisar ler JSON gigante.

Requer (Supabase): executar `sql/011_add_cvm_dfp_metrics_daily.sql`.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional
import unicodedata

from jobs.common import get_supabase_admin_client, log_job_run


def _to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def _safe_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except Exception:
        return None


def _payload_get(payload: Any, *keys: str) -> Any:
    cur: Any = payload
    for k in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    return cur


def _as_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def _extract_from_statement_rows(
    rows: Any,
    *,
    as_of_date: str,
    keywords: List[str],
) -> Optional[float]:
    """Extrai um valor (heurístico) a partir de uma lista de linhas do demonstrativo.

    Estratégia:
    - filtra por DT_REFER == as_of_date (se possível)
    - filtra DS_CONTA contendo qualquer keyword
    - evita dupla contagem mantendo o nível mais agregado (menor profundidade de CD_CONTA)
    - soma VL_CONTA nesse nível
    """
    if not isinstance(rows, list) or not rows:
        return None

    def _norm_text(v: Any) -> str:
        s = str(v or "").strip().lower()
        # Remove acentos e normaliza para facilitar matching por keyword.
        s = unicodedata.normalize("NFKD", s)
        s = "".join(ch for ch in s if not unicodedata.combining(ch))
        # Remove caracteres de substituição comuns em textos com encoding ruim.
        s = s.replace("�", "")
        return s

    target = str(as_of_date or "").strip()
    same_date = [r for r in rows if isinstance(r, dict) and str(r.get("DT_REFER") or "").strip() == target]
    candidates = same_date if same_date else [r for r in rows if isinstance(r, dict)]
    if not candidates:
        return None

    keys = [_norm_text(k) for k in keywords if k and str(k).strip()]
    if not keys:
        return None

    matched: List[dict] = []
    for r in candidates:
        ds = _norm_text(r.get("DS_CONTA"))
        if not ds:
            continue
        if any(k in ds for k in keys):
            matched.append(r)

    if not matched:
        return None

    # Profundidade (menor = mais agregado)
    depths: List[tuple[int, Optional[float]]] = []
    for r in matched:
        cd = _norm_text(r.get("CD_CONTA"))
        depth = cd.count(".") if cd else 999
        depths.append((depth, _as_float(r.get("VL_CONTA"))))

    min_depth = min(d for d, _ in depths)
    total = 0.0
    has_any = False
    for r in matched:
        cd = _norm_text(r.get("CD_CONTA"))
        depth = cd.count(".") if cd else 999
        if depth != min_depth:
            continue
        v = _as_float(r.get("VL_CONTA"))
        if v is None:
            continue
        total += float(v)
        has_any = True

    return total if has_any else None


def _strip_keys(rows: List[Dict[str, Any]], keys: List[str]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        rr = dict(r)
        for k in keys:
            rr.pop(k, None)
        out.append(rr)
    return out


def main(*, year: int, max_rows: int = 5000) -> None:
    sb = get_supabase_admin_client()
    started_at = datetime.now(timezone.utc)

    status = "success"
    message: Optional[str] = None
    rows_written = 0

    try:
        start = date(int(year), 1, 1).isoformat()
        end = date(int(year), 12, 31).isoformat()

        raws = sb.select(
            "fundamentals_raw",
            "select=id,ticker,as_of_date,source,payload"
            f"&source=eq.cvm&as_of_date=gte.{start}&as_of_date=lte.{end}"
            f"&order=as_of_date.desc&limit={int(max_rows)}",
        )

        if not raws:
            print(f"[AVISO] Nenhum payload CVM (DFP) em fundamentals_raw para {year}.")
            return

        out: List[Dict[str, Any]] = []
        for r in raws:
            payload = r.get("payload") if isinstance(r, dict) else None
            if not isinstance(payload, dict):
                continue

            ticker = str(r.get("ticker") or "").strip().upper()
            as_of_date = str(r.get("as_of_date") or "").strip()
            if not ticker or not as_of_date:
                continue

            extracted = _payload_get(payload, "extracted")
            statements = _payload_get(payload, "statements")

            dre = statements.get("DRE") if isinstance(statements, dict) else None
            bpp = statements.get("BPP") if isinstance(statements, dict) else None
            bpa = statements.get("BPA") if isinstance(statements, dict) else None

            fiscal_year = _safe_int(_payload_get(payload, "year")) or int(year)
            cnpj = str(_payload_get(payload, "cnpj") or "").strip()

            extracted_dict = extracted if isinstance(extracted, dict) else {}

            # Dívida/caixa: tenta primeiro pelo extracted; se ausente, deriva dos statements
            divida_bruta = _to_float(extracted_dict.get("divida_bruta"))
            caixa_equivalentes = _to_float(extracted_dict.get("caixa_equivalentes"))
            divida_liquida = _to_float(extracted_dict.get("divida_liquida"))

            if divida_bruta is None:
                divida_bruta = _extract_from_statement_rows(
                    bpp,
                    as_of_date=as_of_date,
                    keywords=["emprest", "financi", "debent", "debênt", "arrend", "leasing", "capta"],
                )

            if caixa_equivalentes is None:
                caixa_equivalentes = _extract_from_statement_rows(
                    bpa,
                    as_of_date=as_of_date,
                    keywords=["caixa", "equival"],
                )

            if divida_liquida is None and divida_bruta is not None and caixa_equivalentes is not None:
                divida_liquida = float(divida_bruta) - float(caixa_equivalentes)

            # Lucro líquido (heurística) pela DRE
            # Nota: keywords com encoding ASCII para pegar mojibake de CSVs CVM
            lucro_liquido = _to_float(extracted_dict.get("lucro_liquido"))
            if lucro_liquido is None:
                lucro_liquido = _extract_from_statement_rows(
                    dre,
                    as_of_date=as_of_date,
                    keywords=[
                        "consolidado do periodo",  # pega "Lucro/Prejuízo Consolidado do Período"
                        "consolidado do exercicio",
                        "lucro liquido",
                        "resultado liquido",
                        "lucro atribuivel",
                    ],
                )

            # Derivados
            roe_percent: Optional[float] = None
            payout_percent_keywords: Optional[float] = None
            divida_liquida_pl: Optional[float] = None

            try:
                pl = _to_float(extracted_dict.get("patrimonio_liquido"))
                if pl is not None and pl != 0 and lucro_liquido is not None:
                    roe_percent = (float(lucro_liquido) / float(pl)) * 100.0
            except Exception:
                roe_percent = None

            try:
                prov = _to_float(extracted_dict.get("proventos_total_keywords"))
                if lucro_liquido is not None and float(lucro_liquido) > 0 and prov is not None:
                    payout_percent_keywords = (float(prov) / float(lucro_liquido)) * 100.0
            except Exception:
                payout_percent_keywords = None

            try:
                pl = _to_float(extracted_dict.get("patrimonio_liquido"))
                if pl is not None and pl != 0 and divida_liquida is not None:
                    divida_liquida_pl = float(divida_liquida) / float(pl)
            except Exception:
                divida_liquida_pl = None

            row = {
                "ticker": ticker,
                "as_of_date": as_of_date,
                "source": "cvm",
                "fiscal_year": fiscal_year,
                "cnpj": cnpj or None,
                "patrimonio_liquido": _to_float(extracted_dict.get("patrimonio_liquido")),
                "proventos_total_keywords": _to_float(extracted_dict.get("proventos_total_keywords")),
                "divida_bruta": divida_bruta,
                "caixa_equivalentes": caixa_equivalentes,
                "divida_liquida": divida_liquida,
                "lucro_liquido": lucro_liquido,
                "roe_percent": roe_percent,
                "payout_percent_keywords": payout_percent_keywords,
                "divida_liquida_pl": divida_liquida_pl,
                "dre_rows_count": len(dre) if isinstance(dre, list) else None,
                "bpp_rows_count": len(bpp) if isinstance(bpp, list) else None,
                "fundamentals_raw_id": r.get("id"),
            }
            out.append(row)

        if not out:
            print(f"[AVISO] Nada para materializar em cvm_dfp_metrics_daily para {year}.")
            return

        try:
            sb.upsert("cvm_dfp_metrics_daily", out, on_conflict="ticker,as_of_date,source")
        except Exception as e:
            # Compatibilidade: se a migration 012 (colunas de alavancagem) não foi aplicada,
            # tenta re-upsert sem as colunas novas.
            msg = str(e)
            if any(k in msg for k in ["divida_bruta", "caixa_equivalentes", "divida_liquida", "lucro_liquido", "roe_percent", "payout_percent_keywords", "divida_liquida_pl", "PGRST", "column"]):
                stripped = _strip_keys(
                    out,
                    [
                        "divida_bruta",
                        "caixa_equivalentes",
                        "divida_liquida",
                        "lucro_liquido",
                        "roe_percent",
                        "payout_percent_keywords",
                        "divida_liquida_pl",
                    ],
                )
                sb.upsert("cvm_dfp_metrics_daily", stripped, on_conflict="ticker,as_of_date,source")
            else:
                raise

        rows_written = len(out)
        print(f"✅ {rows_written} linha(s) materializadas em cvm_dfp_metrics_daily para {year}")

    except Exception as e:
        status = "error"
        message = str(e)
        print(f"[ERRO] Falha ao materializar cvm_dfp_metrics_daily: {e}")
        if "PGRST205" in (message or "") and "cvm_dfp_metrics_daily" in (message or ""):
            print("[DICA] Rode a migração no Supabase: sql/011_add_cvm_dfp_metrics_daily.sql")
            return
        raise

    finally:
        finished_at = datetime.now(timezone.utc)
        log_job_run(
            sb,
            job_name="compute_cvm_dfp_metrics_daily",
            status=status,
            rows_processed=rows_written,
            message=message,
            started_at=started_at,
            finished_at=finished_at,
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Materializa cvm_dfp_metrics_daily a partir de fundamentals_raw (source=cvm)")
    parser.add_argument("--year", type=int, required=True, help="Ano fiscal (ex: 2024)")
    parser.add_argument("--max-rows", type=int, default=5000, help="Limite de payloads lidos (default: 5000)")
    args = parser.parse_args()

    main(year=int(args.year), max_rows=int(args.max_rows))

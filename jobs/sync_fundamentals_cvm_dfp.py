"""Job: Sincronizar fundamentos (DFP) via CVM -> Supabase

Este job baixa o ZIP de DFP (demonstrações anuais) da CVM e salva um snapshot
por ticker em `fundamentals_raw`.

Observações importantes:
- A CVM distribui os dados em arquivos grandes (por ano) — não há endpoint por empresa.
- Aqui fazemos: baixar 1 ano e filtrar as linhas por CNPJ para cada ticker.
- O job existente `sync_fundamentals_cvm.py` continua focado no cadastro (companies_cvm).

Fonte oficial:
- https://dados.cvm.gov.br/

Requer (Supabase): executar `sql/007_add_fundamentals_raw.sql`.
"""

from __future__ import annotations

import os

from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

from integrations.cvm_integration import CVMIntegration
from jobs.common import get_supabase_admin_client, list_active_tickers, log_job_run


def _normalize_cnpj(cnpj: str) -> str:
    digits = "".join(c for c in str(cnpj or "") if c.isdigit())
    return digits.zfill(14) if digits else ""


def _df_filter_by_cnpj(df: Any, cnpj: str) -> Any:
    """Filtra DataFrame CVM por CNPJ (normalizado) de forma robusta."""
    if df is None:
        return None

    cnpj_norm = _normalize_cnpj(cnpj)
    if not cnpj_norm:
        return None

    try:
        series = df["CNPJ_CIA"].astype(str)
        # Normaliza CNPJ do CSV (remove não-dígitos e pad 14)
        series = series.str.replace(r"\D+", "", regex=True).str.zfill(14)
        return df[series == cnpj_norm]
    except Exception:
        return None


def _safe_date(value: Any) -> Optional[str]:
    if value is None:
        return None
    try:
        # pandas Timestamp/date
        if hasattr(value, "date"):
            return value.date().isoformat()
        if hasattr(value, "isoformat"):
            return value.isoformat()
    except Exception:
        pass
    text = str(value).strip()
    if not text:
        return None
    # Tipicamente já vem yyyy-mm-dd
    return text


def _df_rows_for_company(df: Any, cnpj: str, *, max_rows: int = 500) -> List[Dict[str, Any]]:
    """Converte um subconjunto do DataFrame em lista de dicts para JSON."""
    if df is None:
        return []

    sub = _df_filter_by_cnpj(df, cnpj)
    if sub is None:
        return []

    try:
        if len(sub) > max_rows:
            sub = sub.head(max_rows)
    except Exception:
        pass

    cols = [
        c
        for c in [
            "DT_REFER",
            "DENOM_CIA",
            "CD_CONTA",
            "DS_CONTA",
            "ORDEM_EXERC",
            "VL_CONTA",
            "VERSAO",
        ]
        if c in getattr(sub, "columns", [])
    ]

    try:
        if cols:
            sub = sub[cols]
        records = sub.to_dict(orient="records")
        # Normaliza DT_REFER (pandas Timestamp) para string
        for r in records:
            if "DT_REFER" in r:
                r["DT_REFER"] = _safe_date(r.get("DT_REFER"))
        return records
    except Exception:
        return []


def _pick_latest_metric(rows: List[Dict[str, Any]], key: str) -> Optional[float]:
    best_date = ""
    best_val: Optional[float] = None
    for r in rows:
        d = str(r.get("DT_REFER") or "")
        v = r.get(key)
        try:
            fv = float(v) if v is not None else None
        except Exception:
            fv = None
        if fv is None:
            continue
        if d >= best_date:
            best_date = d
            best_val = fv
    return best_val


def main(
    *,
    year: int,
    tickers: Optional[List[str]] = None,
    max_rows_per_statement: int = 500,
) -> None:
    started_at = datetime.now(timezone.utc)
    sb = get_supabase_admin_client()

    status = "success"
    message: Optional[str] = None
    rows_written = 0

    try:
        if not tickers:
            # Prefer tickers que já têm CNPJ (destrava ingestões CVM: DFP/FRE/RI)
            try:
                rows = sb.select(
                    "ticker_mapping",
                    "select=ticker&ativo=eq.true&cnpj=not.is.null&order=ticker.asc",
                )
                tickers = [str(r.get("ticker") or "").strip().upper() for r in rows]
                tickers = [t for t in tickers if t]
            except Exception:
                tickers = []

        if not tickers:
            tickers = list_active_tickers(sb)

        # CI safety: limitar quantidade de tickers por execução (opcional)
        limit_env = os.getenv("DFP_TICKER_LIMIT")
        if limit_env:
            try:
                lim = int(limit_env)
                if lim > 0:
                    tickers = tickers[:lim]
            except Exception:
                pass

        tickers = [t.strip().upper() for t in tickers if t and str(t).strip()]
        tickers = list(dict.fromkeys(tickers))

        if not tickers:
            print("[AVISO] Nenhum ticker ativo encontrado.")
            return

        # Carrega mapping ticker -> CNPJ (quando existir)
        mapping_rows = sb.select(
            "ticker_mapping",
            "select=ticker,cnpj&ativo=eq.true",
        )
        cnpj_by_ticker = {
            str(r.get("ticker") or "").strip().upper(): _normalize_cnpj(str(r.get("cnpj") or ""))
            for r in mapping_rows
            if isinstance(r, dict)
        }

        cvm = CVMIntegration()

        print(f"[*] Baixando DFP {year} da CVM (pode demorar)...")
        demonstracoes = cvm.download_dfp(int(year))
        df_dre = demonstracoes.get("DRE")
        df_bpp = demonstracoes.get("BPP")
        df_bpa = demonstracoes.get("BPA")

        if df_dre is None or df_bpp is None:
            raise RuntimeError("DFP sem DRE/BPP (zip incompleto ou formato inesperado)")

        for i, ticker in enumerate(tickers, start=1):
            print(f"[*] {i}/{len(tickers)}: {ticker}")
            cnpj = cnpj_by_ticker.get(ticker, "")
            if not cnpj:
                print("  [AVISO] Sem CNPJ no ticker_mapping; pulando.")
                continue

            # Extrai linhas (cruas) por empresa
            dre_rows = _df_rows_for_company(df_dre, cnpj, max_rows=max_rows_per_statement)
            bpp_rows = _df_rows_for_company(df_bpp, cnpj, max_rows=max_rows_per_statement)
            bpa_rows = _df_rows_for_company(df_bpa, cnpj, max_rows=max_rows_per_statement)

            # Métricas derivadas (opcional) usando utilitários da integração
            extracted: Dict[str, Any] = {}
            try:
                # Patrimônio Líquido
                bpp_sub = _df_filter_by_cnpj(df_bpp, cnpj)
                pl_df = cvm.extrair_patrimonio_liquido(bpp_sub) if bpp_sub is not None else None
                extracted["patrimonio_liquido"] = _pick_latest_metric(
                    pl_df.to_dict(orient="records") if pl_df is not None else [],
                    "PATRIMONIO_LIQUIDO",
                )
            except Exception:
                extracted["patrimonio_liquido"] = None

            try:
                # Dívida bruta (heurística)
                bpp_sub = _df_filter_by_cnpj(df_bpp, cnpj)
                div_df = cvm.extrair_divida_bruta(bpp_sub) if bpp_sub is not None else None
                extracted["divida_bruta"] = _pick_latest_metric(
                    div_df.to_dict(orient="records") if div_df is not None else [],
                    "DIVIDA_BRUTA",
                )
            except Exception:
                extracted["divida_bruta"] = None

            try:
                # Caixa e equivalentes (heurística) — requer BPA
                if df_bpa is None:
                    extracted["caixa_equivalentes"] = None
                else:
                    bpa_sub = _df_filter_by_cnpj(df_bpa, cnpj)
                    cx_df = cvm.extrair_caixa_equivalentes(bpa_sub) if bpa_sub is not None else None
                    extracted["caixa_equivalentes"] = _pick_latest_metric(
                        cx_df.to_dict(orient="records") if cx_df is not None else [],
                        "CAIXA_EQUIVALENTES",
                    )
            except Exception:
                extracted["caixa_equivalentes"] = None

            try:
                # Dívida líquida (quando ambos existem)
                d = extracted.get("divida_bruta")
                c = extracted.get("caixa_equivalentes")
                if d is None or c is None:
                    extracted["divida_liquida"] = None
                else:
                    extracted["divida_liquida"] = float(d) - float(c)
            except Exception:
                extracted["divida_liquida"] = None

            try:
                # Proventos encontrados por keyword (heurístico)
                dre_sub = _df_filter_by_cnpj(df_dre, cnpj)
                prov_df = cvm.extrair_dividendos(dre_sub) if dre_sub is not None else None
                extracted["proventos_total_keywords"] = _pick_latest_metric(
                    prov_df.to_dict(orient="records") if prov_df is not None else [],
                    "PROVENTOS_TOTAL",
                )
            except Exception:
                extracted["proventos_total_keywords"] = None

            # Define as_of_date como a última DT_REFER que aparecer nos dados filtrados
            latest_dates = [
                str(r.get("DT_REFER") or "")
                for r in (dre_rows + bpp_rows + bpa_rows)
                if r.get("DT_REFER")
            ]
            as_of = max(latest_dates) if latest_dates else date(int(year), 12, 31).isoformat()

            payload: Dict[str, Any] = {
                "ticker": ticker,
                "cnpj": cnpj,
                "year": int(year),
                "statements": {
                    "DRE": dre_rows,
                    "BPP": bpp_rows,
                    "BPA": bpa_rows,
                },
                "extracted": extracted,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

            row = {
                "ticker": ticker,
                "as_of_date": as_of,
                "source": "cvm",
                "payload": payload,
            }
            sb.upsert("fundamentals_raw", [row], on_conflict="ticker,as_of_date,source")
            rows_written += 1

        print(f"✅ {rows_written} payload(s) DFP salvos em fundamentals_raw (source=cvm)")

    except Exception as e:
        status = "error"
        message = str(e)
        print(f"[ERRO] Falha ao sincronizar DFP CVM: {e}")
        raise

    finally:
        finished_at = datetime.now(timezone.utc)
        log_job_run(
            sb,
            job_name="sync_fundamentals_cvm_dfp",
            status=status,
            rows_processed=rows_written,
            message=message,
            started_at=started_at,
            finished_at=finished_at,
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sincronizar fundamentos (DFP) via CVM -> Supabase")
    parser.add_argument("--year", type=int, required=True, help="Ano fiscal da DFP (ex: 2024)")
    parser.add_argument("--tickers", type=str, default=None, help="Lista de tickers separados por vírgula (opcional)")
    parser.add_argument(
        "--max-rows",
        type=int,
        default=500,
        help="Máximo de linhas por demonstrativo para salvar no payload (default: 500)",
    )

    args = parser.parse_args()

    tickers_arg: Optional[List[str]] = None
    if args.tickers:
        tickers_arg = [t.strip() for t in str(args.tickers).split(",") if t.strip()]

    main(year=int(args.year), tickers=tickers_arg, max_rows_per_statement=int(args.max_rows))

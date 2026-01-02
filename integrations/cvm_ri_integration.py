from __future__ import annotations

import csv
import io
import zipfile
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable

import requests


def _normalize_cnpj(cnpj: str) -> str:
    return "".join(ch for ch in str(cnpj or "") if ch.isdigit())


def _safe_int(value: object) -> int:
    try:
        return int(str(value).strip())
    except Exception:
        return 0


def _safe_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return "" if text in ("nan", "NaN", "None") else text


@dataclass(frozen=True)
class CvmRiSnapshot:
    cnpj: str
    as_of_date: str
    source: str
    payload: dict[str, Any]
    extracted: dict[str, Any]


class CVMRiIntegration:
    """Baixa e parseia dados de RI via CVM (FCA/FRE).

    Fonte (arquivos):
    - https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FCA/DADOS/
    - https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/DADOS/

    MVP: FCA (dri, departamento_acionistas, endereco, canal_divulgacao).
    """

    FCA_BASE = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FCA/DADOS"

    def __init__(self, *, timeout_seconds: int = 180) -> None:
        self._timeout_seconds = int(timeout_seconds)

    def download_fca_zip(self, year: int) -> bytes:
        url = f"{self.FCA_BASE}/fca_cia_aberta_{int(year)}.zip"
        resp = requests.get(url, timeout=self._timeout_seconds)
        resp.raise_for_status()
        return resp.content

    def _iter_csv_rows(self, z: zipfile.ZipFile, filename: str) -> Iterable[dict[str, str]]:
        with z.open(filename) as f:
            raw = f.read()
        # CVM normalmente usa latin1 e separador ;
        text = raw.decode("latin1", errors="replace")
        reader = csv.DictReader(io.StringIO(text), delimiter=";")
        for row in reader:
            if not isinstance(row, dict):
                continue
            yield {str(k).strip(): _safe_text(v) for k, v in row.items() if k is not None}

    def _pick_latest_by_cnpj(self, rows: Iterable[dict[str, str]], *, cnpj_key: str) -> dict[str, dict[str, str]]:
        best: dict[str, dict[str, str]] = {}
        best_rank: dict[str, tuple[str, int]] = {}

        for r in rows:
            cnpj = _normalize_cnpj(r.get(cnpj_key, ""))
            if not cnpj:
                continue
            ref = _safe_text(r.get("Data_Referencia"))
            ver = _safe_int(r.get("Versao"))

            rank = (ref, ver)
            prev = best_rank.get(cnpj)
            if prev is None or rank > prev:
                best_rank[cnpj] = rank
                best[cnpj] = r

        return best

    def load_fca_snapshots(self, year: int) -> list[CvmRiSnapshot]:
        data = self.download_fca_zip(int(year))
        z = zipfile.ZipFile(io.BytesIO(data))

        files = {
            "canal": f"fca_cia_aberta_canal_divulgacao_{int(year)}.csv",
            "dept": f"fca_cia_aberta_departamento_acionistas_{int(year)}.csv",
            "dri": f"fca_cia_aberta_dri_{int(year)}.csv",
            "endereco": f"fca_cia_aberta_endereco_{int(year)}.csv",
        }

        for key, filename in list(files.items()):
            if filename not in z.namelist():
                files.pop(key, None)

        if not files:
            raise RuntimeError(f"Nenhum CSV esperado encontrado no ZIP FCA {year}.")

        canal_by_cnpj = self._pick_latest_by_cnpj(
            self._iter_csv_rows(z, files["canal"]),
            cnpj_key="CNPJ_Companhia",
        )
        dept_by_cnpj = self._pick_latest_by_cnpj(
            self._iter_csv_rows(z, files["dept"]),
            cnpj_key="CNPJ_Companhia",
        )
        dri_by_cnpj = self._pick_latest_by_cnpj(
            self._iter_csv_rows(z, files["dri"]),
            cnpj_key="CNPJ_Companhia",
        )
        end_by_cnpj = self._pick_latest_by_cnpj(
            self._iter_csv_rows(z, files["endereco"]),
            cnpj_key="CNPJ_Companhia",
        )

        all_cnpjs = set(canal_by_cnpj) | set(dept_by_cnpj) | set(dri_by_cnpj) | set(end_by_cnpj)

        out: list[CvmRiSnapshot] = []
        fetched_at = datetime.utcnow().isoformat() + "Z"

        for cnpj in sorted(all_cnpjs):
            dri = dri_by_cnpj.get(cnpj, {})
            dept = dept_by_cnpj.get(cnpj, {})
            end = end_by_cnpj.get(cnpj, {})
            canal = canal_by_cnpj.get(cnpj, {})

            # as_of_date: escolhe a maior data entre os arquivos disponíveis
            dates = [
                _safe_text(dri.get("Data_Referencia")),
                _safe_text(dept.get("Data_Referencia")),
                _safe_text(end.get("Data_Referencia")),
                _safe_text(canal.get("Data_Referencia")),
            ]
            as_of_date = max([d for d in dates if d] or [f"{int(year)}-01-01"])

            def _fmt_phone(prefix_ddi: str, prefix_ddd: str, number: str) -> str:
                ddi = _safe_text(prefix_ddi)
                ddd = _safe_text(prefix_ddd)
                num = _safe_text(number)
                parts = []
                if ddi:
                    parts.append(f"+{ddi}")
                if ddd:
                    parts.append(f"({ddd})")
                if num:
                    parts.append(num)
                return " ".join(parts).strip()

            extracted = {
                "canal_divulgacao": _safe_text(canal.get("Canal_Divulgacao")),
                "dri_nome": _safe_text(dri.get("Responsavel")),
                "dri_email": _safe_text(dri.get("Email")),
                "dri_telefone": _fmt_phone(dri.get("DDI_Telefone", ""), dri.get("DDD_Telefone", ""), dri.get("Telefone", "")),
                "dept_acionistas_contato": _safe_text(dept.get("Contato")),
                "dept_acionistas_email": _safe_text(dept.get("Email")),
                "dept_acionistas_telefone": _fmt_phone(dept.get("DDI_Telefone", ""), dept.get("DDD_Telefone", ""), dept.get("Telefone", "")),
                "endereco_logradouro": _safe_text(end.get("Logradouro")),
                "endereco_complemento": _safe_text(end.get("Complemento")),
                "endereco_bairro": _safe_text(end.get("Bairro")),
                "endereco_cidade": _safe_text(end.get("Cidade")),
                "endereco_uf": _safe_text(end.get("Sigla_UF")),
                "endereco_pais": _safe_text(end.get("Pais")),
                "endereco_cep": _safe_text(end.get("CEP")),
            }

            payload = {
                "cnpj": cnpj,
                "year": int(year),
                "source": "cvm_fca",
                "files": files,
                "dri": dri,
                "departamento_acionistas": dept,
                "endereco": end,
                "canal_divulgacao": canal,
                "extracted": extracted,
                "fetched_at": fetched_at,
            }

            out.append(
                CvmRiSnapshot(
                    cnpj=cnpj,
                    as_of_date=as_of_date,
                    source="cvm_fca",
                    payload=payload,
                    extracted=extracted,
                )
            )

        return out

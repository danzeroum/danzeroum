"""Adaptador PNCP (Portal Nacional de Contratações Públicas).

Usa o endpoint ``/contratacoes/proposta`` (contratações com **recebimento de
propostas em aberto** — o que interessa para concorrer). A API exige:
``dataFinal`` (AAAAMMDD), ``codigoModalidadeContratacao``, ``uf``, ``pagina`` e
``tamanhoPagina`` (≥ 10). Como a API aceita só uma modalidade por requisição,
o adaptador itera pelas modalidades configuradas (6 = Pregão Eletrônico, 8 =
Dispensa). A filtragem por palavra-chave é feita no cliente, sobre o objeto.

A coleta de rede fica isolada em ``fetch_raw``; o parsing é puro (testável offline).
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from datetime import date, timedelta
from typing import Any

import requests

from danzeroum_tracker.adapters.base import AdapterError, OrgaoAdapter
from danzeroum_tracker.adapters.common import (
    extract_records,
    first,
    infer_category,
    map_status,
    matches_keywords,
    parse_datetime,
    safe_float,
)
from danzeroum_tracker.models import Tender

# Aliases mantidos para compatibilidade (uso interno e testes).
_first = first
_safe_float = safe_float
_parse_datetime = parse_datetime

__all__ = [
    "PNCPAdapter",
    "PNCPError",
    "infer_category",
    "map_status",
    "matches_keywords",
]


class PNCPError(AdapterError):
    """Falha específica do adaptador PNCP."""


class PNCPAdapter(OrgaoAdapter):
    source = "PNCP"

    def __init__(
        self,
        base_url: str = "https://pncp.gov.br/api/consulta/v1",
        uf: str = "SP",
        keywords: Iterable[str] | None = None,
        page_size: int = 50,
        max_pages: int = 5,
        timeout: int = 30,
        session: requests.Session | None = None,
        endpoint: str = "/contratacoes/proposta",
        modalidades: Iterable[int] | None = None,
        horizon_days: int = 365,
        data_final: str | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.uf = uf.upper()
        self.keywords = list(keywords) if keywords is not None else []
        # A API exige tamanhoPagina >= 10.
        self.page_size = max(int(page_size), 10)
        self.max_pages = max_pages
        self.timeout = timeout
        self.endpoint = endpoint
        self.modalidades = list(modalidades) if modalidades is not None else [6, 8]
        self.horizon_days = horizon_days
        self._data_final = data_final
        self._session = session or requests.Session()

    # ── rede (isolada) ──────────────────────────────────────────────────────
    def _default_data_final(self) -> str:
        return (date.today() + timedelta(days=self.horizon_days)).strftime("%Y%m%d")

    def fetch_raw(self) -> Iterable[dict[str, Any]]:
        data_final = self._data_final or self._default_data_final()
        for modalidade in self.modalidades:
            for page in range(1, self.max_pages + 1):
                payload = self._fetch_page(modalidade, page, data_final)
                records = self._extract_records(payload)
                if not records:
                    break
                yield from records
                if len(records) < self.page_size:
                    break

    def _fetch_page(self, modalidade: int, page: int, data_final: str) -> dict[str, Any]:
        params = {
            "dataFinal": data_final,
            "codigoModalidadeContratacao": modalidade,
            "uf": self.uf,
            "pagina": page,
            "tamanhoPagina": self.page_size,
        }
        try:
            resp = self._session.get(
                f"{self.base_url}{self.endpoint}",
                params=params,
                headers={"Accept": "application/json"},
                timeout=self.timeout,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            raise PNCPError(
                f"falha ao consultar PNCP (modalidade {modalidade}, página {page}): {exc}"
            ) from exc
        except ValueError as exc:
            raise PNCPError(f"resposta inválida do PNCP (modalidade {modalidade}): {exc}") from exc

    @staticmethod
    def _extract_records(payload: Any) -> list[dict[str, Any]]:
        return extract_records(payload)

    # ── parsing (puro) ──────────────────────────────────────────────────────
    def parse_tender(self, raw: dict[str, Any]) -> Tender:
        objeto = first(raw, "objetoCompra", "objeto", "objeto_compra", "descricaoCompleta") or ""
        external_id = first(raw, "numeroControlePNCP", "numeroControlePncp", "id", "external_id")
        if external_id is None:
            raise PNCPError("registro do PNCP sem identificador (numeroControlePNCP/id)")

        unidade = raw.get("unidadeOrgao") if isinstance(raw.get("unidadeOrgao"), dict) else {}
        uf = first(raw, "uf", "ufSigla") or unidade.get("ufSigla") or self.uf

        return Tender(
            source=self.source,
            external_id=str(external_id),
            title=str(objeto)[:255] if objeto else f"Edital {external_id}",
            description=first(raw, "descricaoCompleta", "descricao", "descricao_geral") or objeto,
            status=map_status(
                first(raw, "situacaoCompraNome", "situacao", "status", "modalidadeNome")
            ),
            category=infer_category(str(objeto)),
            budget_estimate=safe_float(
                first(raw, "valorTotalEstimado", "valor_estimado", "valorEstimado")
            ),
            publish_date=parse_datetime(
                first(raw, "dataPublicacaoPncp", "data_publicacao", "dataInclusao")
            ),
            deadline=parse_datetime(
                first(
                    raw,
                    "dataEncerramentoProposta",
                    "data_limite_proposta",
                    "dataAberturaProposta",
                )
            ),
            url=self._build_url(raw, str(external_id)),
            uf=str(uf).upper() if uf else None,
            raw_json=raw,
        )

    @staticmethod
    def _build_url(raw: dict[str, Any], external_id: str) -> str:
        link = first(raw, "linkSistemaOrigem", "url_edital", "url")
        if link:
            return str(link)
        orgao = raw.get("orgaoEntidade") if isinstance(raw.get("orgaoEntidade"), dict) else {}
        cnpj = orgao.get("cnpj")
        ano = raw.get("anoCompra")
        seq = raw.get("sequencialCompra")
        if cnpj and ano and seq:
            return f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{seq}"
        return f"https://pncp.gov.br/app/editais?q={external_id}"

    def collect(self) -> Iterator[Tender]:
        """Coleta + filtro por palavra-chave (a API não filtra por palavra)."""
        for raw in self.fetch_raw():
            tender = self.parse_tender(raw)
            if not self.keywords or matches_keywords(tender, self.keywords):
                yield tender

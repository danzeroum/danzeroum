"""Adaptador Compras.gov.br (Dados Abertos / SIASG).

Mesma estratégia do PNCP: rede isolada em ``fetch_raw``, parsing puro e resiliente
a variações de nomes de campo. O endpoint/params exatos devem ser confirmados na
primeira execução real (a API de Dados Abertos evolui entre versões).
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
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

__all__ = ["ComprasGovAdapter", "ComprasGovError"]


class ComprasGovError(AdapterError):
    """Falha específica do adaptador Compras.gov.br."""


class ComprasGovAdapter(OrgaoAdapter):
    source = "COMPRAS_GOV"

    def __init__(
        self,
        base_url: str = "https://dadosabertos.compras.gov.br",
        uf: str = "SP",
        keywords: Iterable[str] | None = None,
        page_size: int = 50,
        max_pages: int = 5,
        timeout: int = 30,
        session: requests.Session | None = None,
        endpoint: str = "/modulo-contratacoes/1_consultarContratacoes",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.uf = uf.upper()
        self.keywords = list(keywords) if keywords is not None else []
        self.page_size = page_size
        self.max_pages = max_pages
        self.timeout = timeout
        self.endpoint = endpoint
        self._session = session or requests.Session()

    # ── rede (isolada) ──────────────────────────────────────────────────────
    def fetch_raw(self) -> Iterable[dict[str, Any]]:
        for page in range(1, self.max_pages + 1):
            payload = self._fetch_page(page)
            records = extract_records(payload)
            if not records:
                break
            yield from records
            if len(records) < self.page_size:
                break

    def _fetch_page(self, page: int) -> dict[str, Any]:
        params = {
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
            raise ComprasGovError(f"falha ao consultar Compras.gov (página {page}): {exc}") from exc
        except ValueError as exc:
            raise ComprasGovError(
                f"resposta inválida do Compras.gov (página {page}): {exc}"
            ) from exc

    # ── parsing (puro) ──────────────────────────────────────────────────────
    def parse_tender(self, raw: dict[str, Any]) -> Tender:
        objeto = first(raw, "objetoCompra", "descricaoCompra", "objeto", "descricao") or ""
        external_id = first(
            raw,
            "numeroControlePNCP",
            "identificadorCompra",
            "idCompra",
            "numeroCompra",
            "id",
            "external_id",
        )
        if external_id is None:
            raise ComprasGovError("registro do Compras.gov sem identificador")

        unidade = raw.get("unidadeOrgao") if isinstance(raw.get("unidadeOrgao"), dict) else {}
        uf = first(raw, "uf", "ufSigla") or unidade.get("ufSigla") or self.uf

        return Tender(
            source=self.source,
            external_id=str(external_id),
            title=str(objeto)[:255] if objeto else f"Contratação {external_id}",
            description=first(raw, "descricaoCompleta", "descricao", "objetoCompra") or objeto,
            status=map_status(first(raw, "situacaoCompraNome", "situacao", "status")),
            category=infer_category(str(objeto)),
            budget_estimate=safe_float(
                first(raw, "valorTotalEstimado", "valorEstimado", "valorTotalHomologado")
            ),
            publish_date=parse_datetime(
                first(raw, "dataPublicacaoPncp", "dataPublicacao", "dataInclusao")
            ),
            deadline=parse_datetime(
                first(raw, "dataEncerramentoProposta", "dataAberturaProposta", "dataLimiteProposta")
            ),
            url=first(raw, "linkSistemaOrigem", "urlCompra", "url")
            or f"https://www.gov.br/compras/pt-br?q={external_id}",
            uf=str(uf).upper() if uf else None,
            raw_json=raw,
        )

    def collect(self) -> Iterator[Tender]:
        for raw in self.fetch_raw():
            tender = self.parse_tender(raw)
            if not self.keywords or matches_keywords(tender, self.keywords):
                yield tender

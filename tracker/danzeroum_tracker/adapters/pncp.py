"""Adaptador PNCP (Portal Nacional de Contratações Públicas).

A API de consulta do PNCP filtra por modalidade/data/UF, não por palavra-chave,
então a filtragem por palavra-chave é feita no cliente, sobre o objeto do edital.

O ``parse_tender`` é resiliente: aceita variações de nomes de campo (camelCase da
API real e snake_case) porque o contrato exato pode mudar entre versões da API.
A coleta de rede fica isolada em ``fetch_raw``; o parsing é puro (testável offline).
"""

from __future__ import annotations

import unicodedata
from collections.abc import Iterable, Iterator
from datetime import datetime
from typing import Any

import requests

from danzeroum_tracker.adapters.base import AdapterError, OrgaoAdapter
from danzeroum_tracker.models import Tender

_STATUS_MAP = {
    "em_andamento": "OPEN",
    "recebendo_proposta": "OPEN",
    "recebendo_propostas": "OPEN",
    "propostas_abertas": "OPEN",
    "divulgada": "OPEN",
    "publicado": "OPEN",
    "adjudicado": "AWARDED",
    "homologado": "AWARDED",
    "encerrado": "CLOSED",
    "encerrada": "CLOSED",
    "concluido": "CLOSED",
    "revogado": "CANCELLED",
    "cancelado": "CANCELLED",
    "anulado": "CANCELLED",
}

_TI_TERMS = (
    "tecnologia da informacao",
    "tecnologia",
    "informatica",
    "software",
    "sistema",
    "desenvolvimento de sistema",
    "hospedagem",
    "tratamento de dados",
    "data center",
    "datacenter",
    "nuvem",
    "cloud",
    "suporte tecnico",
    "ti ",
)
_TELECOM_TERMS = ("telecom", "telefonia", "internet", "link de dados", "fibra", "rede de dados")


class PNCPError(AdapterError):
    """Falha específica do adaptador PNCP."""


def _normalize(text: str) -> str:
    """Minúsculo e sem acentos, para comparação robusta."""
    nfkd = unicodedata.normalize("NFKD", text or "")
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


def _first(raw: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in raw and raw[key] not in (None, ""):
            return raw[key]
    return None


def _safe_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_datetime(value: Any) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def map_status(status: Any) -> str:
    return _STATUS_MAP.get(_normalize(str(status or "")).strip(), "OPEN")


def infer_category(objeto: str) -> str:
    text = _normalize(objeto)
    if any(term in text for term in _TI_TERMS):
        return "TI"
    if any(term in text for term in _TELECOM_TERMS):
        return "TELECOM"
    return "OUTROS"


def matches_keywords(tender: Tender, keywords: Iterable[str]) -> bool:
    """True se o objeto/descrição contém alguma das palavras-chave (sem acento)."""
    haystack = _normalize(f"{tender.title} {tender.description or ''}")
    return any(_normalize(kw) in haystack for kw in keywords)


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
        endpoint: str = "/contratacoes/publicacao",
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
            records = self._extract_records(payload)
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
            raise PNCPError(f"falha ao consultar PNCP (página {page}): {exc}") from exc
        except ValueError as exc:
            raise PNCPError(f"resposta inválida do PNCP (página {page}): {exc}") from exc

    @staticmethod
    def _extract_records(payload: Any) -> list[dict[str, Any]]:
        """A API pode devolver uma lista direta ou um envelope com ``data``/``items``."""
        if isinstance(payload, list):
            return [r for r in payload if isinstance(r, dict)]
        if isinstance(payload, dict):
            for key in ("data", "items", "itens", "resultado", "content"):
                value = payload.get(key)
                if isinstance(value, list):
                    return [r for r in value if isinstance(r, dict)]
        return []

    # ── parsing (puro) ──────────────────────────────────────────────────────
    def parse_tender(self, raw: dict[str, Any]) -> Tender:
        objeto = _first(raw, "objetoCompra", "objeto", "objeto_compra", "descricaoCompleta") or ""
        external_id = _first(
            raw, "numeroControlePNCP", "numeroControlePncp", "id", "external_id"
        )
        if external_id is None:
            raise PNCPError("registro do PNCP sem identificador (numeroControlePNCP/id)")

        unidade = raw.get("unidadeOrgao") if isinstance(raw.get("unidadeOrgao"), dict) else {}
        uf = _first(raw, "uf", "ufSigla") or unidade.get("ufSigla") or self.uf

        return Tender(
            source=self.source,
            external_id=str(external_id),
            title=str(objeto)[:255] if objeto else f"Edital {external_id}",
            description=_first(raw, "descricaoCompleta", "descricao", "descricao_geral") or objeto,
            status=map_status(
                _first(raw, "situacaoCompraNome", "situacao", "status", "modalidadeNome")
            ),
            category=infer_category(str(objeto)),
            budget_estimate=_safe_float(
                _first(raw, "valorTotalEstimado", "valor_estimado", "valorEstimado")
            ),
            publish_date=_parse_datetime(
                _first(raw, "dataPublicacaoPncp", "data_publicacao", "dataInclusao")
            ),
            deadline=_parse_datetime(
                _first(
                    raw,
                    "dataEncerramentoProposta",
                    "data_limite_proposta",
                    "dataAberturaProposta",
                )
            ),
            url=_first(raw, "linkSistemaOrigem", "url_edital", "url")
            or f"https://pncp.gov.br/app/editais?q={external_id}",
            uf=str(uf).upper() if uf else None,
            raw_json=raw,
        )

    def collect(self) -> Iterator[Tender]:
        """Coleta + filtro por palavra-chave (a API não filtra por palavra)."""
        for raw in self.fetch_raw():
            tender = self.parse_tender(raw)
            if not self.keywords or matches_keywords(tender, self.keywords):
                yield tender

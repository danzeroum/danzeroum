"""Adaptadores baseados em scraping de HTML (Compras SP, Prefeitura SP).

Esses portais não têm API pública estável, então a coleta é por scraping.

⚠️ SELETORES "A CONFIRMAR": os seletores CSS abaixo são *placeholders* plausíveis.
Eles devem ser validados/ajustados na primeira execução real, com acesso à rede e
ao HTML atual do portal (use o comando `search`/`collect` e ajuste `DEFAULT_SELECTORS`).
A arquitetura (rede isolada em ``fetch_raw``, parsing puro em ``parse_html``) permite
testar a extração offline com um HTML de fixture e trocar os seletores sem mexer no core.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Any

import requests
from bs4 import BeautifulSoup

from danzeroum_tracker.adapters.base import AdapterError, OrgaoAdapter
from danzeroum_tracker.adapters.common import (
    absolute_url,
    infer_category,
    map_status,
    matches_keywords,
    parse_date_br,
    parse_money_br,
    stable_id,
)
from danzeroum_tracker.models import Tender

__all__ = [
    "HTMLListingAdapter",
    "ScraperError",
    "ComprasSPAdapter",
    "PrefeituraSPAdapter",
]


class ScraperError(AdapterError):
    """Falha de um adaptador de scraping (rede ou estrutura do HTML mudou)."""


class HTMLListingAdapter(OrgaoAdapter):
    """Adaptador genérico de listagem HTML, parametrizado por seletores CSS.

    ``selectors`` mapeia campos → CSS (relativo a cada linha):
      row, title, link, value, deadline, status, external_id
    """

    source = "HTML"
    base_url = ""
    listing_path = "/"
    default_selectors: dict[str, str] = {}

    def __init__(
        self,
        base_url: str | None = None,
        uf: str = "SP",
        keywords: Iterable[str] | None = None,
        timeout: int = 30,
        session: requests.Session | None = None,
        selectors: dict[str, str] | None = None,
        listing_path: str | None = None,
        # Aceitos por compatibilidade com a fábrica de adaptadores (ignorados aqui).
        page_size: int | None = None,
        max_pages: int | None = None,
    ) -> None:
        self.base_url = (base_url or self.base_url).rstrip("/")
        self.uf = uf.upper()
        self.keywords = list(keywords) if keywords is not None else []
        self.timeout = timeout
        self.listing_path = listing_path or self.listing_path
        self.selectors = {**self.default_selectors, **(selectors or {})}
        self._session = session or requests.Session()

    # ── rede (isolada) ──────────────────────────────────────────────────────
    def fetch_raw(self) -> Iterable[dict[str, Any]]:
        html = self._fetch_listing()
        return self.parse_html(html)

    def _fetch_listing(self) -> str:
        try:
            resp = self._session.get(
                f"{self.base_url}{self.listing_path}",
                headers={"Accept": "text/html", "User-Agent": "danzeroum-tracker/0.1"},
                timeout=self.timeout,
            )
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as exc:
            raise ScraperError(f"falha ao baixar listagem de {self.source}: {exc}") from exc

    # ── parsing (puro) ──────────────────────────────────────────────────────
    def _text(self, row, field: str) -> str | None:
        sel = self.selectors.get(field)
        if not sel:
            return None
        el = row.select_one(sel)
        return el.get_text(" ", strip=True) if el else None

    def parse_html(self, html: str) -> list[dict[str, Any]]:
        soup = BeautifulSoup(html or "", "html.parser")
        row_sel = self.selectors.get("row")
        rows = soup.select(row_sel) if row_sel else []
        out: list[dict[str, Any]] = []
        for row in rows:
            title = self._text(row, "title")
            if not title:
                continue
            link_sel = self.selectors.get("link")
            link_el = row.select_one(link_sel) if link_sel else None
            href = link_el.get("href") if link_el else None
            out.append(
                {
                    "title": title,
                    "value": self._text(row, "value"),
                    "deadline": self._text(row, "deadline"),
                    "status": self._text(row, "status"),
                    "external_id": self._text(row, "external_id"),
                    "url": href,
                }
            )
        return out

    def parse_tender(self, raw: dict[str, Any]) -> Tender:
        title = (raw.get("title") or "").strip()
        if not title:
            raise ScraperError(f"linha de {self.source} sem título")
        url = absolute_url(raw.get("url"), self.base_url)
        external_id = stable_id(raw.get("external_id") or "", url or "", title)
        return Tender(
            source=self.source,
            external_id=external_id,
            title=title[:255],
            description=title,
            status=map_status(raw.get("status")),
            category=infer_category(title),
            budget_estimate=parse_money_br(raw.get("value")),
            deadline=parse_date_br(raw.get("deadline")),
            url=url,
            uf=self.uf,
            raw_json=raw,
        )

    def collect(self) -> Iterator[Tender]:
        for raw in self.fetch_raw():
            tender = self.parse_tender(raw)
            if not self.keywords or matches_keywords(tender, self.keywords):
                yield tender


class ComprasSPAdapter(HTMLListingAdapter):
    """Compras SP (BEC / compras.sp.gov.br). Seletores a confirmar."""

    source = "COMPRAS_SP"
    base_url = "https://www.bec.sp.gov.br"
    listing_path = "/becsp/aspx/oferta/OfertaPesquisa.aspx"
    default_selectors = {
        "row": "table.licitacoes tr.linha",
        "title": "td.objeto",
        "link": "td.objeto a",
        "value": "td.valor",
        "deadline": "td.prazo",
        "status": "td.situacao",
    }


class PrefeituraSPAdapter(HTMLListingAdapter):
    """Prefeitura de SP (e-Negócios Públicos). Seletores a confirmar."""

    source = "PREF_SP"
    base_url = "https://e-negocioscidadesp.prefeitura.sp.gov.br"
    listing_path = "/Account/Edital/Lista"
    default_selectors = {
        "row": "table#tabelaEditais tbody tr",
        "title": "td.objeto",
        "link": "td.objeto a",
        "value": "td.valorEstimado",
        "deadline": "td.dataEncerramento",
        "status": "td.situacao",
    }

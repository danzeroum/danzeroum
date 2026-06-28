"""Adaptadores por órgão.

V1: PNCP + Compras.gov.br (API). V2: Compras SP + Prefeitura SP (scraping).
"""

from __future__ import annotations

from danzeroum_tracker.adapters.base import AdapterError, OrgaoAdapter
from danzeroum_tracker.adapters.comprasgov import ComprasGovAdapter, ComprasGovError
from danzeroum_tracker.adapters.pncp import PNCPAdapter, PNCPError
from danzeroum_tracker.adapters.scraper import (
    ComprasSPAdapter,
    HTMLListingAdapter,
    PrefeituraSPAdapter,
    ScraperError,
)

__all__ = [
    "AdapterError",
    "OrgaoAdapter",
    "PNCPAdapter",
    "PNCPError",
    "ComprasGovAdapter",
    "ComprasGovError",
    "HTMLListingAdapter",
    "ComprasSPAdapter",
    "PrefeituraSPAdapter",
    "ScraperError",
]

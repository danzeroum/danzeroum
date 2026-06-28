"""Adaptadores por órgão. V1: PNCP + Compras.gov.br (ambos via API)."""

from __future__ import annotations

from danzeroum_tracker.adapters.base import AdapterError, OrgaoAdapter
from danzeroum_tracker.adapters.comprasgov import ComprasGovAdapter, ComprasGovError
from danzeroum_tracker.adapters.pncp import PNCPAdapter, PNCPError

__all__ = [
    "AdapterError",
    "OrgaoAdapter",
    "PNCPAdapter",
    "PNCPError",
    "ComprasGovAdapter",
    "ComprasGovError",
]

"""Adaptadores por órgão. V1: PNCP."""

from __future__ import annotations

from danzeroum_tracker.adapters.base import AdapterError, OrgaoAdapter
from danzeroum_tracker.adapters.pncp import PNCPAdapter, PNCPError

__all__ = ["AdapterError", "OrgaoAdapter", "PNCPAdapter", "PNCPError"]

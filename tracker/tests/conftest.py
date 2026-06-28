"""Fixtures e dublês compartilhados pelos testes."""

from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from danzeroum_tracker.adapters.base import OrgaoAdapter
from danzeroum_tracker.models import Tender

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def pncp_records() -> list[dict[str, Any]]:
    return json.loads((FIXTURES / "pncp_sample.json").read_text(encoding="utf-8"))


class FakeResponse:
    def __init__(self, payload: Any, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code
        self.headers: dict[str, str] = {}
        # Suporta tanto JSON (.json()) quanto HTML (.text).
        self.text = payload if isinstance(payload, str) else ""

    def json(self) -> Any:
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            import requests

            raise requests.HTTPError(f"HTTP {self.status_code}")


class FakeSession:
    """Sessão requests falsa: 1ª página devolve os registros, demais vazias."""

    def __init__(self, pages: list[Any]):
        self._pages = pages
        self.calls: list[dict] = []

    def get(self, url, params=None, headers=None, timeout=None):  # noqa: A002
        params = params or {}
        self.calls.append({"url": url, "params": params})
        page = int(params.get("pagina", 1))
        payload = self._pages[page - 1] if page - 1 < len(self._pages) else []
        return FakeResponse(payload)


class StubAdapter(OrgaoAdapter):
    """Adaptador de teste: devolve tenders prontos, sem rede."""

    source = "STUB"

    def __init__(self, tenders: Iterable[Tender]):
        self._tenders = list(tenders)

    def fetch_raw(self):
        return [t.raw_json for t in self._tenders]

    def parse_tender(self, raw):
        raise NotImplementedError

    def collect(self):
        yield from self._tenders


@pytest.fixture
def sample_tenders() -> list[Tender]:
    return [
        Tender(
            source="STUB",
            external_id="A1",
            title="Suporte técnico e manutenção de TI",
            description="atestado de capacidade técnica exigido",
            category="TI",
            budget_estimate=80000.0,
            deadline=datetime(2026, 12, 30, 18, 0, 0),
            uf="SP",
        ),
        Tender(
            source="STUB",
            external_id="A2",
            title="Aquisição de material de escritório",
            description="papel, canetas",
            category="OUTROS",
            budget_estimate=5000.0,
            uf="SP",
        ),
    ]

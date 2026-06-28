import json
from pathlib import Path

import pytest

from danzeroum_tracker.adapters.comprasgov import ComprasGovAdapter, ComprasGovError
from tests.conftest import FakeResponse, FakeSession

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def comprasgov_payload():
    return json.loads((FIXTURES / "comprasgov_sample.json").read_text(encoding="utf-8"))


def test_parse_maps_comprasgov_fields(comprasgov_payload):
    adapter = ComprasGovAdapter()
    record = comprasgov_payload["resultado"][0]
    t = adapter.parse_tender(record)
    assert t.source == "COMPRAS_GOV"
    assert t.external_id == "CG-2026-000123"
    assert t.category == "TI"
    assert t.status == "OPEN"
    assert t.budget_estimate == 350000.0
    assert t.uf == "SP"
    assert t.deadline.isoformat() == "2026-12-28T18:00:00"
    assert t.url == "https://www.gov.br/compras/edital/123"


def test_parse_uses_id_fallback_and_builds_url(comprasgov_payload):
    adapter = ComprasGovAdapter()
    t = adapter.parse_tender(comprasgov_payload["resultado"][1])  # usa idCompra
    assert t.external_id == "456"
    assert "q=456" in t.url


def test_parse_requires_id():
    adapter = ComprasGovAdapter()
    with pytest.raises(ComprasGovError):
        adapter.parse_tender({"objetoCompra": "sem id"})


def test_fetch_raw_reads_resultado_envelope(comprasgov_payload):
    session = FakeSession(pages=[comprasgov_payload])
    adapter = ComprasGovAdapter(page_size=50, session=session)
    records = list(adapter.fetch_raw())
    assert len(records) == 2


def test_collect_filters_by_keyword(comprasgov_payload):
    session = FakeSession(pages=[comprasgov_payload])
    adapter = ComprasGovAdapter(keywords=["desenvolvimento", "software"], session=session)
    tenders = list(adapter.collect())
    assert len(tenders) == 1
    assert tenders[0].external_id == "CG-2026-000123"


def test_fetch_page_http_error_raises():
    class BadSession:
        def get(self, *a, **k):
            return FakeResponse({}, status_code=503)

    adapter = ComprasGovAdapter(session=BadSession())
    with pytest.raises(ComprasGovError):
        list(adapter.fetch_raw())

"""Tests for GET /tenders and GET /tenders/{id}."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.main import app

_TENDER = {
    "id": "aaaaaaaa-0000-0000-0000-000000000001",
    "source": "PNCP",
    "external_id": "ext-1",
    "title": "Edital de teste 1",
    "status": "OPEN",
    "category": "TI",
    "budget_estimate": 100_000.0,
    "publish_date": None,
    "deadline": None,
    "url": "https://example.com/1",
    "uf": "SP",
    "created_at": "2026-01-01T00:00:00",
    "score": {
        "fit_score": 0.85,
        "risk_score": 0.2,
        "complexity_score": 0.3,
        "recommendation": "GO",
        "key_requirements": ["Atestado técnico"],
        "pricing_guidance": "R$ 80k–90k",
        "analysis_text": "Boa aderência.",
    },
}


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setattr(
        "api.routers.tenders.search_tenders",
        lambda conn, **kw: ([_TENDER], 1),
    )
    monkeypatch.setattr(
        "api.routers.tenders.get_tender_detail",
        lambda conn, tender_id: (_TENDER | {"description": "desc", "raw_json": {}}) if tender_id == _TENDER["id"] else None,
    )
    # get_conn raises 503 without DATABASE_URL — override to return a sentinel
    from api.deps import get_conn
    app.dependency_overrides[get_conn] = lambda: None
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_list_tenders_shape(client):
    r = client.get("/tenders")
    assert r.status_code == 200
    body = r.json()
    assert "items" in body and "total" in body
    assert body["total"] == 1
    assert body["items"][0]["source"] == "PNCP"


def test_list_tenders_recommendation_filter(client, monkeypatch):
    captured = {}
    monkeypatch.setattr(
        "api.routers.tenders.search_tenders",
        lambda conn, **kw: (captured.update(kw) or ([_TENDER], 1)),
    )
    client.get("/tenders?recommendation=GO")
    assert captured.get("recommendation") == "GO"


def test_list_tenders_invalid_recommendation(client):
    r = client.get("/tenders?recommendation=INVALID")
    assert r.status_code == 422


def test_list_tenders_invalid_sort(client):
    r = client.get("/tenders?sort=invalid")
    assert r.status_code == 422


def test_list_tenders_min_fit_out_of_range(client):
    r = client.get("/tenders?min_fit=1.5")
    assert r.status_code == 422


def test_get_tender_detail(client):
    r = client.get(f"/tenders/{_TENDER['id']}")
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == _TENDER["id"]
    assert "score" in body


def test_get_tender_not_found(client):
    r = client.get("/tenders/aaaaaaaa-0000-0000-0000-000000000099")
    assert r.status_code == 404

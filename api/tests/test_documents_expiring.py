"""Tests for GET /documents/expiring e expiring_docs_as_alerts."""

from __future__ import annotations

from datetime import date

import pytest
from fastapi.testclient import TestClient

from api.db import expiring_docs_as_alerts
from api.deps import get_conn
from api.main import app


def test_expiring_docs_as_alerts_levels():
    docs = [
        {"id": "1", "type": "CND", "name": "CND Federal", "days_left": -5},
        {"id": "2", "type": "FGTS", "name": "CRF FGTS", "days_left": 3},
        {"id": "3", "type": "CRF", "name": "Simples", "days_left": 20},
    ]
    alerts = expiring_docs_as_alerts(docs)
    assert alerts[0]["level"] == "danger" and "VENCIDA" in alerts[0]["body"]
    assert alerts[1]["level"] == "danger" and "3 dia" in alerts[1]["body"]
    assert alerts[2]["level"] == "review" and "20 dia" in alerts[2]["body"]
    assert all(a["kind"] == "documento" for a in alerts)
    assert alerts[0]["id"] == "doc-1"


_FIXTURE = [
    {"id": "abc", "type": "CND", "name": "CND Federal", "expiry_date": date(2026, 7, 5), "days_left": 5, "level": "critical"},
]


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setattr(
        "api.routers.documents.get_expiring_documents",
        lambda conn, within_days=30: _FIXTURE,
    )
    app.dependency_overrides[get_conn] = lambda: None
    c = TestClient(app)
    c.post("/auth/login", json={"username": "admin", "password": "test"})
    yield c
    app.dependency_overrides.clear()


def test_expiring_endpoint_shape(client):
    r = client.get("/documents/expiring")
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    assert body[0]["type"] == "CND"
    assert body[0]["days_left"] == 5
    assert body[0]["level"] == "critical"


def test_expiring_endpoint_requires_auth():
    app.dependency_overrides[get_conn] = lambda: None
    try:
        anon = TestClient(app)
        assert anon.get("/documents/expiring").status_code == 401
    finally:
        app.dependency_overrides.clear()

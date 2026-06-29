"""Tests for GET /alerts."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.deps import get_conn


@pytest.fixture()
def client(monkeypatch):
    _ALERTS = [
        {"id": "abc", "kind": "oportunidade", "level": "go", "title": "Teste GO", "body": "Aderência 85%", "tender_id": "abc"},
    ]
    monkeypatch.setattr(
        "api.routers.alerts.get_recent_alerts",
        lambda conn, limit=20: _ALERTS,
    )
    app.dependency_overrides[get_conn] = lambda: None
    c = TestClient(app)
    c.post("/auth/login", json={"username": "admin", "password": "test"})
    yield c
    app.dependency_overrides.clear()


def test_alerts_list_shape(client):
    r = client.get("/alerts")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    assert len(body) == 1
    alert = body[0]
    for field in ("id", "kind", "level", "title", "body"):
        assert field in alert


def test_alerts_empty(monkeypatch):
    monkeypatch.setattr(
        "api.routers.alerts.get_recent_alerts",
        lambda conn, limit=20: [],
    )
    app.dependency_overrides[get_conn] = lambda: None
    with TestClient(app) as c:
        c.post("/auth/login", json={"username": "admin", "password": "test"})
        r = c.get("/alerts")
    app.dependency_overrides.clear()
    assert r.status_code == 200
    assert r.json() == []

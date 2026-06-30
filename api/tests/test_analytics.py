"""Tests for GET /analytics e a agregação pura _compute_analytics."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.db import _compute_analytics
from api.deps import get_conn
from api.main import app


def test_compute_analytics_win_rate_and_values():
    status_rows = [
        {"status": "WIN", "cnt": 3, "total_value": 300_000},
        {"status": "LOST", "cnt": 1, "total_value": 50_000},
        {"status": "SENT", "cnt": 2, "total_value": 80_000},
        {"status": "DRAFT", "cnt": 1, "total_value": 0},
    ]
    monthly_rows = [
        {"month": "2026-01", "status": "WIN", "cnt": 2},
        {"month": "2026-01", "status": "LOST", "cnt": 1},
        {"month": "2026-02", "status": "WIN", "cnt": 1},
    ]
    out = _compute_analytics(status_rows, monthly_rows)
    assert out["total_proposals"] == 7
    assert out["decided"] == 4
    assert out["win_rate"] == 0.75  # 3 / (3 + 1)
    assert out["value_won"] == 300_000
    assert out["value_lost"] == 50_000
    assert out["value_pipeline"] == 80_000  # SENT + DRAFT (UNDER_REVIEW=0)
    assert out["by_status"]["WIN"] == 3
    # Série mensal ordenada e somada por mês.
    assert out["monthly"][0] == {"month": "2026-01", "sent": 3, "won": 2, "lost": 1}
    assert out["monthly"][1] == {"month": "2026-02", "sent": 1, "won": 1, "lost": 0}


def test_compute_analytics_empty():
    out = _compute_analytics([], [])
    assert out["total_proposals"] == 0
    assert out["win_rate"] == 0.0
    assert out["decided"] == 0
    assert out["monthly"] == []


_FIXTURE = {
    "total_proposals": 4,
    "by_status": {"WIN": 2, "LOST": 1, "SENT": 1},
    "win_rate": 0.6667,
    "decided": 3,
    "value_won": 200_000.0,
    "value_lost": 40_000.0,
    "value_pipeline": 30_000.0,
    "monthly": [{"month": "2026-03", "sent": 2, "won": 1, "lost": 1}],
}


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setattr("api.routers.analytics.get_proposal_analytics", lambda conn: _FIXTURE)
    app.dependency_overrides[get_conn] = lambda: None
    c = TestClient(app)
    c.post("/auth/login", json={"username": "admin", "password": "test"})
    yield c
    app.dependency_overrides.clear()


def test_analytics_route_shape(client):
    r = client.get("/analytics")
    assert r.status_code == 200
    body = r.json()
    assert body["total_proposals"] == 4
    assert body["win_rate"] == 0.6667
    assert body["value_won"] == 200_000.0
    assert body["monthly"][0]["month"] == "2026-03"


def test_analytics_requires_auth():
    app.dependency_overrides[get_conn] = lambda: None
    try:
        anon = TestClient(app)
        assert anon.get("/analytics").status_code == 401
    finally:
        app.dependency_overrides.clear()

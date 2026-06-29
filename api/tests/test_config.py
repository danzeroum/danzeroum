"""Tests for GET /config and PUT /config.

SMTP secrets must never appear in the response.
_STORE is redirected to tmp_path to avoid polluting the repo.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.main import app
import api.deps as deps_mod


@pytest.fixture()
def client(monkeypatch, tmp_path):
    # Redirect JSON store so PUT /config doesn't write to the real file
    monkeypatch.setattr("api.config_store._STORE", tmp_path / "cfg.json")
    # Reset settings singleton so env changes don't bleed across tests
    deps_mod._settings = None
    c = TestClient(app)
    c.post("/auth/login", json={"username": "admin", "password": "test"})
    yield c
    deps_mod._settings = None


def test_get_config_shape(client):
    r = client.get("/config")
    assert r.status_code == 200
    body = r.json()
    for field in ("sources", "uf", "keywords", "scorer", "collect_interval_hours", "min_fit_alert"):
        assert field in body, f"Missing field: {field}"


def test_get_config_no_smtp_secrets(client):
    r = client.get("/config")
    body = r.json()
    for secret in ("smtp_host", "smtp_pass", "smtp_user", "smtp_password", "database_url"):
        assert secret not in body, f"Secret exposed: {secret}"


def test_put_config_patch(client):
    r = client.put("/config", json={"collect_interval_hours": 6})
    assert r.status_code == 200
    assert r.json()["collect_interval_hours"] == 6


def test_put_config_keywords(client):
    r = client.put("/config", json={"keywords": ["ia", "compliance", "saúde"]})
    assert r.status_code == 200
    assert "ia" in r.json()["keywords"]


def test_put_config_persists(client):
    client.put("/config", json={"min_fit_alert": 0.9})
    r = client.get("/config")
    assert r.json()["min_fit_alert"] == 0.9


def test_put_config_ignores_smtp(client):
    # SMTP keys must be in _ALLOWED_KEYS to be persisted — they are NOT, so they're silently dropped
    r = client.put("/config", json={"collect_interval_hours": 3, "smtp_pass": "hacked"})
    assert r.status_code == 200
    assert "smtp_pass" not in r.json()

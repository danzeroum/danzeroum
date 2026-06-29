"""Tests for POST /collect and GET /collect/{run_id}."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.main import app
import api.routers.collect as collect_mod


@pytest.fixture()
def client(monkeypatch):
    # Patch background executor to run synchronously and succeed without DB
    from danzeroum_tracker.storage import InMemoryRepository

    def _fake_execute(run_id: str) -> None:
        repo = InMemoryRepository()
        collect_mod._runs[run_id] = {
            "status": "done",
            "result": {"collected": 0, "new_tenders": 0, "scored": 0, "alerts": 0, "errors": []},
        }

    monkeypatch.setattr(collect_mod, "_execute_collection", _fake_execute)
    # Clear run registry between tests
    collect_mod._runs.clear()
    c = TestClient(app)
    c.post("/auth/login", json={"username": "admin", "password": "test"})
    yield c
    collect_mod._runs.clear()


def test_post_collect_returns_202(client):
    r = client.post("/collect")
    assert r.status_code == 202
    body = r.json()
    assert "run_id" in body
    assert body["status"] == "running"


def test_get_run_status_done(client):
    post = client.post("/collect")
    run_id = post.json()["run_id"]
    # TestClient runs BackgroundTasks synchronously after response
    r = client.get(f"/collect/{run_id}")
    assert r.status_code == 200
    assert r.json()["status"] == "done"


def test_get_run_not_found(client):
    r = client.get("/collect/nao-existe")
    assert r.status_code == 404


def test_list_runs(client):
    client.post("/collect")
    r = client.get("/collect")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) >= 1

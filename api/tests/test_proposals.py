import uuid

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from api.main import app
from api.deps import get_conn

# get_conn usa row_factory=dict_row: linhas são dict e as colunas uuid chegam
# como objetos UUID.
_PROP_ID = uuid.UUID("22222222-2222-4222-8222-222222222222")
_TENDER_ID = uuid.UUID("33333333-3333-4333-8333-333333333333")

@pytest.fixture()
def client():
    mock_conn = MagicMock()
    list_cur = MagicMock(); list_cur.fetchall.return_value = []
    fetch_cur = MagicMock()
    fetch_cur.fetchone.return_value = {
        "id": _PROP_ID, "tender_id": _TENDER_ID, "tender_title": "Some Tender",
        "status": "DRAFT", "price_offered": None, "validity_days": None,
        "version": 1, "notes": None, "submitted_at": None,
    }
    update_cur = MagicMock(); update_cur.rowcount = 1
    def fake_execute(q, params=None):
        if "INSERT" in q: return MagicMock(rowcount=1)
        if "UPDATE" in q: return update_cur
        if "WHERE p.id=" in q: return fetch_cur
        return list_cur
    mock_conn.execute.side_effect = fake_execute
    app.dependency_overrides[get_conn] = lambda: mock_conn
    with TestClient(app) as c:
        c.post("/auth/login", json={"username": "admin", "password": "test"})
        yield c
    app.dependency_overrides.clear()

def test_list_proposals_empty(client):
    r = client.get("/proposals")
    assert r.status_code == 200
    assert r.json() == []

def test_create_proposal(client):
    r = client.post("/proposals", json={"tender_id": str(_TENDER_ID)})
    assert r.status_code == 201
    assert r.json()["status"] == "DRAFT"
    # UUIDs do banco saem serializados como str.
    assert r.json()["id"] == str(_PROP_ID)
    assert r.json()["tender_id"] == str(_TENDER_ID)

def test_patch_proposal_status(client):
    r = client.patch(f"/proposals/{_PROP_ID}/status", json={"status": "SENT"})
    assert r.status_code == 200

def test_delete_proposal(client):
    r = client.delete("/proposals/some-id")
    assert r.status_code == 204

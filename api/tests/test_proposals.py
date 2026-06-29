import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from api.main import app
from api.deps import get_conn

@pytest.fixture()
def client():
    mock_conn = MagicMock()
    list_cur = MagicMock(); list_cur.fetchall.return_value = []
    fetch_cur = MagicMock()
    fetch_cur.fetchone.return_value = ("prop-id","tender-id","Some Tender","DRAFT",None,None,1,None,None)
    update_cur = MagicMock(); update_cur.rowcount = 1
    def fake_execute(q, params=None):
        if "INSERT" in q: return MagicMock(rowcount=1)
        if "UPDATE" in q: return update_cur
        if "WHERE p.id=" in q: return fetch_cur
        return list_cur
    mock_conn.execute.side_effect = fake_execute
    app.dependency_overrides[get_conn] = lambda: mock_conn
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def test_list_proposals_empty(client):
    r = client.get("/proposals")
    assert r.status_code == 200
    assert r.json() == []

def test_create_proposal(client):
    r = client.post("/proposals", json={"tender_id": "tender-id"})
    assert r.status_code == 201
    assert r.json()["status"] == "DRAFT"

def test_patch_proposal_status(client):
    r = client.patch("/proposals/prop-id/status", json={"status": "SENT"})
    assert r.status_code == 200

def test_delete_proposal(client):
    r = client.delete("/proposals/some-id")
    assert r.status_code == 204

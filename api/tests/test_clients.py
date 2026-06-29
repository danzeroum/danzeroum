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
    fetch_cur.fetchone.return_value = ("client-id","Acme Corp","LEAD",None,None,None,None,"LEAD",None,"2024-01-01T00:00:00")
    update_cur = MagicMock(); update_cur.rowcount = 1
    def fake_execute(q, params=None):
        if "INSERT" in q: return MagicMock(rowcount=1)
        if "UPDATE" in q: return update_cur
        if "WHERE id=" in q: return fetch_cur
        return list_cur
    mock_conn.execute.side_effect = fake_execute
    app.dependency_overrides[get_conn] = lambda: mock_conn
    with TestClient(app) as c:
        c.post("/auth/login", json={"username": "admin", "password": "test"})
        yield c
    app.dependency_overrides.clear()

def test_list_clients_empty(client):
    r = client.get("/clients")
    assert r.status_code == 200
    assert r.json() == []

def test_create_client(client):
    r = client.post("/clients", json={"name": "Acme Corp"})
    assert r.status_code == 201
    assert r.json()["name"] == "Acme Corp"

def test_patch_client(client):
    r = client.patch("/clients/client-id", json={"status": "CLIENT"})
    assert r.status_code == 200

def test_delete_client(client):
    r = client.delete("/clients/some-id")
    assert r.status_code == 204

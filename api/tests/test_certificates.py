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
    fetch_cur.fetchone.return_value = ("cert-id","Acme",None,None,None,None,None,None,None,"2024-01-01T00:00:00")
    def fake_execute(q, params=None):
        if "INSERT" in q: return MagicMock(rowcount=1)
        if "WHERE id=" in q: return fetch_cur
        return list_cur
    mock_conn.execute.side_effect = fake_execute
    app.dependency_overrides[get_conn] = lambda: mock_conn
    with TestClient(app) as c:
        c.post("/auth/login", json={"username": "admin", "password": "test"})
        yield c
    app.dependency_overrides.clear()

def test_list_certificates_empty(client):
    r = client.get("/certificates")
    assert r.status_code == 200
    assert r.json() == []

def test_create_certificate(client):
    r = client.post("/certificates", data={"client_name": "Acme"})
    assert r.status_code == 201
    assert r.json()["client_name"] == "Acme"

def test_delete_certificate(client):
    r = client.delete("/certificates/some-id")
    assert r.status_code == 204

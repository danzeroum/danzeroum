import io
import uuid

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from api.main import app
from api.deps import get_conn

_DOC_ID = uuid.UUID("55555555-5555-4555-8555-555555555555")

@pytest.fixture()
def client():
    mock_conn = MagicMock()
    list_cur = MagicMock()
    list_cur.fetchall.return_value = []
    fetch_cur = MagicMock()
    # get_conn usa row_factory=dict_row: linhas são dict, uuid vem como UUID.
    fetch_cur.fetchone.return_value = {
        "id": _DOC_ID, "type": "CND", "subtype": None, "name": "CND Federal",
        "file_name": None, "mime_type": None, "issue_date": None,
        "expiry_date": None, "is_valid": True, "notes": None,
        "created_at": "2024-01-01T00:00:00",
    }

    def fake_execute(q, params=None):
        if "INSERT INTO documents" in q:
            return MagicMock(rowcount=1)
        elif "SELECT" in q and "WHERE id=" in q:
            return fetch_cur
        else:
            return list_cur

    mock_conn.execute.side_effect = fake_execute
    app.dependency_overrides[get_conn] = lambda: mock_conn
    with TestClient(app) as c:
        c.post("/auth/login", json={"username": "admin", "password": "test"})
        yield c
    app.dependency_overrides.clear()

def test_list_documents_empty(client):
    r = client.get("/documents")
    assert r.status_code == 200
    assert r.json() == []

def test_create_document_json_fields(client):
    r = client.post("/documents", data={"type": "CND", "name": "CND Federal"})
    assert r.status_code == 201
    assert r.json()["type"] == "CND"

def test_delete_document(client):
    r = client.delete("/documents/some-id")
    assert r.status_code == 204

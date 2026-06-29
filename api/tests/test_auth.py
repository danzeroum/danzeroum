"""Testes de autenticação."""

import bcrypt
import pytest
from fastapi.testclient import TestClient

import api.routers.auth as auth_mod
from api.main import app
from api.deps import get_conn

_HASH = bcrypt.hashpw(b"secret123", bcrypt.gensalt()).decode()


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setattr(auth_mod, "_USERNAME", "admin")
    monkeypatch.setattr(auth_mod, "_PASSWORD_HASH", _HASH)
    monkeypatch.setattr(auth_mod, "_SECRET", "test-secret")
    # Recria o signer com o segredo de teste
    from itsdangerous import URLSafeTimedSerializer
    monkeypatch.setattr(auth_mod, "_signer", URLSafeTimedSerializer("test-secret", salt="dz-session"))
    # Stub get_conn para evitar erro 503 em rotas protegidas
    from unittest.mock import MagicMock
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_cur.fetchall.return_value = []
    mock_cur.fetchone.return_value = (0, {}, [])
    mock_conn.execute.return_value = mock_cur
    app.dependency_overrides[get_conn] = lambda: mock_conn
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


def test_health_public(client):
    r = client.get("/health")
    assert r.status_code == 200


def test_protected_without_cookie(client):
    r = client.get("/report")
    assert r.status_code == 401


def test_login_wrong_password(client):
    r = client.post("/auth/login", json={"username": "admin", "password": "wrong"})
    assert r.status_code == 401


def test_login_wrong_username(client):
    r = client.post("/auth/login", json={"username": "hacker", "password": "secret123"})
    assert r.status_code == 401


def test_login_ok_sets_cookie(client):
    r = client.post("/auth/login", json={"username": "admin", "password": "secret123"})
    assert r.status_code == 200
    assert r.json()["user"]["username"] == "admin"
    assert "dz_session" in r.cookies


def test_me_without_cookie(client):
    r = client.get("/auth/me")
    assert r.status_code == 401


def test_me_with_cookie(client):
    client.post("/auth/login", json={"username": "admin", "password": "secret123"})
    r = client.get("/auth/me")
    assert r.status_code == 200
    assert r.json()["username"] == "admin"


def test_protected_with_cookie(client):
    client.post("/auth/login", json={"username": "admin", "password": "secret123"})
    r = client.get("/report")
    assert r.status_code == 200


def test_logout_clears_cookie(client):
    client.post("/auth/login", json={"username": "admin", "password": "secret123"})
    r = client.post("/auth/logout")
    assert r.status_code == 200
    r2 = client.get("/auth/me")
    assert r2.status_code == 401

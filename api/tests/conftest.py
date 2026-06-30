"""Shared fixtures for API tests.

Strategy:
- /health, /collect, /config: no DB — tested directly or via monkeypatch
- /tenders, /alerts: monkeypatch api.db functions where imported in routers
- /report: override get_repo dependency with InMemoryRepository
- /config: redirect _STORE to tmp_path to avoid polluting the repo
"""

from __future__ import annotations

import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: testes que exigem um PostgreSQL real (DATABASE_URL)"
    )
from fastapi.testclient import TestClient

from api.main import app
from api.deps import get_repo
from danzeroum_tracker.storage import InMemoryRepository
from danzeroum_tracker.models import Score, Tender


def _make_tender(n: int = 1) -> Tender:
    return Tender(
        source="PNCP",
        external_id=f"ext-{n}",
        title=f"Edital de teste {n}",
        description="Descrição",
        status="OPEN",
        category="TI",
        budget_estimate=100_000.0 * n,
        uf="SP",
        url=f"https://example.com/{n}",
    )


def _make_score(recommendation: str = "GO") -> Score:
    return Score(
        fit_score=0.85,
        risk_score=0.2,
        complexity_score=0.3,
        recommendation=recommendation,
        key_requirements=["Atestado técnico"],
        pricing_guidance="R$ 80k–90k",
        analysis_text="Boa aderência.",
    )


@pytest.fixture()
def mem_repo() -> InMemoryRepository:
    repo = InMemoryRepository()
    t = _make_tender(1)
    tid, _ = repo.upsert_tender(t)
    repo.save_score(tid, _make_score("GO"))
    t2 = _make_tender(2)
    tid2, _ = repo.upsert_tender(t2)
    repo.save_score(tid2, _make_score("REVIEW"))
    return repo


@pytest.fixture()
def client(mem_repo: InMemoryRepository):
    app.dependency_overrides[get_repo] = lambda: mem_repo
    c = TestClient(app)
    c.post("/auth/login", json={"username": "admin", "password": "test"})
    yield c
    app.dependency_overrides.clear()


# --- Auth fixture helpers ---
import bcrypt
import api.routers.auth as auth_mod
from itsdangerous import URLSafeTimedSerializer

_TEST_HASH = bcrypt.hashpw(b"test", bcrypt.gensalt()).decode()


@pytest.fixture(autouse=True)
def _patch_auth(monkeypatch):
    """Patch auth module vars and auto-login all test clients."""
    monkeypatch.setattr(auth_mod, "_USERNAME", "admin")
    monkeypatch.setattr(auth_mod, "_PASSWORD_HASH", _TEST_HASH)
    monkeypatch.setattr(auth_mod, "_SECRET", "test-secret")
    monkeypatch.setattr(auth_mod, "_signer", URLSafeTimedSerializer("test-secret", salt="dz-session"))


@pytest.fixture()
def authed_client(client):
    """Retorna o client já autenticado (cookie dz_session injetado)."""
    client.post("/auth/login", json={"username": "admin", "password": "test"})
    return client

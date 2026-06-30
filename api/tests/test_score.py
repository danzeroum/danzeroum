"""Tests for POST /score/{tender_id} (re-scoring sob demanda)."""

from __future__ import annotations


def _first_tender_id(mem_repo):
    return mem_repo.list_tenders()[0]["id"]


def test_rescore_persists_and_returns_score(client, mem_repo):
    tid = _first_tender_id(mem_repo)
    before = len(mem_repo.scores_for(tid))

    r = client.post(f"/score/{tid}")
    assert r.status_code == 200
    body = r.json()
    assert body["recommendation"] in ("GO", "REVIEW", "SKIP")
    assert 0.0 <= body["fit_score"] <= 1.0
    assert isinstance(body["key_requirements"], list)

    # Persistiu um novo score para o edital.
    assert len(mem_repo.scores_for(tid)) == before + 1


def test_rescore_unknown_tender_404(client):
    r = client.post("/score/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_rescore_invalid_scorer_400(client, mem_repo):
    tid = _first_tender_id(mem_repo)
    r = client.post(f"/score/{tid}?scorer=banana")
    assert r.status_code == 400


def test_rescore_llm_without_key_uses_heuristic(client, mem_repo):
    # Sem DEEPSEEK_API_KEY, scorer=llm degrada para heurístico (200, sem erro).
    tid = _first_tender_id(mem_repo)
    r = client.post(f"/score/{tid}?scorer=llm")
    assert r.status_code == 200
    assert r.json()["recommendation"] in ("GO", "REVIEW", "SKIP")


def test_rescore_requires_auth(mem_repo):
    from fastapi.testclient import TestClient

    from api.deps import get_repo
    from api.main import app

    app.dependency_overrides[get_repo] = lambda: mem_repo
    try:
        anon = TestClient(app)
        tid = _first_tender_id(mem_repo)
        r = anon.post(f"/score/{tid}")
        assert r.status_code == 401
    finally:
        app.dependency_overrides.clear()

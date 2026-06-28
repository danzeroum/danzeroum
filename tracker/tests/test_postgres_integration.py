"""Integração com PostgreSQL real. Pulado se DATABASE_URL não estiver definido.

No CI roda contra um serviço postgres (ver .github/workflows/tracker_ci.yml).
Localmente: aplique sql/schema.sql num banco e exporte DATABASE_URL.
"""

from __future__ import annotations

import os
from datetime import datetime

import pytest

from danzeroum_tracker.models import Score, Tender

DATABASE_URL = os.environ.get("DATABASE_URL", "")

pytestmark = pytest.mark.integration

if not DATABASE_URL:
    pytest.skip("DATABASE_URL não definido — pulando testes de integração", allow_module_level=True)


@pytest.fixture
def repo():
    from danzeroum_tracker.storage.postgres import PostgresRepository

    r = PostgresRepository(DATABASE_URL)
    # limpa tabelas para um teste determinístico
    import psycopg

    with psycopg.connect(DATABASE_URL) as conn, conn.cursor() as cur:
        cur.execute("TRUNCATE tender_scores, tenders RESTART IDENTITY CASCADE;")
        conn.commit()
    return r


def _tender(ext="PG-1"):
    return Tender(
        source="PNCP",
        external_id=ext,
        title="Suporte técnico de TI",
        description="atestado exigido",
        status="OPEN",
        category="TI",
        budget_estimate=120000.0,
        publish_date=datetime(2026, 6, 1, 9, 0, 0),
        deadline=datetime(2026, 12, 30, 18, 0, 0),
        url="https://pncp.gov.br/app/editais/x",
        uf="SP",
        raw_json={"numeroControlePNCP": ext},
    )


def test_upsert_is_idempotent_and_scores_persist(repo):
    tid, new = repo.upsert_tender(_tender())
    assert new is True
    assert repo.count() == 1

    tid2, new2 = repo.upsert_tender(_tender())
    assert new2 is False
    assert tid2 == tid
    assert repo.count() == 1

    sid = repo.save_score(
        tid,
        Score(
            risk_score=0.2,
            fit_score=0.8,
            complexity_score=0.3,
            recommendation="GO",
            key_requirements=["atestado"],
            pricing_guidance="x",
            analysis_text="ok",
        ),
    )
    assert sid

    rows = repo.list_tenders(limit=10)
    assert len(rows) == 1
    assert rows[0]["source"] == "PNCP"
    assert rows[0]["category"] == "TI"

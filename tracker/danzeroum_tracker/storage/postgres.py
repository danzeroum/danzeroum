"""Repositório PostgreSQL (psycopg 3). Schema em ``sql/schema.sql``."""

from __future__ import annotations

import psycopg
from psycopg.types.json import Jsonb

from danzeroum_tracker.models import Score, Tender
from danzeroum_tracker.storage.base import TenderRepository

_UPSERT_TENDER = """
INSERT INTO tenders (
    source, external_id, title, description, status, category,
    budget_estimate, publish_date, deadline, url, uf, raw_json, updated_at
) VALUES (
    %(source)s, %(external_id)s, %(title)s, %(description)s, %(status)s, %(category)s,
    %(budget_estimate)s, %(publish_date)s, %(deadline)s, %(url)s, %(uf)s, %(raw_json)s, NOW()
)
ON CONFLICT (source, external_id) DO UPDATE SET
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    status = EXCLUDED.status,
    category = EXCLUDED.category,
    budget_estimate = EXCLUDED.budget_estimate,
    publish_date = EXCLUDED.publish_date,
    deadline = EXCLUDED.deadline,
    url = EXCLUDED.url,
    uf = EXCLUDED.uf,
    raw_json = EXCLUDED.raw_json,
    updated_at = NOW()
RETURNING id, (xmax = 0) AS inserted;
"""

_INSERT_SCORE = """
INSERT INTO tender_scores (
    tender_id, risk_score, fit_score, complexity_score,
    recommendation, key_requirements, pricing_guidance, analysis_text
) VALUES (
    %(tender_id)s, %(risk_score)s, %(fit_score)s, %(complexity_score)s,
    %(recommendation)s, %(key_requirements)s, %(pricing_guidance)s, %(analysis_text)s
)
RETURNING id;
"""

_LIST = """
SELECT id, source, external_id, title, status, category,
       budget_estimate, deadline, url, uf, created_at
FROM tenders
ORDER BY created_at DESC
LIMIT %(limit)s;
"""

_LIST_SCORED = """
SELECT t.id, t.source, t.external_id, t.title, t.status, t.category,
       t.budget_estimate, t.deadline, t.url, t.uf,
       s.fit_score, s.risk_score, s.recommendation
FROM tenders t
LEFT JOIN LATERAL (
    SELECT fit_score, risk_score, recommendation
    FROM tender_scores ts
    WHERE ts.tender_id = t.id
    ORDER BY ts.analyzed_at DESC
    LIMIT 1
) s ON TRUE
ORDER BY s.fit_score DESC NULLS LAST, t.created_at DESC
LIMIT %(limit)s;
"""


class PostgresRepository(TenderRepository):
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    def _connect(self) -> psycopg.Connection:
        return psycopg.connect(self.database_url)

    def upsert_tender(self, tender: Tender) -> tuple[str, bool]:
        params = {
            **tender.to_dict(),
            "publish_date": tender.publish_date,
            "deadline": tender.deadline,
            "raw_json": Jsonb(tender.raw_json or {}),
        }
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(_UPSERT_TENDER, params)
            row = cur.fetchone()
            conn.commit()
        return str(row[0]), bool(row[1])

    def save_score(self, tender_id: str, score: Score) -> str:
        params = {
            "tender_id": tender_id,
            "risk_score": score.risk_score,
            "fit_score": score.fit_score,
            "complexity_score": score.complexity_score,
            "recommendation": score.recommendation,
            "key_requirements": Jsonb(list(score.key_requirements)),
            "pricing_guidance": score.pricing_guidance,
            "analysis_text": score.analysis_text,
        }
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(_INSERT_SCORE, params)
            row = cur.fetchone()
            conn.commit()
        return str(row[0])

    def list_tenders(self, limit: int = 50) -> list[dict]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(_LIST, {"limit": limit})
            cols = [d.name for d in cur.description]
            rows = cur.fetchall()
        return [dict(zip(cols, row, strict=True)) for row in rows]

    def list_scored(self, limit: int = 50) -> list[dict]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(_LIST_SCORED, {"limit": limit})
            cols = [d.name for d in cur.description]
            rows = cur.fetchall()
        return [dict(zip(cols, row, strict=True)) for row in rows]

    def count(self) -> int:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM tenders;")
            (total,) = cur.fetchone()
        return int(total)

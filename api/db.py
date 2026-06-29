"""Direct psycopg queries for joined tender+score data not covered by TenderRepository."""

from __future__ import annotations

import psycopg

_BASE = """
SELECT
    t.id::text,
    t.source,
    t.external_id,
    t.title,
    t.description,
    t.status,
    t.category,
    t.budget_estimate,
    t.publish_date,
    t.deadline,
    t.url,
    t.uf,
    t.raw_json,
    t.created_at,
    s.risk_score,
    s.fit_score,
    s.complexity_score,
    s.recommendation,
    s.key_requirements,
    s.pricing_guidance,
    s.analysis_text
FROM tenders t
LEFT JOIN LATERAL (
    SELECT risk_score, fit_score, complexity_score, recommendation,
           key_requirements, pricing_guidance, analysis_text
    FROM tender_scores ts
    WHERE ts.tender_id = t.id
    ORDER BY ts.analyzed_at DESC
    LIMIT 1
) s ON TRUE
"""

_ORDER = {
    "fit": "s.fit_score DESC NULLS LAST, t.created_at DESC",
    "deadline": "t.deadline ASC NULLS LAST",
    "budget": "t.budget_estimate DESC NULLS LAST",
}


def _to_score(row: dict) -> dict | None:
    if row.get("fit_score") is None:
        return None
    return {
        "risk_score": float(row["risk_score"]),
        "fit_score": float(row["fit_score"]),
        "complexity_score": float(row["complexity_score"]),
        "recommendation": row["recommendation"],
        "key_requirements": row["key_requirements"] or [],
        "pricing_guidance": row["pricing_guidance"],
        "analysis_text": row["analysis_text"],
    }


def _to_summary(row: dict) -> dict:
    return {
        "id": row["id"],
        "source": row["source"],
        "external_id": row["external_id"],
        "title": row["title"],
        "status": row["status"],
        "category": row["category"],
        "budget_estimate": float(row["budget_estimate"]) if row["budget_estimate"] is not None else None,
        "publish_date": row["publish_date"],
        "deadline": row["deadline"],
        "url": row["url"],
        "uf": row["uf"],
        "created_at": row["created_at"],
        "score": _to_score(row),
    }


def search_tenders(
    conn: psycopg.Connection,
    *,
    q: str | None = None,
    uf: str | None = None,
    category: str | None = None,
    recommendation: str | None = None,
    min_fit: float | None = None,
    sort: str = "fit",
    page: int = 1,
    size: int = 50,
) -> tuple[list[dict], int]:
    conditions: list[str] = []
    params: list = []

    if q:
        conditions.append("(t.title ILIKE %s OR t.description ILIKE %s)")
        params += [f"%{q}%", f"%{q}%"]
    if uf:
        conditions.append("t.uf = %s")
        params.append(uf)
    if category:
        conditions.append("t.category = %s")
        params.append(category)
    if recommendation:
        conditions.append("s.recommendation = %s")
        params.append(recommendation)
    if min_fit is not None:
        conditions.append("s.fit_score >= %s")
        params.append(min_fit)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    order = _ORDER.get(sort, _ORDER["fit"])
    offset = (page - 1) * size

    with conn.cursor() as cur:
        cur.execute(
            f"SELECT COUNT(*) AS cnt FROM tenders t LEFT JOIN LATERAL (SELECT fit_score, recommendation FROM tender_scores ts WHERE ts.tender_id = t.id ORDER BY ts.analyzed_at DESC LIMIT 1) s ON TRUE {where}",
            params,
        )
        total: int = cur.fetchone()["cnt"]  # type: ignore[index]

        cur.execute(
            f"{_BASE} {where} ORDER BY {order} LIMIT %s OFFSET %s",
            params + [size, offset],
        )
        rows = cur.fetchall()

    return [_to_summary(r) for r in rows], total  # type: ignore[arg-type]


def get_tender_detail(conn: psycopg.Connection, tender_id: str) -> dict | None:
    with conn.cursor() as cur:
        cur.execute(f"{_BASE} WHERE t.id = %s::uuid", [tender_id])
        row = cur.fetchone()
    if row is None:
        return None
    result = _to_summary(row)  # type: ignore[arg-type]
    result["description"] = row["description"]  # type: ignore[index]
    result["raw_json"] = row["raw_json"] or {}  # type: ignore[index]
    return result


def get_recent_alerts(conn: psycopg.Connection, limit: int = 20) -> list[dict]:
    """Derive alerts from recent GO/REVIEW tenders (no alerts table in schema)."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT t.id::text, t.title, t.deadline, s.fit_score, s.recommendation
            FROM tenders t
            JOIN LATERAL (
                SELECT fit_score, recommendation
                FROM tender_scores ts
                WHERE ts.tender_id = t.id
                ORDER BY ts.analyzed_at DESC
                LIMIT 1
            ) s ON TRUE
            WHERE s.recommendation IN ('GO', 'REVIEW')
              AND t.status = 'OPEN'
            ORDER BY t.created_at DESC
            LIMIT %s
            """,
            [limit],
        )
        rows = cur.fetchall()

    alerts = []
    for r in rows:  # type: ignore[union-attr]
        level = "go" if r["recommendation"] == "GO" else "review"  # type: ignore[index]
        fit = f"{float(r['fit_score']):.0%}" if r["fit_score"] else "—"  # type: ignore[index]
        alerts.append(
            {
                "id": r["id"],  # type: ignore[index]
                "kind": "oportunidade",
                "level": level,
                "title": r["title"],  # type: ignore[index]
                "body": f"Aderência {fit} — {r['recommendation']}",  # type: ignore[index]
                "tender_id": r["id"],  # type: ignore[index]
            }
        )
    return alerts

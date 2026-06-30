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


# ── Analytics de propostas (win rate, valor ganho/perdido, série mensal) ────────

# Status que ainda estão "em jogo" (compõem o valor em pipeline).
_PIPELINE_STATUSES = ("DRAFT", "SENT", "UNDER_REVIEW")


def _compute_analytics(status_rows: list[dict], monthly_rows: list[dict]) -> dict:
    """Agrega contagens/valores por status e a série mensal. Função pura (testável)."""
    by_status: dict[str, int] = {}
    value_by_status: dict[str, float] = {}
    for r in status_rows:
        st = r["status"] or "UNKNOWN"
        by_status[st] = int(r["cnt"])
        value_by_status[st] = float(r["total_value"] or 0)

    won = by_status.get("WIN", 0)
    lost = by_status.get("LOST", 0)
    decided = won + lost
    win_rate = (won / decided) if decided else 0.0

    months: dict[str, dict] = {}
    for r in monthly_rows:
        m = r["month"]
        st = r["status"] or "UNKNOWN"
        c = int(r["cnt"])
        point = months.setdefault(m, {"month": m, "sent": 0, "won": 0, "lost": 0})
        point["sent"] += c
        if st == "WIN":
            point["won"] += c
        elif st == "LOST":
            point["lost"] += c

    return {
        "total_proposals": sum(by_status.values()),
        "by_status": by_status,
        "win_rate": round(win_rate, 4),
        "decided": decided,
        "value_won": round(value_by_status.get("WIN", 0.0), 2),
        "value_lost": round(value_by_status.get("LOST", 0.0), 2),
        "value_pipeline": round(
            sum(value_by_status.get(s, 0.0) for s in _PIPELINE_STATUSES), 2
        ),
        "monthly": [months[k] for k in sorted(months)],
    }


def get_proposal_analytics(conn: psycopg.Connection) -> dict:
    """Indicadores de negócio a partir da tabela ``proposals``."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT status, COUNT(*) AS cnt, COALESCE(SUM(price_offered), 0) AS total_value "
            "FROM proposals GROUP BY status"
        )
        status_rows = cur.fetchall()
        cur.execute(
            "SELECT to_char(date_trunc('month', submitted_at), 'YYYY-MM') AS month, "
            "status, COUNT(*) AS cnt FROM proposals "
            "WHERE submitted_at IS NOT NULL GROUP BY 1, 2 ORDER BY 1"
        )
        monthly_rows = cur.fetchall()
    return _compute_analytics(status_rows, monthly_rows)  # type: ignore[arg-type]


# ── Vencimento de certidões/documentos ──────────────────────────────────────────


def _doc_level(days_left: int) -> str:
    if days_left < 0:
        return "expired"
    if days_left <= 7:
        return "critical"
    if days_left <= 15:
        return "warning"
    return "notice"


def get_expiring_documents(conn: psycopg.Connection, within_days: int = 30) -> list[dict]:
    """Documentos/certidões com ``expiry_date`` em até ``within_days`` (inclui vencidos)."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id::text AS id, type, name, expiry_date, "
            "(expiry_date - CURRENT_DATE) AS days_left "
            "FROM documents "
            "WHERE expiry_date IS NOT NULL AND expiry_date <= (CURRENT_DATE + %s) "
            "ORDER BY expiry_date ASC",
            [within_days],
        )
        rows = cur.fetchall()
    out = []
    for r in rows:  # type: ignore[union-attr]
        days = int(r["days_left"])  # type: ignore[index]
        out.append(
            {
                "id": r["id"],  # type: ignore[index]
                "type": r["type"],  # type: ignore[index]
                "name": r["name"],  # type: ignore[index]
                "expiry_date": r["expiry_date"],  # type: ignore[index]
                "days_left": days,
                "level": _doc_level(days),
            }
        )
    return out


def expiring_docs_as_alerts(docs: list[dict]) -> list[dict]:
    """Converte documentos a vencer em alertas (kind=documento). Função pura."""
    alerts = []
    for d in docs:
        days = int(d["days_left"])
        label = d.get("name") or d.get("type") or "documento"
        if days < 0:
            body = f"VENCIDA há {abs(days)} dia(s)"
            level = "danger"
        else:
            body = f"vence em {days} dia(s)"
            level = "danger" if days <= 7 else "review"
        alerts.append(
            {
                "id": f"doc-{d['id']}",
                "kind": "documento",
                "level": level,
                "title": f"Certidão {label}",
                "body": body,
                "tender_id": None,
            }
        )
    return alerts


def get_recent_alerts(conn: psycopg.Connection, limit: int = 20) -> list[dict]:
    """Alertas: oportunidades (GO/REVIEW) + certidões a vencer (kind=documento)."""
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

    # Certidões a vencer entram primeiro (mais críticas). Best-effort: se a query
    # de documentos falhar, os alertas de oportunidade ainda são devolvidos.
    try:
        docs = expiring_docs_as_alerts(get_expiring_documents(conn, within_days=30))
    except Exception:  # noqa: BLE001
        docs = []
    return docs + alerts

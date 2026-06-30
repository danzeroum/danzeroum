"""Tests for proposal PDF generation e submitted_at no envio."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from api.deps import get_conn
from api.main import app
from api.pdf import build_proposal_pdf

# (id, tender_id, tender_title, status, price_offered, validity_days, version, notes, submitted_at)
_ROW = ("prop-1", "tender-1", "Suporte técnico de TI", "SENT", 95000.0, 60, 1, "Inclui SLA 8x5", None)


def test_build_proposal_pdf_returns_pdf_bytes():
    data = {
        "tender_title": "Suporte técnico de TI",
        "source": "PNCP",
        "external_id": "ext-9",
        "price_offered": 95000.0,
        "validity_days": 60,
        "status": "SENT",
        "version": 1,
        "notes": "Inclui SLA 8x5 e atendimento remoto.",
    }
    pdf = build_proposal_pdf(data)
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 800


def test_build_proposal_pdf_without_notes():
    pdf = build_proposal_pdf({"tender_title": "X", "price_offered": None})
    assert pdf.startswith(b"%PDF")


@pytest.fixture()
def client():
    def fake_execute(q, params=None):
        cur = MagicMock()
        if "WHERE p.id=" in q:
            cur.fetchone.return_value = _ROW
        elif "FROM tenders WHERE id=" in q:
            cur.fetchone.return_value = ("PNCP", "ext-9")
        else:
            cur.fetchone.return_value = None
        cur.rowcount = 1
        return cur

    mock_conn = MagicMock()
    mock_conn.execute.side_effect = fake_execute
    app.dependency_overrides[get_conn] = lambda: mock_conn
    with TestClient(app) as c:
        c.post("/auth/login", json={"username": "admin", "password": "test"})
        yield c
    app.dependency_overrides.clear()


def test_proposal_pdf_endpoint(client):
    r = client.get("/proposals/prop-1/pdf")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content.startswith(b"%PDF")
    assert "attachment" in r.headers.get("content-disposition", "")


def test_proposal_pdf_not_found():
    mock_conn = MagicMock()
    cur = MagicMock()
    cur.fetchone.return_value = None
    mock_conn.execute.return_value = cur
    app.dependency_overrides[get_conn] = lambda: mock_conn
    try:
        with TestClient(app) as c:
            c.post("/auth/login", json={"username": "admin", "password": "test"})
            r = c.get("/proposals/missing/pdf")
        assert r.status_code == 404
    finally:
        app.dependency_overrides.clear()

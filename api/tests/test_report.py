"""Tests for GET /report."""

from __future__ import annotations


def test_report_shape(client):
    r = client.get("/report")
    assert r.status_code == 200
    body = r.json()
    assert "total" in body
    assert "por_recomendacao" in body
    assert isinstance(body["por_recomendacao"], dict)
    assert "top" in body


def test_report_totals(client):
    r = client.get("/report")
    body = r.json()
    # mem_repo fixture seeds 2 tenders: 1 GO, 1 REVIEW
    assert body["total"] == 2
    assert body["por_recomendacao"].get("GO", 0) >= 1
    assert body["por_recomendacao"].get("REVIEW", 0) >= 1

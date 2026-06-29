"""Pydantic I/O schemas for the Danzeroum Tracker API."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ScoreOut(BaseModel):
    risk_score: float
    fit_score: float
    complexity_score: float
    recommendation: str  # GO | REVIEW | SKIP
    key_requirements: list[str]
    pricing_guidance: str | None = None
    analysis_text: str | None = None


class TenderSummary(BaseModel):
    id: str
    source: str
    external_id: str
    title: str
    status: str
    category: str
    budget_estimate: float | None
    publish_date: datetime | None
    deadline: datetime | None
    url: str | None
    uf: str | None
    created_at: datetime
    score: ScoreOut | None = None


class TenderDetail(TenderSummary):
    description: str | None = None
    raw_json: dict[str, Any] = {}


class PaginatedTenders(BaseModel):
    items: list[TenderSummary]
    total: int
    page: int
    size: int


class CollectionRunStatus(BaseModel):
    run_id: str
    status: str  # running | done | error
    result: dict[str, Any] | None = None


class ReportOut(BaseModel):
    total: int
    por_recomendacao: dict[str, int]
    top: list[dict[str, Any]]


class ConfigOut(BaseModel):
    sources: list[str]
    modalidades: list[int]
    proposal_horizon_days: int
    uf: str
    keywords: list[str]
    scorer: str
    collect_interval_hours: float
    min_fit_alert: float
    page_size: int
    max_pages: int


class ConfigPatch(BaseModel):
    sources: list[str] | None = None
    modalidades: list[int] | None = None
    proposal_horizon_days: int | None = None
    uf: str | None = None
    keywords: list[str] | None = None
    scorer: str | None = None
    collect_interval_hours: float | None = None
    min_fit_alert: float | None = None
    page_size: int | None = None
    max_pages: int | None = None


class AlertOut(BaseModel):
    id: str
    kind: str   # oportunidade | prazo | documento
    level: str  # go | review | danger
    title: str
    body: str
    tender_id: str | None = None

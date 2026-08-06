"""Pydantic I/O schemas for the Danzeroum Tracker API."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, model_validator


class _UUIDStr(BaseModel):
    """Converte objetos UUID em str antes da validação.

    ``get_conn`` usa ``row_factory=dict_row``, e o psycopg devolve colunas
    ``uuid`` como objetos ``UUID`` — mas estes schemas declaram ``id`` e
    ``tender_id`` como ``str``.
    """

    @model_validator(mode="before")
    @classmethod
    def _coerce_uuids(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return {k: str(v) if isinstance(v, UUID) else v for k, v in data.items()}
        return data


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


class MonthlyPoint(BaseModel):
    month: str  # YYYY-MM
    sent: int
    won: int
    lost: int


class AnalyticsOut(BaseModel):
    total_proposals: int
    by_status: dict[str, int]
    win_rate: float          # WIN / (WIN + LOST)
    decided: int             # WIN + LOST
    value_won: float
    value_lost: float
    value_pipeline: float    # DRAFT + SENT + UNDER_REVIEW
    monthly: list[MonthlyPoint]


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


class AlertOut(_UUIDStr):
    id: str
    kind: str   # oportunidade | prazo | documento
    level: str  # go | review | danger
    title: str
    body: str
    tender_id: str | None = None


# Documents
class DocumentOut(_UUIDStr):
    id: str
    type: str
    subtype: str | None = None
    name: str | None = None
    file_name: str | None = None
    mime_type: str | None = None
    issue_date: date | None = None
    expiry_date: date | None = None
    is_valid: bool = True
    notes: str | None = None
    created_at: datetime

class DocumentExpiringOut(BaseModel):
    id: str
    type: str
    name: str | None = None
    expiry_date: date
    days_left: int
    level: str  # expired | critical | warning | notice

class DocumentCreate(BaseModel):
    type: str
    subtype: str | None = None
    name: str | None = None
    issue_date: date | None = None
    expiry_date: date | None = None
    notes: str | None = None

# Proposals
class ProposalOut(_UUIDStr):
    id: str
    tender_id: str
    tender_title: str | None = None
    status: str
    price_offered: float | None = None
    validity_days: int | None = None
    version: int = 1
    notes: str | None = None
    submitted_at: datetime | None = None

class ProposalCreate(BaseModel):
    tender_id: str
    status: str = "DRAFT"
    price_offered: float | None = None
    validity_days: int | None = None
    notes: str | None = None

class ProposalStatusPatch(BaseModel):
    status: str  # DRAFT|SENT|UNDER_REVIEW|WIN|LOST|DISQUALIFIED

# Clients
class ClientOut(_UUIDStr):
    id: str
    name: str | None = None
    type: str | None = None
    cnpj: str | None = None
    contact_name: str | None = None
    email: str | None = None
    phone: str | None = None
    status: str | None = None
    notes: str | None = None
    created_at: datetime

class ClientCreate(BaseModel):
    name: str
    type: str = "LEAD"
    cnpj: str | None = None
    contact_name: str | None = None
    email: str | None = None
    phone: str | None = None
    status: str = "LEAD"
    notes: str | None = None

class ClientPatch(BaseModel):
    name: str | None = None
    status: str | None = None
    contact_name: str | None = None
    email: str | None = None
    phone: str | None = None
    notes: str | None = None

# Technical Certificates
class CertificateOut(_UUIDStr):
    id: str
    client_name: str | None = None
    project_description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    project_value: float | None = None
    scope: str | None = None
    file_name: str | None = None
    mime_type: str | None = None
    created_at: datetime

class CertificateCreate(BaseModel):
    client_name: str
    project_description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    project_value: float | None = None
    scope: str | None = None

# Calculator (stateless)
class CalcInput(BaseModel):
    revenue: float           # usado como RBT12 (receita dos últimos 12 meses)
    payroll_pct: float       # folha/receita → Fator R
    direct_cost_pct: float
    margin_pct: float
    iss_pct: float = 0.0     # ISS municipal adicional, fora do Simples (opcional)

class CalcOut(BaseModel):
    min_price: float
    direct_cost: float
    tax_burden: float
    effective_margin: float
    anexo: str
    fator_r: float
    effective_rate: float    # alíquota efetiva do Simples (progressiva)
    iss_pct: float = 0.0

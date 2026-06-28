"""Modelos de domínio (schema canônico), independentes de banco e de fonte."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

# Status normalizado do edital.
TENDER_STATUSES = ("OPEN", "CLOSED", "AWARDED", "CANCELLED")
# Categorias inferidas.
CATEGORIES = ("TI", "TELECOM", "OUTROS")
# Recomendações do scorer.
RECOMMENDATIONS = ("GO", "REVIEW", "SKIP")


@dataclass
class Tender:
    """Edital normalizado, comum a todas as fontes."""

    source: str
    external_id: str
    title: str
    description: str | None = None
    status: str = "OPEN"
    category: str = "OUTROS"
    budget_estimate: float | None = None
    publish_date: datetime | None = None
    deadline: datetime | None = None
    url: str | None = None
    uf: str | None = None
    raw_json: dict[str, Any] = field(default_factory=dict)

    @property
    def dedupe_key(self) -> tuple[str, str]:
        """Chave de deduplicação estável (origem + id nativo)."""
        return (self.source, self.external_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "external_id": self.external_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "category": self.category,
            "budget_estimate": self.budget_estimate,
            "publish_date": self.publish_date.isoformat() if self.publish_date else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "url": self.url,
            "uf": self.uf,
        }


@dataclass
class Score:
    """Resultado da análise de aderência (scorer)."""

    risk_score: float
    fit_score: float
    complexity_score: float
    recommendation: str
    key_requirements: list[str] = field(default_factory=list)
    pricing_guidance: str | None = None
    analysis_text: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "risk_score": round(self.risk_score, 2),
            "fit_score": round(self.fit_score, 2),
            "complexity_score": round(self.complexity_score, 2),
            "recommendation": self.recommendation,
            "key_requirements": list(self.key_requirements),
            "pricing_guidance": self.pricing_guidance,
        }

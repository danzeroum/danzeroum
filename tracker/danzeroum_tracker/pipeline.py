"""Orquestração: coleta → dedupe (upsert) → score → alertas."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from danzeroum_tracker.adapters.base import AdapterError, OrgaoAdapter
from danzeroum_tracker.models import Tender
from danzeroum_tracker.scoring.base import Scorer
from danzeroum_tracker.storage.base import TenderRepository


@dataclass
class CollectionResult:
    collected: int = 0
    new: int = 0
    scored: int = 0
    alerts: list[dict] = field(default_factory=list)
    errors: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "collected": self.collected,
            "new": self.new,
            "scored": self.scored,
            "alerts": self.alerts,
            "errors": self.errors,
        }


def run_collection(
    adapters: Iterable[OrgaoAdapter],
    repo: TenderRepository,
    scorer: Scorer,
    *,
    min_fit_alert: float = 0.4,
) -> CollectionResult:
    """Roda a coleta de todos os adaptadores e pontua os editais novos.

    Idempotente: editais já vistos (mesmo source+external_id) são atualizados,
    não duplicados, e não são re-pontuados.
    """
    result = CollectionResult()
    for adapter in adapters:
        source = getattr(adapter, "source", "?")
        try:
            for tender in adapter.collect():
                result.collected += 1
                tender_id, is_new = repo.upsert_tender(tender)
                if not is_new:
                    continue
                result.new += 1
                score = scorer.score(tender)
                repo.save_score(tender_id, score)
                result.scored += 1
                if score.fit_score >= min_fit_alert and score.recommendation != "SKIP":
                    result.alerts.append(_alert(tender, tender_id, score))
        except AdapterError as exc:
            # Isola a falha: uma fonte com erro não derruba a coleta das demais.
            result.errors.append({"source": source, "error": str(exc)})
    return result


def _alert(tender: Tender, tender_id: str, score) -> dict:
    return {
        "tender_id": tender_id,
        "source": tender.source,
        "external_id": tender.external_id,
        "title": tender.title,
        "url": tender.url,
        "budget_estimate": tender.budget_estimate,
        "deadline": tender.deadline.isoformat() if tender.deadline else None,
        "fit_score": score.fit_score,
        "risk_score": score.risk_score,
        "recommendation": score.recommendation,
    }

"""Repositório em memória — testes e modo dry-run (sem banco)."""

from __future__ import annotations

import uuid
from datetime import datetime

from danzeroum_tracker.models import Score, Tender
from danzeroum_tracker.storage.base import TenderRepository


def _parse_dt(value) -> datetime | None:
    if isinstance(value, datetime) or value is None:
        return value
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


class InMemoryRepository(TenderRepository):
    def __init__(self) -> None:
        # chave de dedupe → registro
        self._tenders: dict[tuple[str, str], dict] = {}
        self._scores: dict[str, list[dict]] = {}

    def upsert_tender(self, tender: Tender) -> tuple[str, bool]:
        key = tender.dedupe_key
        existing = self._tenders.get(key)
        if existing is not None:
            existing.update(tender.to_dict())
            return existing["id"], False
        tender_id = str(uuid.uuid4())
        record = {"id": tender_id, **tender.to_dict()}
        self._tenders[key] = record
        return tender_id, True

    def get_tender(self, tender_id: str) -> Tender | None:
        for rec in self._tenders.values():
            if rec["id"] == tender_id:
                return Tender(
                    source=rec["source"],
                    external_id=rec["external_id"],
                    title=rec["title"],
                    description=rec.get("description"),
                    status=rec.get("status", "OPEN"),
                    category=rec.get("category", "OUTROS"),
                    budget_estimate=rec.get("budget_estimate"),
                    publish_date=_parse_dt(rec.get("publish_date")),
                    deadline=_parse_dt(rec.get("deadline")),
                    url=rec.get("url"),
                    uf=rec.get("uf"),
                    raw_json=rec.get("raw_json") or {},
                )
        return None

    def save_score(self, tender_id: str, score: Score) -> str:
        score_id = str(uuid.uuid4())
        self._scores.setdefault(tender_id, []).append({"id": score_id, **score.to_dict()})
        return score_id

    def list_tenders(self, limit: int = 50) -> list[dict]:
        return list(self._tenders.values())[:limit]

    def list_scored(self, limit: int = 50) -> list[dict]:
        out = []
        for rec in self._tenders.values():
            scores = self._scores.get(rec["id"], [])
            latest = scores[-1] if scores else {}
            out.append(
                {
                    **rec,
                    "fit_score": latest.get("fit_score"),
                    "risk_score": latest.get("risk_score"),
                    "recommendation": latest.get("recommendation"),
                }
            )
        out.sort(key=lambda r: (r.get("fit_score") or 0.0), reverse=True)
        return out[:limit]

    def count(self) -> int:
        return len(self._tenders)

    # auxiliares de teste/dry-run
    def scores_for(self, tender_id: str) -> list[dict]:
        return self._scores.get(tender_id, [])

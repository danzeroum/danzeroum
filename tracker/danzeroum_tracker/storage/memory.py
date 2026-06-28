"""Repositório em memória — testes e modo dry-run (sem banco)."""

from __future__ import annotations

import uuid

from danzeroum_tracker.models import Score, Tender
from danzeroum_tracker.storage.base import TenderRepository


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

    def save_score(self, tender_id: str, score: Score) -> str:
        score_id = str(uuid.uuid4())
        self._scores.setdefault(tender_id, []).append({"id": score_id, **score.to_dict()})
        return score_id

    def list_tenders(self, limit: int = 50) -> list[dict]:
        return list(self._tenders.values())[:limit]

    def count(self) -> int:
        return len(self._tenders)

    # auxiliares de teste/dry-run
    def scores_for(self, tender_id: str) -> list[dict]:
        return self._scores.get(tender_id, [])

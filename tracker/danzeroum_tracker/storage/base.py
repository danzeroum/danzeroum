"""Interface de persistência (porta de saída)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from danzeroum_tracker.models import Score, Tender


class TenderRepository(ABC):
    """Contrato de persistência de editais e scores."""

    @abstractmethod
    def upsert_tender(self, tender: Tender) -> tuple[str, bool]:
        """Insere ou atualiza por (source, external_id).

        Retorna ``(id, is_new)`` — ``is_new=True`` se o edital ainda não existia.
        """

    @abstractmethod
    def save_score(self, tender_id: str, score: Score) -> str:
        """Persiste o resultado do scorer e retorna o id do score."""

    @abstractmethod
    def list_tenders(self, limit: int = 50) -> list[dict]:
        """Lista editais (mais recentes primeiro)."""

    @abstractmethod
    def list_scored(self, limit: int = 50) -> list[dict]:
        """Lista editais com o score mais recente (fit/risk/recommendation), por fit desc."""

    @abstractmethod
    def count(self) -> int:
        """Total de editais armazenados."""

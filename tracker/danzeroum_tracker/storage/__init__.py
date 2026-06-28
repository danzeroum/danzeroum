"""Armazenamento. ``InMemoryRepository`` para testes/dry-run; PostgreSQL em prod."""

from __future__ import annotations

from danzeroum_tracker.storage.base import TenderRepository
from danzeroum_tracker.storage.memory import InMemoryRepository

__all__ = ["TenderRepository", "InMemoryRepository", "build_repository"]


def build_repository(database_url: str = "") -> TenderRepository:
    """Factory: sem ``database_url`` → memória; com URL → PostgreSQL."""
    if not database_url or database_url == ":memory:":
        return InMemoryRepository()
    # Import tardio: evita exigir psycopg quando se usa apenas memória.
    from danzeroum_tracker.storage.postgres import PostgresRepository

    return PostgresRepository(database_url)

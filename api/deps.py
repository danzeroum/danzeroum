"""FastAPI dependencies — settings singleton and DB connection."""

from __future__ import annotations

from typing import Generator

import psycopg
from psycopg.rows import dict_row
from fastapi import HTTPException

from danzeroum_tracker.config import Settings
from danzeroum_tracker.storage import TenderRepository, build_repository

_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings.from_env()
    return _settings


def get_repo() -> TenderRepository:
    cfg = get_settings()
    return build_repository(cfg.database_url)


def get_conn() -> Generator[psycopg.Connection, None, None]:
    cfg = get_settings()
    if not cfg.database_url:
        raise HTTPException(503, "DATABASE_URL não configurado — banco indisponível")
    try:
        with psycopg.connect(cfg.database_url, row_factory=dict_row) as conn:
            yield conn
    except psycopg.OperationalError as exc:
        raise HTTPException(503, f"Banco indisponível: {exc}") from exc

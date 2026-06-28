"""FastAPI dependencies — settings singleton and DB connection."""

from __future__ import annotations

from typing import Generator

import psycopg
from psycopg.rows import dict_row

from danzeroum_tracker.config import Settings

_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings.from_env()
    return _settings


def get_conn() -> Generator[psycopg.Connection, None, None]:
    cfg = get_settings()
    with psycopg.connect(cfg.database_url, row_factory=dict_row) as conn:
        yield conn

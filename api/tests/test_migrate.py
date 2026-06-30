"""Testes do runner de migrations (descoberta/ordem + integração Postgres)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from api.migrate import apply_migrations, discover_migrations, main


def test_discover_migrations_sorted(tmp_path: Path):
    (tmp_path / "002_b.sql").write_text("-- b")
    (tmp_path / "001_a.sql").write_text("-- a")
    (tmp_path / "ignore.txt").write_text("nope")
    names = [p.name for p in discover_migrations(tmp_path)]
    assert names == ["001_a.sql", "002_b.sql"]


def test_discover_migrations_empty_dir(tmp_path: Path):
    assert discover_migrations(tmp_path / "naoexiste") == []


def test_main_noop_without_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert main() == 0


def test_real_migrations_dir_has_files():
    # Garante que o runner enxerga as migrations reais da API.
    names = [p.name for p in discover_migrations()]
    assert "002_add_file_data.sql" in names


# ── Integração (Postgres real; pulado sem DATABASE_URL) ─────────────────────────

DATABASE_URL = os.environ.get("DATABASE_URL", "")


@pytest.mark.integration
@pytest.mark.skipif(not DATABASE_URL, reason="DATABASE_URL não definido")
def test_apply_migrations_idempotent():
    import psycopg

    schema = (
        Path(__file__).resolve().parents[2] / "tracker" / "sql" / "schema.sql"
    ).read_text(encoding="utf-8")

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            # schema base limpo + aplicado (como faz o initdb do Postgres).
            cur.execute("DROP TABLE IF EXISTS schema_migrations CASCADE;")
            cur.execute(schema)
            cur.execute("ALTER TABLE documents DROP COLUMN IF EXISTS file_data;")
        conn.commit()

        applied = apply_migrations(conn)
        assert "002_add_file_data.sql" in applied

        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM information_schema.columns "
                "WHERE table_name='documents' AND column_name='file_data';"
            )
            assert cur.fetchone() is not None
            cur.execute("SELECT COUNT(*) FROM schema_migrations;")
            assert cur.fetchone()[0] >= 1

        # 2ª execução: nada pendente (idempotente).
        assert apply_migrations(conn) == []

"""Runner de migrations da API — aplica api/migrations/*.sql idempotentemente.

O schema base vem de ``tracker/sql/schema.sql`` (aplicado pelo initdb do Postgres).
Este runner aplica as migrations incrementais da API sobre ele, registrando o que já
foi aplicado numa tabela ``schema_migrations``. Roda no startup do contêiner da API
(ver ``api/entrypoint.sh``) e no CI.

Uso:
  DATABASE_URL=postgresql://... python -m api.migrate

Sem ``DATABASE_URL``: loga e sai 0 (não quebra ambientes locais/teste sem banco).
"""

from __future__ import annotations

import logging
import os
import sys
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="[migrate] %(message)s")
logger = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"

_ENSURE_TABLE = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    filename   TEXT PRIMARY KEY,
    applied_at TIMESTAMP NOT NULL DEFAULT NOW()
);
"""


def discover_migrations(directory: Path = MIGRATIONS_DIR) -> list[Path]:
    """Lista os .sql em ordem de nome (001_, 002_, ...)."""
    if not directory.exists():
        return []
    return sorted(p for p in directory.glob("*.sql") if p.is_file())


def _connect_with_retry(database_url: str, *, attempts: int = 5, delay: float = 2.0):
    import psycopg

    last: Exception | None = None
    for i in range(1, attempts + 1):
        try:
            return psycopg.connect(database_url)
        except psycopg.OperationalError as exc:  # banco ainda aquecendo
            last = exc
            logger.info("banco indisponível (tentativa %d/%d): %s", i, attempts, exc)
            if i < attempts:
                time.sleep(delay)
    assert last is not None
    raise last


def apply_migrations(conn, directory: Path = MIGRATIONS_DIR) -> list[str]:
    """Aplica as migrations pendentes. Retorna os nomes aplicados nesta execução."""
    with conn.cursor() as cur:
        cur.execute(_ENSURE_TABLE)
        conn.commit()
        cur.execute("SELECT filename FROM schema_migrations;")
        applied = {row[0] for row in cur.fetchall()}

    newly: list[str] = []
    for path in discover_migrations(directory):
        if path.name in applied:
            continue
        sql = path.read_text(encoding="utf-8")
        # Cada migration em sua própria transação: falha isola e não deixa schema parcial.
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
                cur.execute(
                    "INSERT INTO schema_migrations (filename) VALUES (%s);", [path.name]
                )
            conn.commit()
        except Exception:
            conn.rollback()
            logger.error("falha ao aplicar %s", path.name)
            raise
        logger.info("aplicada: %s", path.name)
        newly.append(path.name)

    if not newly:
        logger.info("nenhuma migration pendente")
    return newly


def main() -> int:
    database_url = os.environ.get("DATABASE_URL", "")
    if not database_url:
        logger.info("DATABASE_URL não configurado — nada a fazer")
        return 0
    try:
        conn = _connect_with_retry(database_url)
    except Exception as exc:  # noqa: BLE001
        logger.error("não foi possível conectar ao banco: %s", exc)
        return 1
    try:
        apply_migrations(conn)
    except Exception as exc:  # noqa: BLE001 - falha real de migration deve bloquear o boot
        logger.error("migration falhou: %s", exc)
        return 1
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.deps import get_settings
from api.schemas import ReportOut

router = APIRouter(prefix="/report", tags=["report"])


@router.get("", response_model=ReportOut)
def get_report(top_n: int = 10):
    cfg = get_settings()
    if not cfg.database_url:
        raise HTTPException(503, "DATABASE_URL não configurado")
    try:
        from danzeroum_tracker.reporting import build_report
        from danzeroum_tracker.storage.postgres import PostgresRepository

        repo = PostgresRepository(cfg.database_url)
        rows = repo.list_scored(limit=500)
        return build_report(rows, top_n=top_n)
    except Exception as exc:
        raise HTTPException(503, f"Banco indisponível: {exc}") from exc

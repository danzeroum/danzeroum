from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from api.deps import get_repo
from api.schemas import ReportOut
from danzeroum_tracker.storage import TenderRepository

router = APIRouter(prefix="/report", tags=["report"])

Repo = Annotated[TenderRepository, Depends(get_repo)]


@router.get("", response_model=ReportOut)
def get_report(repo: Repo, top_n: int = 10):
    try:
        from danzeroum_tracker.reporting import build_report

        rows = repo.list_scored(limit=500)
        return build_report(rows, top_n=top_n)
    except Exception as exc:
        raise HTTPException(503, f"Banco indisponível: {exc}") from exc

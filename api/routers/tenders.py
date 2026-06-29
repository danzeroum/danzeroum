from __future__ import annotations

from typing import Annotated

import psycopg
from fastapi import APIRouter, Depends, HTTPException, Query

from api.db import get_tender_detail, search_tenders
from api.deps import get_conn
from api.schemas import PaginatedTenders, TenderDetail

router = APIRouter(prefix="/tenders", tags=["tenders"])

Conn = Annotated[psycopg.Connection, Depends(get_conn)]


@router.get("", response_model=PaginatedTenders)
def list_tenders(
    conn: Conn,
    q: str | None = Query(None),
    uf: str | None = Query(None),
    category: str | None = Query(None),
    recommendation: str | None = Query(None, pattern="^(GO|REVIEW|SKIP)$"),
    min_fit: float | None = Query(None, ge=0.0, le=1.0),
    sort: str = Query("fit", pattern="^(fit|deadline|budget)$"),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
):
    items, total = search_tenders(
        conn,
        q=q,
        uf=uf,
        category=category,
        recommendation=recommendation,
        min_fit=min_fit,
        sort=sort,
        page=page,
        size=size,
    )
    return {"items": items, "total": total, "page": page, "size": size}


@router.get("/{tender_id}", response_model=TenderDetail)
def get_tender(conn: Conn, tender_id: str):
    detail = get_tender_detail(conn, tender_id)
    if detail is None:
        raise HTTPException(404, "Edital não encontrado")
    return detail

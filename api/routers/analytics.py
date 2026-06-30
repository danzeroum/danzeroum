"""Analytics de negócio — indicadores derivados das propostas.

Transforma o histórico de ``proposals`` em métricas de gestão (taxa de vitória,
valor ganho/perdido, pipeline e evolução mensal) que dizem onde vale a pena licitar.
"""

from __future__ import annotations

from typing import Annotated

import psycopg
from fastapi import APIRouter, Depends, HTTPException

from api.db import get_proposal_analytics
from api.deps import get_conn
from api.schemas import AnalyticsOut

router = APIRouter(prefix="/analytics", tags=["analytics"])

Conn = Annotated[psycopg.Connection, Depends(get_conn)]


@router.get("", response_model=AnalyticsOut)
def get_analytics(conn: Conn):
    try:
        return get_proposal_analytics(conn)
    except Exception as exc:  # noqa: BLE001 - falha de banco vira 503
        raise HTTPException(503, f"Banco indisponível: {exc}") from exc

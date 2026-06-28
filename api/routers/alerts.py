from __future__ import annotations

from typing import Annotated

import psycopg
from fastapi import APIRouter, Depends

from api.db import get_recent_alerts
from api.deps import get_conn

router = APIRouter(prefix="/alerts", tags=["alerts"])

Conn = Annotated[psycopg.Connection, Depends(get_conn)]


@router.get("")
def list_alerts(conn: Conn, limit: int = 20):
    return get_recent_alerts(conn, limit=limit)

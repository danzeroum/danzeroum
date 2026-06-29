"""Clients / CRM router."""
from __future__ import annotations
import uuid
from typing import Annotated
import psycopg
from fastapi import APIRouter, Depends, HTTPException
from api.deps import get_conn
from api.schemas import ClientCreate, ClientOut, ClientPatch

router = APIRouter(prefix="/clients", tags=["clients"])
Conn = Annotated[psycopg.Connection, Depends(get_conn)]

_COLS = "id, name, type, cnpj, contact_name, email, phone, status, notes, created_at"

@router.get("", response_model=list[ClientOut])
def list_clients(conn: Conn, status: str | None = None):
    q = f"SELECT {_COLS} FROM clients WHERE 1=1"
    params: list = []
    if status:
        q += " AND status=%s"
        params.append(status)
    q += " ORDER BY created_at DESC"
    rows = conn.execute(q, params).fetchall()
    cols = _COLS.split(", ")
    return [ClientOut(**r) for r in rows]

@router.post("", response_model=ClientOut, status_code=201)
def create_client(body: ClientCreate, conn: Conn):
    c_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO clients (id, name, type, cnpj, contact_name, email, phone, status, notes) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        [c_id, body.name, body.type, body.cnpj, body.contact_name, body.email, body.phone, body.status, body.notes]
    )
    conn.commit()
    row = conn.execute(f"SELECT {_COLS} FROM clients WHERE id=%s", [c_id]).fetchone()
    cols = _COLS.split(", ")
    return ClientOut(**row)

@router.patch("/{client_id}", response_model=ClientOut)
def patch_client(client_id: str, body: ClientPatch, conn: Conn):
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(400, "No fields to update")
    set_clause = ", ".join(f"{k}=%s" for k in updates)
    conn.execute(f"UPDATE clients SET {set_clause} WHERE id=%s", [*updates.values(), client_id])
    conn.commit()
    row = conn.execute(f"SELECT {_COLS} FROM clients WHERE id=%s", [client_id]).fetchone()
    if not row:
        raise HTTPException(404)
    cols = _COLS.split(", ")
    return ClientOut(**row)

@router.delete("/{client_id}", status_code=204)
def delete_client(client_id: str, conn: Conn):
    conn.execute("DELETE FROM clients WHERE id=%s", [client_id])
    conn.commit()

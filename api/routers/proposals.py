"""Proposals router."""
from __future__ import annotations
import uuid
from typing import Annotated
import psycopg
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from api.deps import get_conn
from api.pdf import build_proposal_pdf
from api.schemas import ProposalCreate, ProposalOut, ProposalStatusPatch

router = APIRouter(prefix="/proposals", tags=["proposals"])
Conn = Annotated[psycopg.Connection, Depends(get_conn)]

_COLS = "p.id, p.tender_id, t.title AS tender_title, p.status, p.price_offered, p.validity_days, p.version, p.notes, p.submitted_at"

@router.get("", response_model=list[ProposalOut])
def list_proposals(conn: Conn, status: str | None = None):
    q = f"SELECT {_COLS} FROM proposals p LEFT JOIN tenders t ON t.id=p.tender_id WHERE 1=1"
    params: list = []
    if status:
        q += " AND p.status=%s"
        params.append(status)
    q += " ORDER BY p.submitted_at DESC NULLS LAST"
    rows = conn.execute(q, params).fetchall()
    cols = ["id","tender_id","tender_title","status","price_offered","validity_days","version","notes","submitted_at"]
    return [ProposalOut(**{k: float(v) if k=="price_offered" and v is not None else v for k,v in zip(cols,r)}) for r in rows]

@router.post("", response_model=ProposalOut, status_code=201)
def create_proposal(body: ProposalCreate, conn: Conn):
    prop_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO proposals (id, tender_id, status, price_offered, validity_days, notes) VALUES (%s,%s,%s,%s,%s,%s)",
        [prop_id, body.tender_id, body.status, body.price_offered, body.validity_days, body.notes]
    )
    conn.commit()
    row = conn.execute(f"SELECT {_COLS} FROM proposals p LEFT JOIN tenders t ON t.id=p.tender_id WHERE p.id=%s", [prop_id]).fetchone()
    cols = ["id","tender_id","tender_title","status","price_offered","validity_days","version","notes","submitted_at"]
    return ProposalOut(**{k: float(v) if k=="price_offered" and v is not None else v for k,v in zip(cols,row)})

@router.get("/{prop_id}/pdf")
def proposal_pdf(prop_id: str, conn: Conn):
    """Gera o PDF da proposta (edital + preço) pronto para envio."""
    row = conn.execute(
        f"SELECT {_COLS} FROM proposals p LEFT JOIN tenders t ON t.id=p.tender_id WHERE p.id=%s",
        [prop_id],
    ).fetchone()
    if not row:
        raise HTTPException(404)
    cols = ["id","tender_id","tender_title","status","price_offered","validity_days","version","notes","submitted_at"]
    data = {k: (float(v) if k == "price_offered" and v is not None else v) for k, v in zip(cols, row)}
    # Enriquecimento opcional do edital (fonte / identificador) para o cabeçalho.
    tinfo = conn.execute(
        "SELECT source, external_id FROM tenders WHERE id=%s", [data.get("tender_id")]
    ).fetchone()
    if tinfo:
        data["source"], data["external_id"] = tinfo[0], tinfo[1]
    pdf = build_proposal_pdf(data)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="proposta-{prop_id}.pdf"'},
    )


@router.patch("/{prop_id}/status", response_model=ProposalOut)
def patch_proposal_status(prop_id: str, body: ProposalStatusPatch, conn: Conn):
    # Ao marcar como ENVIADA, carimba submitted_at (alimenta os analytics mensais).
    if body.status == "SENT":
        result = conn.execute(
            "UPDATE proposals SET status=%s, submitted_at=COALESCE(submitted_at, NOW()) WHERE id=%s",
            [body.status, prop_id],
        )
    else:
        result = conn.execute("UPDATE proposals SET status=%s WHERE id=%s", [body.status, prop_id])
    if result.rowcount == 0:
        raise HTTPException(404)
    conn.commit()
    row = conn.execute(f"SELECT {_COLS} FROM proposals p LEFT JOIN tenders t ON t.id=p.tender_id WHERE p.id=%s", [prop_id]).fetchone()
    cols = ["id","tender_id","tender_title","status","price_offered","validity_days","version","notes","submitted_at"]
    return ProposalOut(**{k: float(v) if k=="price_offered" and v is not None else v for k,v in zip(cols,row)})

@router.delete("/{prop_id}", status_code=204)
def delete_proposal(prop_id: str, conn: Conn):
    conn.execute("DELETE FROM proposals WHERE id=%s", [prop_id])
    conn.commit()

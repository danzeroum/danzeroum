"""Documents router — certidões, alvarás e outros documentos da empresa."""
from __future__ import annotations
import uuid
from typing import Annotated
import psycopg
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File
from fastapi.responses import Response
from api.deps import get_conn
from api.schemas import DocumentCreate, DocumentOut

router = APIRouter(prefix="/documents", tags=["documents"])
Conn = Annotated[psycopg.Connection, Depends(get_conn)]

@router.get("", response_model=list[DocumentOut])
def list_documents(conn: Conn, type: str | None = None, valid: bool | None = None):
    q = """SELECT id, type, subtype, name, file_name, mime_type,
                  issue_date, expiry_date, is_valid, notes, created_at
           FROM documents WHERE 1=1"""
    params: list = []
    if type:
        q += " AND type = %s"
        params.append(type)
    if valid is not None:
        q += " AND is_valid = %s"
        params.append(valid)
    q += " ORDER BY created_at DESC"
    rows = conn.execute(q, params).fetchall()
    cols = ["id","type","subtype","name","file_name","mime_type","issue_date","expiry_date","is_valid","notes","created_at"]
    return [DocumentOut(**r) for r in rows]

@router.post("", response_model=DocumentOut, status_code=201)
async def create_document(
    conn: Conn,
    type: str = Form(...),
    subtype: str | None = Form(None),
    name: str | None = Form(None),
    issue_date: str | None = Form(None),
    expiry_date: str | None = Form(None),
    notes: str | None = Form(None),
    file: UploadFile | None = File(None),
):
    doc_id = str(uuid.uuid4())
    file_data = None
    file_name = None
    mime_type = None
    if file and file.filename:
        file_data = await file.read()
        file_name = file.filename
        mime_type = file.content_type
    conn.execute(
        """INSERT INTO documents (id, type, subtype, name, file_data, file_name, mime_type, issue_date, expiry_date, notes)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        [doc_id, type, subtype, name, file_data, file_name, mime_type,
         issue_date or None, expiry_date or None, notes]
    )
    conn.commit()
    row = conn.execute(
        "SELECT id,type,subtype,name,file_name,mime_type,issue_date,expiry_date,is_valid,notes,created_at FROM documents WHERE id=%s",
        [doc_id]
    ).fetchone()
    cols = ["id","type","subtype","name","file_name","mime_type","issue_date","expiry_date","is_valid","notes","created_at"]
    return DocumentOut(**row)

@router.get("/{doc_id}/file")
def get_document_file(doc_id: str, conn: Conn):
    row = conn.execute(
        "SELECT file_data, file_name, mime_type FROM documents WHERE id=%s", [doc_id]
    ).fetchone()
    if not row:
        raise HTTPException(404)
    file_data, file_name, mime_type = row
    if not file_data:
        raise HTTPException(404, "No file attached")
    return Response(
        content=bytes(file_data),
        media_type=mime_type or "application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{file_name or "file"}"'},
    )

@router.delete("/{doc_id}", status_code=204)
def delete_document(doc_id: str, conn: Conn):
    conn.execute("DELETE FROM documents WHERE id=%s", [doc_id])
    conn.commit()

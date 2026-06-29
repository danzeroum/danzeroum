"""Technical certificates router."""
from __future__ import annotations
import uuid
from typing import Annotated
import psycopg
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File
from fastapi.responses import Response
from api.deps import get_conn
from api.schemas import CertificateOut

router = APIRouter(prefix="/certificates", tags=["certificates"])
Conn = Annotated[psycopg.Connection, Depends(get_conn)]

@router.get("", response_model=list[CertificateOut])
def list_certificates(conn: Conn):
    rows = conn.execute(
        """SELECT id, client_name, project_description, start_date, end_date,
                  project_value, scope, file_name, mime_type, created_at
           FROM technical_certificates ORDER BY created_at DESC"""
    ).fetchall()
    cols = ["id","client_name","project_description","start_date","end_date","project_value","scope","file_name","mime_type","created_at"]
    return [CertificateOut(**dict(zip(cols, r))) for r in rows]

@router.post("", response_model=CertificateOut, status_code=201)
async def create_certificate(
    conn: Conn,
    client_name: str = Form(...),
    project_description: str | None = Form(None),
    start_date: str | None = Form(None),
    end_date: str | None = Form(None),
    project_value: float | None = Form(None),
    scope: str | None = Form(None),
    file: UploadFile | None = File(None),
):
    cert_id = str(uuid.uuid4())
    file_data = None
    file_name = None
    mime_type = None
    if file and file.filename:
        file_data = await file.read()
        file_name = file.filename
        mime_type = file.content_type
    conn.execute(
        """INSERT INTO technical_certificates (id, client_name, project_description, start_date, end_date, project_value, scope, file_data, file_name, mime_type)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        [cert_id, client_name, project_description, start_date or None, end_date or None, project_value, scope, file_data, file_name, mime_type]
    )
    conn.commit()
    row = conn.execute(
        "SELECT id,client_name,project_description,start_date,end_date,project_value,scope,file_name,mime_type,created_at FROM technical_certificates WHERE id=%s",
        [cert_id]
    ).fetchone()
    cols = ["id","client_name","project_description","start_date","end_date","project_value","scope","file_name","mime_type","created_at"]
    return CertificateOut(**dict(zip(cols, row)))

@router.get("/{cert_id}/file")
def get_certificate_file(cert_id: str, conn: Conn):
    row = conn.execute(
        "SELECT file_data, file_name, mime_type FROM technical_certificates WHERE id=%s", [cert_id]
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

@router.delete("/{cert_id}", status_code=204)
def delete_certificate(cert_id: str, conn: Conn):
    conn.execute("DELETE FROM technical_certificates WHERE id=%s", [cert_id])
    conn.commit()

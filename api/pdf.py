"""Geração de PDF de proposta comercial (edital → preço → proposta).

Fecha o ciclo: a partir do edital e do preço ofertado, produz um PDF de proposta
pronto para envio. Usa reportlab (pure-python), sem serviço externo.
"""

from __future__ import annotations

from datetime import date, datetime
from io import BytesIO
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

_STATUS_LABEL = {
    "DRAFT": "Rascunho",
    "SENT": "Enviada",
    "UNDER_REVIEW": "Em análise",
    "WIN": "Vencedora",
    "LOST": "Perdida",
    "DISQUALIFIED": "Desclassificada",
}


def _brl(value: Any) -> str:
    if value in (None, ""):
        return "—"
    try:
        return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError):
        return str(value)


def _fmt_date(value: Any) -> str:
    if isinstance(value, datetime | date):
        return value.strftime("%d/%m/%Y")
    return str(value) if value else "—"


def build_proposal_pdf(data: dict) -> bytes:
    """Monta o PDF da proposta a partir de um dict (proposta + edital). Devolve bytes."""
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    left = 2 * cm
    y = height - 2 * cm

    c.setFont("Helvetica-Bold", 18)
    c.drawString(left, y, "Danzeroum — Proposta Comercial")
    y -= 0.7 * cm
    c.setFont("Helvetica", 9)
    c.setFillGray(0.4)
    c.drawString(left, y, f"Emitida em {_fmt_date(date.today())}")
    c.setFillGray(0)
    y -= 1.2 * cm

    def section(title: str) -> None:
        nonlocal y
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left, y, title)
        y -= 0.2 * cm
        c.setStrokeGray(0.8)
        c.line(left, y, width - 2 * cm, y)
        y -= 0.55 * cm

    def row(label: str, value: str) -> None:
        nonlocal y
        c.setFont("Helvetica-Bold", 10)
        c.drawString(left, y, f"{label}:")
        c.setFont("Helvetica", 10)
        c.drawString(left + 4.5 * cm, y, value[:80])
        y -= 0.6 * cm

    section("Edital")
    row("Objeto", str(data.get("tender_title") or "—"))
    row("Fonte", str(data.get("source") or "—"))
    row("Identificador", str(data.get("external_id") or "—"))

    y -= 0.3 * cm
    section("Proposta")
    row("Preço ofertado", _brl(data.get("price_offered")))
    row("Validade (dias)", str(data.get("validity_days") or "—"))
    row("Situação", _STATUS_LABEL.get(str(data.get("status")), str(data.get("status") or "—")))
    row("Versão", str(data.get("version") or 1))

    notes = data.get("notes")
    if notes:
        y -= 0.3 * cm
        section("Observações")
        c.setFont("Helvetica", 10)
        for line in _wrap(str(notes), 90):
            c.drawString(left, y, line)
            y -= 0.5 * cm

    c.setFont("Helvetica-Oblique", 8)
    c.setFillGray(0.5)
    c.drawString(left, 1.5 * cm, "Danzeroum Tecnologia — proposta gerada automaticamente.")

    c.showPage()
    c.save()
    return buf.getvalue()


def _wrap(text: str, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for w in words:
        if len(current) + len(w) + 1 > width:
            lines.append(current)
            current = w
        else:
            current = f"{current} {w}".strip()
    if current:
        lines.append(current)
    return lines or [""]

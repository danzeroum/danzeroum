"""Alerta ativo de vencimento de certidões/documentos da empresa.

Certidão vencida = perda de habilitação. A tabela ``documents`` já guarda
``expiry_date``; aqui varremos os vencimentos e avisamos ANTES (janelas 30/15/7
dias e vencidas), reusando o transporte SMTP das notificações.

Degradação suave: sem SMTP configurado, apenas devolve a lista (no-op de envio);
sem ``DATABASE_URL`` ou sem documentos a vencer, não faz nada.
"""

from __future__ import annotations

import html
from dataclasses import dataclass
from datetime import date
from email.message import EmailMessage
from typing import TYPE_CHECKING

from danzeroum_tracker.notifications import Transport, _smtplib_transport

if TYPE_CHECKING:
    from danzeroum_tracker.config import Settings

# Janela padrão (dias) para começar a avisar.
DEFAULT_WITHIN_DAYS = 30


@dataclass
class ExpiringDoc:
    id: str
    type: str
    name: str | None
    expiry_date: date
    days_left: int
    level: str  # 'expired' | 'critical' | 'warning' | 'notice'

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "expiry_date": self.expiry_date.isoformat(),
            "days_left": self.days_left,
            "level": self.level,
        }


def _level(days_left: int) -> str:
    if days_left < 0:
        return "expired"
    if days_left <= 7:
        return "critical"
    if days_left <= 15:
        return "warning"
    return "notice"


def select_expiring(
    rows: list[dict], *, today: date, within_days: int = DEFAULT_WITHIN_DAYS
) -> list[ExpiringDoc]:
    """Filtra documentos vencendo em até ``within_days`` (inclui vencidos). Função pura."""
    out: list[ExpiringDoc] = []
    for r in rows:
        expiry = r.get("expiry_date")
        if expiry is None:
            continue
        days_left = (expiry - today).days
        if days_left <= within_days:
            out.append(
                ExpiringDoc(
                    id=str(r.get("id")),
                    type=str(r.get("type") or "DOC"),
                    name=r.get("name"),
                    expiry_date=expiry,
                    days_left=days_left,
                    level=_level(days_left),
                )
            )
    out.sort(key=lambda d: d.days_left)
    return out


def format_cert_alert(docs: list[ExpiringDoc]) -> tuple[str, str, str]:
    """Monta (assunto, texto, html) do aviso de vencimento."""
    n = len(docs)
    expired = sum(1 for d in docs if d.level == "expired")
    suffix = f" — {expired} vencida(s)" if expired else ""
    subject = f"[Danzeroum] {n} certidão(ões) a vencer{suffix}"
    text_lines = ["Documentos/certidões exigindo atenção:", ""]
    html_rows = []
    for d in docs:
        label = d.name or d.type
        situacao = "VENCIDA" if d.days_left < 0 else f"vence em {d.days_left} dia(s)"
        text_lines.append(f"- [{d.type}] {label}: {situacao} ({d.expiry_date.isoformat()})")
        html_rows.append(
            f"<li><b>[{html.escape(d.type)}]</b> {html.escape(label)} — "
            f"{html.escape(situacao)} <small>({d.expiry_date.isoformat()})</small></li>"
        )
    text = "\n".join(text_lines)
    html_body = f"<p>{n} documento(s) exigindo atenção:</p><ul>{''.join(html_rows)}</ul>"
    return subject, text, html_body


_QUERY = """
SELECT id::text AS id, type, name, expiry_date
FROM documents
WHERE expiry_date IS NOT NULL AND expiry_date <= (CURRENT_DATE + %(within)s)
ORDER BY expiry_date ASC;
"""


def query_expiring_documents(
    database_url: str, within_days: int = DEFAULT_WITHIN_DAYS
) -> list[dict]:
    """Consulta os documentos a vencer no banco. Devolve [] sem ``database_url``."""
    if not database_url:
        return []
    import psycopg
    from psycopg.rows import dict_row

    with psycopg.connect(database_url, row_factory=dict_row) as conn, conn.cursor() as cur:
        cur.execute(_QUERY, {"within": within_days})
        return cur.fetchall()


def _send(settings: Settings, docs: list[ExpiringDoc], transport: Transport | None) -> int:
    """Envia o e-mail de aviso se SMTP estiver configurado. Retorna nº de docs avisados."""
    if not docs or not settings.smtp_host or not settings.mail_to:
        return 0
    subject, text, html_body = format_cert_alert(docs)
    msg = EmailMessage()
    msg["Subject"] = subject
    from_addr = settings.smtp_from or settings.smtp_user
    name = settings.smtp_from_name
    msg["From"] = f"{name} <{from_addr}>" if name else from_addr
    msg["To"] = settings.mail_to
    msg.set_content(text)
    msg.add_alternative(html_body, subtype="html")
    send = transport or _smtplib_transport
    send(
        host=settings.smtp_host,
        port=settings.smtp_port,
        encryption=settings.smtp_encryption,
        user=settings.smtp_user,
        password=settings.smtp_pass,
        message=msg,
    )
    return len(docs)


def run_cert_alert(
    settings: Settings,
    *,
    within_days: int = DEFAULT_WITHIN_DAYS,
    today: date | None = None,
    rows: list[dict] | None = None,
    transport: Transport | None = None,
) -> dict:
    """Varre vencimentos e (best-effort) envia e-mail. ``rows``/``today`` p/ teste."""
    if rows is None:
        rows = query_expiring_documents(settings.database_url, within_days)
    docs = select_expiring(rows, today=today or date.today(), within_days=within_days)
    notified = 0
    error = None
    try:
        notified = _send(settings, docs, transport)
    except Exception as exc:  # noqa: BLE001 - envio é best-effort
        error = str(exc)
    payload = {"expiring": [d.to_dict() for d in docs], "notified": notified}
    if error:
        payload["notify_error"] = error
    return payload

"""Testes do alerta de vencimento de certidões/documentos."""

from __future__ import annotations

from datetime import date

from danzeroum_tracker.certs import (
    format_cert_alert,
    run_cert_alert,
    select_expiring,
)
from danzeroum_tracker.config import Settings

TODAY = date(2026, 6, 30)


def _rows():
    return [
        {"id": "1", "type": "CND", "name": "CND Federal", "expiry_date": date(2026, 6, 20)},   # vencida (-10)
        {"id": "2", "type": "FGTS", "name": "CRF FGTS", "expiry_date": date(2026, 7, 3)},       # 3 dias (critical)
        {"id": "3", "type": "CRF", "name": "Simples", "expiry_date": date(2026, 7, 12)},        # 12 (warning)
        {"id": "4", "type": "EST", "name": "Estadual", "expiry_date": date(2026, 7, 25)},       # 25 (notice)
        {"id": "5", "type": "MUN", "name": "Municipal", "expiry_date": date(2026, 9, 1)},       # 63 (fora)
        {"id": "6", "type": "X", "name": "Sem validade", "expiry_date": None},                  # ignorado
    ]


def test_select_expiring_filters_and_classifies():
    docs = select_expiring(_rows(), today=TODAY, within_days=30)
    ids = [d.id for d in docs]
    assert ids == ["1", "2", "3", "4"]  # ordenado por days_left, exclui 5 (fora) e 6 (sem data)
    by_id = {d.id: d for d in docs}
    assert by_id["1"].level == "expired" and by_id["1"].days_left == -10
    assert by_id["2"].level == "critical"
    assert by_id["3"].level == "warning"
    assert by_id["4"].level == "notice"


def test_select_expiring_custom_window():
    docs = select_expiring(_rows(), today=TODAY, within_days=7)
    assert [d.id for d in docs] == ["1", "2"]


def test_format_cert_alert_mentions_expired():
    docs = select_expiring(_rows(), today=TODAY, within_days=30)
    subject, text, html_body = format_cert_alert(docs)
    assert "vencida" in subject.lower()
    assert "CND Federal" in text
    assert "<li>" in html_body and "CRF FGTS" in html_body


def test_run_cert_alert_sends_when_smtp_configured():
    captured = {}

    def fake_transport(*, host, port, encryption, user, password, message):
        captured["subject"] = message["Subject"]
        captured["to"] = message["To"]

    settings = Settings.from_env({"SMTP_HOST": "smtp.test", "MAIL_TO": "to@d.com", "SMTP_USER": "u"})
    payload = run_cert_alert(settings, today=TODAY, rows=_rows(), transport=fake_transport)
    assert payload["notified"] == 4
    assert len(payload["expiring"]) == 4
    assert captured["to"] == "to@d.com"


def test_run_cert_alert_noop_without_smtp():
    settings = Settings.from_env({})  # sem SMTP
    payload = run_cert_alert(settings, today=TODAY, rows=_rows())
    assert payload["notified"] == 0
    assert len(payload["expiring"]) == 4  # detecta, mas não envia


def test_run_cert_alert_no_docs():
    settings = Settings.from_env({"SMTP_HOST": "smtp.test", "MAIL_TO": "to@d.com"})
    payload = run_cert_alert(settings, today=TODAY, rows=[], transport=lambda **k: None)
    assert payload == {"expiring": [], "notified": 0}


def test_cli_certs_alert_command_wires_through():
    import io
    import json

    from danzeroum_tracker.cli import cmd_certs_alert

    out = io.StringIO()
    rc = cmd_certs_alert(Settings.from_env({}), rows=_rows(), out=out)
    assert rc == 0
    payload = json.loads(out.getvalue())
    # Estrutura (a contagem depende da data real; aqui só validamos a fiação).
    assert isinstance(payload["expiring"], list)
    assert payload["notified"] == 0  # sem SMTP configurado

"""Testes do crm_sync (mapeamento puro + upsert idempotente)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crm_sync import lead_to_client, sync_leads  # noqa: E402


def _lead(**kw):
    base = {
        "id": "lead_1",
        "nome": "Maria Souza",
        "cargo": "CTO",
        "empresa": "ACME Tecnologia Ltda",
        "linkedin_url": "https://www.linkedin.com/in/maria",
        "setor": "Financial Services",
        "origem_repo": "buildtovalue-governance",
        "keywords": ["AI governance"],
        "status": "novo",
        "notas": "",
    }
    base.update(kw)
    return base


# ── mapeamento puro ─────────────────────────────────────────────────────────────


def test_lead_to_client_maps_fields():
    c = lead_to_client(_lead())
    assert c is not None
    assert c["source"] == "CRM"
    assert c["name"] == "ACME Tecnologia Ltda"   # empresa vira o nome
    assert c["contact_name"] == "Maria Souza"
    assert c["status"] == "LEAD"
    assert "Cargo: CTO" in c["notes"]
    assert "linkedin.com/in/maria" in c["notes"]
    assert "Keywords: AI governance" in c["notes"]


def test_lead_to_client_status_mapping():
    assert lead_to_client(_lead(status="fechado"))["status"] == "CLIENT"
    assert lead_to_client(_lead(status="perdido"))["status"] == "ARCHIVED"
    assert lead_to_client(_lead(status="desconhecido"))["status"] == "LEAD"


def test_lead_to_client_skips_placeholder():
    placeholder = {
        "nome": "(preencher manualmente após a pesquisa)",
        "empresa": "(preencher)",
        "status": "novo",
    }
    assert lead_to_client(placeholder) is None


def test_lead_to_client_uses_name_when_no_company():
    c = lead_to_client(_lead(empresa=""))
    assert c["name"] == "Maria Souza"


# ── upsert idempotente (conn fake) ──────────────────────────────────────────────


class _Cursor:
    def __init__(self, result):
        self._result = result

    def fetchone(self):
        return self._result


class FakeConn:
    """Conn psycopg-like em memória, parseando SELECT/INSERT/UPDATE de clients."""

    def __init__(self):
        self.rows: list[dict] = []
        self.commits = 0

    def execute(self, sql, params=None):
        params = params or []
        s = sql.upper()
        if s.lstrip().startswith("SELECT"):
            if "LOWER(NAME)=" in s:
                name, contact = params[0], params[1]
                for r in self.rows:
                    if r["name"].lower() == name.lower() and \
                       (r.get("contact_name") or "").lower() == (contact or "").lower():
                        return _Cursor((r["id"],))
            else:  # busca por e-mail
                email = params[0]
                for r in self.rows:
                    if r.get("email") and r["email"].lower() == email.lower():
                        return _Cursor((r["id"],))
            return _Cursor(None)
        if s.lstrip().startswith("INSERT"):
            keys = ["id", "source", "name", "type", "cnpj", "contact_name",
                    "email", "phone", "status", "notes"]
            self.rows.append(dict(zip(keys, params)))
            return _Cursor(None)
        if s.lstrip().startswith("UPDATE"):
            cid = params[-1]
            for r in self.rows:
                if r["id"] == cid:
                    r.update({
                        "name": params[0], "type": params[1], "contact_name": params[2],
                        "email": params[3], "phone": params[4], "status": params[5],
                        "notes": params[6],
                    })
            return _Cursor(None)
        return _Cursor(None)

    def commit(self):
        self.commits += 1


def test_sync_inserts_then_updates_idempotent():
    conn = FakeConn()
    leads = [_lead()]

    r1 = sync_leads(conn, leads)
    assert r1 == {"inserted": 1, "updated": 0, "skipped": 0}
    assert len(conn.rows) == 1

    # 2ª passada: mesma lista → atualiza, não duplica.
    r2 = sync_leads(conn, leads)
    assert r2 == {"inserted": 0, "updated": 1, "skipped": 0}
    assert len(conn.rows) == 1
    assert conn.commits == 2


def test_sync_skips_placeholder_leads():
    conn = FakeConn()
    leads = [_lead(), {"nome": "(preencher)", "empresa": "(preencher)"}]
    r = sync_leads(conn, leads)
    assert r["inserted"] == 1
    assert r["skipped"] == 1


def test_sync_dedupes_by_email():
    conn = FakeConn()
    a = _lead(nome="Maria Souza", email="m@acme.com")
    b = _lead(nome="Maria S.", empresa="ACME S/A", email="m@acme.com")  # mesmo e-mail
    sync_leads(conn, [a])
    r = sync_leads(conn, [b])
    assert r["updated"] == 1
    assert len(conn.rows) == 1

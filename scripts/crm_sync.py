#!/usr/bin/env python3
"""crm_sync.py — sincroniza os leads do CRM flat-file para a tabela ``clients``.

Unifica os dois CRMs: o flat-file de prospecção (crm/leads*.json, gerado pelo
crm_collector) e o CRM da aplicação (tabela ``clients`` + tela CRM). Idempotente:
rodar de novo atualiza os registros existentes (marcados com source='CRM'), não
duplica.

Uso:
  DATABASE_URL=postgresql://... python scripts/crm_sync.py            # lê crm/leads.private.json
  DATABASE_URL=postgresql://... python scripts/crm_sync.py --file crm/leads.example.json
  python scripts/crm_sync.py --dry-run --file crm/leads.example.json  # só mostra o mapeamento
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from pathlib import Path

CRM_DIR = Path(__file__).resolve().parent.parent / "crm"
DEFAULT_LEADS = CRM_DIR / "leads.private.json"

# status do funil flat-file → status da tabela clients (LEAD | CLIENT | ARCHIVED)
_STATUS_MAP = {
    "fechado": "CLIENT",
    "lead_quente": "LEAD",
    "demo": "LEAD",
    "respondeu": "LEAD",
    "contatado": "LEAD",
    "novo": "LEAD",
    "query": "LEAD",
    "perdido": "ARCHIVED",
    "descartado": "ARCHIVED",
    "arquivado": "ARCHIVED",
}


def _is_placeholder(value: str | None) -> bool:
    return not value or value.strip().startswith("(")


def lead_to_client(lead: dict) -> dict | None:
    """Mapeia um lead do flat-file para os campos de ``clients``. ``None`` se inválido."""
    empresa = (lead.get("empresa") or "").strip()
    nome = (lead.get("nome") or "").strip()
    name = empresa if not _is_placeholder(empresa) else nome
    if _is_placeholder(name):
        return None  # sem nome utilizável (ex.: lead de exemplo) → ignora

    contact = nome if not _is_placeholder(nome) else None
    status = _STATUS_MAP.get((lead.get("status") or "").strip().lower(), "LEAD")

    parts: list[str] = []
    if not _is_placeholder(lead.get("cargo")):
        parts.append(f"Cargo: {lead['cargo'].strip()}")
    if not _is_placeholder(lead.get("setor")):
        parts.append(f"Setor: {lead['setor'].strip()}")
    if not _is_placeholder(lead.get("linkedin_url")):
        parts.append(lead["linkedin_url"].strip())
    if lead.get("origem_repo"):
        parts.append(f"Origem: {lead['origem_repo']}")
    keywords = lead.get("keywords") or []
    if keywords:
        parts.append("Keywords: " + ", ".join(keywords))
    if lead.get("notas"):
        parts.append(lead["notas"].strip())

    return {
        "source": "CRM",
        "name": name,
        "type": "LEAD",
        "cnpj": None,
        "contact_name": contact,
        "email": (lead.get("email") or None),
        "phone": (lead.get("phone") or lead.get("telefone") or None),
        "status": status,
        "notes": " | ".join(parts) or None,
    }


def _find_existing(conn, client: dict) -> str | None:
    """Procura um cliente CRM equivalente (por e-mail, senão por nome+contato)."""
    if client["email"]:
        row = conn.execute(
            "SELECT id FROM clients WHERE source='CRM' AND lower(email)=lower(%s) LIMIT 1",
            [client["email"]],
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT id FROM clients WHERE source='CRM' AND lower(name)=lower(%s) "
            "AND lower(coalesce(contact_name,''))=lower(coalesce(%s,'')) LIMIT 1",
            [client["name"], client["contact_name"]],
        ).fetchone()
    if row is None:
        return None
    return row[0] if not isinstance(row, dict) else row["id"]


def upsert_client(conn, client: dict) -> str:
    """Insere ou atualiza um cliente CRM. Retorna 'inserted' ou 'updated'."""
    existing = _find_existing(conn, client)
    if existing is not None:
        conn.execute(
            "UPDATE clients SET name=%s, type=%s, contact_name=%s, email=%s, phone=%s, "
            "status=%s, notes=%s WHERE id=%s",
            [client["name"], client["type"], client["contact_name"], client["email"],
             client["phone"], client["status"], client["notes"], existing],
        )
        return "updated"
    conn.execute(
        "INSERT INTO clients (id, source, name, type, cnpj, contact_name, email, phone, status, notes) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        [str(uuid.uuid4()), client["source"], client["name"], client["type"], client["cnpj"],
         client["contact_name"], client["email"], client["phone"], client["status"], client["notes"]],
    )
    return "inserted"


def sync_leads(conn, leads: list[dict]) -> dict:
    """Sincroniza uma lista de leads para ``clients``. Idempotente."""
    result = {"inserted": 0, "updated": 0, "skipped": 0}
    for lead in leads:
        client = lead_to_client(lead)
        if client is None:
            result["skipped"] += 1
            continue
        result[upsert_client(conn, client)] += 1
    conn.commit()
    return result


def load_leads(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sincroniza leads do CRM para a tabela clients")
    parser.add_argument("--file", default=str(DEFAULT_LEADS), help="arquivo JSON de leads")
    parser.add_argument("--dry-run", action="store_true", help="só mostra o mapeamento, não grava")
    args = parser.parse_args(argv)

    leads = load_leads(Path(args.file))
    if args.dry_run:
        mapped = [c for c in (lead_to_client(lead) for lead in leads) if c is not None]
        json.dump({"would_sync": mapped, "total": len(mapped)}, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0

    database_url = os.environ.get("DATABASE_URL", "")
    if not database_url:
        print("DATABASE_URL não configurado", file=sys.stderr)
        return 1

    import psycopg

    with psycopg.connect(database_url) as conn:
        result = sync_leads(conn, leads)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

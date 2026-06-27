#!/usr/bin/env python3
"""
crm_collector.py — CRM flat-file da Danzeroum.

Modo padrão (sem dados pessoais, seguro p/ repo público):
  - lê crm/targets.json
  - gera crm/queries.json  (URLs de busca do LinkedIn por case/cargo/setor — sem nomes)
  - gera crm/pipeline.json (resumo agregado do funil)

Modo opcional --stargazers (dados pessoais — fica LOCAL/gitignored):
  - coleta quem deu star nos repos e grava em crm/leads.private.json
  - NÃO envia mensagens; só registra. Use com moderação (AUP do GitHub).

Uso:
  python scripts/crm_collector.py
  python scripts/crm_collector.py --stargazers
"""

import argparse
import hashlib
import json
import os
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

CRM_DIR = Path(__file__).resolve().parent.parent / "crm"
TARGETS_FILE = CRM_DIR / "targets.json"
QUERIES_FILE = CRM_DIR / "queries.json"
PIPELINE_FILE = CRM_DIR / "pipeline.json"
PRIVATE_LEADS_FILE = CRM_DIR / "leads.private.json"   # gitignored

GITHUB_USER = "danzeroum"
STATUS_FLOW = ["novo", "query", "contatado", "respondeu", "demo", "fechado", "lead_quente"]


# ── helpers ───────────────────────────────────────────────────────────────────
def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path, default):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def short_id(prefix: str, *parts: str) -> str:
    raw = ":".join(parts)
    return prefix + hashlib.md5(raw.encode("utf-8")).hexdigest()[:8]


def linkedin_people_search(title: str, keyword: str, location: str) -> str:
    params = {"keywords": f"{title} {keyword}", "origin": "GLOBAL_SEARCH_HEADER"}
    base = "https://www.linkedin.com/search/results/people/"
    return f"{base}?{urllib.parse.urlencode(params)}&location={urllib.parse.quote(location)}"


# ── geração das queries (sem PII) ─────────────────────────────────────────────
def generate_queries(config: dict) -> list:
    location = config.get("location_default", "Brasil")
    out = []
    for t in config.get("targets", []):
        repo = t["repo"]
        kw0 = (t.get("keywords") or [""])[0]
        for title in t.get("titles", []):
            for industry in t.get("industries", []):
                out.append({
                    "id": short_id("q_", repo, title, industry),
                    "origem_repo": repo,
                    "repo_url": t.get("repo_url", ""),
                    "cargo_alvo": title,
                    "setor": industry,
                    "keywords": t.get("keywords", []),
                    "linkedin_search_url": linkedin_people_search(title, kw0, location),
                    "mensagem_template": t.get("message_template", ""),
                    "status": "query",
                    "gerado_em": now_iso(),
                })
    return out


def build_pipeline(queries: list, private_leads: list) -> dict:
    by_status: dict[str, int] = {}
    for item in queries:
        by_status[item.get("status", "query")] = by_status.get(item.get("status", "query"), 0) + 1
    for lead in private_leads:
        s = lead.get("status", "novo")
        by_status[s] = by_status.get(s, 0) + 1
    return {
        "atualizado_em": now_iso(),
        "total_queries": len(queries),
        "total_leads_privados": len(private_leads),
        "por_status": by_status,
    }


# ── stargazers (PII — opcional, local/gitignored) ─────────────────────────────
def fetch_stargazers(repo: str) -> list:
    try:
        import requests  # dependência só usada neste modo
    except ImportError:
        print("⚠️  módulo 'requests' não instalado (pip install requests) — pulando stargazers.")
        return []

    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    users, page = [], 1
    while True:
        url = f"https://api.github.com/repos/{GITHUB_USER}/{repo}/stargazers"
        try:
            resp = requests.get(url, headers=headers, params={"per_page": 100, "page": page}, timeout=15)
        except Exception as e:
            print(f"   erro de rede em {repo} p{page}: {e}")
            break
        if resp.status_code == 403 and resp.headers.get("X-RateLimit-Remaining") == "0":
            print(f"   rate limit atingido em {repo} — pare ou use GITHUB_TOKEN.")
            break
        if resp.status_code != 200:
            print(f"   {repo} p{page}: HTTP {resp.status_code} — pulando.")
            break
        batch = resp.json()
        if not batch:
            break
        users.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return users


def collect_stargazers(config: dict) -> int:
    print("\n⚠️  PRIVACIDADE: coletando dados pessoais (usernames do GitHub).")
    print("   → gravados SOMENTE em crm/leads.private.json (gitignored, fica local).")
    print("   → não faça outreach em massa não solicitado (AUP do GitHub).\n")

    leads = load_json(PRIVATE_LEADS_FILE, [])
    seen = {l.get("id") for l in leads}
    added = 0
    for t in config.get("targets", []):
        repo = t["repo"]
        for user in fetch_stargazers(repo):
            login = user.get("login", "")
            lid = short_id("gh_", repo, login)
            if lid in seen:
                continue
            seen.add(lid)
            leads.append({
                "id": lid,
                "nome": login,
                "empresa": "",
                "cargo": "Developer / Tech Lead",
                "github_url": user.get("html_url", ""),
                "linkedin_url": "",
                "setor": "Technology",
                "origem_repo": repo,
                "keywords": t.get("keywords", []),
                "mensagem_conexao": "",
                "data_captacao": now_iso(),
                "status": "lead_quente",
                "tags": [repo, "github_star"],
                "notas": f"Deu star em {repo}",
            })
            added += 1
    save_json(PRIVATE_LEADS_FILE, leads)
    print(f"⭐ stargazers: +{added} (total privado: {len(leads)}) em {PRIVATE_LEADS_FILE.name}")
    return added


# ── main ──────────────────────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser(description="CRM collector da Danzeroum")
    ap.add_argument("--stargazers", action="store_true",
                    help="coleta stargazers do GitHub para crm/leads.private.json (dados pessoais, local)")
    args = ap.parse_args()

    print("🚀 CRM Collector — Danzeroum")
    print(f"   {now_iso()}\n")

    if not TARGETS_FILE.exists():
        print(f"❌ {TARGETS_FILE} não encontrado.")
        return 1
    config = load_json(TARGETS_FILE, {})

    # 1) queries não-pessoais
    queries = generate_queries(config)
    save_json(QUERIES_FILE, queries)
    print(f"🔍 queries.json: {len(queries)} buscas geradas (sem dados pessoais)")

    # 2) stargazers (opcional)
    if args.stargazers:
        collect_stargazers(config)

    # 3) pipeline agregado
    private_leads = load_json(PRIVATE_LEADS_FILE, [])
    pipeline = build_pipeline(queries, private_leads)
    save_json(PIPELINE_FILE, pipeline)
    print(f"📊 pipeline.json: {pipeline['por_status']}")

    print("\n💡 Próximos passos:")
    print("   1. Abra crm/queries.json e pesquise os alvos no LinkedIn.")
    print("   2. Registre leads reais em crm/leads.private.json (copie de leads.example.json).")
    print("   3. Atualize 'status' conforme avança (contatado → respondeu → demo → fechado).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

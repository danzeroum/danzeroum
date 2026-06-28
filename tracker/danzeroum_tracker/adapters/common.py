"""Helpers puros compartilhados entre adaptadores (parsing resiliente).

Reaproveitados por PNCP e Compras.gov (e futuros órgãos) para evitar duplicação.
Tudo aqui é puro e testável offline.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from collections.abc import Iterable
from datetime import datetime
from typing import Any

from danzeroum_tracker.models import Tender

# Mapeamento de situações (termos normalizados) → status canônico.
STATUS_TERMS: dict[str, str] = {
    "em_andamento": "OPEN",
    "recebendo_proposta": "OPEN",
    "recebendo_propostas": "OPEN",
    "propostas_abertas": "OPEN",
    "aberta": "OPEN",
    "aberto": "OPEN",
    "divulgada": "OPEN",
    "divulgada no pncp": "OPEN",
    "publicado": "OPEN",
    "publicada": "OPEN",
    "adjudicado": "AWARDED",
    "adjudicada": "AWARDED",
    "homologado": "AWARDED",
    "homologada": "AWARDED",
    "encerrado": "CLOSED",
    "encerrada": "CLOSED",
    "concluido": "CLOSED",
    "concluida": "CLOSED",
    "revogado": "CANCELLED",
    "revogada": "CANCELLED",
    "cancelado": "CANCELLED",
    "cancelada": "CANCELLED",
    "anulado": "CANCELLED",
    "anulada": "CANCELLED",
}

_TI_TERMS = (
    "tecnologia da informacao",
    "tecnologia",
    "informatica",
    "software",
    "sistema",
    "desenvolvimento de sistema",
    "hospedagem",
    "tratamento de dados",
    "data center",
    "datacenter",
    "nuvem",
    "cloud",
    "suporte tecnico",
    "ti ",
)
_TELECOM_TERMS = ("telecom", "telefonia", "internet", "link de dados", "fibra", "rede de dados")


def normalize(text: str) -> str:
    """Minúsculo e sem acentos, para comparação robusta."""
    nfkd = unicodedata.normalize("NFKD", text or "")
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


def first(raw: dict[str, Any], *keys: str) -> Any:
    """Primeiro valor não-vazio entre as chaves candidatas."""
    for key in keys:
        if key in raw and raw[key] not in (None, ""):
            return raw[key]
    return None


def safe_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_datetime(value: Any) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def map_status(status: Any) -> str:
    return STATUS_TERMS.get(normalize(str(status or "")).strip(), "OPEN")


def infer_category(objeto: str) -> str:
    text = normalize(objeto)
    if any(term in text for term in _TI_TERMS):
        return "TI"
    if any(term in text for term in _TELECOM_TERMS):
        return "TELECOM"
    return "OUTROS"


def matches_keywords(tender: Tender, keywords: Iterable[str]) -> bool:
    """True se objeto/descrição contém alguma das palavras-chave (sem acento)."""
    haystack = normalize(f"{tender.title} {tender.description or ''}")
    return any(normalize(kw) in haystack for kw in keywords)


def parse_money_br(text: Any) -> float | None:
    """Converte 'R$ 120.000,00' → 120000.0. Tolera None/strings livres."""
    if text in (None, ""):
        return None
    if isinstance(text, int | float):
        return float(text)
    cleaned = re.sub(r"[^\d,.-]", "", str(text))
    if not cleaned:
        return None
    if "," in cleaned:
        # Formato BR explícito: '.' = milhar, ',' = decimal.
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif "." in cleaned:
        # Sem vírgula: desambigua pelo tamanho do último grupo.
        # '.' com 3 dígitos finais = milhar BR (5.000 → 5000); senão, decimal.
        if len(cleaned.rsplit(".", 1)[1]) == 3:
            cleaned = cleaned.replace(".", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_date_br(text: Any) -> datetime | None:
    """Converte datas no formato BR ('30/12/2026', '30/12/2026 18:00')."""
    if not text or not isinstance(text, str):
        return None
    match = re.search(r"\d{2}/\d{2}/\d{4}(?:[ T]\d{2}:\d{2}(?::\d{2})?)?", text)
    if not match:
        return None
    raw = match.group(0).replace("T", " ")
    for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def stable_id(*parts: str, max_len: int = 120) -> str:
    """ID de dedupe estável. Usa o valor curto direto; senão, hash determinístico.

    Útil para scraping, onde o 'id' pode ser uma URL longa (> coluna do banco).
    """
    raw = "|".join(p for p in parts if p)
    if raw and len(raw) <= max_len:
        return raw
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:24]


def absolute_url(href: str | None, base_url: str) -> str | None:
    """Resolve URLs relativas contra a base do portal."""
    if not href:
        return None
    if href.startswith(("http://", "https://")):
        return href
    return f"{base_url.rstrip('/')}/{href.lstrip('/')}"


def extract_records(payload: Any, keys: Iterable[str] = ()) -> list[dict[str, Any]]:
    """Extrai a lista de registros de uma resposta (lista direta ou envelope)."""
    if isinstance(payload, list):
        return [r for r in payload if isinstance(r, dict)]
    if isinstance(payload, dict):
        for key in (*keys, "data", "items", "itens", "resultado", "content", "_embedded"):
            value = payload.get(key)
            if isinstance(value, list):
                return [r for r in value if isinstance(r, dict)]
    return []

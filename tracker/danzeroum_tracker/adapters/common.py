"""Helpers puros compartilhados entre adaptadores (parsing resiliente).

Reaproveitados por PNCP e Compras.gov (e futuros órgãos) para evitar duplicação.
Tudo aqui é puro e testável offline.
"""

from __future__ import annotations

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

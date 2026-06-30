"""Download e extração de texto de anexos de edital (PDF).

Best-effort por natureza: portais variam, anexos podem faltar ou estar protegidos.
Qualquer falha é absorvida e devolve string vazia — o scorer (heurístico ou LLM)
continua funcionando só com título/descrição quando não há texto de edital.
"""

from __future__ import annotations

import logging

import requests

logger = logging.getLogger(__name__)

# Chaves em ``Tender.raw_json`` onde um texto de edital já extraído pode estar.
_RAW_TEXT_KEYS = ("edital_text", "attachment_text", "edital_texto", "texto_edital")


def _truncate(text: str, max_chars: int) -> str:
    """Trunca preservando o início (onde costumam estar objeto e habilitação)."""
    if max_chars > 0 and len(text) > max_chars:
        return text[:max_chars]
    return text


def extract_pdf_text(data: bytes, *, max_chars: int = 24000) -> str:
    """Extrai texto de um PDF em memória. Devolve "" se não der para extrair.

    Importa ``pypdf`` de forma preguiçosa para não custar nada quando não há PDF.
    """
    if not data:
        return ""
    try:
        import io

        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(data))
        parts = [page.extract_text() or "" for page in reader.pages]
    except Exception as exc:  # noqa: BLE001 - extração é best-effort
        logger.warning("falha ao extrair texto do PDF: %s", exc)
        return ""
    text = "\n".join(p.strip() for p in parts if p.strip())
    return _truncate(text, max_chars)


def download_and_extract(
    url: str,
    *,
    session: requests.Session | None = None,
    timeout: int = 30,
    max_chars: int = 24000,
) -> str:
    """Baixa ``url`` e, se for PDF, extrai o texto. Best-effort: nunca lança."""
    if not url:
        return ""
    sess = session or requests.Session()
    try:
        resp = sess.get(url, timeout=timeout)
        resp.raise_for_status()
    except Exception as exc:  # noqa: BLE001 - download é best-effort
        logger.warning("falha ao baixar anexo %s: %s", url, exc)
        return ""
    content_type = resp.headers.get("Content-Type", "").lower()
    is_pdf = "pdf" in content_type or url.lower().endswith(".pdf")
    if not is_pdf:
        return ""
    return extract_pdf_text(resp.content, max_chars=max_chars)


def edital_text_from_raw(raw_json: dict, *, max_chars: int = 24000) -> str:
    """Recupera texto de edital já presente em ``raw_json`` (sem rede)."""
    for key in _RAW_TEXT_KEYS:
        value = raw_json.get(key)
        if isinstance(value, str) and value.strip():
            return _truncate(value, max_chars)
    return ""

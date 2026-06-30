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


def _extract_zip_pdfs(data: bytes, *, max_chars: int) -> str:
    """Extrai e concatena o texto dos PDFs dentro de um ZIP (PNCP empacota assim)."""
    import io
    import zipfile

    parts: list[str] = []
    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
        for name in zf.namelist():
            if not name.lower().endswith(".pdf"):
                continue
            try:
                with zf.open(name) as fh:
                    text = extract_pdf_text(fh.read(), max_chars=max_chars)
            except Exception:  # noqa: BLE001 - um arquivo ruim não derruba os demais
                continue
            if text:
                parts.append(text)
            if sum(len(p) for p in parts) >= max_chars:
                break
    except Exception as exc:  # noqa: BLE001 - extração é best-effort
        logger.warning("falha ao ler o ZIP do edital: %s", exc)
        return ""
    return _truncate("\n".join(parts), max_chars)


def extract_text_auto(data: bytes, *, max_chars: int = 24000) -> str:
    """Detecta PDF ou ZIP (de PDFs) pelo cabeçalho e extrai o texto. "" caso contrário."""
    if not data:
        return ""
    if data[:4] == b"%PDF":
        return extract_pdf_text(data, max_chars=max_chars)
    if data[:2] == b"PK":  # assinatura de ZIP
        return _extract_zip_pdfs(data, max_chars=max_chars)
    return ""


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
    # Detecta por cabeçalho (PDF/ZIP) — o PNCP serve octet-stream sem extensão.
    return extract_text_auto(resp.content, max_chars=max_chars)


def edital_text_from_raw(raw_json: dict, *, max_chars: int = 24000) -> str:
    """Recupera texto de edital já presente em ``raw_json`` (sem rede)."""
    for key in _RAW_TEXT_KEYS:
        value = raw_json.get(key)
        if isinstance(value, str) and value.strip():
            return _truncate(value, max_chars)
    return ""


# Base da API de arquivos do PNCP (diferente da API de consulta).
PNCP_ARQUIVOS_BASE = "https://pncp.gov.br/api/pncp/v1"


def fetch_pncp_edital_text(
    raw_json: dict,
    *,
    session: requests.Session | None = None,
    timeout: int = 40,
    max_chars: int = 24000,
    api_base: str = PNCP_ARQUIVOS_BASE,
) -> str:
    """Baixa o documento de Edital do PNCP e extrai o texto. Best-effort: "" em falha.

    Usa ``orgaoEntidade.cnpj`` + ``anoCompra`` + ``sequencialCompra`` do ``raw_json``
    do PNCP para montar a URL de arquivos, escolhe o documento do tipo "Edital" (ou o
    primeiro) e extrai o texto (tratando ZIP de PDFs).
    """
    org = raw_json.get("orgaoEntidade") if isinstance(raw_json.get("orgaoEntidade"), dict) else {}
    cnpj = org.get("cnpj")
    ano = raw_json.get("anoCompra")
    seq = raw_json.get("sequencialCompra")
    if not (cnpj and ano and seq):
        return ""
    sess = session or requests.Session()
    listing = f"{api_base}/orgaos/{cnpj}/compras/{ano}/{seq}/arquivos"
    try:
        resp = sess.get(listing, headers={"Accept": "application/json"}, timeout=timeout)
        resp.raise_for_status()
        files = resp.json()
    except Exception as exc:  # noqa: BLE001 - best-effort
        logger.warning("falha ao listar arquivos do PNCP (%s): %s", listing, exc)
        return ""
    if not isinstance(files, list) or not files:
        return ""
    edital = next(
        (f for f in files if str(f.get("tipoDocumentoNome", "")).lower().startswith("edital")),
        files[0],
    )
    file_url = edital.get("url") or edital.get("uri")
    if not file_url:
        return ""
    try:
        fr = sess.get(file_url, timeout=timeout)
        fr.raise_for_status()
    except Exception as exc:  # noqa: BLE001 - best-effort
        logger.warning("falha ao baixar edital do PNCP (%s): %s", file_url, exc)
        return ""
    return extract_text_auto(fr.content, max_chars=max_chars)

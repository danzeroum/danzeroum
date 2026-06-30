"""Testes da extração de texto de edital (download + PDF)."""

from __future__ import annotations

import pytest

from danzeroum_tracker import extraction
from danzeroum_tracker.extraction import (
    download_and_extract,
    edital_text_from_raw,
    extract_pdf_text,
    extract_text_auto,
    fetch_pncp_edital_text,
)


class FakeResponse:
    def __init__(self, *, content=b"", content_type="application/pdf", status=200):
        self.content = content
        self.headers = {"Content-Type": content_type}
        self._status = status

    def raise_for_status(self):
        if self._status >= 400:
            raise RuntimeError(f"HTTP {self._status}")


class FakeSession:
    def __init__(self, response):
        self._response = response
        self.calls = []

    def get(self, url, timeout=30):
        self.calls.append(url)
        return self._response


def test_extract_pdf_text_empty_bytes():
    assert extract_pdf_text(b"") == ""


def test_extract_pdf_text_invalid_pdf_is_best_effort():
    # Bytes que não são PDF não podem derrubar a coleta — devolve "".
    assert extract_pdf_text(b"not a pdf at all") == ""


def test_extract_pdf_text_joins_pages(monkeypatch):
    class FakePage:
        def __init__(self, text):
            self._text = text

        def extract_text(self):
            return self._text

    class FakeReader:
        def __init__(self, _stream):
            self.pages = [FakePage("Objeto: suporte de TI"), FakePage(""), FakePage("Habilitação")]

    import pypdf

    monkeypatch.setattr(pypdf, "PdfReader", FakeReader)
    out = extract_pdf_text(b"%PDF-fake")
    assert "Objeto: suporte de TI" in out
    assert "Habilitação" in out


def test_extract_pdf_text_truncates(monkeypatch):
    class FakePage:
        def extract_text(self):
            return "x" * 5000

    class FakeReader:
        def __init__(self, _stream):
            self.pages = [FakePage()]

    import pypdf

    monkeypatch.setattr(pypdf, "PdfReader", FakeReader)
    assert len(extract_pdf_text(b"%PDF-fake", max_chars=100)) == 100


def test_download_and_extract_skips_non_pdf():
    sess = FakeSession(FakeResponse(content=b"<html>", content_type="text/html"))
    assert download_and_extract("http://x/page.html", session=sess) == ""
    assert sess.calls == ["http://x/page.html"]


def test_download_and_extract_reads_pdf(monkeypatch):
    monkeypatch.setattr(extraction, "extract_pdf_text", lambda data, max_chars=24000: "EDITAL")
    sess = FakeSession(FakeResponse(content=b"%PDF-1.4", content_type="application/pdf"))
    assert download_and_extract("http://x/edital.pdf", session=sess) == "EDITAL"


def test_download_and_extract_empty_url():
    assert download_and_extract("") == ""


def test_download_and_extract_network_error_is_best_effort():
    sess = FakeSession(FakeResponse(status=500))
    assert download_and_extract("http://x/edital.pdf", session=sess) == ""


@pytest.mark.parametrize("key", ["edital_text", "attachment_text", "edital_texto", "texto_edital"])
def test_edital_text_from_raw_keys(key):
    assert edital_text_from_raw({key: "  conteúdo do edital  "}) == "  conteúdo do edital  "


def test_edital_text_from_raw_missing():
    assert edital_text_from_raw({"outra": "coisa"}) == ""
    assert edital_text_from_raw({}) == ""


# ── ZIP / detecção automática (PNCP empacota o edital como ZIP de PDFs) ──────────


def _zip_with_pdf(name="Anexo.pdf", content=b"%PDF-fake") -> bytes:
    import io
    import zipfile

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("pasta/", b"")
        zf.writestr(f"pasta/{name}", content)
        zf.writestr("pasta/Planilha.xlsx", b"not a pdf")
    return buf.getvalue()


def test_extract_text_auto_detects_pdf(monkeypatch):
    monkeypatch.setattr(extraction, "extract_pdf_text", lambda data, max_chars=24000: "PDF-OK")
    assert extract_text_auto(b"%PDF-1.7 ...") == "PDF-OK"


def test_extract_text_auto_detects_zip(monkeypatch):
    class FakePage:
        def extract_text(self):
            return "OBJETO: aquisição de barras"

    class FakeReader:
        def __init__(self, _stream):
            self.pages = [FakePage()]

    import pypdf

    monkeypatch.setattr(pypdf, "PdfReader", FakeReader)
    out = extract_text_auto(_zip_with_pdf())
    assert "OBJETO: aquisição de barras" in out


def test_extract_text_auto_unknown_returns_empty():
    assert extract_text_auto(b"<html>not a doc</html>") == ""
    assert extract_text_auto(b"") == ""


# ── fetch do edital no PNCP ──────────────────────────────────────────────────────


class _Resp:
    def __init__(self, *, json_data=None, content=b""):
        self._json = json_data
        self.content = content

    def raise_for_status(self):
        pass

    def json(self):
        return self._json


class _PNCPSession:
    """Devolve o JSON de arquivos na 1ª chamada e os bytes do edital na 2ª."""

    def __init__(self, files, content):
        self._files = files
        self._content = content
        self.urls = []

    def get(self, url, headers=None, timeout=30):
        self.urls.append(url)
        if url.endswith("/arquivos"):
            return _Resp(json_data=self._files)
        return _Resp(content=self._content)


_RAW = {"orgaoEntidade": {"cnpj": "50853555000154"}, "anoCompra": 2024, "sequencialCompra": 169}


def test_fetch_pncp_edital_prefers_edital_doc(monkeypatch):
    monkeypatch.setattr(extraction, "extract_text_auto", lambda data, max_chars=24000: "TEXTO-EDITAL")
    files = [
        {"tipoDocumentoNome": "Contrato", "url": "https://x/arquivos/3"},
        {"tipoDocumentoNome": "Edital", "url": "https://x/arquivos/1"},
    ]
    sess = _PNCPSession(files, b"PK\x03\x04zip")
    out = fetch_pncp_edital_text(_RAW, session=sess, max_chars=1000)
    assert out == "TEXTO-EDITAL"
    # baixou o doc do tipo "Edital" (arquivos/1), não o contrato.
    assert sess.urls[-1].endswith("/arquivos/1")


def test_fetch_pncp_edital_missing_keys_returns_empty():
    assert fetch_pncp_edital_text({"anoCompra": 2024}) == ""
    assert fetch_pncp_edital_text({}) == ""

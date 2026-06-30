"""Testes da extração de texto de edital (download + PDF)."""

from __future__ import annotations

import pytest

from danzeroum_tracker import extraction
from danzeroum_tracker.extraction import (
    download_and_extract,
    edital_text_from_raw,
    extract_pdf_text,
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

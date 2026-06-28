import pytest

from danzeroum_tracker.adapters.scraper import (
    ComprasSPAdapter,
    PrefeituraSPAdapter,
    ScraperError,
)
from tests.conftest import FakeResponse, FakeSession

COMPRAS_SP_HTML = """
<html><body>
<table class="licitacoes">
  <tr class="linha">
    <td class="objeto"><a href="/becsp/edital/1">Suporte técnico e manutenção de informática</a></td>
    <td class="valor">R$ 120.000,00</td>
    <td class="prazo">30/12/2026 18:00</td>
    <td class="situacao">Aberta</td>
  </tr>
  <tr class="linha">
    <td class="objeto"><a href="/becsp/edital/2">Aquisição de material de limpeza</a></td>
    <td class="valor">R$ 8.000,00</td>
    <td class="prazo">15/12/2026</td>
    <td class="situacao">Aberta</td>
  </tr>
</table>
</body></html>
"""

PREF_SP_HTML = """
<html><body>
<table id="tabelaEditais"><tbody>
  <tr>
    <td class="objeto"><a href="Edital/Detalhe/99">Desenvolvimento de sistema de gestão</a></td>
    <td class="valorEstimado">R$ 250.000,00</td>
    <td class="dataEncerramento">28/12/2026</td>
    <td class="situacao">Publicada</td>
  </tr>
</tbody></table>
</body></html>
"""


def test_comprassp_parse_html_extracts_rows():
    rows = ComprasSPAdapter().parse_html(COMPRAS_SP_HTML)
    assert len(rows) == 2
    assert rows[0]["value"] == "R$ 120.000,00"
    assert rows[0]["url"] == "/becsp/edital/1"


def test_comprassp_parse_tender_maps_fields():
    adapter = ComprasSPAdapter()
    t = adapter.parse_tender(adapter.parse_html(COMPRAS_SP_HTML)[0])
    assert t.source == "COMPRAS_SP"
    assert t.category == "TI"
    assert t.status == "OPEN"
    assert t.budget_estimate == 120000.0
    assert t.deadline.isoformat() == "2026-12-30T18:00:00"
    assert t.url == "https://www.bec.sp.gov.br/becsp/edital/1"
    assert t.external_id  # estável (id|url|title curto ou hash)


def test_comprassp_collect_filters_keywords():
    session = FakeSession(pages=[COMPRAS_SP_HTML])
    adapter = ComprasSPAdapter(keywords=["informatica", "suporte"], session=session)
    tenders = list(adapter.collect())
    assert len(tenders) == 1
    assert "limpeza" not in tenders[0].title.lower()


def test_prefsp_parse_tender_maps_fields():
    session = FakeSession(pages=[PREF_SP_HTML])
    adapter = PrefeituraSPAdapter(session=session)
    tenders = list(adapter.collect())
    assert len(tenders) == 1
    t = tenders[0]
    assert t.source == "PREF_SP"
    assert t.category == "TI"
    assert t.budget_estimate == 250000.0
    assert t.deadline.isoformat() == "2026-12-28T00:00:00"
    assert t.url == "https://e-negocioscidadesp.prefeitura.sp.gov.br/Edital/Detalhe/99"


def test_parse_tender_requires_title():
    with pytest.raises(ScraperError):
        ComprasSPAdapter().parse_tender({"title": ""})


def test_fetch_listing_http_error_raises():
    class BadSession:
        def get(self, *a, **k):
            return FakeResponse({}, status_code=500)

    with pytest.raises(ScraperError):
        list(ComprasSPAdapter(session=BadSession()).fetch_raw())


def test_empty_html_yields_nothing():
    assert ComprasSPAdapter().parse_html("<html></html>") == []

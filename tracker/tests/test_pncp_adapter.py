import pytest

from danzeroum_tracker.adapters.pncp import (
    PNCPAdapter,
    PNCPError,
    _first,
    _parse_datetime,
    _safe_float,
    infer_category,
    map_status,
    matches_keywords,
)
from danzeroum_tracker.models import Tender
from tests.conftest import FakeResponse, FakeSession


# ── helpers puros ─────────────────────────────────────────────────────────────
def test_first_picks_first_non_empty():
    assert _first({"a": "", "b": None, "c": "x"}, "a", "b", "c") == "x"
    assert _first({}, "a") is None


def test_safe_float():
    assert _safe_float("12.5") == 12.5
    assert _safe_float(None) is None
    assert _safe_float("") is None
    assert _safe_float("abc") is None


@pytest.mark.parametrize(
    "value,expected",
    [
        ("2026-06-01T09:00:00", "2026-06-01T09:00:00"),
        ("2026-06-01T09:00:00Z", "2026-06-01T09:00:00"),
        ("2026-06-01 09:00:00", "2026-06-01T09:00:00"),
        ("2026-06-01", "2026-06-01T00:00:00"),
    ],
)
def test_parse_datetime_formats(value, expected):
    assert _parse_datetime(value).isoformat() == expected


def test_parse_datetime_invalid():
    assert _parse_datetime("nonsense") is None
    assert _parse_datetime(None) is None
    assert _parse_datetime(123) is None


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Divulgada", "OPEN"),
        ("Recebendo Propostas", "OPEN"),
        ("Homologado", "AWARDED"),
        ("Encerrada", "CLOSED"),
        ("Cancelado", "CANCELLED"),
        ("qualquer", "OPEN"),
    ],
)
def test_map_status(raw, expected):
    assert map_status(raw) == expected


@pytest.mark.parametrize(
    "objeto,expected",
    [
        ("Suporte técnico de informática", "TI"),
        ("Serviço de hospedagem em nuvem", "TI"),
        ("Link de internet e telefonia", "TELECOM"),
        ("Compra de gêneros alimentícios", "OUTROS"),
    ],
)
def test_infer_category(objeto, expected):
    assert infer_category(objeto) == expected


def test_matches_keywords_ignores_accents():
    t = Tender(source="x", external_id="1", title="Manutenção de Informática", description="")
    assert matches_keywords(t, ["informatica"]) is True
    assert matches_keywords(t, ["limpeza"]) is False


# ── parse_tender ──────────────────────────────────────────────────────────────
def test_parse_tender_maps_pncp_fields(pncp_records):
    adapter = PNCPAdapter()
    t = adapter.parse_tender(pncp_records[0])
    assert t.source == "PNCP"
    assert t.external_id == "00000000000191-1-000001/2026"
    assert t.category == "TI"
    assert t.status == "OPEN"
    assert t.budget_estimate == 120000.0
    assert t.uf == "SP"
    assert t.deadline.isoformat() == "2026-12-30T18:00:00"
    assert t.url.startswith("https://pncp.gov.br/")


def test_parse_tender_requires_id():
    adapter = PNCPAdapter()
    with pytest.raises(PNCPError):
        adapter.parse_tender({"objetoCompra": "sem id"})


def test_parse_tender_builds_url_when_missing(pncp_records):
    adapter = PNCPAdapter()
    t = adapter.parse_tender(pncp_records[1])  # sem linkSistemaOrigem
    assert "q=" in t.url


# ── extração de envelope / paginação ──────────────────────────────────────────
def test_extract_records_list_and_envelope():
    assert PNCPAdapter._extract_records([{"a": 1}]) == [{"a": 1}]
    assert PNCPAdapter._extract_records({"data": [{"a": 1}]}) == [{"a": 1}]
    assert PNCPAdapter._extract_records({"itens": [{"b": 2}]}) == [{"b": 2}]
    assert PNCPAdapter._extract_records({"nada": 1}) == []
    assert PNCPAdapter._extract_records("oops") == []


def test_fetch_raw_paginates(pncp_records):
    # página 1 cheia (== page_size), página 2 vazia → para.
    session = FakeSession(pages=[pncp_records, []])
    adapter = PNCPAdapter(page_size=3, max_pages=5, session=session)
    got = list(adapter.fetch_raw())
    assert len(got) == 3


def test_collect_filters_by_keyword(pncp_records):
    session = FakeSession(pages=[pncp_records])
    adapter = PNCPAdapter(
        keywords=["tecnologia", "software", "hospedagem"],
        page_size=50,
        session=session,
    )
    tenders = list(adapter.collect())
    # o item de "material de limpeza/alimentícios" é filtrado fora.
    titles = [t.title for t in tenders]
    assert len(tenders) == 2
    assert all("aliment" not in t.lower() for t in titles)


def test_fetch_page_http_error_raises():
    class BadSession:
        def get(self, *a, **k):
            return FakeResponse({}, status_code=500)

    adapter = PNCPAdapter(session=BadSession())
    with pytest.raises(PNCPError):
        list(adapter.fetch_raw())

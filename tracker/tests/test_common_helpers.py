import pytest

from danzeroum_tracker.adapters.common import (
    absolute_url,
    parse_date_br,
    parse_money_br,
    stable_id,
)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("R$ 120.000,00", 120000.0),
        ("1.234.567,89", 1234567.89),
        ("R$ 5.000", 5000.0),
        ("350000.00", 350000.0),
        (1500, 1500.0),
        (None, None),
        ("", None),
        ("sob consulta", None),
    ],
)
def test_parse_money_br(raw, expected):
    assert parse_money_br(raw) == expected


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("30/12/2026", "2026-12-30T00:00:00"),
        ("Encerra em 30/12/2026 18:00", "2026-12-30T18:00:00"),
        ("05/06/2026 09:30:00", "2026-06-05T09:30:00"),
    ],
)
def test_parse_date_br(raw, expected):
    assert parse_date_br(raw).isoformat() == expected


def test_parse_date_br_invalid():
    assert parse_date_br("sem data") is None
    assert parse_date_br(None) is None


def test_stable_id_short_passthrough_and_hash():
    assert stable_id("ABC-123") == "ABC-123"
    long = "https://portal.example/" + "x" * 200
    sid = stable_id(long, max_len=120)
    assert len(sid) == 24
    # determinístico
    assert sid == stable_id(long, max_len=120)


def test_absolute_url():
    assert absolute_url("/edital/1", "https://b.gov") == "https://b.gov/edital/1"
    assert absolute_url("https://x/y", "https://b.gov") == "https://x/y"
    assert absolute_url(None, "https://b.gov") is None

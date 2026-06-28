import pytest

from danzeroum_tracker.adapters.comprasgov import ComprasGovAdapter
from danzeroum_tracker.adapters.pncp import PNCPAdapter
from danzeroum_tracker.cli import build_adapters
from danzeroum_tracker.config import Settings


def test_default_builds_only_pncp():
    adapters = build_adapters(Settings.from_env({}))
    assert len(adapters) == 1
    assert isinstance(adapters[0], PNCPAdapter)


def test_builds_both_sources_in_order():
    adapters = build_adapters(Settings.from_env({"TRACKER_SOURCES": "pncp,comprasgov"}))
    assert [type(a) for a in adapters] == [PNCPAdapter, ComprasGovAdapter]


def test_unknown_source_raises():
    with pytest.raises(ValueError):
        build_adapters(Settings.from_env({"TRACKER_SOURCES": "saturno"}))

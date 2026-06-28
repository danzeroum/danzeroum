from datetime import datetime

from danzeroum_tracker.models import Score, Tender


def test_tender_dedupe_key_and_dict():
    t = Tender(
        source="PNCP",
        external_id="X1",
        title="t",
        publish_date=datetime(2026, 1, 2, 3, 4, 5),
        deadline=datetime(2026, 2, 3, 4, 5, 6),
    )
    assert t.dedupe_key == ("PNCP", "X1")
    d = t.to_dict()
    assert d["publish_date"] == "2026-01-02T03:04:05"
    assert d["deadline"] == "2026-02-03T04:05:06"
    assert "raw_json" not in d  # raw_json não vai no dict canônico


def test_score_dict_rounds():
    s = Score(
        risk_score=0.126,
        fit_score=0.811,
        complexity_score=0.5,
        recommendation="GO",
        key_requirements=["atestado"],
    )
    d = s.to_dict()
    assert d["risk_score"] == 0.13
    assert d["fit_score"] == 0.81
    assert d["recommendation"] == "GO"
    assert d["key_requirements"] == ["atestado"]

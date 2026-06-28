import pytest

from danzeroum_tracker.scoring.schema import (
    SCORE_SCHEMA,
    ScoreValidationError,
    validate_score,
)


def _valid():
    return {
        "risk_score": 0.3,
        "fit_score": 0.7,
        "complexity_score": 0.4,
        "recommendation": "GO",
        "key_requirements": ["atestado"],
        "pricing_guidance": "x",
    }


def test_schema_has_required_fields():
    assert set(SCORE_SCHEMA["required"]) == {
        "risk_score",
        "fit_score",
        "complexity_score",
        "recommendation",
        "key_requirements",
    }


def test_validate_accepts_valid():
    assert validate_score(_valid()) == _valid()


def test_validate_rejects_missing_field():
    data = _valid()
    del data["fit_score"]
    with pytest.raises(ScoreValidationError):
        validate_score(data)


def test_validate_rejects_out_of_range():
    data = _valid()
    data["risk_score"] = 1.5
    with pytest.raises(ScoreValidationError):
        validate_score(data)


def test_validate_rejects_bad_enum():
    data = _valid()
    data["recommendation"] = "MAYBE"
    with pytest.raises(ScoreValidationError):
        validate_score(data)

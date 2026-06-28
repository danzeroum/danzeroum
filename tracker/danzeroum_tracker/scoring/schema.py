"""JSON Schema da saída do scorer + validação (vale para heurística e LLM)."""

from __future__ import annotations

from typing import Any

import jsonschema

SCORE_SCHEMA: dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Tender Scoring Result",
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "risk_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "fit_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "complexity_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "recommendation": {"type": "string", "enum": ["GO", "REVIEW", "SKIP"]},
        "key_requirements": {"type": "array", "items": {"type": "string"}},
        "pricing_guidance": {"type": ["string", "null"]},
    },
    "required": [
        "risk_score",
        "fit_score",
        "complexity_score",
        "recommendation",
        "key_requirements",
    ],
}


class ScoreValidationError(ValueError):
    """Saída do scorer não está em conformidade com o schema."""


def validate_score(data: dict[str, Any]) -> dict[str, Any]:
    """Valida ``data`` contra ``SCORE_SCHEMA``. Lança ``ScoreValidationError``."""
    try:
        jsonschema.validate(instance=data, schema=SCORE_SCHEMA)
    except jsonschema.ValidationError as exc:
        raise ScoreValidationError(exc.message) from exc
    return data

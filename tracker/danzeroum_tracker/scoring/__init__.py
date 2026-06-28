"""Camada de scoring — agnóstica ao provedor de LLM.

V1 usa um scorer heurístico (sem LLM, sem custo, sem chave de API). A interface
``Scorer`` permite plugar OpenAI/Gemini/Claude/Ollama numa rodada futura sem
tocar no core.
"""

from __future__ import annotations

from danzeroum_tracker.scoring.base import Scorer
from danzeroum_tracker.scoring.heuristic import HeuristicScorer
from danzeroum_tracker.scoring.schema import SCORE_SCHEMA, ScoreValidationError, validate_score

__all__ = [
    "Scorer",
    "HeuristicScorer",
    "SCORE_SCHEMA",
    "ScoreValidationError",
    "validate_score",
    "get_scorer",
]


def get_scorer(name: str = "heuristic") -> Scorer:
    """Factory: resolve um scorer pelo nome (default ``heuristic``)."""
    name = (name or "heuristic").lower()
    if name == "heuristic":
        return HeuristicScorer()
    raise ValueError(
        f"scorer desconhecido: {name!r} (disponíveis: heuristic). "
        "Provedores de LLM serão adicionados numa rodada futura."
    )

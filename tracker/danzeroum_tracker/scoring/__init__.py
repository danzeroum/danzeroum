"""Camada de scoring — agnóstica ao provedor de LLM.

Dois scorers: ``heuristic`` (sem LLM, sem custo, sem chave — baseline e fallback) e
``llm`` (DeepSeek, endpoint OpenAI-compatível). A interface ``Scorer`` mantém o core
desacoplado do provedor.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from danzeroum_tracker.scoring.base import LLMProvider, Scorer
from danzeroum_tracker.scoring.heuristic import HeuristicScorer
from danzeroum_tracker.scoring.schema import SCORE_SCHEMA, ScoreValidationError, validate_score

if TYPE_CHECKING:
    from danzeroum_tracker.config import Settings

logger = logging.getLogger(__name__)

__all__ = [
    "Scorer",
    "LLMProvider",
    "HeuristicScorer",
    "SCORE_SCHEMA",
    "ScoreValidationError",
    "validate_score",
    "get_scorer",
]


def get_scorer(name: str = "heuristic", *, settings: Settings | None = None) -> Scorer:
    """Factory: resolve um scorer pelo nome (default ``heuristic``).

    ``llm``/``deepseek`` exige ``settings`` com ``DEEPSEEK_API_KEY``; sem a chave (ou
    sem ``settings``) cai no heurístico, registrando um aviso — nunca lança por falta
    de credencial (mesma degradação suave das notificações).
    """
    name = (name or "heuristic").lower()
    if name == "heuristic":
        return HeuristicScorer()
    if name in ("llm", "deepseek"):
        from danzeroum_tracker.scoring.llm import LLMScorer, build_provider

        provider = build_provider(settings) if settings is not None else None
        if provider is None:
            logger.warning(
                "scorer %r pedido mas DEEPSEEK_API_KEY não está configurada — "
                "usando heurístico",
                name,
            )
            return HeuristicScorer()
        max_chars = settings.llm_max_chars if settings else 24000
        edital_fetcher = None
        if settings is not None and settings.fetch_edital_text:
            from danzeroum_tracker.extraction import fetch_pncp_edital_text

            def edital_fetcher(tender):
                return fetch_pncp_edital_text(tender.raw_json or {}, max_chars=max_chars)

        return LLMScorer(
            provider,
            fallback=HeuristicScorer(),
            max_chars=max_chars,
            edital_fetcher=edital_fetcher,
        )
    raise ValueError(
        f"scorer desconhecido: {name!r} (disponíveis: heuristic, llm)."
    )

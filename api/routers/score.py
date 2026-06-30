"""Re-scoring de um edital sob demanda.

O pipeline de coleta só pontua editais NOVOS. Este endpoint permite re-pontuar um
edital já armazenado — útil para reprocessar com o scorer LLM (DeepSeek) depois que
a chave for configurada, ou após ajustar a heurística.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from api.deps import get_repo, get_settings
from api.schemas import ScoreOut
from danzeroum_tracker.config import Settings
from danzeroum_tracker.storage import TenderRepository

router = APIRouter(prefix="/score", tags=["score"])

Repo = Annotated[TenderRepository, Depends(get_repo)]
Cfg = Annotated[Settings, Depends(get_settings)]


@router.post("/{tender_id}", response_model=ScoreOut)
def rescore(tender_id: str, repo: Repo, settings: Cfg, scorer: str | None = None):
    """Re-pontua o edital e persiste o novo score. ``scorer`` força heuristic|llm."""
    try:
        tender = repo.get_tender(tender_id)
    except Exception as exc:  # noqa: BLE001 - falha de banco vira 503
        raise HTTPException(503, f"Banco indisponível: {exc}") from exc
    if tender is None:
        raise HTTPException(404, "Edital não encontrado")

    from danzeroum_tracker.scoring import get_scorer

    try:
        engine = get_scorer(scorer or settings.scorer, settings=settings)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    result = engine.score(tender)
    repo.save_score(tender_id, result)
    return ScoreOut(
        risk_score=result.risk_score,
        fit_score=result.fit_score,
        complexity_score=result.complexity_score,
        recommendation=result.recommendation,
        key_requirements=list(result.key_requirements),
        pricing_guidance=result.pricing_guidance,
        analysis_text=result.analysis_text,
    )

from datetime import UTC, datetime

from danzeroum_tracker.models import Tender
from danzeroum_tracker.scoring import HeuristicScorer, validate_score


def test_ti_tender_is_go(sample_tenders):
    scorer = HeuristicScorer()
    score = scorer.score(sample_tenders[0])  # TI, suporte/manutenção, atestado
    assert score.fit_score >= 0.6
    assert score.recommendation == "GO"
    assert "atestado" in score.key_requirements
    assert score.pricing_guidance


def test_non_ti_tender_is_skip(sample_tenders):
    scorer = HeuristicScorer()
    score = scorer.score(sample_tenders[1])  # material de escritório
    assert score.fit_score < 0.3
    assert score.recommendation == "SKIP"


def test_scores_are_clamped_for_extreme_tender():
    scorer = HeuristicScorer()
    tender = Tender(
        source="x",
        external_id="1",
        title="Sistema de missão crítica com alta disponibilidade 24x7 e integração",
        description="sla redundancia interoperabilidade " * 50,
        category="TI",
        budget_estimate=5_000_000.0,
        deadline=datetime.now(UTC),  # prazo expirando → risco alto
    )
    score = scorer.score(tender)
    assert 0.0 <= score.risk_score <= 1.0
    assert 0.0 <= score.fit_score <= 1.0
    assert 0.0 <= score.complexity_score <= 1.0
    assert score.complexity_score > 0.5


def test_output_conforms_to_schema(sample_tenders):
    scorer = HeuristicScorer()
    for tender in sample_tenders:
        validate_score(scorer.score(tender).to_dict())


def test_recommendation_review_band():
    scorer = HeuristicScorer()
    # TELECOM: fit base 0.3, sem termos de TI → entre 0.3 e 0.6 → REVIEW
    tender = Tender(
        source="x",
        external_id="1",
        title="Contratação de link de internet dedicado",
        description="fornecimento de telefonia",
        category="TELECOM",
        budget_estimate=10000.0,
    )
    score = scorer.score(tender)
    assert score.recommendation == "REVIEW"

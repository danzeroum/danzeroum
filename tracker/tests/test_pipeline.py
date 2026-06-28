from danzeroum_tracker.pipeline import run_collection
from danzeroum_tracker.scoring import HeuristicScorer
from danzeroum_tracker.storage import InMemoryRepository
from tests.conftest import StubAdapter


def test_run_collection_scores_new_and_alerts(sample_tenders):
    repo = InMemoryRepository()
    result = run_collection(
        [StubAdapter(sample_tenders)],
        repo,
        HeuristicScorer(),
        min_fit_alert=0.4,
    )
    assert result.collected == 2
    assert result.new == 2
    assert result.scored == 2
    # só o edital de TI (GO) gera alerta; o de "OUTROS" (SKIP) não.
    assert len(result.alerts) == 1
    assert result.alerts[0]["external_id"] == "A1"
    assert result.alerts[0]["recommendation"] == "GO"


def test_run_collection_is_idempotent(sample_tenders):
    repo = InMemoryRepository()
    run_collection([StubAdapter(sample_tenders)], repo, HeuristicScorer())
    second = run_collection([StubAdapter(sample_tenders)], repo, HeuristicScorer())
    assert second.collected == 2
    assert second.new == 0          # dedupe: nada novo
    assert second.scored == 0
    assert second.alerts == []
    assert repo.count() == 2

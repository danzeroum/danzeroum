from danzeroum_tracker.adapters.base import AdapterError, OrgaoAdapter
from danzeroum_tracker.pipeline import run_collection
from danzeroum_tracker.scoring import HeuristicScorer
from danzeroum_tracker.storage import InMemoryRepository
from tests.conftest import StubAdapter


class _FailingAdapter(OrgaoAdapter):
    source = "BROKEN"

    def fetch_raw(self):
        raise AdapterError("boom")

    def parse_tender(self, raw):  # pragma: no cover
        raise NotImplementedError

    def collect(self):
        raise AdapterError("boom")


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


def test_run_collection_isolates_failing_source(sample_tenders):
    repo = InMemoryRepository()
    result = run_collection(
        [_FailingAdapter(), StubAdapter(sample_tenders)],
        repo,
        HeuristicScorer(),
    )
    # a fonte quebrada não derruba a coleta: a boa é processada e o erro é registrado.
    assert result.new == 2
    assert len(result.errors) == 1
    assert result.errors[0]["source"] == "BROKEN"
    assert "boom" in result.errors[0]["error"]


def test_run_collection_is_idempotent(sample_tenders):
    repo = InMemoryRepository()
    run_collection([StubAdapter(sample_tenders)], repo, HeuristicScorer())
    second = run_collection([StubAdapter(sample_tenders)], repo, HeuristicScorer())
    assert second.collected == 2
    assert second.new == 0          # dedupe: nada novo
    assert second.scored == 0
    assert second.alerts == []
    assert repo.count() == 2

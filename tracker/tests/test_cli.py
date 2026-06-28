import io
import json

from danzeroum_tracker import cli
from danzeroum_tracker.config import Settings
from danzeroum_tracker.scoring import HeuristicScorer
from danzeroum_tracker.storage import InMemoryRepository
from tests.conftest import StubAdapter


def _settings():
    return Settings.from_env({})


def test_main_schema_returns_zero():
    buf = io.StringIO()
    rc = cli.main(["schema"], out=buf)
    assert rc == 0
    data = json.loads(buf.getvalue())
    assert data["title"] == "Tender Scoring Result"


def test_main_version():
    # --version sai com SystemExit(0)
    try:
        cli.main(["--version"])
    except SystemExit as exc:
        assert exc.code == 0


def test_cmd_search_sorts_by_fit(sample_tenders):
    buf = io.StringIO()
    rc = cli.cmd_search(
        _settings(),
        limit=10,
        adapters=[StubAdapter(sample_tenders)],
        scorer=HeuristicScorer(),
        out=buf,
    )
    assert rc == 0
    rows = json.loads(buf.getvalue())
    assert [r["external_id"] for r in rows] == ["A1", "A2"]  # TI primeiro (fit maior)
    assert rows[0]["score"]["recommendation"] == "GO"


def test_cmd_collect_with_memory(sample_tenders):
    repo = InMemoryRepository()
    buf = io.StringIO()
    rc = cli.cmd_collect(
        _settings(),
        repo=repo,
        adapters=[StubAdapter(sample_tenders)],
        scorer=HeuristicScorer(),
        out=buf,
    )
    assert rc == 0
    out = json.loads(buf.getvalue())
    assert out["new"] == 2
    assert repo.count() == 2


def test_cmd_list(sample_tenders):
    repo = InMemoryRepository()
    cli.cmd_collect(
        _settings(),
        repo=repo,
        adapters=[StubAdapter(sample_tenders)],
        scorer=HeuristicScorer(),
        out=io.StringIO(),
    )
    buf = io.StringIO()
    rc = cli.cmd_list(_settings(), limit=10, repo=repo, out=buf)
    assert rc == 0
    assert len(json.loads(buf.getvalue())) == 2


def test_cmd_schedule_finite(sample_tenders):
    repo = InMemoryRepository()
    buf = io.StringIO()
    slept = []
    rc = cli.cmd_schedule(
        _settings(),
        repo=repo,
        adapters=[StubAdapter(sample_tenders)],
        scorer=HeuristicScorer(),
        iterations=1,
        sleep_fn=lambda s: slept.append(s),
        out=buf,
    )
    assert rc == 0
    assert repo.count() == 2
    assert slept == []  # com iterations=1 não chega a dormir

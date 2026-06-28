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


class _CountingNotifier:
    def __init__(self):
        self.calls = []

    def notify(self, result):
        self.calls.append(result)
        return len(result.get("alerts", []))


def test_cmd_collect_invokes_notifier(sample_tenders):
    repo = InMemoryRepository()
    notifier = _CountingNotifier()
    buf = io.StringIO()
    cli.cmd_collect(
        _settings(),
        repo=repo,
        adapters=[StubAdapter(sample_tenders)],
        scorer=HeuristicScorer(),
        notifier=notifier,
        out=buf,
    )
    out = json.loads(buf.getvalue())
    assert out["notified"] == 1  # 1 alerta (o edital de TI)
    assert len(notifier.calls) == 1


class _ExplodingNotifier:
    def notify(self, result):
        raise RuntimeError("SMTP auth failed")


def test_cmd_collect_survives_notifier_failure(sample_tenders):
    repo = InMemoryRepository()
    buf = io.StringIO()
    rc = cli.cmd_collect(
        _settings(),
        repo=repo,
        adapters=[StubAdapter(sample_tenders)],
        scorer=HeuristicScorer(),
        notifier=_ExplodingNotifier(),
        out=buf,
    )
    assert rc == 0                       # não derruba o comando
    out = json.loads(buf.getvalue())     # resultado ainda é emitido
    assert out["new"] == 2
    assert out["notified"] == 0
    assert "SMTP auth failed" in out["notify_error"]
    assert repo.count() == 2             # dados persistidos apesar do erro de e-mail


def test_cmd_report_text_and_json(sample_tenders):
    repo = InMemoryRepository()
    cli.cmd_collect(
        _settings(),
        repo=repo,
        adapters=[StubAdapter(sample_tenders)],
        scorer=HeuristicScorer(),
        notifier=_CountingNotifier(),
        out=io.StringIO(),
    )
    # texto
    buf = io.StringIO()
    assert cli.cmd_report(_settings(), limit=5, fmt="text", repo=repo, out=buf) == 0
    assert "Total de editais: 2" in buf.getvalue()
    # json
    buf = io.StringIO()
    assert cli.cmd_report(_settings(), limit=5, fmt="json", repo=repo, out=buf) == 0
    data = json.loads(buf.getvalue())
    assert data["total"] == 2
    assert data["top"][0]["recommendation"] == "GO"


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

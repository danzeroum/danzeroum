from danzeroum_tracker.models import Score, Tender
from danzeroum_tracker.storage import InMemoryRepository, build_repository


def _tender(ext="1", title="t"):
    return Tender(source="PNCP", external_id=ext, title=title, category="TI")


def test_build_repository_defaults_to_memory():
    assert isinstance(build_repository(""), InMemoryRepository)
    assert isinstance(build_repository(":memory:"), InMemoryRepository)


def test_upsert_new_then_update():
    repo = InMemoryRepository()
    id1, new1 = repo.upsert_tender(_tender("1", "primeiro"))
    assert new1 is True
    assert repo.count() == 1

    id2, new2 = repo.upsert_tender(_tender("1", "atualizado"))
    assert new2 is False
    assert id2 == id1
    assert repo.count() == 1
    assert repo.list_tenders()[0]["title"] == "atualizado"


def test_distinct_keys_are_separate():
    repo = InMemoryRepository()
    repo.upsert_tender(_tender("1"))
    repo.upsert_tender(_tender("2"))
    assert repo.count() == 2


def test_save_and_get_score():
    repo = InMemoryRepository()
    tid, _ = repo.upsert_tender(_tender("1"))
    score = Score(
        risk_score=0.2,
        fit_score=0.8,
        complexity_score=0.3,
        recommendation="GO",
        key_requirements=["atestado"],
    )
    sid = repo.save_score(tid, score)
    assert sid
    saved = repo.scores_for(tid)
    assert len(saved) == 1
    assert saved[0]["recommendation"] == "GO"


def test_list_respects_limit():
    repo = InMemoryRepository()
    for i in range(5):
        repo.upsert_tender(_tender(str(i)))
    assert len(repo.list_tenders(limit=3)) == 3

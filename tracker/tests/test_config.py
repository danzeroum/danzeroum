from danzeroum_tracker.config import DEFAULT_KEYWORDS, Settings


def test_defaults_when_env_empty():
    s = Settings.from_env({})
    assert s.database_url == ""
    assert s.uf == "SP"
    assert s.scorer == "heuristic"
    assert s.collect_interval_hours == 24.0
    assert s.keywords == DEFAULT_KEYWORDS


def test_env_overrides():
    s = Settings.from_env(
        {
            "DATABASE_URL": "postgresql://u:p@db:5432/x",
            "TRACKER_UF": "rj",
            "TRACKER_KEYWORDS": "ti, software , ",
            "TRACKER_SCORER": "heuristic",
            "COLLECT_INTERVAL_HOURS": "6",
            "TRACKER_MIN_FIT": "0.5",
        }
    )
    assert s.database_url == "postgresql://u:p@db:5432/x"
    assert s.uf == "RJ"
    assert s.keywords == ["ti", "software"]
    assert s.collect_interval_hours == 6.0
    assert s.min_fit_alert == 0.5

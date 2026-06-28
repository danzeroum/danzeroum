from danzeroum_tracker.config import DEFAULT_KEYWORDS, Settings


def test_defaults_when_env_empty():
    s = Settings.from_env({})
    assert s.database_url == ""
    assert s.uf == "SP"
    assert s.scorer == "heuristic"
    assert s.collect_interval_hours == 24.0
    assert s.keywords == DEFAULT_KEYWORDS
    assert s.sources == ["pncp"]  # Compras.gov existe mas não é default


def test_sources_override():
    s = Settings.from_env({"TRACKER_SOURCES": "PNCP, ComprasGov"})
    assert s.sources == ["pncp", "comprasgov"]


def test_empty_string_env_falls_back_to_default():
    # Cenário Docker: ${VAR:-} injeta variável vazia — deve usar o default, não "".
    s = Settings.from_env(
        {
            "PNCP_BASE_URL": "",
            "TRACKER_PAGE_SIZE": "",
            "TRACKER_UF": "",
            "SMTP_PORT": "",
            "TRACKER_SCORER": "",
        }
    )
    assert s.pncp_base_url == "https://pncp.gov.br/api/consulta/v1"
    assert s.page_size == 50
    assert s.uf == "SP"
    assert s.smtp_port == 465
    assert s.scorer == "heuristic"


def test_base_url_override_when_set():
    s = Settings.from_env({"PNCP_BASE_URL": "https://example.test/api"})
    assert s.pncp_base_url == "https://example.test/api"


def test_modalidades_default_and_override():
    assert Settings.from_env({}).modalidades == [6, 8]
    assert Settings.from_env({"TRACKER_MODALIDADES": "6"}).modalidades == [6]
    assert Settings.from_env({"TRACKER_MODALIDADES": "6, 8, 9"}).modalidades == [6, 8, 9]


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

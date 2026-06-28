from danzeroum_tracker.reporting import build_report, render_markdown, render_text

ROWS = [
    {
        "source": "PNCP",
        "external_id": "A1",
        "title": "Suporte de TI",
        "url": "http://x/1",
        "budget_estimate": 80000.0,
        "deadline": "2026-12-30T18:00:00",
        "fit_score": 0.8,
        "risk_score": 0.3,
        "recommendation": "GO",
    },
    {
        "source": "PNCP",
        "external_id": "A2",
        "title": "Material de limpeza",
        "url": "http://x/2",
        "budget_estimate": 5000.0,
        "deadline": None,
        "fit_score": 0.1,
        "risk_score": 0.2,
        "recommendation": "SKIP",
    },
    {
        "source": "COMPRAS_GOV",
        "external_id": "B1",
        "title": "Sem score",
        "url": None,
        "budget_estimate": None,
        "deadline": None,
        "fit_score": None,
        "risk_score": None,
        "recommendation": None,
    },
]


def test_build_report_counts_and_orders():
    r = build_report(ROWS, top_n=10)
    assert r["total"] == 3
    assert r["por_recomendacao"] == {"GO": 1, "SKIP": 1, "SEM_SCORE": 1}
    # ordenado por fit desc; o de maior fit primeiro
    assert r["top"][0]["external_id"] == "A1"


def test_build_report_top_n_limits():
    r = build_report(ROWS, top_n=1)
    assert len(r["top"]) == 1
    assert r["top"][0]["external_id"] == "A1"


def test_render_text_contains_summary():
    out = render_text(build_report(ROWS))
    assert "Total de editais: 3" in out
    assert "GO=1" in out
    assert "Suporte de TI" in out


def test_render_markdown_table():
    out = render_markdown(build_report(ROWS))
    assert out.startswith("# Relatório")
    assert "| # | Rec. | Fit |" in out
    assert "Suporte de TI" in out


def test_empty_report():
    r = build_report([], top_n=10)
    assert r["total"] == 0
    assert "nenhuma oportunidade" in render_text(r).lower()
    assert "Nenhuma oportunidade" in render_markdown(r)

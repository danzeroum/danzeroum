"""Testes do scorer via LLM (DeepSeek) e da degradação suave."""

from __future__ import annotations

import json

from danzeroum_tracker.config import Settings
from danzeroum_tracker.models import Tender
from danzeroum_tracker.scoring import get_scorer
from danzeroum_tracker.scoring.heuristic import HeuristicScorer
from danzeroum_tracker.scoring.llm import DeepSeekProvider, LLMScorer, build_provider


def _tender(**kw) -> Tender:
    base = dict(
        source="PNCP",
        external_id="ext-1",
        title="Contratação de suporte técnico de TI",
        description="Serviço de manutenção de sistemas",
        category="TI",
        budget_estimate=120_000.0,
        uf="SP",
    )
    base.update(kw)
    return Tender(**base)


class StubProvider:
    """Provider que devolve uma resposta fixa (sem rede)."""

    name = "stub"

    def __init__(self, response: str):
        self.response = response
        self.calls: list[tuple[str, str]] = []

    def complete(self, system_prompt, user_prompt, *, temperature=0.3, max_tokens=1200):
        self.calls.append((system_prompt, user_prompt))
        return self.response


_VALID = json.dumps(
    {
        "risk_score": 0.3,
        "fit_score": 0.82,
        "complexity_score": 0.4,
        "recommendation": "GO",
        "key_requirements": ["Atestado de capacidade técnica", "CND federal"],
        "pricing_guidance": "Faixa R$ 90k–110k",
        "analysis_text": "Aderente ao perfil de TI da empresa.",
    }
)


def test_llm_scorer_parses_valid_json():
    provider = StubProvider(_VALID)
    score = LLMScorer(provider).score(_tender())
    assert score.recommendation == "GO"
    assert score.fit_score == 0.82
    assert "Atestado de capacidade técnica" in score.key_requirements
    assert score.pricing_guidance == "Faixa R$ 90k–110k"
    assert score.analysis_text == "Aderente ao perfil de TI da empresa."


def test_llm_scorer_handles_markdown_fences():
    provider = StubProvider(f"```json\n{_VALID}\n```")
    score = LLMScorer(provider).score(_tender())
    assert score.recommendation == "GO"
    assert score.fit_score == 0.82


def test_llm_scorer_coerces_invalid_recommendation_and_clamps():
    bad = json.dumps(
        {
            "risk_score": 5,  # fora de 0..1 → clamp para 1.0
            "fit_score": -2,  # → 0.0
            "complexity_score": 0.5,
            "recommendation": "TALVEZ",  # inválido → REVIEW
            "key_requirements": "Atestado",  # string → vira lista
        }
    )
    score = LLMScorer(StubProvider(bad)).score(_tender())
    assert score.recommendation == "REVIEW"
    assert score.risk_score == 1.0
    assert score.fit_score == 0.0
    assert score.key_requirements == ["Atestado"]


def test_llm_scorer_falls_back_on_invalid_json():
    score = LLMScorer(StubProvider("isto não é json"), fallback=HeuristicScorer()).score(_tender())
    # Deve casar com o resultado do heurístico (não lança, retorna Score válido).
    expected = HeuristicScorer().score(_tender())
    assert score.recommendation == expected.recommendation
    assert score.fit_score == expected.fit_score


def test_llm_scorer_includes_edital_text_in_prompt():
    provider = StubProvider(_VALID)
    t = _tender(raw_json={"edital_text": "OBJETO: aquisição de licenças de software"})
    LLMScorer(provider).score(t)
    _system, user = provider.calls[0]
    assert "aquisição de licenças de software" in user


# ── DeepSeekProvider (cliente HTTP, sem rede real) ──────────────────────────────


class FakeHTTPResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


class FakeHTTPSession:
    def __init__(self, content):
        self._content = content
        self.last = {}

    def post(self, url, json=None, headers=None, timeout=None):
        self.last = {"url": url, "json": json, "headers": headers, "timeout": timeout}
        return FakeHTTPResponse(
            {"choices": [{"message": {"content": self._content}}]}
        )


def test_deepseek_provider_builds_request_and_parses_content():
    sess = FakeHTTPSession(_VALID)
    provider = DeepSeekProvider(
        api_key="sk-test", base_url="https://api.deepseek.com/", model="deepseek-v4-flash",
        session=sess,
    )
    out = provider.complete("sys", "user")
    assert out == _VALID
    assert sess.last["url"] == "https://api.deepseek.com/chat/completions"
    assert sess.last["headers"]["Authorization"] == "Bearer sk-test"
    assert sess.last["json"]["model"] == "deepseek-v4-flash"
    assert sess.last["json"]["response_format"] == {"type": "json_object"}
    assert sess.last["json"]["messages"][0]["role"] == "system"


def test_deepseek_provider_end_to_end_with_llm_scorer():
    provider = DeepSeekProvider(api_key="sk", session=FakeHTTPSession(_VALID))
    score = LLMScorer(provider).score(_tender())
    assert score.recommendation == "GO"


# ── Factory / degradação suave ──────────────────────────────────────────────────


def test_build_provider_none_without_key():
    assert build_provider(Settings.from_env({})) is None


def test_build_provider_deepseek_with_key():
    settings = Settings.from_env({"DEEPSEEK_API_KEY": "sk-x", "DEEPSEEK_MODEL": "deepseek-v4-pro"})
    provider = build_provider(settings)
    assert isinstance(provider, DeepSeekProvider)
    assert provider.model == "deepseek-v4-pro"


def test_get_scorer_llm_falls_back_to_heuristic_without_key():
    scorer = get_scorer("llm", settings=Settings.from_env({}))
    assert isinstance(scorer, HeuristicScorer)


def test_get_scorer_llm_returns_llm_scorer_with_key():
    settings = Settings.from_env({"DEEPSEEK_API_KEY": "sk-x"})
    scorer = get_scorer("deepseek", settings=settings)
    assert isinstance(scorer, LLMScorer)


def test_get_scorer_heuristic_unchanged():
    assert isinstance(get_scorer("heuristic"), HeuristicScorer)
    assert isinstance(get_scorer(), HeuristicScorer)

"""Scorer heurístico — sem LLM, determinístico, sem custo nem chave de API.

Serve de baseline funcional na V1 e de fallback quando não há provedor de LLM.
A interface é idêntica à de um scorer baseado em LLM (ver ``scoring.base.Scorer``).
"""

from __future__ import annotations

import unicodedata
from datetime import UTC, datetime

from danzeroum_tracker.models import Score, Tender

# Termos que indicam aderência ao perfil de TI da Danzeroum (CNAEs 6209/6204/6311).
_FIT_TERMS = (
    "tecnologia da informacao",
    "suporte tecnico",
    "manutencao",
    "software",
    "sistema",
    "desenvolvimento",
    "hospedagem",
    "tratamento de dados",
    "data center",
    "nuvem",
    "cloud",
    "informatica",
    "backup",
    "servidor",
    "rede",
)
# Termos de complexidade elevada (exigem mais capacidade/risco operacional).
_COMPLEX_TERMS = (
    "integracao",
    "alta disponibilidade",
    "missao critica",
    "24x7",
    "24 x 7",
    "sla",
    "datacenter",
    "redundancia",
    "barramento",
    "interoperabilidade",
)
# Pistas de requisitos de habilitação a extrair para a lista key_requirements.
_REQ_HINTS = (
    "atestado",
    "capital social",
    "certidao",
    "certidão",
    "habilitacao",
    "habilitação",
    "qualificacao tecnica",
    "garantia",
    "visita tecnica",
    "registro",
    "cnpj",
)

# Faixa de valor (R$) considerada "confortável" para uma ME de TI.
_COMFORT_MAX_BUDGET = 200_000.0


def _normalize(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text or "")
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _now() -> datetime:
    return datetime.now(UTC)


class HeuristicScorer:
    name = "heuristic"

    def __init__(self, comfort_max_budget: float = _COMFORT_MAX_BUDGET) -> None:
        self.comfort_max_budget = comfort_max_budget

    def score(self, tender: Tender) -> Score:
        text = _normalize(f"{tender.title} {tender.description or ''}")

        fit = self._fit(tender, text)
        complexity = self._complexity(text)
        risk = self._risk(tender, complexity)
        requirements = self._requirements(text)
        recommendation = self._recommend(fit, risk)
        pricing = self._pricing(tender)
        analysis = (
            f"fit={fit:.2f} risk={risk:.2f} complexity={complexity:.2f} "
            f"→ {recommendation} (heurística, categoria={tender.category})"
        )
        return Score(
            risk_score=round(risk, 2),
            fit_score=round(fit, 2),
            complexity_score=round(complexity, 2),
            recommendation=recommendation,
            key_requirements=requirements,
            pricing_guidance=pricing,
            analysis_text=analysis,
        )

    # ── componentes ─────────────────────────────────────────────────────────
    def _fit(self, tender: Tender, text: str) -> float:
        base = 0.6 if tender.category == "TI" else (0.3 if tender.category == "TELECOM" else 0.1)
        hits = sum(1 for term in _FIT_TERMS if term in text)
        return _clamp(base + min(hits, 4) * 0.1)

    def _complexity(self, text: str) -> float:
        hits = sum(1 for term in _COMPLEX_TERMS if term in text)
        length_factor = min(len(text) / 4000.0, 0.3)
        return _clamp(0.2 + hits * 0.15 + length_factor)

    def _risk(self, tender: Tender, complexity: float) -> float:
        risk = 0.2 + 0.4 * complexity
        # Orçamento acima da zona de conforto eleva o risco para uma ME.
        if tender.budget_estimate and tender.budget_estimate > self.comfort_max_budget:
            over = min(tender.budget_estimate / self.comfort_max_budget, 5.0)
            risk += 0.1 * (over - 1.0)
        # Prazo curto de proposta eleva o risco.
        if tender.deadline is not None:
            deadline = tender.deadline
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=UTC)
            days = (deadline - _now()).total_seconds() / 86400.0
            if days < 3:
                risk += 0.2
            elif days < 7:
                risk += 0.1
        return _clamp(risk)

    def _requirements(self, text: str) -> list[str]:
        found = []
        for hint in _REQ_HINTS:
            norm = _normalize(hint)
            if norm in text and norm not in found:
                found.append(norm)
        return found

    def _recommend(self, fit: float, risk: float) -> str:
        if fit < 0.3:
            return "SKIP"
        if fit >= 0.6 and risk <= 0.5:
            return "GO"
        return "REVIEW"

    def _pricing(self, tender: Tender) -> str:
        if tender.budget_estimate:
            return (
                f"Valor estimado R$ {tender.budget_estimate:,.2f}. "
                "Calcular preço mínimo: Custo ÷ (1 − carga tributária − margem)."
            )
        return "Sem valor estimado divulgado — solicitar planilha/edital para precificar."

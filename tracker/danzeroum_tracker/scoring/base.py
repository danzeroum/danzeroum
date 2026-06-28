"""Interface do scorer e da camada de LLM (porta de saída)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from danzeroum_tracker.models import Score, Tender


class Scorer(ABC):
    """Pontua a aderência de um edital ao perfil da Danzeroum."""

    #: nome curto do scorer (para logs/auditoria).
    name: str = "abstract"

    @abstractmethod
    def score(self, tender: Tender) -> Score:
        """Retorna risco, aderência, complexidade e recomendação."""


class LLMProvider(ABC):
    """Porta para um provedor de LLM concreto (futuro: OpenAI/Gemini/Claude/Ollama).

    Mantida agnóstica de propósito: a escolha do provedor e a precificação por
    chamada serão decididas numa rodada futura. O core depende só desta interface.
    """

    name: str = "abstract"

    @abstractmethod
    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.3,
        max_tokens: int = 1200,
    ) -> str:
        """Envia o prompt e devolve a resposta bruta (esperada em JSON)."""

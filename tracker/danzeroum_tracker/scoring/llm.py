"""Scorer baseado em LLM (DeepSeek) — provider concreto da porta ``LLMProvider``.

Converte o acervo de editais em decisão real: classificação GO/REVIEW/SKIP
justificada, requisitos-chave extraídos e orientação de preço, a partir do título,
da descrição e (quando disponível) do texto completo do edital.

Degradação suave: sem ``DEEPSEEK_API_KEY`` o ``get_scorer("llm")`` devolve o
``HeuristicScorer``. Em qualquer erro de rede/parse, o ``LLMScorer`` cai no
heurístico para nunca derrubar a coleta.

A API do DeepSeek é compatível com o formato OpenAI (``/chat/completions`` +
``Authorization: Bearer``), então o mesmo provider serve para qualquer endpoint
OpenAI-compatível trocando ``base_url``/``model``.

CUIDADO DE DADOS: aqui só trafega o EDITAL (dado público). Documentos internos da
empresa (certidões, contrato social, atestados) NÃO entram no prompt.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from typing import TYPE_CHECKING

import requests

from danzeroum_tracker.models import RECOMMENDATIONS, Score, Tender
from danzeroum_tracker.scoring.base import LLMProvider, Scorer
from danzeroum_tracker.scoring.heuristic import HeuristicScorer
from danzeroum_tracker.scoring.schema import validate_score

if TYPE_CHECKING:
    from danzeroum_tracker.config import Settings

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "Você é um analista de licitações públicas da Danzeroum, uma microempresa (ME) "
    "brasileira de Tecnologia da Informação (CNAEs 6209-1, 6204-0, 6311-9), optante "
    "pelo Simples Nacional, com zona de conforto de contratos até ~R$ 200 mil. "
    "Avalie a aderência de um edital ao perfil da empresa e responda APENAS com um "
    "objeto JSON, sem texto fora do JSON, com exatamente estes campos: "
    "risk_score (number 0..1), fit_score (number 0..1), complexity_score (number 0..1), "
    "recommendation (string: GO, REVIEW ou SKIP), key_requirements (array de strings "
    "com os requisitos de habilitação/qualificação técnica encontrados), "
    "pricing_guidance (string com orientação de preço, pode ser null) e "
    "analysis_text (string curta justificando a recomendação em português). "
    "GO = boa aderência e risco gerenciável; SKIP = fora do perfil; REVIEW = exige análise humana."
)


def _clamp01(value: object, default: float = 0.0) -> float:
    try:
        num = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default
    return max(0.0, min(1.0, num))


def _coerce_payload(data: dict) -> dict:
    """Normaliza a resposta do LLM para o formato do ``SCORE_SCHEMA``."""
    rec = str(data.get("recommendation", "")).strip().upper()
    if rec not in RECOMMENDATIONS:
        rec = "REVIEW"
    reqs = data.get("key_requirements") or []
    if not isinstance(reqs, list):
        reqs = [str(reqs)]
    reqs = [str(r) for r in reqs]
    pricing = data.get("pricing_guidance")
    pricing = str(pricing) if pricing not in (None, "") else None
    return {
        "risk_score": _clamp01(data.get("risk_score"), 0.5),
        "fit_score": _clamp01(data.get("fit_score"), 0.0),
        "complexity_score": _clamp01(data.get("complexity_score"), 0.5),
        "recommendation": rec,
        "key_requirements": reqs,
        "pricing_guidance": pricing,
    }


def _parse_json(raw: str) -> dict:
    """Extrai o objeto JSON da resposta do LLM, tolerando cercas markdown."""
    text = raw.strip()
    if text.startswith("```"):
        # remove ```json ... ``` ou ``` ... ```
        text = text.split("```", 2)[1] if text.count("```") >= 2 else text.strip("`")
        if text.lstrip().lower().startswith("json"):
            text = text.lstrip()[4:]
    text = text.strip()
    # Se ainda houver texto ao redor, isola do primeiro { ao último }.
    if not text.startswith("{"):
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start : end + 1]
    return json.loads(text)


class DeepSeekProvider(LLMProvider):
    """Cliente HTTP do DeepSeek (endpoint OpenAI-compatível ``/chat/completions``)."""

    name = "deepseek"

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "https://api.deepseek.com",
        model: str = "deepseek-v4-flash",
        timeout: int = 60,
        session: requests.Session | None = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self._session = session or requests.Session()

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.3,
        max_tokens: int = 1200,
    ) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
            "stream": False,
        }
        resp = self._session.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=self.timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


class LLMScorer(Scorer):
    """Pontua via LLM; cai no ``fallback`` (heurístico) em qualquer falha."""

    name = "llm"

    def __init__(
        self,
        provider: LLMProvider,
        *,
        fallback: Scorer | None = None,
        max_chars: int = 24000,
        edital_fetcher: Callable[[Tender], str] | None = None,
    ) -> None:
        self.provider = provider
        self.fallback = fallback or HeuristicScorer()
        self.max_chars = max_chars
        # Opcional: baixa o texto do edital quando não está em raw_json (best-effort).
        self.edital_fetcher = edital_fetcher

    def score(self, tender: Tender) -> Score:
        try:
            raw = self.provider.complete(_SYSTEM_PROMPT, self._user_prompt(tender))
            parsed = _parse_json(raw)
            data = _coerce_payload(parsed)
            validate_score(data)
            analysis = parsed.get("analysis_text") or f"Análise via {self.provider.name}."
            return Score(
                risk_score=round(data["risk_score"], 2),
                fit_score=round(data["fit_score"], 2),
                complexity_score=round(data["complexity_score"], 2),
                recommendation=data["recommendation"],
                key_requirements=data["key_requirements"],
                pricing_guidance=data["pricing_guidance"],
                analysis_text=str(analysis),
            )
        except Exception as exc:  # noqa: BLE001 - LLM é best-effort; heurístico garante resultado
            logger.warning(
                "scoring via LLM falhou para %s/%s (%s) — usando heurístico",
                tender.source,
                tender.external_id,
                exc,
            )
            return self.fallback.score(tender)

    def _user_prompt(self, tender: Tender) -> str:
        # Importação tardia evita custo de import quando o scorer não é usado.
        from danzeroum_tracker.extraction import edital_text_from_raw

        edital = edital_text_from_raw(tender.raw_json or {}, max_chars=self.max_chars)
        if not edital and self.edital_fetcher is not None:
            try:
                edital = self.edital_fetcher(tender)
            except Exception as exc:  # noqa: BLE001 - download é best-effort
                logger.warning("falha ao buscar edital de %s: %s", tender.external_id, exc)
                edital = ""
        budget = tender.budget_estimate if tender.budget_estimate is not None else "(não divulgado)"
        prazo = tender.deadline.isoformat() if tender.deadline else "(não informado)"
        lines = [
            f"Fonte: {tender.source}",
            f"Categoria inferida: {tender.category}",
            f"Título: {tender.title}",
            f"Descrição: {tender.description or '(sem descrição)'}",
            f"Valor estimado (R$): {budget}",
            f"UF: {tender.uf or '—'}",
            f"Prazo: {prazo}",
        ]
        if edital:
            lines.append("\nTexto do edital (pode estar truncado):\n" + edital)
        lines.append(
            "\nResponda APENAS com o JSON pedido (risk_score, fit_score, complexity_score, "
            "recommendation, key_requirements, pricing_guidance, analysis_text)."
        )
        return "\n".join(lines)


def build_provider(settings: Settings) -> LLMProvider | None:
    """DeepSeek se ``DEEPSEEK_API_KEY`` estiver configurada; senão ``None`` (no-op)."""
    if not settings.deepseek_api_key:
        return None
    return DeepSeekProvider(
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        model=settings.deepseek_model,
        timeout=settings.request_timeout,
    )

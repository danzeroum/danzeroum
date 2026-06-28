"""Configuração via variáveis de ambiente (12-factor).

Tudo tem default sensato para rodar localmente/Docker sem segredos.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

# Palavras-chave que casam com os CNAEs da Danzeroum (6209-1, 6204-0, 6311-9).
DEFAULT_KEYWORDS = [
    "tecnologia da informação",
    "tecnologia",
    "suporte técnico",
    "manutenção de equipamentos de informática",
    "software",
    "sistema",
    "desenvolvimento de sistemas",
    "hospedagem",
    "tratamento de dados",
    "data center",
    "nuvem",
    "ti",
]


def _split_csv(value: str | None, default: list[str]) -> list[str]:
    if not value:
        return list(default)
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass
class Settings:
    """Configuração efetiva do rastreador."""

    database_url: str = ""
    pncp_base_url: str = "https://pncp.gov.br/api/consulta/v1"
    comprasgov_base_url: str = "https://dadosabertos.compras.gov.br"
    sources: list[str] = field(default_factory=lambda: ["pncp"])
    uf: str = "SP"
    keywords: list[str] = field(default_factory=lambda: list(DEFAULT_KEYWORDS))
    scorer: str = "heuristic"
    collect_interval_hours: float = 24.0
    min_fit_alert: float = 0.4
    page_size: int = 50
    max_pages: int = 5
    request_timeout: int = 30

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> Settings:
        e = env if env is not None else os.environ
        return cls(
            database_url=e.get("DATABASE_URL", ""),
            pncp_base_url=e.get("PNCP_BASE_URL", cls.pncp_base_url),
            comprasgov_base_url=e.get("COMPRAS_GOV_BASE_URL", cls.comprasgov_base_url),
            sources=[s.lower() for s in _split_csv(e.get("TRACKER_SOURCES"), ["pncp"])],
            uf=e.get("TRACKER_UF", "SP").upper(),
            keywords=_split_csv(e.get("TRACKER_KEYWORDS"), DEFAULT_KEYWORDS),
            scorer=e.get("TRACKER_SCORER", "heuristic"),
            collect_interval_hours=float(e.get("COLLECT_INTERVAL_HOURS", "24")),
            min_fit_alert=float(e.get("TRACKER_MIN_FIT", "0.4")),
            page_size=int(e.get("TRACKER_PAGE_SIZE", "50")),
            max_pages=int(e.get("TRACKER_MAX_PAGES", "5")),
            request_timeout=int(e.get("TRACKER_REQUEST_TIMEOUT", "30")),
        )

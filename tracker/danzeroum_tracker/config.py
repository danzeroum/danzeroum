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


def _env(e: dict[str, str], key: str, default: str) -> str:
    """Valor da env tratando string vazia como 'não definido' (usa o default).

    Importante para o Docker: ``${VAR:-}`` injeta a variável vazia, e sem isso um
    base_url/porta vazios sobrescreveriam o default e quebrariam a coleta.
    """
    value = e.get(key)
    return value if value not in (None, "") else default


@dataclass
class Settings:
    """Configuração efetiva do rastreador."""

    database_url: str = ""
    pncp_base_url: str = "https://pncp.gov.br/api/consulta/v1"
    comprasgov_base_url: str = "https://dadosabertos.compras.gov.br"
    comprassp_base_url: str = "https://www.bec.sp.gov.br"
    prefsp_base_url: str = "https://e-negocioscidadesp.prefeitura.sp.gov.br"
    sources: list[str] = field(default_factory=lambda: ["pncp"])
    uf: str = "SP"
    keywords: list[str] = field(default_factory=lambda: list(DEFAULT_KEYWORDS))
    scorer: str = "heuristic"
    collect_interval_hours: float = 24.0
    min_fit_alert: float = 0.4
    page_size: int = 50
    max_pages: int = 5
    request_timeout: int = 30
    # SMTP (alertas por e-mail) — mesmas variáveis do site. Vazio = no-op.
    smtp_host: str = ""
    smtp_port: int = 465
    smtp_user: str = ""
    smtp_pass: str = ""
    smtp_from: str = ""
    smtp_from_name: str = "Rastreador Danzeroum"
    smtp_encryption: str = "ssl"
    mail_to: str = ""

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> Settings:
        e = env if env is not None else os.environ
        return cls(
            database_url=e.get("DATABASE_URL", ""),
            pncp_base_url=_env(e, "PNCP_BASE_URL", cls.pncp_base_url),
            comprasgov_base_url=_env(e, "COMPRAS_GOV_BASE_URL", cls.comprasgov_base_url),
            comprassp_base_url=_env(e, "COMPRAS_SP_BASE_URL", cls.comprassp_base_url),
            prefsp_base_url=_env(e, "PREF_SP_BASE_URL", cls.prefsp_base_url),
            sources=[s.lower() for s in _split_csv(e.get("TRACKER_SOURCES"), ["pncp"])],
            uf=_env(e, "TRACKER_UF", "SP").upper(),
            keywords=_split_csv(e.get("TRACKER_KEYWORDS"), DEFAULT_KEYWORDS),
            scorer=_env(e, "TRACKER_SCORER", "heuristic"),
            collect_interval_hours=float(_env(e, "COLLECT_INTERVAL_HOURS", "24")),
            min_fit_alert=float(_env(e, "TRACKER_MIN_FIT", "0.4")),
            page_size=int(_env(e, "TRACKER_PAGE_SIZE", "50")),
            max_pages=int(_env(e, "TRACKER_MAX_PAGES", "5")),
            request_timeout=int(_env(e, "TRACKER_REQUEST_TIMEOUT", "30")),
            smtp_host=e.get("SMTP_HOST", ""),
            smtp_port=int(_env(e, "SMTP_PORT", "465")),
            smtp_user=e.get("SMTP_USER", ""),
            smtp_pass=e.get("SMTP_PASS", ""),
            smtp_from=e.get("SMTP_FROM", ""),
            smtp_from_name=_env(e, "SMTP_FROM_NAME", "Rastreador Danzeroum"),
            smtp_encryption=_env(e, "SMTP_ENCRYPTION", "ssl"),
            mail_to=e.get("MAIL_TO", ""),
        )

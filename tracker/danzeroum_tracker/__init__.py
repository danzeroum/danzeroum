"""Rastreador de oportunidades públicas (licitações) da Danzeroum — V1.

Subprojeto isolado: coleta editais de TI via adaptadores por órgão (PNCP na V1),
normaliza para um schema canônico, pontua a aderência ao perfil da Danzeroum
(scorer agnóstico, padrão heurístico sem LLM) e persiste em PostgreSQL.
"""

__version__ = "0.1.0"

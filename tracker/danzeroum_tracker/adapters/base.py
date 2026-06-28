"""Interface base dos adaptadores (padrão hexagonal: porta de entrada de dados)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from typing import Any

from danzeroum_tracker.models import Tender


class AdapterError(RuntimeError):
    """Falha genérica de um adaptador (rede, parsing, etc.)."""


class OrgaoAdapter(ABC):
    """Contrato comum: buscar registros brutos e normalizá-los para ``Tender``.

    O core do sistema só conhece esta interface — nunca a fonte concreta.
    """

    #: identificador curto da fonte (ex.: "PNCP"). Usado em ``Tender.source``.
    source: str = "ABSTRACT"

    @abstractmethod
    def fetch_raw(self) -> Iterable[dict[str, Any]]:
        """Retorna os registros brutos da fonte (já paginados/iterados)."""

    @abstractmethod
    def parse_tender(self, raw: dict[str, Any]) -> Tender:
        """Normaliza um registro bruto para o schema canônico ``Tender``."""

    def collect(self) -> Iterator[Tender]:
        """Pipeline padrão: busca → normaliza. Sobrescreva ``fetch_raw``/``parse``."""
        for raw in self.fetch_raw():
            yield self.parse_tender(raw)

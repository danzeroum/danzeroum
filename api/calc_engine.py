"""Cálculo de preço mínimo via Fator R + Simples Nacional (progressivo).

Corrige o cálculo antigo, que usava alíquota nominal fixa (6%/4,5%). O Simples é
PROGRESSIVO: a alíquota efetiva sai de ``(RBT12 × nominal − parcela_deduzir) / RBT12``,
por faixa de receita bruta dos últimos 12 meses (RBT12) e por anexo (III ou IV,
definido pelo Fator R = folha/receita ≥ 28%).

Função pura e determinística — sem I/O, fácil de testar.
"""

from __future__ import annotations

from dataclasses import dataclass

# Tabelas vigentes (LC 123/2006, redação da LC 155/2016). Cada faixa:
# (teto_RBT12, alíquota_nominal, parcela_a_deduzir).
SIMPLES_ANEXO_III = [
    (180_000.00, 0.060, 0.00),
    (360_000.00, 0.112, 9_360.00),
    (720_000.00, 0.135, 17_640.00),
    (1_800_000.00, 0.160, 35_640.00),
    (3_600_000.00, 0.210, 125_640.00),
    (4_800_000.00, 0.330, 648_000.00),
]
SIMPLES_ANEXO_IV = [
    (180_000.00, 0.045, 0.00),
    (360_000.00, 0.090, 8_100.00),
    (720_000.00, 0.102, 12_420.00),
    (1_800_000.00, 0.140, 39_780.00),
    (3_600_000.00, 0.220, 183_780.00),
    (4_800_000.00, 0.330, 828_000.00),
]

# Fator R que separa Anexo III (≥28%) de Anexo IV (<28%).
FATOR_R_THRESHOLD = 0.28


def _table(anexo: str) -> list[tuple[float, float, float]]:
    return SIMPLES_ANEXO_III if anexo == "III" else SIMPLES_ANEXO_IV


def simples_effective_rate(rbt12: float, anexo: str) -> float:
    """Alíquota EFETIVA do Simples para um RBT12 e anexo. 0..1."""
    table = _table(anexo)
    if rbt12 <= 0:
        return table[0][1]  # 1ª faixa: efetiva == nominal
    nominal, deduzir = table[-1][1], table[-1][2]
    for ceiling, nom, ded in table:
        if rbt12 <= ceiling:
            nominal, deduzir = nom, ded
            break
    effective = (rbt12 * nominal - deduzir) / rbt12
    return max(0.0, effective)


def anexo_for(fator_r: float) -> str:
    return "III" if fator_r >= FATOR_R_THRESHOLD else "IV"


@dataclass
class PriceResult:
    min_price: float
    direct_cost: float
    tax_burden: float
    effective_margin: float
    anexo: str
    fator_r: float
    effective_rate: float  # alíquota efetiva do Simples (sem ISS extra)
    iss_pct: float


def compute_price(
    *,
    revenue: float,
    payroll_pct: float,
    direct_cost_pct: float,
    margin_pct: float,
    iss_pct: float = 0.0,
) -> PriceResult:
    """Preço mínimo = custo direto / (1 − alíquota efetiva − ISS − margem).

    ``revenue`` é usado como RBT12 (receita dos últimos 12 meses) para a faixa.
    ``iss_pct`` é um ISS municipal adicional, FORA do Simples (default 0 — para
    optante do Simples o ISS já está embutido no DAS; use só se aplicável).
    """
    fator_r = payroll_pct
    anexo = anexo_for(fator_r)
    effective_rate = simples_effective_rate(revenue, anexo)
    direct_cost = revenue * direct_cost_pct

    denom = 1.0 - effective_rate - iss_pct - margin_pct
    min_price = direct_cost / denom if denom > 0 else 0.0
    total_tax_rate = effective_rate + iss_pct
    return PriceResult(
        min_price=min_price,
        direct_cost=direct_cost,
        tax_burden=min_price * total_tax_rate,
        effective_margin=min_price * margin_pct,
        anexo=anexo,
        fator_r=fator_r,
        effective_rate=effective_rate,
        iss_pct=iss_pct,
    )

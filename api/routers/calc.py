"""Fator R / Simples Nacional price calculator — stateless."""
from __future__ import annotations
from fastapi import APIRouter
from api.schemas import CalcInput, CalcOut

router = APIRouter(prefix="/calc", tags=["calc"])

@router.post("", response_model=CalcOut)
def calc_price(body: CalcInput) -> CalcOut:
    fator_r = body.payroll_pct
    anexo = "III" if fator_r >= 0.28 else "IV"
    tax_rate = 0.06 if anexo == "III" else 0.045
    direct_cost = body.revenue * body.direct_cost_pct
    min_price = direct_cost / (1 - tax_rate - body.margin_pct) if (1 - tax_rate - body.margin_pct) > 0 else 0.0
    tax_burden = min_price * tax_rate
    effective_margin = min_price * body.margin_pct
    return CalcOut(
        min_price=min_price,
        direct_cost=direct_cost,
        tax_burden=tax_burden,
        effective_margin=effective_margin,
        anexo=anexo,
        fator_r=fator_r,
    )

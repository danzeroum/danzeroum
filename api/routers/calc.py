"""Fator R / Simples Nacional price calculator — stateless, progressivo."""
from __future__ import annotations

from fastapi import APIRouter

from api.calc_engine import compute_price
from api.schemas import CalcInput, CalcOut

router = APIRouter(prefix="/calc", tags=["calc"])


@router.post("", response_model=CalcOut)
def calc_price(body: CalcInput) -> CalcOut:
    r = compute_price(
        revenue=body.revenue,
        payroll_pct=body.payroll_pct,
        direct_cost_pct=body.direct_cost_pct,
        margin_pct=body.margin_pct,
        iss_pct=body.iss_pct,
    )
    return CalcOut(
        min_price=r.min_price,
        direct_cost=r.direct_cost,
        tax_burden=r.tax_burden,
        effective_margin=r.effective_margin,
        anexo=r.anexo,
        fator_r=r.fator_r,
        effective_rate=r.effective_rate,
        iss_pct=r.iss_pct,
    )

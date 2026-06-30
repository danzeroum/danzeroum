"""Testes do motor de cálculo progressivo (Simples Nacional + Fator R)."""

from __future__ import annotations

import pytest

from api.calc_engine import (
    anexo_for,
    compute_price,
    simples_effective_rate,
)


def test_effective_rate_first_bracket_equals_nominal():
    # 1ª faixa (até 180k): efetiva == nominal (parcela a deduzir = 0).
    assert simples_effective_rate(120_000, "III") == pytest.approx(0.06)
    assert simples_effective_rate(120_000, "IV") == pytest.approx(0.045)


def test_effective_rate_second_bracket_anexo_iii():
    # RBT12 = 300k, Anexo III, faixa 2: (300000*0.112 - 9360)/300000 = 0.0808
    assert simples_effective_rate(300_000, "III") == pytest.approx(0.0808, abs=1e-4)


def test_effective_rate_is_progressive():
    # A efetiva cresce com o RBT12 dentro do anexo.
    rates = [simples_effective_rate(r, "III") for r in (100_000, 300_000, 600_000, 1_000_000)]
    assert rates == sorted(rates)
    assert all(0 < x < 0.33 for x in rates)


def test_effective_rate_zero_revenue_safe():
    assert simples_effective_rate(0, "III") == pytest.approx(0.06)


def test_anexo_threshold():
    assert anexo_for(0.28) == "III"   # no limiar entra no III
    assert anexo_for(0.2799) == "IV"
    assert anexo_for(0.5) == "III"


def test_compute_price_uses_progressive_rate_not_flat():
    # Com RBT12 alto, a efetiva > 6% nominal → preço maior que o cálculo antigo.
    r = compute_price(revenue=1_000_000, payroll_pct=0.35, direct_cost_pct=0.5, margin_pct=0.15)
    assert r.anexo == "III"
    assert r.effective_rate > 0.06  # progressivo, não o flat de 6%
    # min_price = direct_cost / (1 - eff - 0 - 0.15)
    expected = (1_000_000 * 0.5) / (1 - r.effective_rate - 0.15)
    assert r.min_price == pytest.approx(expected)


def test_compute_price_iss_increases_price_and_tax():
    base = compute_price(revenue=200_000, payroll_pct=0.1, direct_cost_pct=0.4, margin_pct=0.1)
    with_iss = compute_price(
        revenue=200_000, payroll_pct=0.1, direct_cost_pct=0.4, margin_pct=0.1, iss_pct=0.05
    )
    assert with_iss.min_price > base.min_price
    assert with_iss.tax_burden > base.tax_burden
    assert with_iss.anexo == "IV"  # fator R 0.1 < 0.28


def test_compute_price_infeasible_margin_returns_zero():
    # Soma de alíquota + ISS + margem >= 1 → denominador não positivo → 0.
    r = compute_price(revenue=120_000, payroll_pct=0.35, direct_cost_pct=0.5, margin_pct=0.99)
    assert r.min_price == 0.0

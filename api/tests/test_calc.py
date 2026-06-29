import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_calc_anexo_iii():
    r = client.post("/calc", json={"revenue": 500000, "payroll_pct": 0.35, "direct_cost_pct": 0.5, "margin_pct": 0.15})
    assert r.status_code == 200
    data = r.json()
    assert data["anexo"] == "III"
    assert data["fator_r"] == pytest.approx(0.35)
    assert data["min_price"] > 0

def test_calc_anexo_iv():
    r = client.post("/calc", json={"revenue": 500000, "payroll_pct": 0.1, "direct_cost_pct": 0.5, "margin_pct": 0.15})
    assert r.status_code == 200
    data = r.json()
    assert data["anexo"] == "IV"

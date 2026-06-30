import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { calcPrice } from '../api/client'
import type { CalcOut } from '../api/types'

function Slider({ label, value, min, max, step, onChange, fmt }: {
  label: string; value: number; min: number; max: number; step: number
  onChange: (v: number) => void; fmt: (v: number) => string
}) {
  return (
    <div style={{ marginBottom: 18 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
        <span className="field-label">{label}</span>
        <span className="tnum" style={{ fontSize: '.86rem', fontWeight: 600, color: 'var(--ink)' }}>{fmt(value)}</span>
      </div>
      <input type="range" min={min} max={max} step={step} value={value}
        onChange={e => onChange(Number(e.target.value))}
        style={{ width: '100%', accentColor: 'var(--accent)' }} />
    </div>
  )
}

function fmtBRL(n: number): string {
  return n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

export default function Calc() {
  const [revenue, setRevenue] = useState(500000)
  const [payrollPct, setPayrollPct] = useState(0.28)
  const [directCostPct, setDirectCostPct] = useState(0.50)
  const [marginPct, setMarginPct] = useState(0.15)
  const [issPct, setIssPct] = useState(0)
  const [result, setResult] = useState<CalcOut | null>(null)

  const calc = useMutation({
    mutationFn: calcPrice,
    onSuccess: setResult,
  })

  return (
    <div className="page fade-up">
      <h1 className="h-page" style={{ marginBottom: 22 }}>Calculadora — Fator R / Simples</h1>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        <div className="card" style={{ padding: '24px 28px' }}>
          <h2 className="h-sec" style={{ marginBottom: 20 }}>Parâmetros</h2>
          <Slider label="Receita bruta anual" value={revenue} min={100000} max={5000000} step={10000}
            onChange={setRevenue} fmt={fmtBRL} />
          <Slider label="Folha / Receita" value={payrollPct} min={0.05} max={0.60} step={0.01}
            onChange={setPayrollPct} fmt={v => `${(v * 100).toFixed(0)}%`} />
          <Slider label="Custo direto / Receita" value={directCostPct} min={0.10} max={0.80} step={0.01}
            onChange={setDirectCostPct} fmt={v => `${(v * 100).toFixed(0)}%`} />
          <Slider label="Margem desejada" value={marginPct} min={0.05} max={0.40} step={0.01}
            onChange={setMarginPct} fmt={v => `${(v * 100).toFixed(0)}%`} />
          <Slider label="ISS extra (fora do Simples)" value={issPct} min={0} max={0.05} step={0.005}
            onChange={setIssPct} fmt={v => `${(v * 100).toFixed(1)}%`} />
          <button className="btn" onClick={() => calc.mutate({ revenue, payroll_pct: payrollPct, direct_cost_pct: directCostPct, margin_pct: marginPct, iss_pct: issPct })}
            disabled={calc.isPending} style={{ marginTop: 8, width: '100%' }}>
            {calc.isPending ? 'Calculando…' : 'Calcular preço mínimo'}
          </button>
        </div>

        <div className="card" style={{ padding: '24px 28px' }}>
          <h2 className="h-sec" style={{ marginBottom: 20 }}>Resultado</h2>
          {!result ? (
            <p style={{ color: 'var(--muted)', marginTop: 40, textAlign: 'center' }}>Ajuste os parâmetros e clique em calcular</p>
          ) : (
            <>
              <div style={{ marginBottom: 20, textAlign: 'center' }}>
                <span style={{
                  display: 'inline-block', padding: '6px 18px', borderRadius: 20,
                  background: result.anexo === 'III' ? 'var(--go)' : 'var(--review)',
                  color: '#fff', fontWeight: 700, fontSize: '.9rem', marginBottom: 8,
                }}>
                  Anexo {result.anexo}
                </span>
                <p style={{ fontSize: '.84rem', color: 'var(--muted)' }}>
                  Fator R: <span className="tnum" style={{ fontWeight: 600, color: 'var(--ink)' }}>{(result.fator_r * 100).toFixed(1)}%</span>
                  {' · '}Alíquota efetiva: <span className="tnum" style={{ fontWeight: 600, color: 'var(--ink)' }}>{(result.effective_rate * 100).toFixed(2)}%</span>
                </p>
              </div>
              <div style={{ borderTop: '1px solid var(--line)', paddingTop: 16 }}>
                {([
                  { label: 'Preço mínimo', value: fmtBRL(result.min_price), highlight: true },
                  { label: 'Custo direto', value: fmtBRL(result.direct_cost), highlight: false },
                  { label: 'Carga tributária', value: fmtBRL(result.tax_burden), highlight: false },
                  { label: 'Margem efetiva', value: fmtBRL(result.effective_margin), highlight: false },
                ] as { label: string; value: string; highlight: boolean }[]).map(({ label, value, highlight }) => (
                  <div key={label} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12, alignItems: 'center' }}>
                    <span style={{ fontSize: '.86rem', color: 'var(--text)' }}>{label}</span>
                    <span className="tnum" style={{ fontWeight: highlight ? 700 : 500, fontSize: highlight ? '1.1rem' : '.9rem', color: highlight ? 'var(--ink)' : 'var(--text)' }}>{value}</span>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getTender } from '../api/client'
import { RecoTag, Gauge, DeadlinePill, Icons } from '../components/icons'

function fmtBRL(n: number | null): string {
  if (!n || n <= 0) return '—'
  return n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 })
}

function Field({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div style={{ marginBottom: 14 }}>
      <p className="field-label" style={{ marginBottom: 4 }}>{label}</p>
      <p style={{ fontSize: '.9rem', color: 'var(--text)' }}>{value || '—'}</p>
    </div>
  )
}

const REC_BANNER: Record<string, { bg: string; color: string }> = {
  GO: { bg: 'var(--go-wash)', color: 'var(--go)' },
  REVIEW: { bg: 'var(--review-wash)', color: 'var(--review)' },
  SKIP: { bg: 'var(--skip-wash)', color: 'var(--skip)' },
}

export default function TenderDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [drawerOpen, setDrawerOpen] = useState(false)

  const { data, isLoading, error } = useQuery({
    queryKey: ['tender', id],
    queryFn: () => getTender(id!),
    enabled: !!id,
  })

  if (isLoading) return <div className="page"><p style={{ color: 'var(--muted)' }}>Carregando…</p></div>
  if (error || !data) return (
    <div className="page">
      <div className="card" style={{ padding: 32, color: 'var(--danger)' }}>
        {error ? (error as Error).message : 'Edital não encontrado'}
      </div>
    </div>
  )

  const s = data.score
  const banner = s ? (REC_BANNER[s.recommendation] ?? REC_BANNER.SKIP) : null

  return (
    <div className="page fade-up">
      {/* Back */}
      <button className="btn btn-ghost btn-sm" style={{ marginBottom: 16 }} onClick={() => navigate('/oportunidades')}>
        ← Voltar
      </button>

      {/* Header */}
      <div style={{ marginBottom: 22 }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12, flexWrap: 'wrap' }}>
          <h1 className="h-page" style={{ flex: 1, marginBottom: 6 }}>{data.title}</h1>
          {s && <RecoTag rec={s.recommendation} />}
        </div>
        <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap', fontSize: '.82rem', color: 'var(--muted)' }}>
          <span className="tnum">{data.source}</span>
          <span>·</span>
          <span>{data.uf}</span>
          <span>·</span>
          <span>{data.category}</span>
          {data.url && (
            <>
              <span>·</span>
              <a href={data.url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent-ink)', display: 'flex', alignItems: 'center', gap: 4 }}>
                Edital <Icons.ext size={12} />
              </a>
            </>
          )}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.15fr', gap: 20, alignItems: 'start' }}>
        {/* Left col — metadata + description */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div className="card" style={{ padding: '18px 20px' }}>
            <h2 className="h-sec" style={{ marginBottom: 16 }}>Dados do Edital</h2>
            <Field label="Número / ID externo" value={data.external_id} />
            <Field label="Orçamento estimado" value={fmtBRL(data.budget_estimate)} />
            <Field label="Publicado em" value={data.publish_date ? new Date(data.publish_date).toLocaleDateString('pt-BR') : null} />
            <Field label="Prazo de entrega" value={
              <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                {data.deadline ? new Date(data.deadline).toLocaleDateString('pt-BR') : '—'}
                <DeadlinePill deadline={data.deadline} />
              </span>
            } />
            <Field label="Status" value={data.status} />
            <Field label="Modalidade / Categoria" value={data.category} />
          </div>

          {data.description && (
            <div className="card" style={{ padding: '18px 20px' }}>
              <h2 className="h-sec" style={{ marginBottom: 12 }}>Descrição</h2>
              <p style={{ fontSize: '.88rem', color: 'var(--text)', lineHeight: 1.6 }}>{data.description}</p>
            </div>
          )}

          {s?.key_requirements && s.key_requirements.length > 0 && (
            <div className="card" style={{ padding: '18px 20px' }}>
              <h2 className="h-sec" style={{ marginBottom: 12 }}>Requisitos</h2>
              <ul style={{ listStyle: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: 8 }}>
                {s.key_requirements.map((req, i) => (
                  <li key={i} style={{ fontSize: '.88rem', color: 'var(--text)', display: 'flex', gap: 8, alignItems: 'flex-start' }}>
                    <span style={{ color: 'var(--faint)', flexShrink: 0, marginTop: 2 }}>›</span>
                    {req}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <button className="btn btn-ghost btn-sm" style={{ alignSelf: 'flex-start' }} onClick={() => setDrawerOpen(true)}>
            <Icons.layers size={14} /> Ver JSON bruto
          </button>
        </div>

        {/* Right col — scoring card (sticky) */}
        <div style={{ position: 'sticky', top: 80 }}>
          {s ? (
            <div className="card" style={{ padding: '20px 22px' }}>
              <h2 className="h-sec" style={{ marginBottom: 18 }}>Análise de Scoring</h2>

              {/* Gauges */}
              <div style={{ display: 'flex', justifyContent: 'space-around', marginBottom: 20 }}>
                <Gauge value={s.fit_score} label="Aderência" tone="go" size={72} />
                <Gauge value={s.risk_score} label="Risco" tone="risk" size={72} />
                <Gauge value={s.complexity_score} label="Complexidade" tone="review" size={72} />
              </div>

              {/* Recommendation banner */}
              {banner && (
                <div style={{ background: banner.bg, border: `1px solid ${banner.color}33`, borderRadius: 'var(--radius)', padding: '10px 14px', marginBottom: 16 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <RecoTag rec={s.recommendation} />
                    <span style={{ fontSize: '.88rem', color: 'var(--text)', flex: 1 }}>
                      {s.recommendation === 'GO' && 'Oportunidade boa — vale proposta'}
                      {s.recommendation === 'REVIEW' && 'Merece revisão manual antes de proposta'}
                      {s.recommendation === 'SKIP' && 'Aderência baixa — considere pular'}
                    </span>
                  </div>
                </div>
              )}

              {/* Analysis text */}
              {s.analysis_text && (
                <div style={{ marginBottom: 14 }}>
                  <p className="field-label" style={{ marginBottom: 6 }}>Análise</p>
                  <p style={{ fontSize: '.86rem', color: 'var(--text)', lineHeight: 1.6 }}>{s.analysis_text}</p>
                </div>
              )}

              {/* Pricing guidance */}
              {s.pricing_guidance && (
                <div>
                  <p className="field-label" style={{ marginBottom: 6 }}>Orientação de preço</p>
                  <p style={{ fontSize: '.86rem', color: 'var(--text)', lineHeight: 1.6 }}>{s.pricing_guidance}</p>
                </div>
              )}
            </div>
          ) : (
            <div className="card" style={{ padding: 24, textAlign: 'center', color: 'var(--muted)' }}>
              <Icons.trend size={32} style={{ margin: '0 auto 12px', opacity: .4 }} />
              <p>Este edital ainda não foi pontuado</p>
            </div>
          )}
        </div>
      </div>

      {/* Raw JSON Drawer */}
      {drawerOpen && (
        <>
          <div className="drawer-scrim" onClick={() => setDrawerOpen(false)} />
          <div className="drawer">
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '16px 20px', borderBottom: '1px solid var(--line)' }}>
              <h2 className="h-sec" style={{ flex: 1 }}>JSON bruto</h2>
              <button className="icon-btn" onClick={() => setDrawerOpen(false)}><Icons.close size={16} /></button>
            </div>
            <div className="scroll" style={{ flex: 1, padding: '16px 20px' }}>
              <pre style={{ fontFamily: 'var(--font-mono)', fontSize: '.78rem', color: 'var(--text)', lineHeight: 1.6, whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                {JSON.stringify(data.raw_json, null, 2)}
              </pre>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

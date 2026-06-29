import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { getReport } from '../api/client'
import { RecoTag, FitBar, DeadlinePill, Icons } from '../components/icons'
import type { ReportTopItem } from '../api/types'

function fmtBRL(n: number | null): string {
  if (!n || n <= 0) return '—'
  if (n >= 1_000_000) return `R$ ${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `R$ ${(n / 1_000).toFixed(0)}k`
  return n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function KPI({ label, value, sub, color }: { label: string; value: number | string; sub?: string; color?: string }) {
  return (
    <div className="card fade-in" style={{ padding: '20px 22px' }}>
      <p className="eyebrow" style={{ marginBottom: 8 }}>{label}</p>
      <p style={{ fontSize: '2rem', fontWeight: 700, color: color ?? 'var(--ink)', lineHeight: 1, fontFamily: 'var(--font-mono)' }}>{value}</p>
      {sub && <p style={{ fontSize: '.78rem', color: 'var(--muted)', marginTop: 6 }}>{sub}</p>}
    </div>
  )
}

export default function Dashboard() {
  const navigate = useNavigate()
  const { data, isLoading, error } = useQuery({ queryKey: ['report'], queryFn: getReport, refetchInterval: 30_000 })

  if (isLoading) return (
    <div className="page">
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 16, marginBottom: 24 }}>
        {[0, 1, 2, 3].map(i => <div key={i} className="card" style={{ height: 100, opacity: .4 }} />)}
      </div>
    </div>
  )

  if (error) return (
    <div className="page">
      <div className="card" style={{ padding: 32, color: 'var(--danger)' }}>
        Erro ao carregar relatório: {(error as Error).message}
      </div>
    </div>
  )

  const rec = data?.por_recomendacao ?? {}
  const go = rec['GO'] ?? 0
  const review = rec['REVIEW'] ?? 0

  return (
    <div className="page fade-up">
      <h1 className="h-page" style={{ marginBottom: 22 }}>Painel</h1>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 14, marginBottom: 24 }}>
        <KPI label="Total de editais" value={data?.total ?? 0} />
        <KPI label="Pontuados" value={(data?.top.length ?? 0) > 0 ? (data?.total ?? 0) : 0} />
        <KPI label="GO" value={go} color="var(--go)" />
        <KPI label="Revisar" value={review} color="var(--review)" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.7fr 1fr', gap: 16 }}>
        <div className="card" style={{ overflow: 'hidden' }}>
          <div style={{ padding: '16px 20px 12px', borderBottom: '1px solid var(--line)', display: 'flex', alignItems: 'center', gap: 10 }}>
            <Icons.trend size={16} />
            <h2 className="h-sec">Top oportunidades</h2>
          </div>
          <div className="scroll" style={{ maxHeight: 460 }}>
            <table className="tbl">
              <thead>
                <tr>
                  <th>Objeto</th>
                  <th>Fonte</th>
                  <th>Orçamento</th>
                  <th>Prazo</th>
                  <th>Aderência</th>
                  <th>Reco</th>
                </tr>
              </thead>
              <tbody>
                {(data?.top ?? []).map((t: ReportTopItem, i) => (
                  <tr key={i} onClick={() => navigate(`/oportunidades`)}>
                    <td style={{ maxWidth: 240 }}>
                      <span style={{ display: 'block', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {t.title}
                      </span>
                    </td>
                    <td><span className="tnum" style={{ fontSize: '.76rem', color: 'var(--faint)' }}>{t.source}</span></td>
                    <td className="tnum" style={{ fontSize: '.84rem' }}>{fmtBRL(t.budget_estimate)}</td>
                    <td><DeadlinePill deadline={t.deadline} /></td>
                    <td>{t.fit_score != null ? <FitBar value={t.fit_score} /> : '—'}</td>
                    <td>{t.recommendation ? <RecoTag rec={t.recommendation} sm /> : '—'}</td>
                  </tr>
                ))}
                {(!data?.top.length) && (
                  <tr>
                    <td colSpan={6} style={{ textAlign: 'center', color: 'var(--muted)', padding: 32 }}>
                      Nenhuma oportunidade pontuada — rode uma coleta
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div className="card" style={{ padding: '16px 20px' }}>
            <h2 className="h-sec" style={{ marginBottom: 14 }}>Por recomendação</h2>
            {Object.entries(rec).length === 0
              ? <p style={{ color: 'var(--muted)', fontSize: '.88rem' }}>Sem dados ainda</p>
              : Object.entries(rec).map(([r, n]) => (
                <div key={r} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
                  <RecoTag rec={r} />
                  <span className="tnum" style={{ fontWeight: 600 }}>{n}</span>
                </div>
              ))
            }
          </div>

          <div className="card" style={{ padding: '16px 20px', flex: 1 }}>
            <h2 className="h-sec" style={{ marginBottom: 14 }}>Prazos próximos</h2>
            {(data?.top ?? [])
              .filter(t => t.deadline)
              .sort((a, b) => new Date(a.deadline!).getTime() - new Date(b.deadline!).getTime())
              .slice(0, 5)
              .map((t, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10, gap: 8 }}>
                  <span style={{ fontSize: '.84rem', color: 'var(--text)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flex: 1 }}>{t.title}</span>
                  <DeadlinePill deadline={t.deadline} />
                </div>
              ))}
            {!data?.top.some(t => t.deadline) && (
              <p style={{ color: 'var(--muted)', fontSize: '.88rem' }}>Sem prazos</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

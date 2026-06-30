import { useQuery } from '@tanstack/react-query'
import { getAnalytics } from '../api/client'
import type { Analytics, MonthlyPoint } from '../api/types'

function fmtBRL(n: number | null | undefined): string {
  if (!n || n <= 0) return 'R$ 0'
  if (n >= 1_000_000) return `R$ ${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `R$ ${(n / 1_000).toFixed(0)}k`
  return `R$ ${n.toFixed(0)}`
}

function KPI({ label, value, sub, color }: { label: string; value: string; sub?: string; color?: string }) {
  return (
    <div className="card fade-in" style={{ padding: '18px 20px' }}>
      <p className="eyebrow" style={{ marginBottom: 8 }}>{label}</p>
      <p style={{ fontSize: '1.7rem', fontWeight: 700, color: color ?? 'var(--ink)', lineHeight: 1, fontFamily: 'var(--font-mono)' }}>{value}</p>
      {sub && <p style={{ fontSize: '.76rem', color: 'var(--muted)', marginTop: 6 }}>{sub}</p>}
    </div>
  )
}

const STATUS_COLORS: Record<string, string> = {
  WIN: 'var(--go)',
  LOST: 'var(--danger)',
  SENT: 'var(--review)',
  UNDER_REVIEW: 'var(--review)',
  DRAFT: 'var(--muted)',
  DISQUALIFIED: 'var(--faint)',
}

function StatusBar({ byStatus, total }: { byStatus: Record<string, number>; total: number }) {
  const entries = Object.entries(byStatus).filter(([, n]) => n > 0)
  if (total === 0) return <p style={{ color: 'var(--muted)', fontSize: '.88rem' }}>Sem propostas ainda</p>
  return (
    <div>
      <div style={{ display: 'flex', height: 14, borderRadius: 7, overflow: 'hidden', marginBottom: 12 }}>
        {entries.map(([st, n]) => (
          <div key={st} title={`${st}: ${n}`} style={{ width: `${(n / total) * 100}%`, background: STATUS_COLORS[st] ?? 'var(--muted)' }} />
        ))}
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px 14px' }}>
        {entries.map(([st, n]) => (
          <span key={st} style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: '.78rem', color: 'var(--text)' }}>
            <span style={{ width: 9, height: 9, borderRadius: 2, background: STATUS_COLORS[st] ?? 'var(--muted)' }} />
            {st} <b className="tnum">{n}</b>
          </span>
        ))}
      </div>
    </div>
  )
}

function MonthlyTrend({ monthly }: { monthly: MonthlyPoint[] }) {
  if (monthly.length === 0) return <p style={{ color: 'var(--muted)', fontSize: '.88rem' }}>Sem histórico mensal</p>
  const max = Math.max(1, ...monthly.map(m => m.sent))
  return (
    <div style={{ display: 'flex', alignItems: 'flex-end', gap: 14, height: 130, paddingTop: 8 }}>
      {monthly.slice(-12).map(m => (
        <div key={m.month} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6 }}>
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: 3, height: 100 }}>
            <div title={`Ganhas: ${m.won}`} style={{ width: 8, height: `${(m.won / max) * 100}%`, background: 'var(--go)', borderRadius: '2px 2px 0 0' }} />
            <div title={`Perdidas: ${m.lost}`} style={{ width: 8, height: `${(m.lost / max) * 100}%`, background: 'var(--danger)', borderRadius: '2px 2px 0 0' }} />
            <div title={`Enviadas: ${m.sent}`} style={{ width: 8, height: `${(m.sent / max) * 100}%`, background: 'var(--review)', borderRadius: '2px 2px 0 0', opacity: .55 }} />
          </div>
          <span style={{ fontSize: '.68rem', color: 'var(--faint)', fontFamily: 'var(--font-mono)' }}>{m.month.slice(5)}</span>
        </div>
      ))}
    </div>
  )
}

export default function BusinessAnalytics() {
  const { data, isLoading, error } = useQuery<Analytics>({ queryKey: ['analytics'], queryFn: getAnalytics, refetchInterval: 60_000 })

  if (isLoading) return <div className="card" style={{ height: 120, opacity: .4 }} />
  if (error) return null // analytics é complementar — não derruba o painel se o banco falhar

  const a = data!
  const winPct = a.decided > 0 ? `${(a.win_rate * 100).toFixed(0)}%` : '—'

  return (
    <section style={{ marginTop: 28 }}>
      <h2 className="h-sec" style={{ marginBottom: 14 }}>Desempenho comercial</h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 14, marginBottom: 16 }}>
        <KPI label="Taxa de vitória" value={winPct} sub={`${a.decided} decididas`} color="var(--go)" />
        <KPI label="Valor ganho" value={fmtBRL(a.value_won)} color="var(--go)" />
        <KPI label="Valor perdido" value={fmtBRL(a.value_lost)} color="var(--danger)" />
        <KPI label="Em pipeline" value={fmtBRL(a.value_pipeline)} sub={`${a.total_proposals} propostas`} color="var(--review)" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.4fr', gap: 16 }}>
        <div className="card" style={{ padding: '16px 20px' }}>
          <h3 className="h-sec" style={{ marginBottom: 14, fontSize: '.92rem' }}>Propostas por status</h3>
          <StatusBar byStatus={a.by_status} total={a.total_proposals} />
        </div>
        <div className="card" style={{ padding: '16px 20px' }}>
          <h3 className="h-sec" style={{ marginBottom: 4, fontSize: '.92rem' }}>Evolução mensal</h3>
          <MonthlyTrend monthly={a.monthly} />
        </div>
      </div>
    </section>
  )
}

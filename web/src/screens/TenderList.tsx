import { useState, useEffect, useCallback } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getTenders } from '../api/client'
import { RecoTag, FitBar, DeadlinePill, Icons } from '../components/icons'
import type { TenderFilters } from '../api/types'

const UFS = ['AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO']
const CATS = ['TI', 'TELECOM', 'OUTROS']
const RECS = ['GO', 'REVIEW', 'SKIP']

function fmtBRL(n: number | null): string {
  if (!n || n <= 0) return '—'
  if (n >= 1_000_000) return `R$ ${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `R$ ${(n / 1_000).toFixed(0)}k`
  return `R$ ${n.toFixed(0)}`
}

function useDebounce<T>(value: T, delay: number): T {
  const [dv, setDv] = useState(value)
  useEffect(() => {
    const t = setTimeout(() => setDv(value), delay)
    return () => clearTimeout(t)
  }, [value, delay])
  return dv
}

interface Props { globalSearch?: string }

export default function TenderList({ globalSearch }: Props) {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const [q, setQ] = useState(globalSearch ?? searchParams.get('q') ?? '')
  const [uf, setUf] = useState('')
  const [cat, setCat] = useState('')
  const [rec, setRec] = useState('')
  const [minFit, setMinFit] = useState(0)
  const [sort, setSort] = useState<'fit' | 'deadline' | 'budget'>('fit')
  const [page, setPage] = useState(1)

  useEffect(() => { if (globalSearch) setQ(globalSearch) }, [globalSearch])

  const dq = useDebounce(q, 300)

  const filters: TenderFilters = {
    q: dq || undefined,
    uf: uf || undefined,
    category: cat || undefined,
    recommendation: rec || undefined,
    min_fit: minFit > 0 ? minFit : undefined,
    sort,
    page,
    size: 50,
  }

  const { data, isLoading } = useQuery({
    queryKey: ['tenders', filters],
    queryFn: () => getTenders(filters),
    placeholderData: (prev) => prev,
  })

  const resetPage = useCallback(() => setPage(1), [])

  return (
    <div className="page fade-up">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 18 }}>
        <h1 className="h-page">Oportunidades</h1>
        {data && <span style={{ fontSize: '.84rem', color: 'var(--muted)' }}>{data.total} encontradas</span>}
      </div>

      {/* Filters */}
      <div className="card" style={{ padding: '14px 16px', marginBottom: 16 }}>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center' }}>
          {/* Search */}
          <div style={{ position: 'relative', minWidth: 200 }}>
            <span style={{ position: 'absolute', left: 9, top: '50%', transform: 'translateY(-50%)', color: 'var(--faint)', pointerEvents: 'none' }}>
              <Icons.search size={14} />
            </span>
            <input className="input" style={{ paddingLeft: 30, height: 32, fontSize: '.84rem', width: 220 }}
              placeholder="Buscar…" value={q}
              onChange={e => { setQ(e.target.value); resetPage() }} />
          </div>

          {/* UF chips */}
          <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
            {UFS.filter(u => ['SP', 'SC', 'PR', 'RS', 'DF'].includes(u)).map(u => (
              <button key={u} className={`chip chip-btn${uf === u ? ' on' : ''}`}
                style={{ padding: '3px 8px', fontSize: '.76rem' }}
                onClick={() => { setUf(uf === u ? '' : u); resetPage() }}>{u}</button>
            ))}
          </div>

          {/* Category */}
          <select className="input" style={{ height: 32, width: 110, fontSize: '.84rem' }}
            value={cat} onChange={e => { setCat(e.target.value); resetPage() }}>
            <option value="">Categoria</option>
            {CATS.map(c => <option key={c} value={c}>{c}</option>)}
          </select>

          {/* Recommendation */}
          <div style={{ display: 'flex', gap: 4 }}>
            {RECS.map(r => (
              <button key={r} className={`chip chip-btn${rec === r ? ' on' : ''}`}
                style={{ padding: '3px 8px', fontSize: '.76rem' }}
                onClick={() => { setRec(rec === r ? '' : r); resetPage() }}>{r}</button>
            ))}
          </div>

          {/* Sort */}
          <select className="input" style={{ height: 32, width: 130, fontSize: '.84rem', marginLeft: 'auto' }}
            value={sort} onChange={e => setSort(e.target.value as typeof sort)}>
            <option value="fit">↓ Aderência</option>
            <option value="deadline">↑ Prazo</option>
            <option value="budget">↓ Orçamento</option>
          </select>
        </div>

        {/* Fit slider */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 10 }}>
          <span style={{ fontSize: '.8rem', color: 'var(--muted)', whiteSpace: 'nowrap' }}>Aderência mín.</span>
          <input type="range" min={0} max={1} step={0.05} value={minFit}
            style={{ flex: 1, accentColor: 'var(--accent)', maxWidth: 200 }}
            onChange={e => { setMinFit(Number(e.target.value)); resetPage() }} />
          <span className="tnum" style={{ fontSize: '.8rem', color: 'var(--accent-ink)', minWidth: 32 }}>{minFit.toFixed(2)}</span>
        </div>
      </div>

      {/* Table */}
      <div className="card" style={{ overflow: 'hidden' }}>
        <div className="scroll" style={{ maxHeight: 'calc(100vh - 340px)' }}>
          <table className="tbl">
            <thead>
              <tr>
                <th style={{ width: 80 }}>Fonte</th>
                <th>Órgão / Objeto</th>
                <th>UF</th>
                <th>Orçamento</th>
                <th>Prazo</th>
                <th>Aderência</th>
                <th>Reco</th>
              </tr>
            </thead>
            <tbody>
              {isLoading && (
                <tr><td colSpan={7} style={{ textAlign: 'center', padding: 32, color: 'var(--muted)' }}>Carregando…</td></tr>
              )}
              {!isLoading && !data?.items.length && (
                <tr><td colSpan={7} style={{ textAlign: 'center', padding: 32, color: 'var(--muted)' }}>Nenhum edital encontrado com os filtros atuais</td></tr>
              )}
              {data?.items.map(t => (
                <tr key={t.id} onClick={() => navigate(`/oportunidades/${t.id}`)}>
                  <td><span className="tnum" style={{ fontSize: '.74rem', color: 'var(--faint)' }}>{t.source}</span></td>
                  <td style={{ maxWidth: 320 }}>
                    <span style={{ display: 'block', fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {t.title}
                    </span>
                  </td>
                  <td><span className="tnum" style={{ fontSize: '.8rem' }}>{t.uf ?? '—'}</span></td>
                  <td className="tnum" style={{ fontSize: '.84rem', whiteSpace: 'nowrap' }}>{fmtBRL(t.budget_estimate)}</td>
                  <td><DeadlinePill deadline={t.deadline} /></td>
                  <td>{t.score ? <FitBar value={t.score.fit_score} /> : <span style={{ color: 'var(--faint)' }}>—</span>}</td>
                  <td>{t.score ? <RecoTag rec={t.score.recommendation} sm /> : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {data && data.total > data.size && (
          <div style={{ display: 'flex', justifyContent: 'center', gap: 8, padding: '12px 16px', borderTop: '1px solid var(--line)' }}>
            <button className="btn btn-sm" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>← Anterior</button>
            <span style={{ fontSize: '.84rem', color: 'var(--muted)', alignSelf: 'center' }}>
              Pág. {page} de {Math.ceil(data.total / data.size)}
            </span>
            <button className="btn btn-sm" disabled={page >= Math.ceil(data.total / data.size)} onClick={() => setPage(p => p + 1)}>Próxima →</button>
          </div>
        )}
      </div>
    </div>
  )
}

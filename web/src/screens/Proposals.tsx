import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getProposals, patchProposalStatus, deleteProposal } from '../api/client'
import type { Proposal } from '../api/types'

const COLUMNS = [
  { key: 'DRAFT', label: 'Rascunho', color: 'var(--muted)' },
  { key: 'SENT', label: 'Enviada', color: 'var(--accent)' },
  { key: 'UNDER_REVIEW', label: 'Em análise', color: 'var(--review)' },
  { key: 'WIN', label: 'Ganha', color: 'var(--go)' },
  { key: 'LOST', label: 'Perdida', color: 'var(--danger)' },
  { key: 'DISQUALIFIED', label: 'Inabilitada', color: 'var(--faint)' },
]

function fmtBRL(n: number | null): string {
  if (!n || n <= 0) return '—'
  if (n >= 1_000_000) return `R$ ${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `R$ ${(n / 1_000).toFixed(0)}k`
  return `R$ ${n.toFixed(2)}`
}

export default function Proposals() {
  const qc = useQueryClient()
  const { data = [], isLoading } = useQuery({ queryKey: ['proposals'], queryFn: () => getProposals() })

  const patch = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) => patchProposalStatus(id, status),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['proposals'] }),
  })

  const del = useMutation({
    mutationFn: deleteProposal,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['proposals'] }),
  })

  const byStatus: Record<string, Proposal[]> = {}
  for (const col of COLUMNS) byStatus[col.key] = data.filter(p => p.status === col.key)

  if (isLoading) return <div className="page"><div className="card" style={{ height: 300, opacity: .4 }} /></div>

  return (
    <div className="page fade-up">
      <h1 className="h-page" style={{ marginBottom: 22 }}>Propostas</h1>
      <div style={{ display: 'flex', gap: 12, overflowX: 'auto', paddingBottom: 12 }}>
        {COLUMNS.map(col => (
          <div key={col.key} style={{ minWidth: 200, flex: '0 0 200px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: col.color, flexShrink: 0 }} />
              <span style={{ fontWeight: 600, fontSize: '.86rem', color: 'var(--ink)' }}>{col.label}</span>
              <span style={{ marginLeft: 'auto', fontSize: '.78rem', color: 'var(--muted)' }}>{byStatus[col.key].length}</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {byStatus[col.key].map(p => (
                <div key={p.id} className="card fade-in" style={{ padding: '12px 14px' }}>
                  <p style={{ fontSize: '.84rem', fontWeight: 600, marginBottom: 4, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{p.tender_title ?? p.tender_id}</p>
                  <p className="tnum" style={{ fontSize: '.78rem', color: 'var(--muted)', marginBottom: 8 }}>{fmtBRL(p.price_offered)}</p>
                  <select
                    value={p.status}
                    onChange={e => patch.mutate({ id: p.id, status: e.target.value })}
                    style={{ fontSize: '.74rem', width: '100%', marginBottom: 6 }}
                  >
                    {COLUMNS.map(c => <option key={c.key} value={c.key}>{c.label}</option>)}
                  </select>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <a href={`/api/proposals/${p.id}/pdf`} target="_blank" rel="noopener noreferrer" style={{ fontSize: '.72rem', color: 'var(--accent)', textDecoration: 'none' }}>Baixar PDF</a>
                    <button onClick={() => del.mutate(p.id)} style={{ fontSize: '.72rem', color: 'var(--danger)', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>Remover</button>
                  </div>
                </div>
              ))}
              {!byStatus[col.key].length && (
                <div style={{ border: '2px dashed var(--line)', borderRadius: 8, padding: '20px 10px', textAlign: 'center', color: 'var(--faint)', fontSize: '.78rem' }}>vazio</div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getConfig, putConfig } from '../api/client'
import type { Config } from '../api/types'

const ALL_UFS = ['AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO']
const SOURCES = ['pncp', 'comprasgov', 'comprassp', 'prefsp']

function Toggle({ checked, onChange }: { checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <button
      type="button"
      onClick={() => onChange(!checked)}
      style={{
        width: 42, height: 24, borderRadius: 12, border: 'none',
        background: checked ? 'var(--accent)' : 'var(--line-2)',
        position: 'relative', transition: 'background .2s', cursor: 'pointer', flexShrink: 0,
      }}
    >
      <span style={{
        position: 'absolute', top: 3, left: checked ? 21 : 3, width: 18, height: 18,
        borderRadius: '50%', background: '#fff', transition: 'left .2s var(--ease)',
      }} />
    </button>
  )
}

export default function Config() {
  const qc = useQueryClient()
  const { data, isLoading } = useQuery({ queryKey: ['config'], queryFn: getConfig })
  const [local, setLocal] = useState<Partial<Config>>({})
  const [newKeyword, setNewKeyword] = useState('')
  const [saved, setSaved] = useState(false)

  useEffect(() => { if (data) setLocal(data) }, [data])

  const mutation = useMutation({
    mutationFn: putConfig,
    onSuccess: (updated) => {
      setLocal(updated)
      qc.setQueryData(['config'], updated)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    },
  })

  const cfg: Partial<Config> = { ...data, ...local }

  function update<K extends keyof Config>(key: K, value: Config[K]) {
    setLocal(prev => ({ ...prev, [key]: value }))
  }

  function toggleUf(uf: string) {
    const current = (cfg.uf ?? '').split(',').map(s => s.trim()).filter(Boolean)
    const next = current.includes(uf) ? current.filter(u => u !== uf) : [...current, uf]
    update('uf', next.join(','))
  }

  function toggleSource(src: string) {
    const current = cfg.sources ?? []
    const next = current.includes(src) ? current.filter(s => s !== src) : [...current, src]
    update('sources', next)
  }

  function addKeyword() {
    const kw = newKeyword.trim()
    if (!kw) return
    const current = cfg.keywords ?? []
    if (!current.includes(kw)) update('keywords', [...current, kw])
    setNewKeyword('')
  }

  function removeKeyword(kw: string) {
    update('keywords', (cfg.keywords ?? []).filter(k => k !== kw))
  }

  if (isLoading) return <div className="page"><p style={{ color: 'var(--muted)' }}>Carregando…</p></div>

  const activeUfs = (cfg.uf ?? '').split(',').map(s => s.trim()).filter(Boolean)

  return (
    <form className="page fade-up" onSubmit={e => { e.preventDefault(); mutation.mutate(local as Config) }}>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 22 }}>
        <h1 className="h-page" style={{ flex: 1 }}>Configuração</h1>
        <button type="submit" className="btn btn-primary" disabled={mutation.isPending}>
          {mutation.isPending ? 'Salvando…' : saved ? '✓ Salvo' : 'Salvar configuração'}
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        {/* Left col — collection settings */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {/* Sources */}
          <div className="card" style={{ padding: '18px 20px' }}>
            <h2 className="h-sec" style={{ marginBottom: 14 }}>Fontes de dados</h2>
            {SOURCES.map(src => (
              <div key={src} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '.84rem' }}>{src}</span>
                <Toggle checked={(cfg.sources ?? []).includes(src)} onChange={() => toggleSource(src)} />
              </div>
            ))}
          </div>

          {/* UF chips */}
          <div className="card" style={{ padding: '18px 20px' }}>
            <h2 className="h-sec" style={{ marginBottom: 12 }}>UFs monitoradas</h2>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {ALL_UFS.map(u => (
                <button type="button" key={u}
                  className={`chip chip-btn${activeUfs.includes(u) ? ' on' : ''}`}
                  style={{ fontSize: '.78rem', padding: '3px 9px' }}
                  onClick={() => toggleUf(u)}>{u}</button>
              ))}
            </div>
          </div>

          {/* Keywords */}
          <div className="card" style={{ padding: '18px 20px' }}>
            <h2 className="h-sec" style={{ marginBottom: 12 }}>Palavras-chave</h2>
            <div style={{ display: 'flex', gap: 8, marginBottom: 10 }}>
              <input className="input" style={{ flex: 1 }}
                placeholder="Nova palavra-chave…" value={newKeyword}
                onChange={e => setNewKeyword(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addKeyword() } }} />
              <button type="button" className="btn btn-sm" onClick={addKeyword}>+</button>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {(cfg.keywords ?? []).map(kw => (
                <span key={kw} className="chip" style={{ gap: 5 }}>
                  {kw}
                  <button type="button" onClick={() => removeKeyword(kw)}
                    style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--faint)', lineHeight: 1, padding: 0, fontSize: '1rem' }}>
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Horizon */}
          <div className="card" style={{ padding: '18px 20px' }}>
            <h2 className="h-sec" style={{ marginBottom: 14 }}>Horizonte de busca</h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <input type="range" min={7} max={180} step={1}
                value={cfg.proposal_horizon_days ?? 45}
                style={{ flex: 1, accentColor: 'var(--accent)' }}
                onChange={e => update('proposal_horizon_days', Number(e.target.value))} />
              <span className="tnum" style={{ fontSize: '.9rem', fontWeight: 600, minWidth: 60 }}>
                {cfg.proposal_horizon_days ?? 45} dias
              </span>
            </div>
          </div>
        </div>

        {/* Right col — scoring + scheduler */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {/* Scoring */}
          <div className="card" style={{ padding: '18px 20px' }}>
            <h2 className="h-sec" style={{ marginBottom: 14 }}>Scoring</h2>

            <label style={{ display: 'block', marginBottom: 12 }}>
              <p className="field-label" style={{ marginBottom: 6 }}>Motor de scoring</p>
              <select className="input" value={cfg.scorer ?? 'heuristic'}
                onChange={e => update('scorer', e.target.value)}>
                <option value="heuristic">Heurístico (padrão)</option>
                <option value="llm">LLM (experimental)</option>
              </select>
            </label>

            <label style={{ display: 'block' }}>
              <p className="field-label" style={{ marginBottom: 6 }}>Aderência mínima para alerta</p>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <input type="range" min={0} max={1} step={0.05}
                  value={cfg.min_fit_alert ?? 0.4}
                  style={{ flex: 1, accentColor: 'var(--accent)' }}
                  onChange={e => update('min_fit_alert', Number(e.target.value))} />
                <span className="tnum" style={{ fontSize: '.9rem', fontWeight: 600, minWidth: 38 }}>
                  {(cfg.min_fit_alert ?? 0.4).toFixed(2)}
                </span>
              </div>
            </label>
          </div>

          {/* Scheduler */}
          <div className="card" style={{ padding: '18px 20px' }}>
            <h2 className="h-sec" style={{ marginBottom: 14 }}>Agendamento</h2>
            <label style={{ display: 'block' }}>
              <p className="field-label" style={{ marginBottom: 6 }}>Intervalo de coleta (horas)</p>
              <select className="input" value={cfg.collect_interval_hours ?? 24}
                onChange={e => update('collect_interval_hours', Number(e.target.value))}>
                {[1, 2, 4, 6, 8, 12, 24, 48].map(h => (
                  <option key={h} value={h}>{h}h {h === 24 ? '(diário)' : ''}</option>
                ))}
              </select>
            </label>
          </div>

          {/* Pagination */}
          <div className="card" style={{ padding: '18px 20px' }}>
            <h2 className="h-sec" style={{ marginBottom: 14 }}>Limites de coleta</h2>
            <label style={{ display: 'block', marginBottom: 12 }}>
              <p className="field-label" style={{ marginBottom: 6 }}>Editais por página</p>
              <input className="input" type="number" min={10} max={200}
                value={cfg.page_size ?? 50}
                onChange={e => update('page_size', Number(e.target.value))} />
            </label>
            <label style={{ display: 'block' }}>
              <p className="field-label" style={{ marginBottom: 6 }}>Máximo de páginas por fonte</p>
              <input className="input" type="number" min={1} max={20}
                value={cfg.max_pages ?? 5}
                onChange={e => update('max_pages', Number(e.target.value))} />
            </label>
          </div>
        </div>
      </div>
    </form>
  )
}

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Icons } from '../icons'
import { getAlerts, startCollection } from '../../api/client'
import { useAuth } from '../../context/AuthContext'

interface Props {
  dark: boolean
  onToggleTheme: () => void
  onSearch: (q: string) => void
}

export function Topbar({ dark, onToggleTheme, onSearch }: Props) {
  const navigate = useNavigate()
  const { logout } = useAuth()
  const [q, setQ] = useState('')

  const { data: alerts } = useQuery({ queryKey: ['alerts'], queryFn: getAlerts, refetchInterval: 60_000 })
  const alertCount = alerts?.length ?? 0
  const hasDanger = alerts?.some(a => a.level === 'danger') ?? false

  const collectMutation = useMutation({
    mutationFn: startCollection,
    onSuccess: () => navigate('/coleta'),
  })

  function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    if (q.trim()) {
      onSearch(q.trim())
      navigate('/oportunidades')
    }
  }

  async function handleLogout() {
    await logout()
    navigate('/login')
  }

  return (
    <header className="topbar">
      <form onSubmit={handleSearch} style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1 }}>
        <div style={{ position: 'relative', width: 'min(340px, 42vw)' }}>
          <span style={{ position: 'absolute', left: 9, top: '50%', transform: 'translateY(-50%)', color: 'var(--faint)', pointerEvents: 'none' }}>
            <Icons.search size={15} />
          </span>
          <input
            className="input"
            style={{ paddingLeft: 32, height: 34, fontSize: '.84rem' }}
            placeholder="Buscar oportunidades…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </div>
      </form>

      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginLeft: 'auto' }}>
        <button
          className="btn btn-sm btn-primary"
          style={{ gap: 6 }}
          onClick={() => collectMutation.mutate()}
          disabled={collectMutation.isPending}
        >
          <Icons.collect size={14} />
          {collectMutation.isPending ? 'Iniciando…' : 'Coletar'}
        </button>

        <button className="icon-btn" style={{ position: 'relative' }} onClick={() => navigate('/coleta')}>
          <Icons.bell size={16} />
          {alertCount > 0 && (
            <span style={{
              position: 'absolute', top: 4, right: 4, width: 8, height: 8,
              borderRadius: '50%', background: hasDanger ? 'var(--danger)' : 'var(--go)',
            }} />
          )}
        </button>

        <button className="icon-btn" onClick={onToggleTheme} title="Alternar tema">
          {dark ? <Icons.sun size={16} /> : <Icons.moon size={16} />}
        </button>

        <button className="icon-btn" onClick={handleLogout} title="Sair" style={{ color: 'var(--muted)' }}>
          <Icons.ext size={16} />
        </button>
      </div>
    </header>
  )
}

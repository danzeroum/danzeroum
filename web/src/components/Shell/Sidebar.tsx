import { useNavigate, useLocation } from 'react-router-dom'
import { Icons, Logo } from '../icons'

const NAV = [
  {
    group: 'Operação',
    items: [
      { key: 'dashboard', label: 'Painel', path: '/' },
      { key: 'list', label: 'Oportunidades', path: '/oportunidades' },
      { key: 'collect', label: 'Coleta', path: '/coleta' },
    ],
  },
  {
    group: 'Sistema',
    items: [{ key: 'config', label: 'Configuração', path: '/config' }],
  },
]

export function Sidebar({ dark }: { dark: boolean }) {
  const navigate = useNavigate()
  const { pathname } = useLocation()

  return (
    <aside className="sidebar scroll">
      <div className="sb-brand">
        <Logo size={28} dark={dark} />
        <span className="sb-word">Danzer<span className="z">o</span>um</span>
      </div>

      <nav className="sb-nav">
        {NAV.map(({ group, items }) => (
          <div key={group}>
            <p className="sb-group-label eyebrow">{group}</p>
            {items.map(({ key, label, path }) => {
              const Icon = Icons[key]
              const active = path === '/' ? pathname === '/' : pathname.startsWith(path)
              return (
                <button
                  key={key}
                  className={`nav-item${active ? ' active' : ''}`}
                  onClick={() => navigate(path)}
                >
                  {Icon && <Icon />}
                  {label}
                </button>
              )
            })}
          </div>
        ))}
      </nav>

      <div className="sb-foot">
        <div style={{ padding: '4px 8px', fontSize: '.82rem', color: 'var(--muted)' }}>
          <strong style={{ color: 'var(--ink)', display: 'block' }}>Daniel Lau</strong>
          Administrador
        </div>
      </div>
    </aside>
  )
}

import { useState, type FormEvent } from 'react'
import { apiLogin } from '../api/auth'
import { Logo } from '../components/icons'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await apiLogin(username, password)
      // Recarrega o contexto via navegação — AuthProvider relê /auth/me
      window.location.href = '/'
    } catch {
      setError('Usuário ou senha inválidos.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh', display: 'grid', placeItems: 'center',
      background: 'var(--bg)', fontFamily: 'var(--font)',
    }}>
      <div className="card fade-in" style={{ width: 360, padding: '40px 36px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: 32, gap: 12 }}>
          <Logo size={48} />
          <span style={{ fontWeight: 700, fontSize: '1.1rem', color: 'var(--ink)', letterSpacing: '.02em' }}>
            Danzer<span style={{ color: 'var(--accent)' }}>o</span>um
          </span>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <label className="field-label">Usuário
            <input
              type="text"
              autoComplete="username"
              required
              value={username}
              onChange={e => setUsername(e.target.value)}
              style={{ display: 'block', width: '100%', marginTop: 4 }}
            />
          </label>
          <label className="field-label">Senha
            <input
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={e => setPassword(e.target.value)}
              style={{ display: 'block', width: '100%', marginTop: 4 }}
            />
          </label>

          {error && (
            <p style={{ fontSize: '.84rem', color: 'var(--danger)', margin: 0 }}>{error}</p>
          )}

          <button type="submit" className="btn" disabled={loading} style={{ marginTop: 8, width: '100%' }}>
            {loading ? 'Entrando…' : 'Entrar'}
          </button>
        </form>
      </div>
    </div>
  )
}

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { apiMe, apiLogout, type AuthUser } from '../api/auth'

interface AuthCtx {
  user: AuthUser | null
  loading: boolean
  logout: () => Promise<void>
}

const Ctx = createContext<AuthCtx>({ user: null, loading: true, logout: async () => {} })

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    apiMe()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoading(false))
  }, [])

  async function logout() {
    await apiLogout().catch(() => {})
    setUser(null)
  }

  return <Ctx.Provider value={{ user, loading, logout }}>{children}</Ctx.Provider>
}

export function useAuth() {
  return useContext(Ctx)
}

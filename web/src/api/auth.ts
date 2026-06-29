const BASE = '/api'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { credentials: 'include', ...init })
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText)
    throw new Error(`${res.status} ${text}`)
  }
  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

export interface AuthUser { username: string }

export function apiLogin(username: string, password: string): Promise<{ user: AuthUser }> {
  return request('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
}

export function apiLogout(): Promise<{ ok: boolean }> {
  return request('/auth/logout', { method: 'POST' })
}

export function apiMe(): Promise<AuthUser> {
  return request('/auth/me')
}

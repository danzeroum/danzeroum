import type {
  Alert,
  CollectionRunStatus,
  Config,
  PaginatedTenders,
  Report,
  TenderDetail,
  TenderFilters,
} from './types'

const BASE = '/api'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, init)
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText)
    throw new Error(`${res.status} ${text}`)
  }
  return res.json() as Promise<T>
}

export function getTenders(filters: TenderFilters = {}): Promise<PaginatedTenders> {
  const params = new URLSearchParams()
  if (filters.q) params.set('q', filters.q)
  if (filters.uf) params.set('uf', filters.uf)
  if (filters.category) params.set('category', filters.category)
  if (filters.recommendation) params.set('recommendation', filters.recommendation)
  if (filters.min_fit != null) params.set('min_fit', String(filters.min_fit))
  if (filters.sort) params.set('sort', filters.sort)
  if (filters.page) params.set('page', String(filters.page))
  if (filters.size) params.set('size', String(filters.size))
  const qs = params.toString()
  return request<PaginatedTenders>(`/tenders${qs ? `?${qs}` : ''}`)
}

export function getTender(id: string): Promise<TenderDetail> {
  return request<TenderDetail>(`/tenders/${id}`)
}

export function startCollection(): Promise<CollectionRunStatus> {
  return request<CollectionRunStatus>('/collect', { method: 'POST' })
}

export function getRunStatus(runId: string): Promise<CollectionRunStatus> {
  return request<CollectionRunStatus>(`/collect/${runId}`)
}

export function getCollectRuns(): Promise<CollectionRunStatus[]> {
  return request<CollectionRunStatus[]>('/collect')
}

export function getReport(): Promise<Report> {
  return request<Report>('/report')
}

export function getConfig(): Promise<Config> {
  return request<Config>('/config')
}

export function putConfig(patch: Partial<Config>): Promise<Config> {
  return request<Config>('/config', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(patch),
  })
}

export function getAlerts(): Promise<Alert[]> {
  return request<Alert[]>('/alerts')
}

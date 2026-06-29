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

import type { Document, Certificate, Proposal, Client, CalcInput, CalcOut } from './types'

export function getDocuments(type?: string, valid?: boolean): Promise<Document[]> {
  const params = new URLSearchParams()
  if (type) params.set('type', type)
  if (valid != null) params.set('valid', String(valid))
  const qs = params.toString()
  return request<Document[]>(`/documents${qs ? `?${qs}` : ''}`)
}

export function uploadDocument(formData: FormData): Promise<Document> {
  return request<Document>('/documents', { method: 'POST', body: formData })
}

export function deleteDocument(id: string): Promise<void> {
  return request<void>(`/documents/${id}`, { method: 'DELETE' })
}

export function getCertificates(): Promise<Certificate[]> {
  return request<Certificate[]>('/certificates')
}

export function uploadCertificate(formData: FormData): Promise<Certificate> {
  return request<Certificate>('/certificates', { method: 'POST', body: formData })
}

export function deleteCertificate(id: string): Promise<void> {
  return request<void>(`/certificates/${id}`, { method: 'DELETE' })
}

export function getProposals(status?: string): Promise<Proposal[]> {
  const params = new URLSearchParams()
  if (status) params.set('status', status)
  const qs = params.toString()
  return request<Proposal[]>(`/proposals${qs ? `?${qs}` : ''}`)
}

export function createProposal(body: { tender_id: string; status?: string; price_offered?: number; validity_days?: number; notes?: string }): Promise<Proposal> {
  return request<Proposal>('/proposals', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
}

export function patchProposalStatus(id: string, status: string): Promise<Proposal> {
  return request<Proposal>(`/proposals/${id}/status`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status }) })
}

export function deleteProposal(id: string): Promise<void> {
  return request<void>(`/proposals/${id}`, { method: 'DELETE' })
}

export function getClients(status?: string): Promise<Client[]> {
  const params = new URLSearchParams()
  if (status) params.set('status', status)
  const qs = params.toString()
  return request<Client[]>(`/clients${qs ? `?${qs}` : ''}`)
}

export function createClient(body: { name: string; type?: string; cnpj?: string; contact_name?: string; email?: string; phone?: string; status?: string; notes?: string }): Promise<Client> {
  return request<Client>('/clients', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
}

export function patchClient(id: string, patch: Partial<{ name: string; status: string; contact_name: string; email: string; phone: string; notes: string }>): Promise<Client> {
  return request<Client>(`/clients/${id}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(patch) })
}

export function deleteClient(id: string): Promise<void> {
  return request<void>(`/clients/${id}`, { method: 'DELETE' })
}

export function calcPrice(body: CalcInput): Promise<CalcOut> {
  return request<CalcOut>('/calc', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
}

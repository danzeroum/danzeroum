export interface Score {
  risk_score: number
  fit_score: number
  complexity_score: number
  recommendation: 'GO' | 'REVIEW' | 'SKIP'
  key_requirements: string[]
  pricing_guidance: string | null
  analysis_text: string | null
}

export interface TenderSummary {
  id: string
  source: string
  external_id: string
  title: string
  status: string
  category: string
  budget_estimate: number | null
  publish_date: string | null
  deadline: string | null
  url: string | null
  uf: string | null
  created_at: string
  score: Score | null
}

export interface TenderDetail extends TenderSummary {
  description: string | null
  raw_json: Record<string, unknown>
}

export interface PaginatedTenders {
  items: TenderSummary[]
  total: number
  page: number
  size: number
}

export interface CollectionRunStatus {
  run_id: string
  status: 'running' | 'done' | 'error'
  result: CollectionResult | null
}

export interface CollectionResult {
  collected: number
  new: number
  scored: number
  alerts: unknown[]
  errors: { source?: string; message?: string }[]
  error?: string
}

export interface ReportTopItem {
  source: string
  external_id: string
  title: string
  url: string | null
  budget_estimate: number | null
  deadline: string | null
  fit_score: number | null
  risk_score: number | null
  recommendation: string | null
}

export interface Report {
  total: number
  por_recomendacao: Record<string, number>
  top: ReportTopItem[]
}

export interface MonthlyPoint {
  month: string // YYYY-MM
  sent: number
  won: number
  lost: number
}

export interface Analytics {
  total_proposals: number
  by_status: Record<string, number>
  win_rate: number // 0..1
  decided: number
  value_won: number
  value_lost: number
  value_pipeline: number
  monthly: MonthlyPoint[]
}

export interface Config {
  sources: string[]
  modalidades: number[]
  proposal_horizon_days: number
  uf: string
  keywords: string[]
  scorer: string
  collect_interval_hours: number
  min_fit_alert: number
  page_size: number
  max_pages: number
}

export interface Alert {
  id: string
  kind: string
  level: string
  title: string
  body: string
  tender_id: string | null
}

export interface TenderFilters {
  q?: string
  uf?: string
  category?: string
  recommendation?: string
  min_fit?: number
  sort?: 'fit' | 'deadline' | 'budget'
  page?: number
  size?: number
}

export interface Document {
  id: string
  type: string
  subtype: string | null
  name: string | null
  file_name: string | null
  mime_type: string | null
  issue_date: string | null
  expiry_date: string | null
  is_valid: boolean
  notes: string | null
  created_at: string
}

export interface Certificate {
  id: string
  client_name: string | null
  project_description: string | null
  start_date: string | null
  end_date: string | null
  project_value: number | null
  scope: string | null
  file_name: string | null
  mime_type: string | null
  created_at: string
}

export interface Proposal {
  id: string
  tender_id: string
  tender_title: string | null
  status: string
  price_offered: number | null
  validity_days: number | null
  version: number
  notes: string | null
  submitted_at: string | null
}

export interface Client {
  id: string
  name: string | null
  type: string | null
  cnpj: string | null
  contact_name: string | null
  email: string | null
  phone: string | null
  status: string | null
  notes: string | null
  created_at: string
}

export interface CalcInput {
  revenue: number
  payroll_pct: number
  direct_cost_pct: number
  margin_pct: number
}

export interface CalcOut {
  min_price: number
  direct_cost: number
  tax_burden: number
  effective_margin: number
  anexo: string
  fator_r: number
}

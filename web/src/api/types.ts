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

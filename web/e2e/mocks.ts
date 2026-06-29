/**
 * Playwright route mocks — intercepts /api/* requests so UI tests
 * run without a real backend or database.
 */
import { Page } from '@playwright/test'

// ── Mock data ─────────────────────────────────────────────────────────────────

const TENDERS = [
  {
    id: 'pncp-2026-000412',
    source: 'PNCP',
    org: 'Tribunal de Justiça do Paraná',
    uf: 'PR',
    title: 'Solução de gestão documental e assinatura eletrônica',
    budget: 2480000,
    deadline: '2026-07-14',
    status: 'novo',
    score: {
      fit_score: 0.91, risk_score: 0.22, complexity_score: 0.48,
      recommendation: 'GO',
      key_requirements: ['Atestado de capacidade técnica', 'CND federal', 'Integração ICP-Brasil'],
      pricing_guidance: 'R$ 1,98M – R$ 2,30M',
      analysis_text: 'Forte aderência ao portfólio de gestão documental.',
    },
  },
  {
    id: 'cn-2026-90218',
    source: 'ComprasNet',
    org: 'Ministério da Gestão e Inovação',
    uf: 'DF',
    title: 'Plataforma de inteligência jurídica com IA generativa',
    budget: 5900000,
    deadline: '2026-07-09',
    status: 'novo',
    score: {
      fit_score: 0.84, risk_score: 0.41, complexity_score: 0.72,
      recommendation: 'REVIEW',
      key_requirements: ['Atestado de IA/NLP', 'Hospedagem on-premise'],
      pricing_guidance: 'R$ 4,7M – R$ 5,6M',
      analysis_text: 'Aderência alta, mas complexidade elevada.',
    },
  },
  {
    id: 'pncp-2026-000377',
    source: 'PNCP',
    org: 'Prefeitura de Florianópolis',
    uf: 'SC',
    title: 'Serviço de conciliação contábil automatizada',
    budget: 880000,
    deadline: '2026-07-02',
    status: 'em_analise',
    score: {
      fit_score: 0.88, risk_score: 0.18, complexity_score: 0.35,
      recommendation: 'GO',
      key_requirements: ['Atestado de conciliação', 'CRF FGTS', 'CRC ativo'],
      pricing_guidance: 'R$ 690k – R$ 820k',
      analysis_text: 'Encaixe direto com ConciliaIA.',
    },
  },
  {
    id: 'bec-2026-11540',
    source: 'BEC-SP',
    org: 'SEFAZ São Paulo',
    uf: 'SP',
    title: 'Licenciamento de plataforma de governança corporativa',
    budget: 3200000,
    deadline: '2026-07-21',
    status: 'novo',
    score: {
      fit_score: 0.79, risk_score: 0.34, complexity_score: 0.55,
      recommendation: 'REVIEW',
      key_requirements: ['Capital social R$640k', 'Atestado 1.000 usuários'],
      pricing_guidance: 'R$ 2,6M – R$ 3,0M',
      analysis_text: 'BuildToValue Governance atende o escopo funcional.',
    },
  },
  {
    id: 'pncp-2026-000301',
    source: 'PNCP',
    org: 'Universidade Federal de Santa Catarina',
    uf: 'SC',
    title: 'Chatbot corporativo com IA para atendimento ao estudante',
    budget: 320000,
    deadline: '2026-06-30',
    status: 'em_analise',
    score: {
      fit_score: 0.86, risk_score: 0.15, complexity_score: 0.3,
      recommendation: 'GO',
      key_requirements: ['Atestado de chatbot/IA', 'CND federal'],
      pricing_guidance: 'R$ 250k – R$ 300k',
      analysis_text: 'Encaixe perfeito para btvChatCorp.',
    },
  },
]

const COLLECT_RUNS = [
  { run_id: 'mock-run-1', status: 'done', started_at: '2026-06-28T10:00:00Z', collected: 5, new_tenders: 2, scored: 5, alerts: 2, errors: [] },
]

const REPORT = {
  total: 5,
  por_recomendacao: { GO: 3, REVIEW: 2, SKIP: 0 },
  top: TENDERS.slice(0, 3).map(t => ({
    id: t.id, title: t.title, org: t.org, source: t.source,
    fit_score: t.score.fit_score, recommendation: t.score.recommendation,
    deadline: t.deadline, budget: t.budget,
  })),
  novas: 3,
  prazos_proximos: [
    { id: TENDERS[2].id, title: TENDERS[2].title, deadline: TENDERS[2].deadline },
    { id: TENDERS[0].id, title: TENDERS[0].title, deadline: TENDERS[0].deadline },
  ],
}

const CONFIG = {
  sources: ['pncp', 'comprasgov'],
  uf: 'SP,SC,PR,RS,MG,RJ,GO,DF',
  keywords: ['gestão documental', 'IA', 'compliance'],
  min_fit_alert: 0.7,
  collect_interval_hours: 24,
  scorer: 'openai',
}

const ALERTS = [
  { id: TENDERS[0].id, title: TENDERS[0].title, recommendation: 'GO', fit_score: 0.91, deadline: TENDERS[0].deadline },
  { id: TENDERS[2].id, title: TENDERS[2].title, recommendation: 'GO', fit_score: 0.88, deadline: TENDERS[2].deadline },
]

// ── V2 Mock data ──────────────────────────────────────────────────────────────

export const DOCUMENTS = [
  { id: 'doc-1', type: 'CND', subtype: 'Federal', name: 'CND Federal',
    file_name: 'cnd.pdf', mime_type: 'application/pdf',
    issue_date: '2026-01-01', expiry_date: '2026-12-31',
    is_valid: true, notes: null, created_at: '2026-01-01T00:00:00Z' },
  { id: 'doc-2', type: 'CRF', subtype: null, name: 'CRF FGTS',
    file_name: 'crf.pdf', mime_type: 'application/pdf',
    issue_date: '2026-01-01', expiry_date: '2026-06-01',
    is_valid: false, notes: null, created_at: '2026-01-01T00:00:00Z' },
]

export const CERTIFICATES = [
  { id: 'cert-1', client_name: 'Prefeitura SP',
    project_description: 'Gestão documental', start_date: '2024-01-01',
    end_date: '2024-12-31', project_value: 350000, scope: 'Software',
    file_name: 'atestado.pdf', mime_type: 'application/pdf',
    created_at: '2024-12-31T00:00:00Z' },
]

export const PROPOSALS = [
  { id: 'prop-1', tender_id: 'pncp-2026-000412',
    tender_title: 'Gestão documental', status: 'DRAFT',
    price_offered: 1980000, validity_days: 60, version: 1,
    notes: null, submitted_at: null },
  { id: 'prop-2', tender_id: 'cn-2026-90218',
    tender_title: 'IA generativa', status: 'SENT',
    price_offered: 4700000, validity_days: 30, version: 2,
    notes: null, submitted_at: '2026-06-01T00:00:00Z' },
]

export const CLIENTS = [
  { id: 'cli-1', name: 'TJ-PR', type: 'CLIENT', cnpj: '00.000.000/0001-91',
    contact_name: 'Ana Silva', email: 'ana@tjpr.gov.br', phone: '(41) 3200-0000',
    status: 'CLIENT', notes: null, created_at: '2026-01-01T00:00:00Z' },
  { id: 'cli-2', name: 'MGI', type: 'LEAD', cnpj: null,
    contact_name: null, email: null, phone: null,
    status: 'LEAD', notes: null, created_at: '2026-02-01T00:00:00Z' },
]

// ── Setup function ─────────────────────────────────────────────────────────────

export async function setupMocks(page: Page) {
  let currentConfig = { ...CONFIG }
  let collectRunStatus = 'done'
  const runs = [...COLLECT_RUNS]

  // ── Auth — RequireAuth requires /auth/me → 200 to not redirect ──
  await page.route('**/api/auth/me', route =>
    route.fulfill({ json: { username: 'admin' } })
  )
  await page.route('**/api/auth/login', route =>
    route.fulfill({ json: { user: { username: 'admin' } } })
  )
  await page.route('**/api/auth/logout', route =>
    route.fulfill({ json: { ok: true } })
  )

  // ── Documents ──
  await page.route('**/api/documents/**', route =>
    route.fulfill({ status: 204, body: '' })
  )
  await page.route('**/api/documents', async route => {
    if (route.request().method() === 'GET') route.fulfill({ json: DOCUMENTS })
    else route.fulfill({ json: DOCUMENTS[0] })
  })

  // ── Certificates ──
  await page.route('**/api/certificates/**', route =>
    route.fulfill({ status: 204, body: '' })
  )
  await page.route('**/api/certificates', async route => {
    if (route.request().method() === 'GET') route.fulfill({ json: CERTIFICATES })
    else route.fulfill({ json: CERTIFICATES[0] })
  })

  // ── Proposals ──
  await page.route('**/api/proposals/**', async route => {
    if (route.request().method() === 'PATCH')
      route.fulfill({ json: { ...PROPOSALS[0], status: 'SENT' } })
    else route.fulfill({ status: 204, body: '' })
  })
  await page.route('**/api/proposals', async route => {
    if (route.request().method() === 'GET') route.fulfill({ json: PROPOSALS })
    else route.fulfill({ status: 201, json: PROPOSALS[0] })
  })

  // ── Clients ──
  await page.route('**/api/clients/**', async route => {
    if (route.request().method() === 'PATCH') route.fulfill({ json: CLIENTS[0] })
    else route.fulfill({ status: 204, body: '' })
  })
  await page.route('**/api/clients', async route => {
    if (route.request().method() === 'GET') route.fulfill({ json: CLIENTS })
    else route.fulfill({ status: 201, json: CLIENTS[0] })
  })

  // ── Calc ──
  await page.route('**/api/calc', route =>
    route.fulfill({ json: {
      min_price: 714285.71, direct_cost: 250000, tax_burden: 30000,
      effective_margin: 0.15, anexo: 'III', fator_r: 0.35,
    } })
  )

  await page.route('**/api/health', route =>
    route.fulfill({ json: { status: 'ok' } })
  )

  await page.route('**/api/report', route =>
    route.fulfill({ json: REPORT })
  )

  await page.route('**/api/tenders', route => {
    const url = new URL(route.request().url())
    const rec = url.searchParams.get('recommendation')
    const q = url.searchParams.get('q') ?? ''
    let items = [...TENDERS]
    if (rec) items = items.filter(t => t.score.recommendation === rec)
    if (q) items = items.filter(t => t.title.toLowerCase().includes(q.toLowerCase()))
    route.fulfill({
      json: { items, total: items.length, page: 1, size: 20 },
    })
  })

  await page.route('**/api/tenders/**', route => {
    const url = route.request().url()
    const id = url.split('/api/tenders/')[1]?.split('?')[0]
    const tender = TENDERS.find(t => t.id === id)
    if (!tender) {
      route.fulfill({ status: 404, json: { detail: 'Not found' } })
    } else {
      route.fulfill({ json: { ...tender, raw_json: { mock: true } } })
    }
  })

  await page.route('**/api/config', async route => {
    if (route.request().method() === 'GET') {
      route.fulfill({ json: currentConfig })
    } else if (route.request().method() === 'PUT') {
      const body = JSON.parse(route.request().postData() ?? '{}')
      currentConfig = { ...currentConfig, ...body }
      route.fulfill({ json: currentConfig })
    } else {
      route.continue()
    }
  })

  // /collect with run_id suffix — must come BEFORE the base /collect route
  await page.route('**/api/collect/**', route => {
    const url = route.request().url()
    const runId = url.split('/api/collect/')[1]?.split('?')[0]
    if (runId === 'nao-existe') {
      route.fulfill({ status: 404, json: { detail: 'Not found' } })
    } else {
      route.fulfill({
        json: { run_id: runId ?? 'mock-run-1', status: collectRunStatus, collected: 5, new_tenders: 2, scored: 5, alerts: 2, errors: [] },
      })
    }
  })

  // /collect base — GET lists, POST starts
  await page.route('**/api/collect', async route => {
    if (route.request().method() === 'POST') {
      collectRunStatus = 'running'
      const newRun = { run_id: `mock-run-${runs.length + 1}`, status: 'running', started_at: new Date().toISOString(), collected: 0, new_tenders: 0, scored: 0, alerts: 0, errors: [] }
      runs.unshift(newRun)
      // Simulate quick finish
      setTimeout(() => {
        collectRunStatus = 'done'
        newRun.status = 'done'
        newRun.collected = 5
        newRun.new_tenders = 2
        newRun.scored = 5
        newRun.alerts = 2
      }, 300)
      route.fulfill({
        status: 202,
        json: { run_id: newRun.run_id, status: 'running' },
      })
    } else if (route.request().method() === 'GET') {
      route.fulfill({ json: runs })
    } else {
      route.continue()
    }
  })

  await page.route('**/api/alerts', route =>
    route.fulfill({ json: ALERTS })
  )
}

export const FIRST_TENDER_ID = TENDERS[0].id

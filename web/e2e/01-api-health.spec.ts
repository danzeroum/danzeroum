/**
 * E2E — Camada de API
 * Valida todos os endpoints do backend sem precisar de browser.
 */
import { test, expect } from '@playwright/test'
import { API } from './helpers'

test.describe('API health & contracts', () => {

  test.beforeAll(async ({ request }) => {
    const health = await request.get(`${API}/health`).catch(() => null)
    if (!health?.ok()) { test.skip(); return }
    await request.post(`${API}/auth/login`, {
      data: {
        username: process.env.AUTH_USERNAME ?? 'admin',
        password: process.env.AUTH_PASSWORD ?? 'test',
      },
    })
  })

  test('GET /health → 200 ok', async ({ request }) => {
    const r = await request.get(`${API}/health`)
    expect(r.ok()).toBeTruthy()
    const body = await r.json()
    expect(body.status).toBe('ok')
  })

  test('GET /report → shape correto', async ({ request }) => {
    const r = await request.get(`${API}/report`)
    expect(r.ok()).toBeTruthy()
    const body = await r.json()
    expect(body).toHaveProperty('total')
    expect(body).toHaveProperty('por_recomendacao')
    expect(body).toHaveProperty('top')
    expect(Array.isArray(body.top)).toBeTruthy()
  })

  test('GET /tenders → paginação e shape', async ({ request }) => {
    const r = await request.get(`${API}/tenders`)
    expect(r.ok()).toBeTruthy()
    const body = await r.json()
    expect(body).toHaveProperty('items')
    expect(body).toHaveProperty('total')
    expect(body).toHaveProperty('page')
    expect(body).toHaveProperty('size')
    expect(Array.isArray(body.items)).toBeTruthy()
  })

  test('GET /tenders?recommendation=GO → filtra corretamente', async ({ request }) => {
    const r = await request.get(`${API}/tenders?recommendation=GO`)
    expect(r.ok()).toBeTruthy()
    const body = await r.json()
    for (const item of body.items) {
      if (item.score) expect(item.score.recommendation).toBe('GO')
    }
  })

  test('GET /tenders?sort=deadline → aceita parâmetro de ordenação', async ({ request }) => {
    const r = await request.get(`${API}/tenders?sort=deadline`)
    expect(r.ok()).toBeTruthy()
    expect((await r.json())).toHaveProperty('items')
  })

  test('GET /tenders?sort=invalid → 422 validação', async ({ request }) => {
    const r = await request.get(`${API}/tenders?sort=invalid`)
    expect(r.status()).toBe(422)
  })

  test('GET /tenders/{id} inválido → 404', async ({ request }) => {
    const r = await request.get(`${API}/tenders/00000000-0000-0000-0000-000000000000`)
    expect(r.status()).toBe(404)
  })

  test('GET /config → shape correto', async ({ request }) => {
    const r = await request.get(`${API}/config`)
    expect(r.ok()).toBeTruthy()
    const body = await r.json()
    expect(body).toHaveProperty('sources')
    expect(body).toHaveProperty('keywords')
    expect(body).toHaveProperty('min_fit_alert')
    expect(body).toHaveProperty('collect_interval_hours')
    expect(Array.isArray(body.sources)).toBeTruthy()
    expect(Array.isArray(body.keywords)).toBeTruthy()
  })

  test('PUT /config → persiste e retorna atualizado', async ({ request }) => {
    const patch = { min_fit_alert: 0.55, collect_interval_hours: 12 }
    const put = await request.put(`${API}/config`, { data: patch })
    expect(put.ok()).toBeTruthy()
    const body = await put.json()
    expect(body.min_fit_alert).toBeCloseTo(0.55)
    expect(body.collect_interval_hours).toBeCloseTo(12)

    // Restaurar valores originais
    await request.put(`${API}/config`, { data: { min_fit_alert: 0.4, collect_interval_hours: 24 } })
  })

  test('POST /collect → 202 + run_id', async ({ request }) => {
    const r = await request.post(`${API}/collect`)
    expect(r.status()).toBe(202)
    const body = await r.json()
    expect(body).toHaveProperty('run_id')
    expect(body.status).toBe('running')
  })

  test('GET /collect/{run_id} → polling retorna status', async ({ request }) => {
    // Start a run
    const start = await request.post(`${API}/collect`)
    const { run_id } = await start.json()

    // Poll until done or timeout (max 20s)
    let status = 'running'
    for (let i = 0; i < 20 && status === 'running'; i++) {
      await new Promise(r => setTimeout(r, 1000))
      const poll = await request.get(`${API}/collect/${run_id}`)
      expect(poll.ok()).toBeTruthy()
      const body = await poll.json()
      status = body.status
      expect(['running', 'done', 'error']).toContain(status)
    }
    expect(['done', 'error']).toContain(status)
  })

  test('GET /collect/nao-existe → 404', async ({ request }) => {
    const r = await request.get(`${API}/collect/nao-existe`)
    expect(r.status()).toBe(404)
  })

  test('GET /alerts → lista (pode ser vazia)', async ({ request }) => {
    const r = await request.get(`${API}/alerts`)
    expect(r.ok()).toBeTruthy()
    expect(Array.isArray(await r.json())).toBeTruthy()
  })

})

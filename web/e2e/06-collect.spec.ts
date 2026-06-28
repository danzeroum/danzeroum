/**
 * E2E — Tela Coleta
 * Valida painel de run, log terminal, histórico e polling de status.
 */
import { test, expect } from '@playwright/test'
import { setupMocks } from './mocks'

test.describe('Coleta', () => {

  test.beforeEach(async ({ page }) => {
    await setupMocks(page)
    await page.goto('/coleta')
    await page.waitForLoadState('load')
    await expect(page.locator('h1', { hasText: 'Coleta de Dados' })).toBeVisible({ timeout: 10_000 })
  })

  test('Título "Coleta de Dados" visível', async ({ page }) => {
    await expect(page.locator('h1', { hasText: 'Coleta de Dados' })).toBeVisible()
  })

  test('Botão "Iniciar coleta" visível e habilitado', async ({ page }) => {
    const btn = page.locator('button', { hasText: 'Iniciar coleta' })
    await expect(btn).toBeVisible()
    await expect(btn).not.toBeDisabled()
  })

  test('Terminal de log visível (aguardando coleta)', async ({ page }) => {
    await expect(page.locator('text=aguardando coleta')).toBeVisible()
  })

  test('Painel "Histórico de execuções" visível', async ({ page }) => {
    await expect(page.locator('text=Histórico de execuções')).toBeVisible()
  })

  test('Iniciar coleta: botão dispara POST /collect', async ({ page }) => {
    const [request] = await Promise.all([
      page.waitForRequest(req => req.method() === 'POST' && req.url().includes('/collect')),
      page.locator('button', { hasText: 'Iniciar coleta' }).click(),
    ])
    expect(request.method()).toBe('POST')
  })

  test('Após coleta: botão muda estado para coletando/iniciando', async ({ page }) => {
    await page.locator('button', { hasText: 'Iniciar coleta' }).click()
    await expect(
      page.locator('button', { hasText: /Coletando|Iniciando/ })
    ).toBeVisible({ timeout: 5_000 })
  })

  test('Após coleta mock: log exibe linhas de resultado', async ({ page }) => {
    await page.locator('button', { hasText: 'Iniciar coleta' }).click()

    await expect(
      page.locator('button', { hasText: 'Iniciar coleta' })
    ).toBeVisible({ timeout: 15_000 })

    const logLines = page.locator('[style*="font-mono"] div')
    await expect(logLines.first()).toBeVisible()
  })

  test('Após coleta mock: histórico exibe ao menos uma entrada', async ({ page }) => {
    // History already loaded from mock GET /collect (shows COLLECT_RUNS)
    // The mock starts with 1 run, so #1 should be visible
    await expect(page.locator('text=#1')).toBeVisible({ timeout: 5_000 })
  })

})

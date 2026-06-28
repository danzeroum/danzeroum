/**
 * E2E — Tela Dashboard
 * Valida KPIs, tabela top oportunidades e prazos.
 */
import { test, expect } from '@playwright/test'
import { setupMocks } from './mocks'

test.describe('Dashboard', () => {

  test.beforeEach(async ({ page }) => {
    await setupMocks(page)
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('Título "Painel" está visível', async ({ page }) => {
    await expect(page.locator('h1', { hasText: 'Painel' })).toBeVisible()
  })

  test('4 KPI cards renderizados', async ({ page }) => {
    const cards = page.locator('.card.fade-in')
    await expect(cards).toHaveCount(4, { timeout: 10_000 })
  })

  test('KPI cards têm rótulos corretos', async ({ page }) => {
    await expect(page.locator('.eyebrow', { hasText: 'Total de editais' })).toBeVisible()
    await expect(page.locator('.eyebrow', { hasText: 'GO' })).toBeVisible()
    await expect(page.locator('.eyebrow', { hasText: 'Revisar' })).toBeVisible()
  })

  test('Seção "Top oportunidades" visível', async ({ page }) => {
    await expect(page.locator('text=Top oportunidades')).toBeVisible()
  })

  test('Seção "Por recomendação" visível', async ({ page }) => {
    await expect(page.locator('text=Por recomendação')).toBeVisible()
  })

  test('Seção "Prazos próximos" visível', async ({ page }) => {
    await expect(page.locator('text=Prazos próximos')).toBeVisible()
  })

  test('Tabela Top oportunidades tem cabeçalhos', async ({ page }) => {
    await expect(page.locator('th', { hasText: 'Objeto' })).toBeVisible()
    await expect(page.locator('th', { hasText: 'Fonte' })).toBeVisible()
    await expect(page.locator('th', { hasText: 'Aderência' })).toBeVisible()
    await expect(page.locator('th', { hasText: 'Reco' })).toBeVisible()
  })

  test('Tabela Top oportunidades tem dados do mock', async ({ page }) => {
    // mock returns 3 top tenders
    await expect(page.locator('.tbl tbody tr').first()).toBeVisible()
  })

  test('Clicar linha da tabela navega (se tiver dados)', async ({ page }) => {
    const rows = page.locator('.tbl tbody tr:not(:has(td[colspan]))')
    const count = await rows.count()
    if (count > 0) {
      await rows.first().click()
      await expect(page).toHaveURL(/\/oportunidades/)
    }
  })

})

/**
 * E2E — Tela Detalhe + Score
 * Valida gauges, requisitos, drawer raw JSON e botão voltar.
 */
import { test, expect } from '@playwright/test'
import { setupMocks, FIRST_TENDER_ID } from './mocks'

test.describe('Detalhe de Oportunidade', () => {

  test.beforeEach(async ({ page }) => {
    await setupMocks(page)
  })

  test('Rota inválida exibe mensagem de erro (não 500)', async ({ page }) => {
    await page.goto('/oportunidades/tender-nao-existe')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('text=500')).not.toBeVisible()
    await expect(
      page.locator('text=Edital não encontrado').or(page.locator('[style*="danger"]'))
    ).toBeVisible({ timeout: 8_000 })
  })

  test('Tela de detalhe carrega para tender mockado', async ({ page }) => {
    await page.goto(`/oportunidades/${FIRST_TENDER_ID}`)
    await page.waitForLoadState('networkidle')

    await expect(page.locator('h1.h-page')).toBeVisible({ timeout: 10_000 })
    await expect(page.locator('button', { hasText: '← Voltar' })).toBeVisible()
    await expect(page.locator('text=Dados do Edital')).toBeVisible()
  })

  test('Scoring card visível com gauges', async ({ page }) => {
    await page.goto(`/oportunidades/${FIRST_TENDER_ID}`)
    await page.waitForLoadState('networkidle')
    await expect(page.locator('text=500')).not.toBeVisible()
    await expect(page.locator('text=Análise de Scoring')).toBeVisible()
    await expect(page.locator('svg circle[stroke-dashoffset]').first()).toBeVisible()
    // Use exact label class to avoid strict mode violations
    await expect(page.locator('.field-label', { hasText: 'Aderência' }).first()).toBeVisible()
    await expect(page.locator('.field-label', { hasText: 'Risco' })).toBeVisible()
    await expect(page.locator('.field-label', { hasText: 'Complexidade' })).toBeVisible()
  })

  test('Drawer JSON bruto: abre e fecha com botão X', async ({ page }) => {
    await page.goto(`/oportunidades/${FIRST_TENDER_ID}`)
    await page.waitForLoadState('networkidle')

    const drawerBtn = page.locator('button', { hasText: /JSON bruto/ })
    await expect(drawerBtn).toBeVisible()
    await drawerBtn.click()

    await expect(page.locator('.drawer')).toBeVisible()
    await expect(page.locator('.drawer h2', { hasText: 'JSON bruto' })).toBeVisible()
    await expect(page.locator('.drawer pre')).toBeVisible()

    await page.locator('.drawer .icon-btn').click()
    await expect(page.locator('.drawer')).not.toBeVisible()
  })

  test('Drawer JSON bruto: fechar pelo scrim', async ({ page }) => {
    await page.goto(`/oportunidades/${FIRST_TENDER_ID}`)
    await page.waitForLoadState('networkidle')

    await page.locator('button', { hasText: /JSON bruto/ }).click()
    await expect(page.locator('.drawer')).toBeVisible()

    // Dispatch click directly since the drawer scroll container may overlap
    await page.evaluate(() => {
      const scrim = document.querySelector('.drawer-scrim') as HTMLElement
      scrim?.click()
    })
    await expect(page.locator('.drawer')).not.toBeVisible()
  })

  test('Botão ← Voltar retorna para /oportunidades', async ({ page }) => {
    await page.goto(`/oportunidades/${FIRST_TENDER_ID}`)
    await page.waitForLoadState('networkidle')

    await page.locator('button', { hasText: '← Voltar' }).click()
    await expect(page).toHaveURL(/\/oportunidades$/)
  })

})

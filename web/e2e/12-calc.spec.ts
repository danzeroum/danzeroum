/**
 * E2E — Tela Calculadora Fator R / Simples Nacional (V2)
 */
import { test, expect } from '@playwright/test'
import { setupMocks } from './mocks'

test.describe('Calculadora Fator R', () => {

  test.beforeEach(async ({ page }) => {
    await setupMocks(page)
    await page.goto('/calculadora')
    await page.waitForLoadState('networkidle')
  })

  test('Título "Calculadora" visível', async ({ page }) => {
    await expect(page.locator('h1', { hasText: 'Calculadora' })).toBeVisible()
  })

  test('4 sliders de entrada presentes', async ({ page }) => {
    const sliders = page.locator('input[type="range"]')
    await expect(sliders).toHaveCount(4)
  })

  test('Botão de calcular visível', async ({ page }) => {
    await expect(page.locator('button', { hasText: /Calcul/ })).toBeVisible()
  })

  test('Clicar em calcular exibe resultado: "Anexo III"', async ({ page }) => {
    await page.locator('button', { hasText: /Calcul/ }).click()
    await expect(page.locator('text=Anexo III')).toBeVisible({ timeout: 5000 })
  })

  test('Resultado exibe "Preço mínimo"', async ({ page }) => {
    await page.locator('button', { hasText: /Calcul/ }).click()
    await expect(page.locator('text=Preço mínimo')).toBeVisible({ timeout: 5000 })
  })

  test('Resultado exibe Fator R formatado como percentual', async ({ page }) => {
    await page.locator('button', { hasText: /Calcul/ }).click()
    // fator_r: 0.35 → "35.0%"
    await expect(page.locator('text=35.0%')).toBeVisible({ timeout: 5000 })
  })

})

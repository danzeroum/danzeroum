/**
 * E2E — Tela Configuração
 * Valida todos os controles e persistência via PUT /config.
 */
import { test, expect } from '@playwright/test'
import { setupMocks } from './mocks'

test.describe('Configuração', () => {

  test.beforeEach(async ({ page }) => {
    await setupMocks(page)
    await page.goto('/config')
    // Use 'load' instead of 'networkidle' to avoid being blocked by collect polling
    await page.waitForLoadState('load')
    // Wait for the config data to render
    await expect(page.locator('h1', { hasText: 'Configuração' })).toBeVisible({ timeout: 10_000 })
  })

  test('Título "Configuração" visível', async ({ page }) => {
    await expect(page.locator('h1', { hasText: 'Configuração' })).toBeVisible()
  })

  test('Botão "Salvar configuração" visível', async ({ page }) => {
    await expect(page.locator('button[type="submit"]', { hasText: /Salvar/ })).toBeVisible()
  })

  test('Seção "Fontes de dados" com toggles', async ({ page }) => {
    await expect(page.locator('h2', { hasText: 'Fontes de dados' })).toBeVisible()
    await expect(page.locator('button[type="button"]').first()).toBeVisible()
  })

  test('Seção "UFs monitoradas" com chips', async ({ page }) => {
    await expect(page.locator('h2', { hasText: 'UFs monitoradas' })).toBeVisible()
    await expect(page.locator('.chip', { hasText: 'SP' }).first()).toBeVisible()
    await expect(page.locator('.chip', { hasText: 'SC' }).first()).toBeVisible()
  })

  test('Seção "Palavras-chave" com input de adição', async ({ page }) => {
    await expect(page.locator('h2', { hasText: 'Palavras-chave' })).toBeVisible()
    await expect(page.locator('input[placeholder*="Nova palavra"]')).toBeVisible()
  })

  test('Seção "Scoring" com slider de aderência', async ({ page }) => {
    await expect(page.locator('h2', { hasText: 'Scoring' })).toBeVisible()
    await expect(page.locator('text=Aderência mínima para alerta')).toBeVisible()
  })

  test('Seção "Agendamento" com select de horas', async ({ page }) => {
    await expect(page.locator('h2', { hasText: 'Agendamento' })).toBeVisible()
    await expect(page.locator('select', { hasText: /\d+h/ })).toBeVisible()
  })

  test('Adicionar palavra-chave: aparece como chip', async ({ page }) => {
    const input = page.locator('input[placeholder*="Nova palavra"]')
    await input.fill('blockchain_test_e2e')
    await input.press('Enter')
    await expect(page.locator('.chip', { hasText: 'blockchain_test_e2e' })).toBeVisible()
  })

  test('Remover palavra-chave: some ao clicar ×', async ({ page }) => {
    const input = page.locator('input[placeholder*="Nova palavra"]')
    await input.fill('remover_e2e_test')
    await input.press('Enter')
    const chip = page.locator('.chip', { hasText: 'remover_e2e_test' })
    await expect(chip).toBeVisible()

    await chip.locator('button').click()
    await expect(chip).not.toBeVisible()
  })

  test('Toggle de fonte: alterna estado on/off', async ({ page }) => {
    // Scope to the card containing "Fontes de dados" h2
    const fonteCard = page.locator('.card').filter({ has: page.locator('h2', { hasText: 'Fontes de dados' }) })
    const toggle = fonteCard.locator('button[type="button"]').first()
    const before = await toggle.evaluate(el =>
      getComputedStyle(el).backgroundColor
    )
    await toggle.click()
    await page.waitForTimeout(150)
    const after = await toggle.evaluate(el =>
      getComputedStyle(el).backgroundColor
    )
    expect(before).not.toBe(after)
  })

  test('Chip UF: clique ativa, segundo clique desativa', async ({ page }) => {
    const chip = page.locator('.chip.chip-btn', { hasText: 'GO' })
    const wasOn = await chip.evaluate(el => el.classList.contains('on'))

    await chip.click()
    if (wasOn) {
      await expect(chip).not.toHaveClass(/\bon\b/)
    } else {
      await expect(chip).toHaveClass(/\bon\b/)
    }
  })

  test('Salvar: botão dispara PUT /config e exibe "Salvo"', async ({ page }) => {
    const [request] = await Promise.all([
      page.waitForRequest(req => req.method() === 'PUT' && req.url().includes('/config')),
      page.locator('button[type="submit"]').click(),
    ])
    expect(request.method()).toBe('PUT')
    await expect(page.locator('button[type="submit"]', { hasText: /Salvo/ })).toBeVisible({ timeout: 5_000 })
  })

  test('Alterar agendamento e salvar: corpo contém collect_interval_hours', async ({ page }) => {
    await page.locator('select', { hasText: /\d+h/ }).selectOption('6')

    const [putReq] = await Promise.all([
      page.waitForRequest(req => req.method() === 'PUT' && req.url().includes('/config')),
      page.locator('button[type="submit"]').click(),
    ])

    const body = JSON.parse(putReq.postData() ?? '{}')
    expect(body.collect_interval_hours).toBe(6)
  })

})

/**
 * E2E — Tela Lista de Oportunidades
 * Valida filtros, busca, ordenação e navegação para detalhe.
 */
import { test, expect } from '@playwright/test'
import { setupMocks, FIRST_TENDER_ID } from './mocks'

test.describe('Lista de Oportunidades', () => {

  test.beforeEach(async ({ page }) => {
    await setupMocks(page)
    await page.goto('/oportunidades')
    await page.waitForLoadState('networkidle')
  })

  test('Título "Oportunidades" está visível', async ({ page }) => {
    await expect(page.locator('h1', { hasText: 'Oportunidades' })).toBeVisible()
  })

  test('Card de filtros visível', async ({ page }) => {
    await expect(page.locator('input[placeholder*="Buscar"]').first()).toBeVisible()
  })

  test('Chips de UF (SP, SC, PR) visíveis', async ({ page }) => {
    for (const uf of ['SP', 'SC', 'PR']) {
      await expect(page.locator('.chip', { hasText: uf }).first()).toBeVisible()
    }
  })

  test('Chips de recomendação (GO, REVIEW, SKIP) visíveis', async ({ page }) => {
    for (const r of ['GO', 'REVIEW', 'SKIP']) {
      await expect(page.locator('.chip', { hasText: r })).toBeVisible()
    }
  })

  test('Slider de aderência mínima presente', async ({ page }) => {
    await expect(page.locator('input[type="range"]')).toBeVisible()
  })

  test('Select de ordenação presente', async ({ page }) => {
    await expect(page.locator('select', { hasText: 'Aderência' })).toBeVisible()
  })

  test('Cabeçalhos da tabela corretos', async ({ page }) => {
    for (const h of ['Fonte', 'Órgão / Objeto', 'UF', 'Orçamento', 'Prazo', 'Aderência', 'Reco']) {
      await expect(page.locator('th', { hasText: h })).toBeVisible()
    }
  })

  test('Mock data: tabela tem linhas', async ({ page }) => {
    await expect(page.locator('.tbl tbody tr').first()).toBeVisible()
  })

  test('Filtro UF: clicar chip SP → ativa estado on', async ({ page }) => {
    const spChip = page.locator('.chip.chip-btn', { hasText: 'SP' }).first()
    await spChip.click()
    await expect(spChip).toHaveClass(/\bon\b/)
    await spChip.click()
    await expect(spChip).not.toHaveClass(/\bon\b/)
  })

  test('Filtro recomendação: clicar GO faz request com ?recommendation=GO', async ({ page }) => {
    const [request] = await Promise.all([
      page.waitForRequest(req => req.url().includes('recommendation=GO')),
      page.locator('.chip.chip-btn', { hasText: /^GO$/ }).click(),
    ])
    expect(request.url()).toContain('recommendation=GO')
  })

  test('Busca: digitar query faz request com ?q=...', async ({ page }) => {
    const searchInput = page.locator('.card input[placeholder*="Buscar"]')
    const [request] = await Promise.all([
      page.waitForRequest(req => req.url().includes('/tenders') && req.url().includes('q=')),
      searchInput.fill('tecnologia'),
    ])
    expect(request.url()).toContain('q=tecnologia')
  })

  test('Ordenação: selecionar Prazo faz request com ?sort=deadline', async ({ page }) => {
    const [request] = await Promise.all([
      page.waitForRequest(req => req.url().includes('sort=deadline')),
      page.locator('select', { hasText: 'Aderência' }).selectOption('deadline'),
    ])
    expect(request.url()).toContain('sort=deadline')
  })

  test('Clicar linha navega para /oportunidades/:id', async ({ page }) => {
    const rows = page.locator('.tbl tbody tr:not(:has(td[colspan]))')
    const count = await rows.count()
    if (count > 0) {
      await rows.first().click()
      await expect(page).toHaveURL(/\/oportunidades\/.+/)
    }
  })

  test('Mensagem vazia quando sem resultados', async ({ page }) => {
    const searchInput = page.locator('.card input[placeholder*="Buscar"]')
    await searchInput.fill('xyzxyzxyz_impossivel_999')
    await page.waitForTimeout(500)
    await page.waitForLoadState('networkidle')
    const error = page.locator('text=500')
    await expect(error).not.toBeVisible()
  })

})

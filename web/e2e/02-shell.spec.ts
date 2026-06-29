/**
 * E2E — Shell da aplicação (Sidebar + Topbar)
 * Valida navegação, dark mode, busca global e botão Coletar.
 */
import { test, expect } from '@playwright/test'
import { setupMocks } from './mocks'

test.describe('Shell — Sidebar e Topbar', () => {

  test.beforeEach(async ({ page }) => {
    await setupMocks(page)
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('Sidebar está visível com grupos de navegação', async ({ page }) => {
    await expect(page.locator('.sidebar')).toBeVisible()
    await expect(page.locator('text=Operação')).toBeVisible()
    await expect(page.locator('text=Sistema')).toBeVisible()
  })

  test('Topbar está visível', async ({ page }) => {
    await expect(page.locator('.topbar')).toBeVisible()
  })

  test('Navegação: Painel → ativo na raiz', async ({ page }) => {
    const painelBtn = page.locator('.nav-item', { hasText: 'Painel' })
    await expect(painelBtn).toHaveClass(/active/)
  })

  test('Navegação: clique em Oportunidades → vai para /oportunidades', async ({ page }) => {
    await page.locator('.nav-item', { hasText: 'Oportunidades' }).click()
    await expect(page).toHaveURL(/\/oportunidades/)
    await expect(page.locator('.nav-item', { hasText: 'Oportunidades' })).toHaveClass(/active/)
  })

  test('Navegação: clique em Coleta → vai para /coleta', async ({ page }) => {
    await page.locator('.nav-item', { hasText: 'Coleta' }).click()
    await expect(page).toHaveURL(/\/coleta/)
  })

  test('Navegação: clique em Configuração → vai para /config', async ({ page }) => {
    await page.locator('.nav-item', { hasText: 'Configuração' }).click()
    await expect(page).toHaveURL(/\/config/)
  })

  test('Dark mode: toggle aplica html.dark e persiste em localStorage', async ({ page }) => {
    // Ensure light mode first
    await page.evaluate(() => {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('dz-theme', 'light')
    })

    const html = page.locator('html')
    await expect(html).not.toHaveClass(/dark/)

    // Toggle to dark
    await page.locator('.topbar .icon-btn').last().click()
    await expect(html).toHaveClass(/dark/)

    // Verify localStorage persisted
    const stored = await page.evaluate(() => localStorage.getItem('dz-theme'))
    expect(stored).toBe('dark')

    // Toggle back to light
    await page.locator('.topbar .icon-btn').last().click()
    await expect(html).not.toHaveClass(/dark/)
  })

  test('Busca global: digitar e submeter redireciona para /oportunidades', async ({ page }) => {
    const input = page.locator('.topbar input[placeholder*="Buscar"]')
    await input.fill('software')
    await input.press('Enter')
    await expect(page).toHaveURL(/\/oportunidades/)
  })

  test('Botão Coletar no Topbar: visível e clicável', async ({ page }) => {
    const btn = page.locator('.topbar button', { hasText: /Coletar|Iniciando/ })
    await expect(btn).toBeVisible()
    await btn.click()
    await expect(page).toHaveURL(/\/coleta/)
  })

  test('Sino (bell) no Topbar: clique vai para /coleta', async ({ page }) => {
    const bell = page.locator('.topbar .icon-btn').nth(0)
    await bell.click()
    await expect(page).toHaveURL(/\/coleta/)
  })

  test('Sidebar grupo Empresa: Documentos, Atestados, CRM visíveis', async ({ page }) => {
    await expect(page.locator('text=Empresa')).toBeVisible()
    await expect(page.locator('.nav-item', { hasText: 'Documentos' })).toBeVisible()
    await expect(page.locator('.nav-item', { hasText: 'Atestados' })).toBeVisible()
    await expect(page.locator('.nav-item', { hasText: 'CRM' })).toBeVisible()
  })

  test('Sidebar grupo Operação: Propostas e Calculadora visíveis', async ({ page }) => {
    await expect(page.locator('.nav-item', { hasText: 'Propostas' })).toBeVisible()
    await expect(page.locator('.nav-item', { hasText: 'Calculadora' })).toBeVisible()
  })

  test('Topbar: botão de logout (ícone sair) visível', async ({ page }) => {
    await expect(page.locator('.topbar .icon-btn').last()).toBeVisible()
  })

})

/**
 * E2E — Tela Atestados Técnicos (V2)
 * Valida grid de cards e modal de criação.
 */
import { test, expect } from '@playwright/test'
import { setupMocks } from './mocks'

test.describe('Atestados Técnicos', () => {

  test.beforeEach(async ({ page }) => {
    await setupMocks(page)
    await page.goto('/atestados')
    await page.waitForLoadState('networkidle')
  })

  test('Título "Atestados Técnicos" visível', async ({ page }) => {
    await expect(page.locator('h1', { hasText: 'Atestados Técnicos' })).toBeVisible()
  })

  test('Botão "+ Novo atestado" visível', async ({ page }) => {
    await expect(page.locator('button', { hasText: /Novo atestado/ })).toBeVisible()
  })

  test('Card com client_name "Prefeitura SP" do mock renderizado', async ({ page }) => {
    await expect(page.locator('text=Prefeitura SP')).toBeVisible()
  })

  test('Botão × (excluir) visível no card', async ({ page }) => {
    // O botão de exclusão usa fontSize '1.1rem' e texto ×
    await expect(page.locator('button', { hasText: '×' }).first()).toBeVisible()
  })

  test('Modal de novo atestado abre ao clicar no botão', async ({ page }) => {
    await page.locator('button', { hasText: /Novo atestado/ }).click()
    await expect(page.locator('h2', { hasText: /Novo atestado técnico/ })).toBeVisible()
    await expect(page.locator('button[type="submit"]', { hasText: /Salvar/ })).toBeVisible()
  })

})

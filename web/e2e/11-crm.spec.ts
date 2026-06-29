/**
 * E2E — Tela CRM (Kanban 3 colunas, V2)
 */
import { test, expect } from '@playwright/test'
import { setupMocks } from './mocks'

test.describe('CRM — Clientes', () => {

  test.beforeEach(async ({ page }) => {
    await setupMocks(page)
    await page.goto('/crm')
    await page.waitForLoadState('networkidle')
  })

  test('Título "CRM — Clientes" visível', async ({ page }) => {
    await expect(page.locator('h1', { hasText: 'CRM' })).toBeVisible()
  })

  test('Botão "+ Novo cliente" visível', async ({ page }) => {
    await expect(page.locator('button', { hasText: /Novo cliente/ })).toBeVisible()
  })

  test('Coluna "Lead" visível', async ({ page }) => {
    await expect(page.locator('text=Lead').first()).toBeVisible()
  })

  test('Coluna "Cliente" visível', async ({ page }) => {
    await expect(page.locator('text=Cliente').first()).toBeVisible()
  })

  test('Coluna "Arquivado" visível', async ({ page }) => {
    await expect(page.locator('text=Arquivado')).toBeVisible()
  })

  test('Card "TJ-PR" (status CLIENT) renderizado', async ({ page }) => {
    await expect(page.locator('text=TJ-PR')).toBeVisible()
  })

  test('Card "MGI" (status LEAD) renderizado', async ({ page }) => {
    await expect(page.locator('text=MGI')).toBeVisible()
  })

  test('Modal de novo cliente abre ao clicar no botão', async ({ page }) => {
    await page.locator('button', { hasText: /Novo cliente/ }).click()
    await expect(page.locator('button[type="submit"]', { hasText: /Salvar/ })).toBeVisible()
    await expect(page.locator('button', { hasText: /Cancelar/ })).toBeVisible()
  })

})

/**
 * E2E — Tela Documentos (V2)
 * Valida listagem, chips de status e modal de upload.
 */
import { test, expect } from '@playwright/test'
import { setupMocks } from './mocks'

test.describe('Documentos', () => {

  test.beforeEach(async ({ page }) => {
    await setupMocks(page)
    await page.goto('/documentos')
    // Wait past React Query loading state — data must render before assertions
    await expect(page.locator('h1', { hasText: 'Documentos' })).toBeVisible()
    await expect(page.locator('table').or(page.locator('text=Nenhum documento'))).toBeVisible({ timeout: 10_000 })
  })

  test('Título "Documentos" visível', async ({ page }) => {
    await expect(page.locator('h1', { hasText: 'Documentos' })).toBeVisible()
  })

  test('Botão "+ Novo documento" visível', async ({ page }) => {
    await expect(page.locator('button', { hasText: /Novo documento/ })).toBeVisible()
  })

  test('Tabela lista CND Federal do mock', async ({ page }) => {
    await expect(page.locator('text=CND')).toBeVisible()
  })

  test('Tabela lista CRF do mock', async ({ page }) => {
    await expect(page.locator('text=CRF')).toBeVisible()
  })

  test('Status "Válido" visível (doc-1 is_valid=true, expiry 2026-12-31)', async ({ page }) => {
    await expect(page.locator('text=Válido')).toBeVisible()
  })

  test('Status "Vencido" visível (doc-2 is_valid=false)', async ({ page }) => {
    await expect(page.locator('text=Vencido')).toBeVisible()
  })

  test('Botão × (excluir) visível por linha', async ({ page }) => {
    const delBtns = page.locator('button.btn-sm')
    await expect(delBtns.first()).toBeVisible()
  })

  test('Modal de novo documento abre ao clicar no botão', async ({ page }) => {
    await page.locator('button', { hasText: /Novo documento/ }).click()
    await expect(page.locator('button[type="submit"]', { hasText: /Salvar/ })).toBeVisible()
    await expect(page.locator('button', { hasText: /Cancelar/ })).toBeVisible()
  })

})

/**
 * E2E — Tela Propostas (Kanban 6 colunas, V2)
 */
import { test, expect } from '@playwright/test'
import { setupMocks } from './mocks'

test.describe('Propostas', () => {

  test.beforeEach(async ({ page }) => {
    await setupMocks(page)
    await page.goto('/propostas')
    // Wait past React Query loading state (isLoading replaces kanban with skeleton)
    await expect(page.locator('h1', { hasText: 'Propostas' })).toBeVisible()
    await expect(page.locator('text=Rascunho')).toBeVisible({ timeout: 10_000 })
  })

  test('Título "Propostas" visível', async ({ page }) => {
    await expect(page.locator('h1', { hasText: 'Propostas' })).toBeVisible()
  })

  test('Coluna "Rascunho" (DRAFT) visível', async ({ page }) => {
    await expect(page.locator('text=Rascunho')).toBeVisible()
  })

  test('Coluna "Enviada" (SENT) visível', async ({ page }) => {
    await expect(page.locator('text=Enviada')).toBeVisible()
  })

  test('Coluna "Em análise" (UNDER_REVIEW) visível', async ({ page }) => {
    await expect(page.locator('text=Em análise')).toBeVisible()
  })

  test('Coluna "Ganha" (WIN) visível', async ({ page }) => {
    await expect(page.locator('text=Ganha')).toBeVisible()
  })

  test('Coluna "Perdida" (LOST) visível', async ({ page }) => {
    await expect(page.locator('text=Perdida')).toBeVisible()
  })

  test('Coluna "Inabilitada" (DISQUALIFIED) visível', async ({ page }) => {
    await expect(page.locator('text=Inabilitada')).toBeVisible()
  })

  test('Card DRAFT com título "Gestão documental" presente', async ({ page }) => {
    await expect(page.locator('text=Gestão documental')).toBeVisible()
  })

  test('Card SENT com título "IA generativa" presente', async ({ page }) => {
    await expect(page.locator('text=IA generativa')).toBeVisible()
  })

  test('Botão "Remover" visível em card', async ({ page }) => {
    await expect(page.locator('button', { hasText: 'Remover' }).first()).toBeVisible()
  })

})

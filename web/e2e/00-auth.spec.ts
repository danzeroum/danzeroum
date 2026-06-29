/**
 * E2E — Autenticação (V3)
 * Valida tela de login, redirect sem auth, mensagem de erro e logout.
 */
import { test, expect } from '@playwright/test'
import { setupMocks } from './mocks'

test.describe('Autenticação', () => {

  test('Sem auth → redireciona para /login', async ({ page }) => {
    // Sem setupMocks → /auth/me retorna 401 real (ou network error) → RequireAuth redireciona
    await page.route('**/api/auth/me', route =>
      route.fulfill({ status: 401, json: { detail: 'Não autenticado' } })
    )
    await page.goto('/')
    await expect(page).toHaveURL(/\/login/, { timeout: 5000 })
  })

  test('Tela login: campos username, password e botão Entrar visíveis', async ({ page }) => {
    await page.goto('/login')
    await expect(page.locator('input[autocomplete="username"]')).toBeVisible()
    await expect(page.locator('input[autocomplete="current-password"]')).toBeVisible()
    await expect(page.locator('button[type="submit"]')).toBeVisible()
  })

  test('Credenciais inválidas mostram mensagem de erro', async ({ page }) => {
    await page.route('**/api/auth/login', route =>
      route.fulfill({ status: 401, json: { detail: 'Credenciais inválidas' } })
    )
    await page.goto('/login')
    await page.locator('input[autocomplete="username"]').fill('admin')
    await page.locator('input[autocomplete="current-password"]').fill('errado')
    await page.locator('button[type="submit"]').click()
    await expect(page.locator('text=Usuário ou senha inválidos')).toBeVisible()
  })

  test('Logout: botão no Topbar redireciona para /login', async ({ page }) => {
    await setupMocks(page)
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    // Sobrescrever /auth/me para 401 após logout (simula cookie expirado)
    await page.route('**/api/auth/me', route =>
      route.fulfill({ status: 401, json: { detail: 'Não autenticado' } })
    )
    const logoutBtn = page.locator('.topbar .icon-btn').last()
    await expect(logoutBtn).toBeVisible()
    await logoutBtn.click()
    await expect(page).toHaveURL(/\/login/, { timeout: 5000 })
  })

})

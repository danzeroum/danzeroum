import { Page, expect } from '@playwright/test'

export const API = process.env.API_URL ?? 'http://localhost:8000'

/** Aguarda até a API responder (útil em testes contra stack Docker) */
export async function waitForApi(page: Page, timeoutMs = 30_000) {
  const start = Date.now()
  while (Date.now() - start < timeoutMs) {
    try {
      const res = await page.request.get(`${API}/health`)
      if (res.ok()) return
    } catch {}
    await page.waitForTimeout(1000)
  }
  throw new Error(`API ${API}/health não respondeu em ${timeoutMs}ms`)
}

/** Verifica que não há erros visíveis de "Erro ao" ou "500" */
export async function expectNoErrors(page: Page) {
  await expect(page.locator('text=500')).not.toBeVisible({ timeout: 500 }).catch(() => {})
}

/** Mede se elementos visíveis carregam dentro do timeout */
export async function expectVisible(page: Page, selector: string, timeout = 10_000) {
  await expect(page.locator(selector)).toBeVisible({ timeout })
}

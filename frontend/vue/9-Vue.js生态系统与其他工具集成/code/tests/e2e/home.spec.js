// @ts-check
const { test, expect } = require('@playwright/test')

test('has title', async ({ page }) => {
  await page.goto('/')

  // Expect a title "to contain" a substring.
  await expect(page).toHaveTitle(/Vue.js生态系统/)
})

test('get started link', async ({ page }) => {
  await page.goto('/')

  // Click the get started link.
  await page.getByRole('link', { name: '关于' }).click()

  // Expects the URL to contain about.
  await expect(page).toHaveURL(/.*about/)
})

test('navigation between pages', async ({ page }) => {
  await page.goto('/')
  
  // Check that we are on the home page
  await expect(page.locator('h1')).toContainText('欢迎来到Vue.js生态系统示例')
  
  // Navigate to About page
  await page.click('a[href="/about"]')
  await expect(page.locator('h1')).toContainText('关于我们')
  
  // Navigate back to Home page
  await page.click('a[href="/"]')
  await expect(page.locator('h1')).toContainText('欢迎来到Vue.js生态系统示例')
})
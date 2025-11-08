// advanced-locator.spec.js
const { test, expect } = require('@playwright/test');

test('高级定位器测试', async ({ page }) => {
  await page.goto('/advanced-elements');
  
  // CSS选择器高级用法
  await expect(page.locator('[data-testid="submit-button"]')).toBeVisible();
  await expect(page.locator('button:enabled')).toBeEnabled();
  
  // XPath选择器
  await expect(page.locator('xpath=//button[@id="submit"]')).toBeVisible();
  
  // 文本选择器
  await expect(page.locator('text=Submit')).toBeVisible();
  
  // 定位器链式操作
  const form = page.locator('form#registration');
  await expect(form.locator('input#username')).toBeVisible();
  
  // 元素状态检查
  const element = page.locator('#dynamic-element');
  await expect(element).toBeVisible();
  await expect(element).toBeEnabled();
});
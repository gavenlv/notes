const { test, expect } = require('@playwright/test');

test('我的第一个Playwright测试', async ({ page }) => {
  // 导航到网页
  await page.goto('https://playwright.dev');
  
  // 断言页面标题
  await expect(page).toHaveTitle(/Playwright/);
  
  // 点击"Get started"链接
  await page.click('text=Get started');
  
  // 断言URL包含intro
  await expect(page).toHaveURL(/.*intro/);
});
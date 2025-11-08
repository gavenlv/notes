const { test, expect } = require('@playwright/test');

test('验证Playwright环境', async ({ page }) => {
  // 检查是否能访问Google
  await page.goto('https://www.google.com');
  
  // 检查页面标题
  const title = await page.title();
  console.log('页面标题:', title);
  
  // 断言标题包含Google
  await expect(title).toContain('Google');
  
  // 检查搜索框是否存在
  const searchBox = await page.$('[name="q"]');
  await expect(searchBox).toBeTruthy();
});
const { test, expect } = require('@playwright/test');

test('在不同浏览器中测试百度', async ({ page }) => {
  // 导航到百度
  await page.goto('https://www.baidu.com');
  
  // 检查页面标题
  await expect(page).toHaveTitle(/百度一下/);
  
  // 检查搜索框
  const searchInput = page.locator('#kw');
  await expect(searchInput).toBeVisible();
  
  // 输入搜索词
  await searchInput.fill('Playwright');
  
  // 点击搜索按钮
  await page.click('#su');
  
  // 等待结果页面加载
  await page.waitForSelector('#content_left');
  
  // 检查结果中是否包含Playwright相关内容
  const firstResult = page.locator('.result:first-child');
  await expect(firstResult).toContainText('Playwright');
});
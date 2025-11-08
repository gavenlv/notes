// dynamic-content-test.spec.js
const { test, expect } = require('@playwright/test');
const { DynamicContentPage } = require('../pages/dynamic-content-page');

test('动态内容加载测试', async ({ page }) => {
  const dynamicPage = new DynamicContentPage(page);
  
  // 导航到页面
  await page.goto('/dynamic-content');
  
  // 触发内容加载
  await dynamicPage.loadContent();
  
  // 验证内容已加载
  await expect(dynamicPage.contentArea).toContainText('加载完成');
  
  // 等待进度条完成
  await dynamicPage.waitForProgressComplete();
  
  // 验证进度条状态
  const progressValue = await page.getAttribute('#progress', 'value');
  expect(progressValue).toBe('100');
});
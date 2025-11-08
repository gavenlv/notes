// 最佳实践：使用适当的等待策略
const { test, expect } = require('@playwright/test');

test.describe('等待策略最佳实践', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://example.com');
  });

  test('应该使用自动等待而不是固定延时', async ({ page }) => {
    // ❌ 不好的做法：使用固定的延时
    // await page.waitForTimeout(3000);
    
    // ✅ 好的做法：使用Playwright的自动等待
    const button = page.locator('[data-testid="dynamic-button"]');
    await button.click(); // Playwright会自动等待元素可点击
    
    // ✅ 好的做法：使用明确的等待条件
    const result = page.locator('[data-testid="result"]');
    await result.waitFor({ state: 'visible', timeout: 10000 });
    await expect(result).toContainText('操作完成');
  });

  test('应该使用网络空闲等待页面加载', async ({ page }) => {
    // ✅ 好的做法：等待网络空闲
    await page.goto('https://example.com/data-heavy-page', {
      waitUntil: 'networkidle'
    });
    
    // 现在页面完全加载，可以安全地进行操作
    const dataElement = page.locator('[data-testid="data-loaded"]');
    await expect(dataElement).toBeVisible();
  });

  test('应该使用DOM内容加载等待', async ({ page }) => {
    // ✅ 好的做法：等待DOM内容加载完成
    await page.goto('https://example.com', {
      waitUntil: 'domcontentloaded'
    });
    
    // 对于不需要等待所有资源的页面很有用
    const mainContent = page.locator('[data-testid="main-content"]');
    await expect(mainContent).toBeVisible();
  });

  test('应该使用负载均衡等待策略', async ({ page }) => {
    // ✅ 好的做法：为不同的操作使用适当的等待策略
    
    // 对于导航操作
    await page.goto('https://example.com/slow-page', {
      waitUntil: 'networkidle'
    });
    
    // 对于表单提交
    const submitButton = page.locator('[data-testid="submit-form"]');
    await Promise.all([
      page.waitForResponse(response => 
        response.url().includes('/api/submit') && response.status() === 200
      ),
      submitButton.click()
    ]);
    
    // 对于动态内容
    const dynamicContent = page.locator('[data-testid="dynamic-content"]');
    await dynamicContent.waitFor({ state: 'attached' });
    await expect(dynamicContent).toBeVisible();
  });

  test('应该避免过度等待', async ({ page }) => {
    // ✅ 好的做法：设置合理的超时时间
    const slowElement = page.locator('[data-testid="slow-element"]');
    
    // 为特定元素设置自定义超时
    await slowElement.waitFor({ 
      state: 'visible', 
      timeout: 15000 // 15秒而不是默认的30秒
    });
    
    // ✅ 好的做法：使用条件等待
    await page.waitForFunction(
      () => document.querySelector('[data-testid="ready-indicator"]')?.textContent === 'Ready',
      { timeout: 10000 }
    );
  });
});
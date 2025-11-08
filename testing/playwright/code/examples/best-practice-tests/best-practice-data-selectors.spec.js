// 最佳实践：使用数据属性选择器
const { test, expect } = require('@playwright/test');

test.describe('数据属性选择器最佳实践', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://example.com');
  });

  test('应该使用data-testid选择器', async ({ page }) => {
    // ✅ 好的做法：使用data-testid
    const submitButton = page.locator('[data-testid="submit-button"]');
    await submitButton.click();
    
    // ✅ 好的做法：使用data-testid进行断言
    const successMessage = page.locator('[data-testid="success-message"]');
    await expect(successMessage).toBeVisible();
    await expect(successMessage).toHaveText('操作成功');
  });

  test('应该使用data-cy选择器', async ({ page }) => {
    // ✅ 好的做法：使用data-cy（Cypress风格）
    const form = page.locator('[data-cy="user-form"]');
    const nameInput = form.locator('[data-cy="name-input"]');
    
    await nameInput.fill('测试用户');
    await expect(nameInput).toHaveValue('测试用户');
  });

  test('应该避免使用脆弱的选择器', async ({ page }) => {
    // ❌ 不好的做法：使用CSS类名（容易变化）
    // const button = page.locator('.btn-primary.btn-large');
    
    // ❌ 不好的做法：使用复杂的XPath
    // const element = page.locator('//div[@class="container"]/div[3]/button[1]');
    
    // ✅ 好的做法：使用稳定的属性
    const stableButton = page.locator('[data-testid="primary-action"]');
    await stableButton.click();
  });
});
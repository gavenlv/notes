// element-interaction.spec.js
const { test, expect } = require('@playwright/test');

test('元素交互测试', async ({ page }) => {
  await page.goto('/elements');

  // 点击按钮
  await page.click('#submit-button');

  // 在输入框中输入文本
  await page.fill('#name-input', 'Playwright');

  // 选择下拉选项
  await page.selectOption('#country-select', 'China');

  // 验证复选框被选中
  await page.check('#terms-checkbox');
  await expect(page.locator('#terms-checkbox')).toBeChecked();
});
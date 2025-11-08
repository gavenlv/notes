// data-driven-test.spec.js
const { test, expect } = require('@playwright/test');
const { testData } = require('../data/test-data');

test.describe('数据驱动测试示例', () => {
  test.each(testData.users)('用户登录测试 username=%s', async ({ page }, user) => {
    // 导航到登录页面
    await page.goto('/login');
    
    // 填充用户名和密码
    await page.fill('#username', user.username);
    await page.fill('#password', user.password);
    
    // 点击登录按钮
    await page.click('#login-button');
    
    // 验证登录结果
    // 这里根据实际应用逻辑调整验证方式
    // await expect(page).toHaveURL('/dashboard');
  });
});
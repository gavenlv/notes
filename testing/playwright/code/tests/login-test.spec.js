// login-test.spec.js
const { test } = require('@playwright/test');
const { LoginPage } = require('../pages/login-page');

test('用户登录测试', async ({ page }) => {
  const loginPage = new LoginPage(page);
  
  await loginPage.navigate();
  await loginPage.login('testuser', 'password123');
  
  // 验证登录成功
  await expect(page).toHaveURL('/dashboard');
});
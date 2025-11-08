// register-test.spec.js
const { test, expect } = require('@playwright/test');
const { RegisterPage } = require('../pages/register-page');

test('用户注册流程测试', async ({ page }) => {
  const registerPage = new RegisterPage(page);
  
  // 导航到注册页面
  await page.goto('/register');
  
  // 执行注册操作
  await registerPage.register('newuser', 'newuser@example.com', 'password123');
  
  // 验证注册成功
  await expect(page).toHaveURL('/welcome');
  await expect(page.locator('.welcome-message')).toContainText('欢迎注册');
});
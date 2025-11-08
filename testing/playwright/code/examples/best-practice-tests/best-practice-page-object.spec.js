// 最佳实践：使用页面对象模式
const { test, expect } = require('@playwright/test');
const { LoginPage } = require('../pages/LoginPage');

test.describe('页面对象模式最佳实践', () => {
  let loginPage;
  
  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    await loginPage.goto();
  });

  test('应该成功登录', async () => {
    await loginPage.login('validuser', 'validpassword');
    
    const isSuccessVisible = await loginPage.isSuccessMessageVisible();
    expect(isSuccessVisible).toBeTruthy();
  });

  test('应该显示错误消息当凭证无效', async () => {
    await loginPage.login('invaliduser', 'wrongpassword');
    
    const errorMessage = await loginPage.getErrorMessage();
    expect(errorMessage).toContain('用户名或密码错误');
  });

  test('应该验证登录表单的UI元素', async () => {
    // 验证所有必要的UI元素都存在
    await expect(loginPage.usernameInput).toBeVisible();
    await expect(loginPage.passwordInput).toBeVisible();
    await expect(loginPage.loginButton).toBeVisible();
    await expect(loginPage.loginButton).toBeEnabled();
    
    // 验证输入框的属性
    await expect(loginPage.usernameInput).toHaveAttribute('type', 'text');
    await expect(loginPage.passwordInput).toHaveAttribute('type', 'password');
  });
});
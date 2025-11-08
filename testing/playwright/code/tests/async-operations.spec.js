// async-operations.spec.js
const { test, expect } = require('@playwright/test');

test('异步操作同步测试', async ({ page }) => {
  await page.goto('/async-operations');
  
  // 处理多个并行操作
  const [loginResponse, userDataResponse] = await Promise.all([
    page.waitForResponse('**/login'),
    page.waitForResponse('**/user-data'),
    page.click('#login-button')
  ]);
  
  // 验证所有响应
  expect(loginResponse.status()).toBe(200);
  expect(userDataResponse.status()).toBe(200);
  
  // 等待元素文本变化
  await page.waitForFunction(() => {
    return document.querySelector('#status').textContent.trim().length > 0;
  });
  
  // 等待元素属性变化
  await page.waitForFunction(() => {
    return document.querySelector('#progress').getAttribute('value') === '100';
  });
});
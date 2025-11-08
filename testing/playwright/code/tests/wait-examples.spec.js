// wait-examples.spec.js
const { test, expect } = require('@playwright/test');

test('等待机制示例', async ({ page }) => {
  // 设置页面超时
  test.setTimeout(60000);
  
  await page.goto('/wait-examples');
  
  // 等待元素状态
  await page.waitForSelector('#element', { state: 'visible' });
  await page.waitForSelector('#element', { state: 'hidden' });
  
  // 等待页面加载状态
  await page.waitForLoadState('domcontentloaded');
  await page.waitForLoadState('networkidle');
  
  // 等待自定义条件
  await page.waitForFunction(() => {
    return document.querySelector('#status').innerText === 'Complete';
  });
  
  // 等待网络请求
  const [response] = await Promise.all([
    page.waitForResponse('**/api/data'),
    page.click('#load-data-button')
  ]);
  
  expect(response.status()).toBe(200);
});
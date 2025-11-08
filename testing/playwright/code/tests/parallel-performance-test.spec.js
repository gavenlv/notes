// tests/parallel-performance-test.spec.js
const { test, expect } = require('@playwright/test');
const { PerformanceMonitor } = require('../helpers/performance-monitor');

const monitor = new PerformanceMonitor();

// 创建多个相似的测试用例来演示并行执行
for (let i = 1; i <= 5; i++) {
  test(`并行性能测试用例 ${i}`, async ({ page, workerInfo }) => {
    const testName = `测试用例 ${i}-${workerInfo.workerIndex}`;
    monitor.start(testName);
    
    // 模拟导航到页面
    await page.goto('/');
    
    // 模拟一些操作
    await page.waitForTimeout(500);
    
    // 验证页面标题
    const title = await page.title();
    expect(title).toBeTruthy();
    
    monitor.end(testName);
    
    // 输出性能信息
    console.log(`${testName} 执行时间: ${monitor.getDuration(testName)}ms`);
  });
}

// 测试独立性验证
test('独立测试用例1', async ({ page }) => {
  monitor.start('独立测试1');
  
  await page.goto('/');
  await page.waitForTimeout(300);
  
  const title = await page.title();
  expect(title).toBeTruthy();
  
  monitor.end('独立测试1');
  console.log(`独立测试1 执行时间: ${monitor.getDuration('独立测试1')}ms`);
});

test('独立测试用例2', async ({ page }) => {
  monitor.start('独立测试2');
  
  await page.goto('/');
  await page.waitForTimeout(300);
  
  const title = await page.title();
  expect(title).toBeTruthy();
  
  monitor.end('独立测试2');
  console.log(`独立测试2 执行时间: ${monitor.getDuration('独立测试2')}ms`);
});
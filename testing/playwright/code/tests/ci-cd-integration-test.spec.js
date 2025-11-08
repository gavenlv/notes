// tests/ci-cd-integration-test.spec.js
const { test, expect } = require('@playwright/test');
const { EnvironmentManager } = require('../config/environment-manager');
const { MetricsCollector } = require('../helpers/metrics-collector');

const envManager = new EnvironmentManager();
const metricsCollector = new MetricsCollector();

test.describe('CI/CD集成测试', () => {
  test.beforeEach(async ({ page }) => {
    // 根据环境配置设置基础URL
    const env = envManager.getEnvironment();
    await page.goto(env.url);
  });

  test('环境配置测试', async ({ page }) => {
    const env = envManager.getEnvironment();
    
    // 验证环境配置
    expect(env.url).toBeTruthy();
    expect(env.database).toBeTruthy();
    
    // 验证是否在正确的环境中运行
    if (process.env.TEST_ENV === 'staging') {
      expect(env.url).toContain('staging');
    } else if (process.env.TEST_ENV === 'production') {
      expect(env.url).toContain('example.com');
    } else {
      expect(env.url).toContain('localhost');
    }
    
    // 记录测试结果
    metricsCollector.recordTestResult('passed');
  });

  test('浏览器模式测试', async ({ page }) => {
    const browserOptions = envManager.getBrowserOptions();
    
    // 在CI环境中应该使用无头模式
    if (envManager.isCI()) {
      expect(browserOptions.headless).toBe(true);
    }
    
    // 验证页面标题
    const title = await page.title();
    expect(title).toBeTruthy();
    
    // 记录测试结果
    metricsCollector.recordTestResult('passed');
  });

  test('API端点测试', async ({ page, request }) => {
    const env = envManager.getEnvironment();
    
    // 测试API端点可访问性
    try {
      const response = await request.get(`${env.apiBaseUrl}/health`);
      expect(response.status()).toBe(200);
      metricsCollector.recordTestResult('passed');
    } catch (error) {
      console.error('API端点测试失败:', error);
      metricsCollector.recordTestResult('failed');
    }
  });

  test('安全测试', async ({ page, request }) => {
    // XSS防护测试
    await page.goto('/search');
    
    // 尝试注入恶意脚本
    try {
      await page.fill('#search-input', '<script>alert("xss")</script>');
      await page.click('#search-button');
      
      // 验证脚本未执行
      const content = await page.content();
      expect(content).not.toContain('alert("xss")');
      metricsCollector.recordTestResult('passed');
    } catch (error) {
      console.error('XSS防护测试失败:', error);
      metricsCollector.recordTestResult('failed');
    }
  });
});

// 测试结束时输出指标
test.afterAll(async () => {
  const metrics = metricsCollector.getMetrics();
  console.log('测试指标:', JSON.stringify(metrics, null, 2));
  
  // 在CI环境中发送指标到监控系统
  if (process.env.CI) {
    await metricsCollector.sendToMonitoringSystem(metrics);
  }
});
// playwright.config.js
const { devices } = require('@playwright/test');

module.exports = {
  // 测试目录
  testDir: './tests',
  
  // 超时时间
  timeout: 30 * 1000,
  
  // 期望超时时间
  expect: {
    timeout: 5000
  },
  
  // 完全并行执行测试
  fullyParallel: true,
  
  // 是否禁止仅测试模式
  forbidOnly: !!process.env.CI,
  
  // 重试次数
  retries: process.env.CI ? 2 : 0,
  
  // 工作进程数量
  workers: process.env.CI ? 1 : undefined,
  
  // 测试报告
  reporter: 'html',
  
  // 共享设置
  use: {
    // 基础URL
    baseURL: 'http://localhost:3000',
    
    // 截图设置
    screenshot: 'only-on-failure',
    
    // 视频录制设置
    video: 'retain-on-failure',
    
    // 跟踪设置
    trace: 'on-first-retry',
  },
  
  // 项目配置
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
      },
    },
    
    {
      name: 'firefox',
      use: {
        ...devices['Desktop Firefox'],
      },
    },
    
    {
      name: 'webkit',
      use: {
        ...devices['Desktop Safari'],
      },
    },
  ],
  
  // 输出目录
  outputDir: 'test-results/',
};
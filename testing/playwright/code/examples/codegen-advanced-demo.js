// examples/codegen-advanced-demo.js
const { chromium, devices } = require('@playwright/test');

/**
 * CodeGen高级演示示例
 * 展示CodeGen的高级功能和最佳实践
 */

// 高级示例1：移动端设备录制
async function mobileDeviceRecording() {
  const browser = await chromium.launch({ headless: false });
  
  // 使用预设的移动设备配置
  const pixel5 = devices['Pixel 5'];
  const context = await browser.newContext({
    ...pixel5,
    locale: 'en-US',
    geolocation: { longitude: 37.7749, latitude: -122.4194 },
    permissions: ['geolocation'],
  });
  
  const page = await context.newPage();

  // 访问移动端优化的网站
  await page.goto('https://m.example.com');

  // 模拟触摸操作
  await page.tap('input[type="search"]');
  await page.fill('input[type="search"]', 'restaurants near me');
  await page.tap('button[type="submit"]');

  // 等待地理定位相关的搜索结果
  await page.waitForSelector('text="nearby"');

  console.log('✅ 移动端设备录制演示完成');
  await browser.close();
}

// 高级示例2：地理位置和本地化测试
async function geolocationAndLocalizationTest() {
  const browser = await chromium.launch({ headless: false });
  
  const context = await browser.newContext({
    locale: 'zh-CN',
    timezoneId: 'Asia/Shanghai',
    geolocation: { longitude: 116.4074, latitude: 39.9042 }, // 北京
    permissions: ['geolocation'],
  });
  
  const page = await context.newPage();

  // 访问本地化网站
  await page.goto('https://example.com/localized');

  // 验证本地化内容
  await page.waitForSelector('text="中文"');
  
  // 搜索本地服务
  await page.click('input[placeholder*="搜索"]');
  await page.fill('input[placeholder*="搜索"]', '餐厅');
  await page.press('input[placeholder*="搜索"]', 'Enter');

  // 等待基于地理位置的结果
  await page.waitForSelector('text="北京"');

  console.log('✅ 地理位置和本地化测试演示完成');
  await browser.close();
}

// 高级示例3：网络请求拦截和修改
async function networkInterceptionDemo() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // 设置网络请求拦截
  await page.route('**/api/users', (route) => {
    // 修改响应数据
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        { id: 1, name: 'CodeGen User', email: 'codegen@example.com' }
      ])
    });
  });

  // 访问需要API数据的页面
  await page.goto('https://example.com/users');

  // 触发API请求
  await page.click('button:has-text("Load Users")');

  // 验证修改后的数据
  await page.waitForSelector('text="CodeGen User"');
  await page.waitForSelector('text="codegen@example.com"');

  console.log('✅ 网络请求拦截演示完成');
  await browser.close();
}

// 高级示例4：认证状态保持
async function authenticationStateDemo() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // 登录流程
  await page.goto('https://example.com/login');
  await page.fill('input[name="username"]', 'testuser');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');

  // 等待登录成功
  await page.waitForSelector('text="Welcome, testuser"');

  // 保存认证状态
  await context.storageState({ path: 'auth.json' });

  console.log('✅ 认证状态已保存');
  await browser.close();

  // 在新会话中使用保存的认证状态
  const browser2 = await chromium.launch({ headless: false });
  const context2 = await browser2.newContext({
    storageState: 'auth.json'
  });
  const page2 = await context2.newPage();

  // 直接访问需要认证的页面
  await page2.goto('https://example.com/dashboard');
  
  // 验证已登录状态
  await page2.waitForSelector('text="Welcome, testuser"');

  console.log('✅ 认证状态保持演示完成');
  await browser2.close();
}

// 高级示例5：多标签页和弹窗处理
async function multiTabAndPopupHandling() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // 监听新页面事件
  const [newPage] = await Promise.all([
    context.waitForEvent('page'),
    page.click('a[target="_blank"]') // 点击在新标签页打开的链接
  ]);

  // 等待新页面加载
  await newPage.waitForLoadState();

  // 在新页面中操作
  await newPage.click('button:has-text("Action")');
  await newPage.waitForSelector('text="Success"');

  // 处理弹窗
  page.on('dialog', async dialog => {
    console.log(`Dialog message: ${dialog.message()}`);
    await dialog.accept();
  });

  // 触发弹窗
  await page.click('button:has-text("Show Alert")');

  console.log('✅ 多标签页和弹窗处理演示完成');
  await browser.close();
}

// 高级示例6：文件上传和下载
async function fileUploadAndDownload() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // 文件上传
  await page.goto('https://example.com/upload');
  
  // 等待文件选择器
  await page.waitForSelector('input[type="file"]');
  
  // 上传文件
  await page.setInputFiles('input[type="file"]', {
    name: 'test-file.txt',
    mimeType: 'text/plain',
    buffer: Buffer.from('This is a test file for CodeGen upload')
  });

  // 等待上传完成
  await page.waitForSelector('text="Upload successful"');

  // 文件下载
  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.click('button:has-text("Download")') // 点击下载按钮
  ]);

  // 保存下载的文件
  const path = await download.path();
  console.log(`File downloaded to: ${path}`);

  console.log('✅ 文件上传和下载演示完成');
  await browser.close();
}

// 高级示例7：截图和视频录制
async function screenshotAndVideoRecording() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({
    recordVideo: {
      dir: 'videos/',
      size: { width: 1280, height: 720 }
    }
  });
  
  const page = await context.newPage();

  // 访问页面并操作
  await page.goto('https://demo.playwright.dev/todomvc/');

  // 全页面截图
  await page.screenshot({ 
    path: 'screenshots/fullpage.png',
    fullPage: true 
  });

  // 添加待办事项
  await page.fill('[placeholder="What needs to be done?"]', 'Screenshot task');
  await page.press('[placeholder="What needs to be done?"]', 'Enter');

  // 元素截图
  const todoItem = page.locator('.todo-list li').first();
  await todoItem.screenshot({ path: 'screenshots/todo-item.png' });

  // 视口截图
  await page.screenshot({ path: 'screenshots/viewport.png' });

  console.log('✅ 截图和视频录制演示完成');
  await browser.close();
}

// 高级示例8：性能分析和监控
async function performanceAnalysis() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // 启用性能分析
  await page.goto('https://example.com');

  // 监控页面加载性能
  const performanceTiming = await page.evaluate(() => {
    return JSON.parse(JSON.stringify(window.performance.timing));
  });

  console.log('页面加载时间:', performanceTiming.loadEventEnd - performanceTiming.navigationStart);

  // 监控网络请求性能
  const requestMetrics = [];
  page.on('request', request => {
    requestMetrics.push({
      url: request.url(),
      startTime: Date.now()
    });
  });

  page.on('response', response => {
    const metric = requestMetrics.find(m => m.url === response.url());
    if (metric) {
      metric.duration = Date.now() - metric.startTime;
      metric.status = response.status();
    }
  });

  // 触发一些网络请求
  await page.click('button:has-text("Load Data")');
  await page.waitForLoadState('networkidle');

  // 输出性能指标
  console.log('网络请求性能指标:', requestMetrics);

  console.log('✅ 性能分析演示完成');
  await browser.close();
}

// 高级示例9：跨浏览器测试自动化
async function crossBrowserTesting() {
  const browsers = ['chromium', 'firefox', 'webkit'];
  
  for (const browserType of browsers) {
    console.log(`Testing on ${browserType}...`);
    
    const browser = await require('@playwright/test')[browserType].launch({ headless: false });
    const context = await browser.newContext();
    const page = await context.newPage();

    // 访问测试页面
    await page.goto('https://demo.playwright.dev/todomvc/');

    // 执行基本操作
    await page.fill('[placeholder="What needs to be done?"]', `Test on ${browserType}`);
    await page.press('[placeholder="What needs to be done?"]', 'Enter');

    // 验证操作结果
    await page.waitForSelector(`text=Test on ${browserType}`);

    console.log(`✅ ${browserType} 测试完成`);
    await browser.close();
  }
}

// 高级示例10：自定义CodeGen配置
async function customCodegenConfiguration() {
  const browser = await chromium.launch({ headless: false });
  
  // 自定义配置，模拟CodeGen的高级设置
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    locale: 'en-US',
    timezoneId: 'America/New_York',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    deviceScaleFactor: 1,
    isMobile: false,
    hasTouch: false,
    defaultBrowserType: 'chromium'
  });

  const page = await context.newPage();

  // 设置额外的HTTP头
  await page.setExtraHTTPHeaders({
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache'
  });

  // 访问页面
  await page.goto('https://example.com');

  // 使用自定义选择器引擎
  await page.addScriptTag({
    content: `
      // 自定义选择器逻辑
      window.customSelector = function(text) {
        return Array.from(document.querySelectorAll('*')).find(
          el => el.textContent.includes(text)
        );
      };
    `
  });

  // 使用自定义选择器
  await page.evaluate(() => {
    const element = window.customSelector('Submit');
    if (element) element.click();
  });

  console.log('✅ 自定义CodeGen配置演示完成');
  await browser.close();
}

// 运行所有高级演示
async function runAllAdvancedDemos() {
  console.log('🚀 开始CodeGen高级演示...\n');
  
  try {
    await mobileDeviceRecording();
    console.log('');
    
    await geolocationAndLocalizationTest();
    console.log('');
    
    await networkInterceptionDemo();
    console.log('');
    
    await authenticationStateDemo();
    console.log('');
    
    await multiTabAndPopupHandling();
    console.log('');
    
    await fileUploadAndDownload();
    console.log('');
    
    await screenshotAndVideoRecording();
    console.log('');
    
    await performanceAnalysis();
    console.log('');
    
    await crossBrowserTesting();
    console.log('');
    
    await customCodegenConfiguration();
    console.log('');
    
    console.log('🎉 所有CodeGen高级演示完成！');
  } catch (error) {
    console.error('❌ 高级演示失败:', error);
  }
}

// 导出函数供其他模块使用
module.exports = {
  mobileDeviceRecording,
  geolocationAndLocalizationTest,
  networkInterceptionDemo,
  authenticationStateDemo,
  multiTabAndPopupHandling,
  fileUploadAndDownload,
  screenshotAndVideoRecording,
  performanceAnalysis,
  crossBrowserTesting,
  customCodegenConfiguration,
  runAllAdvancedDemos
};

// 如果直接运行此文件，执行所有演示
if (require.main === module) {
  runAllAdvancedDemos();
}
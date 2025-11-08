// examples/codegen-demo.js
const { chromium } = require('@playwright/test');

/**
 * CodeGen演示示例
 * 展示如何使用Playwright CodeGen生成的代码
 */

// 示例1：基本的CodeGen生成代码演示
async function basicCodegenDemo() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // 访问示例网站
  await page.goto('https://demo.playwright.dev/todomvc/');

  // 添加待办事项 - 这是CodeGen会生成的典型代码
  await page.click('[placeholder="What needs to be done?"]');
  await page.fill('[placeholder="What needs to be done?"]', 'Buy groceries');
  await page.press('[placeholder="What needs to be done?"]', 'Enter');

  // 验证待办事项已添加
  await page.waitForSelector('text=Buy groceries');
  
  console.log('✅ 基本CodeGen演示完成');
  await browser.close();
}

// 示例2：表单交互演示
async function formInteractionDemo() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // 访问表单页面
  await page.goto('https://demo.playwright.dev/reqres.in/api/users');

  // 填写表单 - CodeGen生成的典型模式
  await page.click('input[name="name"]');
  await page.fill('input[name="name"]', 'John Doe');
  
  await page.click('input[name="email"]');
  await page.fill('input[name="email"]', 'john.doe@example.com');
  
  await page.click('input[name="password"]');
  await page.fill('input[name="password"]', 'SecurePassword123!');

  // 选择下拉选项
  await page.selectOption('select[name="role"]', 'admin');
  
  // 勾选复选框
  await page.check('input[type="checkbox"]');

  // 提交表单
  await page.click('button[type="submit"]');

  console.log('✅ 表单交互演示完成');
  await browser.close();
}

// 示例3：复杂的用户交互演示
async function complexInteractionDemo() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // 访问复杂的交互页面
  await page.goto('https://demo.playwright.dev/');

  // 导航到文档页面
  await page.click('text=Docs');
  await page.waitForLoadState('networkidle');

  // 搜索文档
  await page.click('[placeholder="Search docs"]');
  await page.fill('[placeholder="Search docs"]', 'codegen');
  await page.press('[placeholder="Search docs"]', 'Enter');

  // 等待搜索结果
  await page.waitForSelector('text=codegen');

  // 点击第一个搜索结果
  await page.click('.search-result-item:first-child');
  
  // 验证页面加载
  await page.waitForLoadState('domcontentloaded');

  console.log('✅ 复杂交互演示完成');
  await browser.close();
}

// 示例4：等待和断言演示
async function waitAndAssertionDemo() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  await page.goto('https://demo.playwright.dev/todomvc/');

  // 添加待办事项
  await page.fill('[placeholder="What needs to be done?"]', 'Test CodeGen');
  await page.press('[placeholder="What needs to be done?"]', 'Enter');

  // 等待元素出现 - CodeGen自动添加的等待
  await page.waitForSelector('text=Test CodeGen');

  // 标记为完成
  await page.click('input[type="checkbox"]');

  // 等待状态变化
  await page.waitForSelector('.completed');

  // 验证元素状态
  const todoItem = await page.locator('li');
  await todoItem.waitFor({ state: 'visible' });

  console.log('✅ 等待和断言演示完成');
  await browser.close();
}

// 示例5：iframe处理演示
async function iframeHandlingDemo() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // 访问包含iframe的页面
  await page.goto('https://demo.playwright.dev/iframe');

  // 等待iframe加载
  await page.waitForSelector('iframe');

  // 获取iframe
  const frame = await page.frame({ url: /.*iframe.*/ });
  
  if (frame) {
    // 在iframe中操作
    await frame.click('button:has-text("Click me")');
    await frame.waitForSelector('text="Button clicked"');
  }

  console.log('✅ iframe处理演示完成');
  await browser.close();
}

// 示例6：移动端模拟演示
async function mobileSimulationDemo() {
  const browser = await chromium.launch({ headless: false });
  
  // 模拟iPhone 12
  const context = await browser.newContext({
    ...require('@playwright/test').devices['iPhone 12'],
  });
  
  const page = await context.newPage();

  await page.goto('https://demo.playwright.dev/todomvc/');

  // 移动端交互 - CodeGen会生成适合移动端的代码
  await page.tap('[placeholder="What needs to be done?"]');
  await page.fill('[placeholder="What needs to be done?"]', 'Mobile test');
  await page.press('[placeholder="What needs to be done?"]', 'Enter');

  await page.waitForSelector('text=Mobile test');

  console.log('✅ 移动端模拟演示完成');
  await browser.close();
}

// 示例7：网络请求录制演示
async function networkRecordingDemo() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // 启用网络请求录制
  const requests = [];
  page.on('request', request => {
    requests.push({
      url: request.url(),
      method: request.method(),
      headers: request.headers()
    });
  });

  await page.goto('https://demo.playwright.dev/reqres.in/api/users');

  // 触发网络请求
  await page.click('button:has-text("Load Users")');
  
  // 等待网络请求完成
  await page.waitForLoadState('networkidle');

  console.log('📡 录制的网络请求:', requests.length);
  console.log('✅ 网络请求录制演示完成');
  await browser.close();
}

// 示例8：CodeGen生成的最佳实践代码
async function bestPracticesDemo() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // 最佳实践1：使用明确的等待
  await page.goto('https://demo.playwright.dev/todomvc/');
  await page.waitForLoadState('networkidle');

  // 最佳实践2：使用文本定位器
  await page.click('text="What needs to be done?"');
  await page.fill('input[placeholder="What needs to be done?"]', 'Best practice');
  
  // 最佳实践3：使用键盘事件
  await page.keyboard.press('Enter');

  // 最佳实践4：验证操作结果
  await expect(page.locator('text="Best practice"')).toBeVisible();

  // 最佳实践5：处理动态内容
  await page.waitForTimeout(1000); // 等待动画完成
  await expect(page.locator('.todo-list li')).toHaveCount(1);

  console.log('✅ 最佳实践演示完成');
  await browser.close();
}

// 运行所有演示
async function runAllDemos() {
  console.log('🚀 开始CodeGen演示...\n');
  
  try {
    await basicCodegenDemo();
    console.log('');
    
    await formInteractionDemo();
    console.log('');
    
    await complexInteractionDemo();
    console.log('');
    
    await waitAndAssertionDemo();
    console.log('');
    
    await iframeHandlingDemo();
    console.log('');
    
    await mobileSimulationDemo();
    console.log('');
    
    await networkRecordingDemo();
    console.log('');
    
    await bestPracticesDemo();
    console.log('');
    
    console.log('🎉 所有CodeGen演示完成！');
  } catch (error) {
    console.error('❌ 演示失败:', error);
  }
}

// 导出函数供其他模块使用
module.exports = {
  basicCodegenDemo,
  formInteractionDemo,
  complexInteractionDemo,
  waitAndAssertionDemo,
  iframeHandlingDemo,
  mobileSimulationDemo,
  networkRecordingDemo,
  bestPracticesDemo,
  runAllDemos
};

// 如果直接运行此文件，执行所有演示
if (require.main === module) {
  runAllDemos();
}
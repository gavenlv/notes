// examples/codegen-best-practices.js
/**
 * CodeGen最佳实践示例
 * 展示CodeGen的最佳实践和高级技巧
 */

const { CodegenCommandBuilder } = require('./codegen-custom-commands');
const fs = require('fs');
const path = require('path');

/**
 * CodeGen最佳实践管理器
 */
class CodegenBestPracticesManager {
  constructor(config = {}) {
    this.config = {
      outputDir: config.outputDir || './best-practice-tests',
      standardsFile: config.standardsFile || './codegen-standards.json',
      ...config
    };
    
    this.standards = this.loadStandards();
    this.setupDirectories();
  }

  setupDirectories() {
    if (!fs.existsSync(this.config.outputDir)) {
      fs.mkdirSync(this.config.outputDir, { recursive: true });
    }
  }

  loadStandards() {
    if (fs.existsSync(this.config.standardsFile)) {
      return JSON.parse(fs.readFileSync(this.config.standardsFile, 'utf8'));
    }
    
    return this.createDefaultStandards();
  }

  createDefaultStandards() {
    return {
      naming: {
        testFilePattern: '^(feature|component|page)-[a-z-]+\\.spec\\.js$',
        testNamePattern: '^should (test|verify|check|ensure) [a-z ]+$',
        selectorPattern: '^[a-z-]+$'
      },
      structure: {
        requireDescribe: true,
        maxTestsPerFile: 10,
        requireBeforeEach: true,
        requireAfterEach: true
      },
      selectors: {
        preferDataTestId: true,
        avoidXPath: true,
        useAccessibleSelectors: true,
        avoidBrittleSelectors: true
      },
      assertions: {
        requireExplicitAssertions: true,
        avoidGenericAssertions: true,
        useAppropriateTimeouts: true
      },
      performance: {
        maxTestDuration: 30000,
        requireParallelExecution: true,
        optimizeSelectorStrategy: true
      },
      maintainability: {
        requireComments: true,
        usePageObjects: true,
        avoidCodeDuplication: true,
        useConsistentFormatting: true
      }
    };
  }

  /**
   * 最佳实践1: 使用数据属性选择器
   */
  generateDataAttributeSelectors() {
    console.log('生成使用数据属性选择器的测试...');
    
    const testContent = `
// 最佳实践：使用数据属性选择器
const { test, expect } = require('@playwright/test');

test.describe('数据属性选择器最佳实践', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://example.com');
  });

  test('应该使用data-testid选择器', async ({ page }) => {
    // ✅ 好的做法：使用data-testid
    const submitButton = page.locator('[data-testid="submit-button"]');
    await submitButton.click();
    
    // ✅ 好的做法：使用data-testid进行断言
    const successMessage = page.locator('[data-testid="success-message"]');
    await expect(successMessage).toBeVisible();
    await expect(successMessage).toHaveText('操作成功');
  });

  test('应该使用data-cy选择器', async ({ page }) => {
    // ✅ 好的做法：使用data-cy（Cypress风格）
    const form = page.locator('[data-cy="user-form"]');
    const nameInput = form.locator('[data-cy="name-input"]');
    
    await nameInput.fill('测试用户');
    await expect(nameInput).toHaveValue('测试用户');
  });

  test('应该避免使用脆弱的选择器', async ({ page }) => {
    // ❌ 不好的做法：使用CSS类名（容易变化）
    // const button = page.locator('.btn-primary.btn-large');
    
    // ❌ 不好的做法：使用复杂的XPath
    // const element = page.locator('//div[@class="container"]/div[3]/button[1]');
    
    // ✅ 好的做法：使用稳定的属性
    const stableButton = page.locator('[data-testid="primary-action"]');
    await stableButton.click();
  });
});
    `;

    const outputPath = path.join(this.config.outputDir, 'best-practice-data-selectors.spec.js');
    fs.writeFileSync(outputPath, testContent.trim());
    
    return outputPath;
  }

  /**
   * 最佳实践2: 使用页面对象模式
   */
  generatePageObjectPattern() {
    console.log('生成使用页面对象模式的测试...');
    
    // 创建页面对象
    const pageObjectContent = `
// pages/LoginPage.js
class LoginPage {
  constructor(page) {
    this.page = page;
    
    // 选择器
    this.usernameInput = page.locator('[data-testid="username-input"]');
    this.passwordInput = page.locator('[data-testid="password-input"]');
    this.loginButton = page.locator('[data-testid="login-button"]');
    this.errorMessage = page.locator('[data-testid="error-message"]');
    this.successMessage = page.locator('[data-testid="success-message"]');
  }
  
  async goto() {
    await this.page.goto('https://example.com/login');
  }
  
  async login(username, password) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }
  
  async getErrorMessage() {
    await this.errorMessage.waitFor({ state: 'visible' });
    return this.errorMessage.textContent();
  }
  
  async isSuccessMessageVisible() {
    return this.successMessage.isVisible();
  }
}

module.exports = { LoginPage };
    `;

    // 创建测试文件
    const testContent = `
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
    `;

    // 创建pages目录
    const pagesDir = path.join(this.config.outputDir, 'pages');
    if (!fs.existsSync(pagesDir)) {
      fs.mkdirSync(pagesDir, { recursive: true });
    }
    
    fs.writeFileSync(path.join(pagesDir, 'LoginPage.js'), pageObjectContent.trim());
    
    const testPath = path.join(this.config.outputDir, 'best-practice-page-object.spec.js');
    fs.writeFileSync(testPath, testContent.trim());
    
    return { pageObject: path.join(pagesDir, 'LoginPage.js'), test: testPath };
  }

  /**
   * 最佳实践3: 使用适当的等待策略
   */
  generateWaitStrategies() {
    console.log('生成使用适当等待策略的测试...');
    
    const testContent = `
// 最佳实践：使用适当的等待策略
const { test, expect } = require('@playwright/test');

test.describe('等待策略最佳实践', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://example.com');
  });

  test('应该使用自动等待而不是固定延时', async ({ page }) => {
    // ❌ 不好的做法：使用固定的延时
    // await page.waitForTimeout(3000);
    
    // ✅ 好的做法：使用Playwright的自动等待
    const button = page.locator('[data-testid="dynamic-button"]');
    await button.click(); // Playwright会自动等待元素可点击
    
    // ✅ 好的做法：使用明确的等待条件
    const result = page.locator('[data-testid="result"]');
    await result.waitFor({ state: 'visible', timeout: 10000 });
    await expect(result).toContainText('操作完成');
  });

  test('应该使用网络空闲等待页面加载', async ({ page }) => {
    // ✅ 好的做法：等待网络空闲
    await page.goto('https://example.com/data-heavy-page', {
      waitUntil: 'networkidle'
    });
    
    // 现在页面完全加载，可以安全地进行操作
    const dataElement = page.locator('[data-testid="data-loaded"]');
    await expect(dataElement).toBeVisible();
  });

  test('应该使用DOM内容加载等待', async ({ page }) => {
    // ✅ 好的做法：等待DOM内容加载完成
    await page.goto('https://example.com', {
      waitUntil: 'domcontentloaded'
    });
    
    // 对于不需要等待所有资源的页面很有用
    const mainContent = page.locator('[data-testid="main-content"]');
    await expect(mainContent).toBeVisible();
  });

  test('应该使用负载均衡等待策略', async ({ page }) => {
    // ✅ 好的做法：为不同的操作使用适当的等待策略
    
    // 对于导航操作
    await page.goto('https://example.com/slow-page', {
      waitUntil: 'networkidle'
    });
    
    // 对于表单提交
    const submitButton = page.locator('[data-testid="submit-form"]');
    await Promise.all([
      page.waitForResponse(response => 
        response.url().includes('/api/submit') && response.status() === 200
      ),
      submitButton.click()
    ]);
    
    // 对于动态内容
    const dynamicContent = page.locator('[data-testid="dynamic-content"]');
    await dynamicContent.waitFor({ state: 'attached' });
    await expect(dynamicContent).toBeVisible();
  });

  test('应该避免过度等待', async ({ page }) => {
    // ✅ 好的做法：设置合理的超时时间
    const slowElement = page.locator('[data-testid="slow-element"]');
    
    // 为特定元素设置自定义超时
    await slowElement.waitFor({ 
      state: 'visible', 
      timeout: 15000 // 15秒而不是默认的30秒
    });
    
    // ✅ 好的做法：使用条件等待
    await page.waitForFunction(
      () => document.querySelector('[data-testid="ready-indicator"]')?.textContent === 'Ready',
      { timeout: 10000 }
    );
  });
});
    `;

    const outputPath = path.join(this.config.outputDir, 'best-practice-wait-strategies.spec.js');
    fs.writeFileSync(outputPath, testContent.trim());
    
    return outputPath;
  }

  /**
   * 最佳实践4: 使用适当的断言
   */
  generateAssertionBestPractices() {
    console.log('生成使用适当断言的测试...');
    
    const testContent = `
// 最佳实践：使用适当的断言
const { test, expect } = require('@playwright/test');

test.describe('断言最佳实践', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://example.com');
  });

  test('应该使用具体的断言而不是通用的断言', async ({ page }) => {
    const button = page.locator('[data-testid="action-button"]');
    
    // ✅ 好的做法：使用具体的断言
    await expect(button).toBeVisible();
    await expect(button).toBeEnabled();
    await expect(button).toHaveText('点击我');
    await expect(button).toHaveAttribute('type', 'button');
    await expect(button).toHaveClass(/btn-primary/);
    
    // ❌ 不好的做法：使用过于通用的断言
    // expect(button).toBeTruthy();
    // expect(await button.textContent()).toBe('点击我');
  });

  test('应该使用适当的文本断言', async ({ page }) => {
    const heading = page.locator('[data-testid="page-heading"]');
    
    // ✅ 好的做法：使用toHaveText进行精确匹配
    await expect(heading).toHaveText('欢迎页面');
    
    // ✅ 好的做法：使用toContainText进行部分匹配
    await expect(heading).toContainText('欢迎');
    
    // ✅ 好的做法：使用正则表达式进行模式匹配
    await expect(heading).toHaveText(/欢迎.*页面/);
    
    // ✅ 好的做法：忽略大小写匹配
    await expect(heading).toHaveText('欢迎页面', { ignoreCase: true });
  });

  test('应该使用适当的属性断言', async ({ page }) => {
    const input = page.locator('[data-testid="email-input"]');
    
    // ✅ 好的做法：验证输入值
    await input.fill('test@example.com');
    await expect(input).toHaveValue('test@example.com');
    
    // ✅ 好的做法：验证属性值
    await expect(input).toHaveAttribute('type', 'email');
    await expect(input).toHaveAttribute('placeholder', '请输入邮箱');
    
    // ✅ 好的做法：验证CSS类
    await expect(input).toHaveClass('form-control');
    await expect(input).toHaveClass(/form-control/);
    
    // ✅ 好的做法：验证ID
    await expect(input).toHaveId('email');
  });

  test('应该使用适当的计数断言', async ({ page }) => {
    const items = page.locator('[data-testid="list-item"]');
    
    // ✅ 好的做法：验证元素数量
    await expect(items).toHaveCount(5);
    
    // ✅ 好的做法：验证最少数量
    await expect(items).toHaveCount(3, { timeout: 5000 });
    
    // ✅ 好的做法：验证非零数量
    await expect(items.first()).toBeVisible();
  });

  test('应该使用适当的URL断言', async ({ page }) => {
    // ✅ 好的做法：验证完整的URL
    await expect(page).toHaveURL('https://example.com/dashboard');
    
    // ✅ 好的做法：验证URL包含特定字符串
    await expect(page).toHaveURL(/dashboard/);
    
    // ✅ 好的做法：验证URL参数
    await expect(page).toHaveURL(/user=\d+/);
    
    // ✅ 好的做法：验证URL不包含敏感信息
    await expect(page).not.toHaveURL(/password=/);
  });

  test('应该使用适当的标题断言', async ({ page }) => {
    // ✅ 好的做法：验证页面标题
    await expect(page).toHaveTitle('示例应用 - 首页');
    
    // ✅ 好的做法：验证标题包含特定文本
    await expect(page).toHaveTitle(/示例应用/);
    
    // ✅ 好的做法：验证标题不包含错误信息
    await expect(page).not.toHaveTitle(/错误/);
  });

  test('应该使用适当的截图断言', async ({ page }) => {
    // ✅ 好的做法：进行视觉回归测试
    await expect(page).toHaveScreenshot('homepage.png');
    
    // ✅ 好的做法：对特定元素截图
    const header = page.locator('[data-testid="header"]');
    await expect(header).toHaveScreenshot('header.png');
    
    // ✅ 好的做法：设置截图选项
    await expect(page).toHaveScreenshot('fullpage.png', {
      fullPage: true,
      mask: [page.locator('[data-testid="timestamp"]')] // 屏蔽动态内容
    });
  });
});
    `;

    const outputPath = path.join(this.config.outputDir, 'best-practice-assertions.spec.js');
    fs.writeFileSync(outputPath, testContent.trim());
    
    return outputPath;
  }

  /**
   * 最佳实践5: 处理动态内容和测试数据
   */
  generateDynamicContentHandling() {
    console.log('生成处理动态内容和测试数据的测试...');
    
    const testContent = `
// 最佳实践：处理动态内容和测试数据
const { test, expect } = require('@playwright/test');

test.describe('动态内容处理最佳实践', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://example.com');
  });

  test('应该处理动态生成的内容', async ({ page }) => {
    // ✅ 好的做法：等待动态内容加载
    const dynamicList = page.locator('[data-testid="dynamic-list"]');
    await dynamicList.waitFor({ state: 'visible' });
    
    // ✅ 好的做法：使用动态选择器
    const items = dynamicList.locator('[data-testid="list-item"]');
    const itemCount = await items.count();
    
    // 验证动态生成的项目
    for (let i = 0; i < itemCount; i++) {
      const item = items.nth(i);
      await expect(item).toBeVisible();
      
      // 验证每个项目都有预期的结构
      const itemTitle = item.locator('[data-testid="item-title"]');
      const itemDescription = item.locator('[data-testid="item-description"]');
      
      await expect(itemTitle).toBeVisible();
      await expect(itemDescription).toBeVisible();
    }
    
    // 验证至少有一个项目
    expect(itemCount).toBeGreaterThan(0);
  });

  test('应该处理时间戳和动态文本', async ({ page }) => {
    // ✅ 好的做法：使用正则表达式匹配动态文本
    const timestamp = page.locator('[data-testid="timestamp"]');
    await expect(timestamp).toHaveText(/\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}/); // 匹配模式而不是具体值
    
    // ✅ 好的做法：在截图时屏蔽动态内容
    await expect(page).toHaveScreenshot('page-with-dynamic-content.png', {
      mask: [timestamp]
    });
  });

  test('应该使用测试数据驱动测试', async ({ page }) => {
    // ✅ 好的做法：使用参数化测试
    const testUsers = [
      { username: 'user1', email: 'user1@example.com', role: 'admin' },
      { username: 'user2', email: 'user2@example.com', role: 'user' },
      { username: 'user3', email: 'user3@example.com', role: 'guest' }
    ];
    
    for (const user of testUsers) {
      await test.step(\`测试用户: \${user.username}\`, async () => {
        // 使用测试数据填充表单
        await page.locator('[data-testid="username-input"]').fill(user.username);
        await page.locator('[data-testid="email-input"]').fill(user.email);
        await page.locator('[data-testid="role-select"]').selectOption(user.role);
        
        // 提交表单
        await page.locator('[data-testid="submit-button"]').click();
        
        // 验证结果
        const userCard = page.locator(\`[data-testid="user-card-\${user.username}"]\`);
        await expect(userCard).toBeVisible();
        await expect(userCard).toContainText(user.username);
        await expect(userCard).toContainText(user.email);
        await expect(userCard).toContainText(user.role);
      });
    }
  });

  test('应该处理异步操作和加载状态', async ({ page }) => {
    // ✅ 好的做法：等待加载状态完成
    const loadButton = page.locator('[data-testid="load-data-button"]');
    const loadingSpinner = page.locator('[data-testid="loading-spinner"]');
    const dataContainer = page.locator('[data-testid="data-container"]');
    
    // 点击加载按钮
    await loadButton.click();
    
    // 等待加载指示器出现
    await expect(loadingSpinner).toBeVisible();
    
    // 等待加载指示器消失
    await expect(loadingSpinner).toBeHidden();
    
    // 现在数据应该已加载
    await expect(dataContainer).toBeVisible();
    await expect(dataContainer.locator('[data-testid="data-item"]')).toHaveCount(5);
  });

  test('应该处理随机生成的内容', async ({ page }) => {
    // ✅ 好的做法：使用模式匹配而不是精确匹配
    const randomId = page.locator('[data-testid="random-id"]');
    await expect(randomId).toHaveText(/ID-[A-Z0-9]{8}/); // 匹配模式而不是具体值
    
    // ✅ 好的做法：验证随机内容的属性而不是具体值
    const randomColor = page.locator('[data-testid="random-color"]');
    const colorValue = await randomColor.getAttribute('style');
    expect(colorValue).toMatch(/background-color: rgb\\(\\d+, \\d+, \\d+\\)/);
  });

  test('应该处理API响应数据', async ({ page }) => {
    // ✅ 好的做法：等待API响应
    const responsePromise = page.waitForResponse(response => 
      response.url().includes('/api/users') && response.status() === 200
    );
    
    // 触发API调用
    await page.locator('[data-testid="load-users-button"]').click();
    
    // 等待响应
    const response = await responsePromise;
    const responseData = await response.json();
    
    // 验证UI反映了API响应
    const userList = page.locator('[data-testid="user-list"]');
    await expect(userList.locator('[data-testid="user-item"]')).toHaveCount(responseData.users.length);
    
    // 验证具体的数据内容
    for (let i = 0; i < responseData.users.length; i++) {
      const user = responseData.users[i];
      const userElement = userList.locator('[data-testid="user-item"]').nth(i);
      await expect(userElement).toContainText(user.name);
      await expect(userElement).toContainText(user.email);
    }
  });
});
    `;

    const outputPath = path.join(this.config.outputDir, 'best-practice-dynamic-content.spec.js');
    fs.writeFileSync(outputPath, testContent.trim());
    
    return outputPath;
  }

  /**
   * 生成所有最佳实践测试
   */
  async generateAllBestPractices() {
    console.log('生成所有最佳实践测试...');
    
    const results = {
      dataSelectors: this.generateDataAttributeSelectors(),
      pageObjects: this.generatePageObjectPattern(),
      waitStrategies: this.generateWaitStrategies(),
      assertions: this.generateAssertionBestPractices(),
      dynamicContent: this.generateDynamicContentHandling()
    };

    // 创建最佳实践指南文档
    const guideContent = `
# CodeGen最佳实践指南

本指南包含了使用Playwright CodeGen时的最佳实践和推荐模式。

## 1. 选择器最佳实践

### ✅ 推荐做法
- 使用 \`data-testid\` 属性作为首选选择器
- 使用 \`data-cy\` 属性（Cypress风格）
- 使用稳定的属性，避免使用CSS类名

### ❌ 避免做法
- 使用复杂的XPath表达式
- 依赖CSS类名和样式
- 使用位置索引选择器

生成的测试文件: ${results.dataSelectors}

## 2. 页面对象模式

### ✅ 推荐做法
- 将页面元素和操作封装在页面对象类中
- 使用描述性的方法名称
- 保持页面对象的单一职责

生成的测试文件: ${results.pageObjects.test}
页面对象文件: ${results.pageObjects.pageObject}

## 3. 等待策略

### ✅ 推荐做法
- 依赖Playwright的自动等待机制
- 使用明确的等待条件
- 设置合理的超时时间

### ❌ 避免做法
- 使用固定的延时等待
- 过度等待元素出现

生成的测试文件: ${results.waitStrategies}

## 4. 断言最佳实践

### ✅ 推荐做法
- 使用具体的断言方法
- 验证具体的属性值
- 使用适当的文本匹配策略

### ❌ 避免做法
- 使用过于通用的断言
- 只验证元素存在而不验证内容

生成的测试文件: ${results.assertions}

## 5. 动态内容处理

### ✅ 推荐做法
- 使用正则表达式匹配动态文本
- 在截图时屏蔽动态内容
- 使用参数化测试处理多组数据

### ❌ 避免做法
- 硬编码动态生成的值
- 依赖具体的时间戳值

生成的测试文件: ${results.dynamicContent}

## 6. 通用建议

### 代码组织
- 将测试按功能模块分组
- 使用描述性的测试名称
- 添加适当的注释说明

### 性能优化
- 并行执行测试
- 复用浏览器上下文
- 优化选择器策略

### 可维护性
- 定期重构测试代码
- 删除过时的测试
- 保持测试的简洁性

## 7. 验证标准

本最佳实践遵循以下标准：
${JSON.stringify(this.standards, null, 2)}

## 8. 持续改进

定期审查和更新最佳实践，确保它们符合项目需求和技术发展。
    `;

    const guidePath = path.join(this.config.outputDir, 'best-practices-guide.md');
    fs.writeFileSync(guidePath, guideContent.trim());

    console.log(`最佳实践指南已生成: ${guidePath}`);
    
    return {
      results,
      guide: guidePath,
      standards: this.standards
    };
  }
}

/**
 * 演示最佳实践
 */
async function demonstrateBestPractices() {
  console.log('=== CodeGen最佳实践演示 ===\n');

  const bestPracticesManager = new CodegenBestPracticesManager({
    outputDir: './best-practice-tests'
  });

  // 生成所有最佳实践测试
  const results = await bestPracticesManager.generateAllBestPractices();

  console.log('\n生成的文件:');
  console.log('- 数据选择器测试:', results.results.dataSelectors);
  console.log('- 页面对象测试:', results.results.pageObjects.test);
  console.log('- 页面对象类:', results.results.pageObjects.pageObject);
  console.log('- 等待策略测试:', results.results.waitStrategies);
  console.log('- 断言测试:', results.results.assertions);
  console.log('- 动态内容测试:', results.results.dynamicContent);
  console.log('- 最佳实践指南:', results.guide);

  console.log('\n=== 最佳实践演示完成 ===');
  
  return results;
}

// 导出所有功能
module.exports = {
  CodegenBestPracticesManager,
  demonstrateBestPractices
};

// 如果直接运行此文件，执行演示
if (require.main === module) {
  demonstrateBestPractices().catch(console.error);
}
# 第3章：Playwright基础脚本开发

## 3.1 测试脚本结构

### 3.1.1 基本测试结构
Playwright测试基于Jest-like的测试运行器，基本结构如下：
```javascript
const { test, expect } = require('@playwright/test');

test('测试描述', async ({ page }) => {
  // 测试代码
});
```

### 3.1.2 测试套件组织
使用describe块来组织相关的测试：
```javascript
const { test, expect } = require('@playwright/test');

test.describe('用户管理模块', () => {
  test('创建新用户', async ({ page }) => {
    // 测试代码
  });

  test('编辑用户信息', async ({ page }) => {
    // 测试代码
  });
});
```

## 3.2 页面对象模式实现

### 3.2.1 页面对象基础类
```javascript
// base-page.js
class BasePage {
  constructor(page) {
    this.page = page;
  }

  async navigateTo(url) {
    await this.page.goto(url);
  }

  async getTitle() {
    return await this.page.title();
  }
}

module.exports = { BasePage };
```

### 3.2.2 具体页面对象实现
```javascript
// home-page.js
const { BasePage } = require('./base-page');

class HomePage extends BasePage {
  constructor(page) {
    super(page);
    this.searchInput = page.locator('#search-input');
    this.searchButton = page.locator('#search-button');
  }

  async search(keyword) {
    await this.searchInput.fill(keyword);
    await this.searchButton.click();
  }
}

module.exports = { HomePage };
```

## 3.3 数据驱动测试

### 3.3.1 使用test.each进行参数化测试
```javascript
const { test, expect } = require('@playwright/test');

test.describe('登录功能测试', () => {
  test.each([
    ['validuser', 'correctpass', true],
    ['invaliduser', 'wrongpass', false],
    ['', 'anypass', false],
  ])('登录测试 username=%s, password=%s', async ({ page }, username, password, expected) => {
    // 测试代码
  });
});
```

### 3.3.2 从外部文件加载测试数据
```javascript
// test-data.js
const testData = {
  users: [
    { username: 'user1', password: 'pass1' },
    { username: 'user2', password: 'pass2' }
  ]
};

module.exports = { testData };
```

## 3.4 测试前置和后置条件

### 3.4.1 beforeEach和afterEach
```javascript
const { test } = require('@playwright/test');

test.beforeEach(async ({ page }) => {
  // 每个测试前执行
  await page.goto('/login');
});

test.afterEach(async ({ page }) => {
  // 每个测试后执行
  await page.close();
});
```

### 3.4.2 beforeAll和afterAll
```javascript
const { test } = require('@playwright/test');

test.beforeAll(async () => {
  // 所有测试前执行一次
  console.log('开始执行测试套件');
});

test.afterAll(async () => {
  // 所有测试后执行一次
  console.log('测试套件执行完毕');
});
```

## 3.5 错误处理和日志记录

### 3.5.1 异常捕获
```javascript
const { test, expect } = require('@playwright/test');

test('错误处理示例', async ({ page }) => {
  try {
    await page.goto('/problematic-page');
    // 可能出错的操作
  } catch (error) {
    console.error('测试过程中发生错误:', error.message);
    throw error; // 重新抛出错误以标记测试失败
  }
});
```

### 3.5.2 自定义日志记录
```javascript
const { test } = require('@playwright/test');

test('带日志的测试', async ({ page }) => {
  console.log('开始导航到首页');
  await page.goto('/');
  console.log('首页加载完成');
  
  console.log('开始搜索操作');
  await page.fill('#search', 'Playwright');
  await page.click('#search-button');
  console.log('搜索操作完成');
});
```

## 3.6 实验：构建完整的用户注册流程测试

### 3.6.1 实验目标
编写一个完整的用户注册流程测试，包括数据验证、表单提交和成功验证。

### 3.6.2 实验步骤
1. 创建注册页面对象
2. 编写注册测试脚本
3. 添加数据验证
4. 验证注册成功

### 3.6.3 实验代码
```javascript
// register-page.js
class RegisterPage {
  constructor(page) {
    this.page = page;
    this.usernameInput = page.locator('#username');
    this.emailInput = page.locator('#email');
    this.passwordInput = page.locator('#password');
    this.confirmPasswordInput = page.locator('#confirm-password');
    this.registerButton = page.locator('#register-button');
  }

  async register(username, email, password) {
    await this.usernameInput.fill(username);
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.confirmPasswordInput.fill(password);
    await this.registerButton.click();
  }
}

module.exports = { RegisterPage };
```

```javascript
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
```

## 3.7 最佳实践

### 3.7.1 代码组织
- 将页面对象放在单独的目录中
- 按功能模块组织测试文件
- 使用清晰的命名约定

### 3.7.2 可维护性
- 避免在测试代码中硬编码值
- 使用配置文件管理环境变量
- 定期重构重复代码

### 3.7.3 性能优化
- 合理使用beforeAll减少重复操作
- 避免不必要的等待
- 并行执行独立的测试

## 3.8 总结
本章介绍了Playwright基础脚本开发的核心概念，包括测试结构、页面对象模式、数据驱动测试、前置后置条件处理等内容。通过实际示例和实验，帮助读者掌握如何构建可维护、可扩展的自动化测试脚本。
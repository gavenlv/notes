# 第2章 Playwright基础概念与核心组件

## 2.1 Playwright核心概念

### 2.1.1 浏览器上下文（Browser Context）

浏览器上下文是Playwright中一个重要的概念，它相当于浏览器中的一个独立会话。每个上下文都有自己的cookies、缓存、本地存储等，彼此之间完全隔离。

```javascript
// 创建浏览器上下文
const context = await browser.newContext();

// 在上下文中创建页面
const page = await context.newPage();
```

### 2.1.2 页面（Page）

页面代表浏览器中的一个标签页。它是与网页交互的主要接口，可以执行导航、点击、输入等操作。

```javascript
// 导航到页面
await page.goto('https://example.com');

// 点击元素
await page.click('#button');

// 输入文本
await page.fill('#input', 'Hello World');
```

### 2.1.3 选择器（Selectors）

选择器用于定位页面中的元素。Playwright支持多种选择器类型：

1. **CSS选择器**
   ```javascript
   await page.click('.button');
   await page.fill('#username', 'testuser');
   ```

2. **文本选择器**
   ```javascript
   await page.click('text=登录');
   await page.click('text="Submit Form"');
   ```

3. **XPath选择器**
   ```javascript
   await page.click('xpath=//button[@id="submit"]');
   ```

4. **链式选择器**
   ```javascript
   await page.click('css=div.card >> text=查看详情');
   ```

### 2.1.4 定位器（Locators）

定位器是Playwright推荐的元素定位方式，它比直接使用选择器更安全和可靠。

```javascript
// 创建定位器
const loginButton = page.locator('#login-button');

// 使用定位器执行操作
await loginButton.click();
await loginButton.isVisible();
```

## 2.2 Playwright架构

### 2.2.1 浏览器驱动

Playwright通过浏览器驱动与浏览器进行通信。每个浏览器都有对应的驱动程序：

- Chromium使用Chrome DevTools Protocol
- Firefox使用WebDriver
- WebKit使用自己的协议

### 2.2.2 测试运行器

Playwright内置了测试运行器，支持：

- 并行执行测试
- 自动重试失败的测试
- 生成详细的测试报告
- 截图和视频录制

### 2.2.3 断言库

Playwright提供了丰富的断言方法：

```javascript
// 页面标题断言
await expect(page).toHaveTitle('Expected Title');

// URL断言
await expect(page).toHaveURL('https://example.com');

// 元素可见性断言
await expect(locator).toBeVisible();

// 文本内容断言
await expect(locator).toHaveText('Expected Text');
```

## 2.3 页面对象模型（Page Object Model）

页面对象模型是一种设计模式，用于将页面元素和操作封装在类中，提高代码的可维护性和可重用性。

### 2.3.1 创建页面对象

```javascript
// login-page.js
class LoginPage {
  constructor(page) {
    this.page = page;
    this.usernameInput = page.locator('#username');
    this.passwordInput = page.locator('#password');
    this.loginButton = page.locator('#login-button');
  }

  async navigate() {
    await this.page.goto('/login');
  }

  async login(username, password) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }
}

module.exports = { LoginPage };
```

### 2.3.2 使用页面对象

```javascript
// login-test.spec.js
const { test } = require('@playwright/test');
const { LoginPage } = require('./pages/login-page');

test('用户登录测试', async ({ page }) => {
  const loginPage = new LoginPage(page);
  
  await loginPage.navigate();
  await loginPage.login('testuser', 'password123');
  
  // 验证登录成功
  await expect(page).toHaveURL('/dashboard');
});
```

## 2.4 Playwright中的等待机制

### 2.4.1 自动等待

Playwright的大多数操作都会自动等待元素出现：

```javascript
// 自动等待元素出现
await page.click('#submit-button');

// 自动等待文本出现
await expect(page.locator('#message')).toHaveText('操作成功');
```

### 2.4.2 显式等待

当需要更精确的控制时，可以使用显式等待：

```javascript
// 等待元素可见
await page.waitForSelector('#loading', { state: 'visible' });

// 等待元素隐藏
await page.waitForSelector('#loading', { state: 'hidden' });

// 等待网络空闲
await page.waitForLoadState('networkidle');
```

## 2.5 网络拦截与模拟

### 2.5.1 拦截请求

```javascript
// 拦截并修改请求
await page.route('**/api/users', route => {
  route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify([{ id: 1, name: 'Mock User' }])
  });
});
```

### 2.5.2 模拟响应

```javascript
// 模拟慢速网络
await page.route('**/api/**', route => {
  setTimeout(() => route.continue(), 2000); // 延迟2秒
});
```

## 2.6 实验：核心组件实践

### 实验1：浏览器上下文隔离

创建`tests/context-isolation.spec.js`：

```javascript
const { test } = require('@playwright/test');

test('浏览器上下文隔离测试', async ({ browser }) => {
  // 创建第一个上下文
  const context1 = await browser.newContext();
  const page1 = await context1.newPage();
  
  // 创建第二个上下文
  const context2 = await browser.newContext();
  const page2 = await context2.newPage();
  
  // 在第一个上下文中登录
  await page1.goto('https://example.com/login');
  await page1.fill('#username', 'user1');
  await page1.fill('#password', 'pass1');
  await page1.click('#login');
  
  // 在第二个上下文中访问页面
  await page2.goto('https://example.com/dashboard');
  
  // 验证两个上下文是隔离的
  // 第二个上下文应该未登录
  await page2.waitForSelector('#login-form');
  
  // 清理
  await context1.close();
  await context2.close();
});
```

### 实验2：页面对象模型实践

创建`pages/search-page.js`：

```javascript
class SearchPage {
  constructor(page) {
    this.page = page;
    this.searchInput = page.locator('#search-input');
    this.searchButton = page.locator('#search-button');
    this.results = page.locator('.search-results');
  }

  async navigate() {
    await this.page.goto('/search');
  }

  async search(query) {
    await this.searchInput.fill(query);
    await this.searchButton.click();
    // 等待结果加载
    await this.page.waitForSelector('.search-results');
  }

  async getResultCount() {
    const count = await this.results.locator('.result-item').count();
    return count;
  }
}

module.exports = { SearchPage };
```

创建`tests/search-test.spec.js`：

```javascript
const { test, expect } = require('@playwright/test');
const { SearchPage } = require('../pages/search-page');

test('搜索功能测试', async ({ page }) => {
  const searchPage = new SearchPage(page);
  
  await searchPage.navigate();
  await searchPage.search('Playwright');
  
  const resultCount = await searchPage.getResultCount();
  console.log(`找到 ${resultCount} 个结果`);
  
  // 验证至少有一个结果
  await expect(resultCount).toBeGreaterThan(0);
});
```

## 2.7 最佳实践

### 2.7.1 使用定位器而非选择器

```javascript
// 推荐：使用定位器
const loginButton = page.locator('#login-button');
await loginButton.click();

// 不推荐：直接使用选择器
await page.click('#login-button');
```

### 2.7.2 合理使用页面对象模型

```javascript
// 对于复杂的页面，使用页面对象模型
class DashboardPage {
  constructor(page) {
    this.page = page;
    this.userMenu = page.locator('.user-menu');
    this.logoutButton = page.locator('#logout');
  }
  
  async logout() {
    await this.userMenu.click();
    await this.logoutButton.click();
  }
}
```

### 2.7.3 合理设置超时时间

```javascript
// 在配置文件中设置合理的超时时间
module.exports = {
  timeout: 30000, // 30秒测试超时
  expect: {
    timeout: 5000  // 5秒断言超时
  }
};
```

## 2.8 本章小结

在本章中，我们深入学习了Playwright的核心概念和组件：

1. **浏览器上下文**：理解上下文的隔离特性
2. **页面对象**：掌握页面交互的基本单位
3. **选择器和定位器**：学会准确定位页面元素
4. **页面对象模型**：提高代码的可维护性
5. **等待机制**：理解自动等待和显式等待
6. **网络控制**：拦截和模拟网络请求

这些概念是Playwright测试开发的基础，掌握它们对于编写高质量的自动化测试至关重要。

## 2.9 练习题

1. 创建一个页面对象模型来封装电商网站的商品搜索功能
2. 实现浏览器上下文隔离的测试，验证不同用户会话的独立性
3. 使用不同的选择器类型定位同一个页面元素，并比较它们的优缺点
4. 实现一个网络拦截器，模拟API响应延迟
5. 编写一个测试，验证页面加载状态的正确处理
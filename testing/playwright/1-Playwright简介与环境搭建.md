# 第1章 Playwright简介与环境搭建

## 1.1 什么是Playwright？

Playwright是一个现代化的端到端Web测试框架，由Microsoft开发并开源。它专为现代Web应用程序设计，支持所有主流浏览器（Chromium、Firefox、WebKit），可以在Windows、Linux和macOS上运行。

### 1.1.1 Playwright的特点

1. **跨浏览器支持**
   - Chromium（Chrome、Edge）
   - Firefox
   - WebKit（Safari）

2. **自动化能力**
   - 自动等待元素出现
   - 模拟真实用户行为
   - 支持移动端测试

3. **强大的网络控制**
   - 拦截和修改网络请求
   - 模拟各种网络条件
   - 处理认证和权限

4. **并行执行**
   - 支持多浏览器并行测试
   - 测试隔离确保稳定性

### 1.1.2 Playwright与其他测试框架的对比

| 特性 | Playwright | Selenium | Cypress |
|------|------------|----------|---------|
| 浏览器支持 | 所有主流浏览器 | 所有主流浏览器 | Chrome, Firefox, Edge |
| 自动等待 | 是 | 否 | 是 |
| 移动端测试 | 是 | 是 | 否 |
| 并行执行 | 是 | 是 | 是 |
| 网络拦截 | 是 | 有限 | 是 |
| 跨域测试 | 是 | 是 | 否 |

## 1.2 环境准备

### 1.2.1 系统要求

- Node.js版本14或更高
- Windows、Linux或macOS操作系统
- 至少4GB RAM（推荐8GB以上）

### 1.2.2 安装Node.js

1. 访问Node.js官方网站：https://nodejs.org/
2. 下载LTS版本（长期支持版本）
3. 运行安装程序并按照提示完成安装
4. 验证安装：
   ```bash
   node --version
   npm --version
   ```

## 1.3 安装Playwright

### 1.3.1 初始化项目

首先创建一个新的项目目录：

```bash
mkdir playwright-tutorial
cd playwright-tutorial
npm init -y
```

### 1.3.2 安装Playwright

使用npm安装Playwright：

```bash
npm install --save-dev @playwright/test
```

### 1.3.3 安装浏览器

Playwright需要安装浏览器才能运行测试：

```bash
npx playwright install
```

此命令会自动安装所有支持的浏览器（Chromium、Firefox、WebKit）。

如果你想只安装特定浏览器，可以指定浏览器名称：

```bash
# 只安装Chromium
npx playwright install chromium

# 只安装Firefox
npx playwright install firefox

# 只安装WebKit
npx playwright install webkit
```

## 1.4 第一个Playwright测试

### 1.4.1 创建测试文件

创建一个名为`first-test.spec.js`的文件：

```javascript
const { test, expect } = require('@playwright/test');

test('我的第一个Playwright测试', async ({ page }) => {
  // 导航到网页
  await page.goto('https://playwright.dev');
  
  // 断言页面标题
  await expect(page).toHaveTitle(/Playwright/);
  
  // 点击"Get started"链接
  await page.click('text=Get started');
  
  // 断言URL包含intro
  await expect(page).toHaveURL(/.*intro/);
});
```

### 1.4.2 运行测试

在终端中运行以下命令：

```bash
npx playwright test
```

### 1.4.3 查看测试报告

测试完成后，可以通过以下命令查看HTML报告：

```bash
npx playwright show-report
```

## 1.5 Playwright配置文件

### 1.5.1 创建配置文件

创建`playwright.config.js`文件来配置Playwright：

```javascript
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
```

## 1.6 实验：环境验证

### 实验1：验证Playwright安装

创建`tests/environment-check.spec.js`：

```javascript
const { test, expect } = require('@playwright/test');

test('验证Playwright环境', async ({ page }) => {
  // 检查是否能访问Google
  await page.goto('https://www.google.com');
  
  // 检查页面标题
  const title = await page.title();
  console.log('页面标题:', title);
  
  // 断言标题包含Google
  await expect(title).toContain('Google');
  
  // 检查搜索框是否存在
  const searchBox = await page.$('[name="q"]');
  await expect(searchBox).toBeTruthy();
});
```

运行测试：
```bash
npx playwright test tests/environment-check.spec.js
```

### 实验2：多浏览器测试

创建`tests/multi-browser.spec.js`：

```javascript
const { test, expect } = require('@playwright/test');

test('在不同浏览器中测试百度', async ({ page }) => {
  // 导航到百度
  await page.goto('https://www.baidu.com');
  
  // 检查页面标题
  await expect(page).toHaveTitle(/百度一下/);
  
  // 检查搜索框
  const searchInput = page.locator('#kw');
  await expect(searchInput).toBeVisible();
  
  // 输入搜索词
  await searchInput.fill('Playwright');
  
  // 点击搜索按钮
  await page.click('#su');
  
  // 等待结果页面加载
  await page.waitForSelector('#content_left');
  
  // 检查结果中是否包含Playwright相关内容
  const firstResult = page.locator('.result:first-child');
  await expect(firstResult).toContainText('Playwright');
});
```

## 1.7 常见问题解决

### 1.7.1 安装问题

如果遇到安装问题，可以尝试以下解决方案：

1. 清除npm缓存：
   ```bash
   npm cache clean --force
   ```

2. 删除node_modules并重新安装：
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

3. 重新安装Playwright浏览器：
   ```bash
   npx playwright install-deps
   npx playwright install
   ```

### 1.7.2 权限问题

在Linux或macOS上，如果遇到权限问题：

```bash
# 使用sudo安装依赖
sudo npx playwright install-deps

# 或者更改npm全局目录
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
export PATH=~/.npm-global/bin:$PATH
```

## 1.8 本章小结

在本章中，我们学习了：

1. Playwright是什么及其主要特点
2. 如何安装和配置Playwright环境
3. 如何编写和运行第一个Playwright测试
4. Playwright配置文件的基本结构
5. 通过实验验证环境配置正确性

下一章我们将深入了解Playwright的核心概念和组件，包括页面对象模型、选择器等重要内容。

## 1.9 练习题

1. 安装Playwright并验证三个浏览器都能正常工作
2. 编写一个测试脚本，访问你常用的网站并验证其功能
3. 修改配置文件，添加更多的测试选项
4. 运行多个测试并查看生成的报告
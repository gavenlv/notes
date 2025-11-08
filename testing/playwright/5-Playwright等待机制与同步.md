# 第5章：Playwright等待机制与同步

## 5.1 等待机制概述

### 5.1.1 自动等待
Playwright内置了智能等待机制，大多数操作会自动等待元素达到可操作状态：
```javascript
// 自动等待元素可见并可点击
await page.locator('#submit-button').click();

// 自动等待元素可见并可填写
await page.locator('#username').fill('testuser');
```

### 5.1.2 等待超时设置
```javascript
// 设置全局超时
const { test } = require('@playwright/test');
test.use({ timeout: 60000 });

// 设置单个操作超时
await page.locator('#element').click({ timeout: 30000 });
```

## 5.2 显式等待

### 5.2.1 等待元素状态
```javascript
// 等待元素可见
await page.waitForSelector('#element', { state: 'visible' });

// 等待元素隐藏
await page.waitForSelector('#element', { state: 'hidden' });

// 等待元素被附加到DOM
await page.waitForSelector('#element', { state: 'attached' });

// 等待元素从DOM中分离
await page.waitForSelector('#element', { state: 'detached' });
```

### 5.2.2 等待页面加载状态
```javascript
// 等待DOM加载完成
await page.waitForLoadState('domcontentloaded');

// 等待网络空闲
await page.waitForLoadState('networkidle');

// 等待页面加载完成
await page.waitForLoadState('load');
```

### 5.2.3 等待函数条件
```javascript
// 等待自定义条件
await page.waitForFunction(() => {
  return document.querySelector('#status').innerText === 'Complete';
});

// 带参数的等待函数
await page.waitForFunction((expectedText) => {
  return document.querySelector('#message').innerText.includes(expectedText);
}, 'Success');
```

## 5.3 网络等待

### 5.3.1 等待网络请求
```javascript
// 等待特定URL的响应
const [response] = await Promise.all([
  page.waitForResponse('**/api/data'),
  page.click('#load-data-button')
]);
expect(response.status()).toBe(200);

// 等待特定请求
const [request] = await Promise.all([
  page.waitForRequest('**/api/submit'),
  page.click('#submit-button')
]);
expect(request.method()).toBe('POST');
```

### 5.3.2 等待网络空闲
```javascript
// 等待所有网络请求完成
await page.goto('/page-with-ajax');
await page.waitForLoadState('networkidle');

// 检查网络请求
const response = await page.waitForResponse('**/api/**');
console.log(`请求URL: ${response.url()}`);
console.log(`响应状态: ${response.status()}`);
```

## 5.4 异步操作同步

### 5.4.1 Promise处理
```javascript
// 处理多个并行操作
const [loginResponse, userDataResponse] = await Promise.all([
  page.waitForResponse('**/login'),
  page.waitForResponse('**/user-data'),
  page.click('#login-button')
]);

// 验证所有响应
expect(loginResponse.status()).toBe(200);
expect(userDataResponse.status()).toBe(200);
```

### 5.4.2 条件等待
```javascript
// 等待元素文本变化
await page.waitForFunction(() => {
  return document.querySelector('#status').textContent.trim().length > 0;
});

// 等待元素属性变化
await page.waitForFunction(() => {
  return document.querySelector('#progress').getAttribute('value') === '100';
});
```

## 5.5 实验：处理动态加载内容

### 5.5.1 实验目标
编写测试脚本处理包含动态加载内容的页面，确保在内容加载完成后再进行操作。

### 5.5.2 实验步骤
1. 创建动态内容页面对象
2. 编写等待动态内容加载的测试
3. 验证内容加载后的操作

### 5.5.3 实验代码
```javascript
// dynamic-content-page.js
class DynamicContentPage {
  constructor(page) {
    this.page = page;
    this.contentArea = page.locator('#content-area');
    this.loadButton = page.locator('#load-content');
  }

  async loadContent() {
    await this.loadButton.click();
    // 等待内容加载完成
    await this.page.waitForSelector('#content-area .loaded-content', { state: 'visible' });
  }

  async waitForProgressComplete() {
    await this.page.waitForFunction(() => {
      const progress = document.querySelector('#progress');
      return progress && progress.getAttribute('value') === '100';
    });
  }
}

module.exports = { DynamicContentPage };
```

```javascript
// dynamic-content-test.spec.js
const { test, expect } = require('@playwright/test');
const { DynamicContentPage } = require('../pages/dynamic-content-page');

test('动态内容加载测试', async ({ page }) => {
  const dynamicPage = new DynamicContentPage(page);
  
  // 导航到页面
  await page.goto('/dynamic-content');
  
  // 触发内容加载
  await dynamicPage.loadContent();
  
  // 验证内容已加载
  await expect(dynamicPage.contentArea).toContainText('加载完成');
  
  // 等待进度条完成
  await dynamicPage.waitForProgressComplete();
  
  // 验证进度条状态
  const progressValue = await page.getAttribute('#progress', 'value');
  expect(progressValue).toBe('100');
});
```

## 5.6 最佳实践

### 5.6.1 合理使用等待
- 优先使用自动等待
- 避免硬编码等待时间
- 根据具体场景选择合适的等待策略

### 5.6.2 超时设置
- 为不同操作设置合理的超时时间
- 在测试配置中统一管理超时设置
- 避免过长的超时导致测试执行时间过长

### 5.6.3 错误处理
- 捕获等待超时异常
- 提供有意义的错误信息
- 实现重试机制处理不稳定的等待

## 5.7 总结
本章详细介绍了Playwright的等待机制与同步技术，包括自动等待、显式等待、网络等待和异步操作同步等内容。通过实际示例和实验，帮助读者掌握如何处理动态加载内容和复杂的异步操作，确保测试脚本的稳定性和可靠性。
# 第4章：Playwright高级元素操作

## 4.1 选择器深入解析

### 4.1.1 CSS选择器高级用法
Playwright支持标准CSS选择器，并提供了一些扩展功能：
```javascript
// 属性选择器
await page.locator('[data-testid="submit-button"]');

// 伪类选择器
await page.locator('button:enabled');
await page.locator('input:focus');

// 组合选择器
await page.locator('form#login .form-group input[type="text"]');
```

### 4.1.2 XPath选择器
对于复杂的元素定位，可以使用XPath：
```javascript
// 基本XPath
await page.locator('xpath=//button[@id="submit"]');

// 复杂XPath
await page.locator('xpath=//div[@class="container"]//span[contains(text(), "Hello")]');
```

### 4.1.3 文本选择器
通过文本内容定位元素：
```javascript
// 精确匹配
await page.locator('text=Submit');

// 部分匹配
await page.locator(':text("Submit")');
await page.locator(':text-is("Submit")');
```

## 4.2 定位器链式操作

### 4.2.1 父子元素定位
```javascript
// 从父元素查找子元素
const form = page.locator('form#registration');
await form.locator('input#username').fill('testuser');

// 从子元素查找父元素
const input = page.locator('input#username');
await input.locator('xpath=..').click(); // 点击父元素
```

### 4.2.2 兄弟元素定位
```javascript
// 查找下一个兄弟元素
await page.locator('label:has-text("Username") + input').fill('testuser');

// 查找所有兄弟元素
await page.locator('div.item ~ div.item').count();
```

## 4.3 动态元素处理

### 4.3.1 等待元素出现
```javascript
// 等待元素可见
await page.waitForSelector('#dynamic-element', { state: 'visible' });

// 等待元素可点击
await page.waitForSelector('#submit-button', { state: 'visible' });
await page.locator('#submit-button').click();
```

### 4.3.2 处理动态内容
```javascript
// 等待文本出现
await page.waitForSelector(':text("Success")');

// 等待元素属性变化
await page.waitForSelector('#status', { 
  state: 'visible',
  timeout: 5000
});
```

## 4.4 元素状态检查

### 4.4.1 检查元素可见性
```javascript
const element = page.locator('#element-id');

// 检查是否可见
const isVisible = await element.isVisible();

// 检查是否启用
const isEnabled = await element.isEnabled();

// 检查是否可编辑
const isEditable = await element.isEditable();
```

### 4.4.2 检查元素内容
```javascript
const element = page.locator('#text-element');

// 获取文本内容
const text = await element.textContent();

// 获取输入框值
const value = await page.locator('#input-field').inputValue();

// 检查是否包含特定文本
const containsText = (await element.textContent()).includes('expected text');
```

## 4.5 复杂交互操作

### 4.5.1 拖放操作
```javascript
// 拖放元素
await page.locator('#draggable').dragTo(page.locator('#droppable'));

// 或者使用更精确的控制
await page.locator('#draggable').hover();
await page.mouse.down();
await page.locator('#droppable').hover();
await page.mouse.up();
```

### 4.5.2 右键菜单操作
```javascript
// 右键点击元素
await page.locator('#element').click({ button: 'right' });

// 点击右键菜单项
await page.locator('.context-menu-item:has-text("Copy")').click();
```

### 4.5.3 键盘操作
```javascript
// 模拟按键
await page.locator('#input').press('Enter');
await page.locator('#input').press('Control+A');
await page.locator('#input').press('Delete');

// 组合键
await page.locator('#input').press('Control+V');
```

## 4.6 实验：电商网站购物车操作自动化

### 4.6.1 实验目标
实现一个完整的电商网站购物车操作流程，包括商品选择、添加到购物车、修改数量、删除商品等操作。

### 4.6.2 实验步骤
1. 创建商品页面对象
2. 创建购物车页面对象
3. 编写添加商品到购物车的测试
4. 编写修改商品数量的测试
5. 编写删除商品的测试

### 4.6.3 实验代码
```javascript
// product-page.js
class ProductPage {
  constructor(page) {
    this.page = page;
    this.addToCartButton = page.locator('#add-to-cart');
    this.quantityInput = page.locator('#quantity');
  }

  async addToCart(quantity = 1) {
    await this.quantityInput.fill(quantity.toString());
    await this.addToCartButton.click();
  }
}

module.exports = { ProductPage };
```

```javascript
// cart-page.js
class CartPage {
  constructor(page) {
    this.page = page;
    this.cartItems = page.locator('.cart-item');
  }

  async updateItemQuantity(itemName, quantity) {
    const item = this.cartItems.filter({ hasText: itemName });
    await item.locator('.quantity-input').fill(quantity.toString());
    await item.locator('.update-button').click();
  }

  async removeItem(itemName) {
    const item = this.cartItems.filter({ hasText: itemName });
    await item.locator('.remove-button').click();
  }

  async getItemQuantity(itemName) {
    const item = this.cartItems.filter({ hasText: itemName });
    return await item.locator('.quantity-input').inputValue();
  }
}

module.exports = { CartPage };
```

```javascript
// cart-test.spec.js
const { test, expect } = require('@playwright/test');
const { ProductPage } = require('../pages/product-page');
const { CartPage } = require('../pages/cart-page');

test('购物车操作测试', async ({ page }) => {
  const productPage = new ProductPage(page);
  const cartPage = new CartPage(page);
  
  // 导航到商品页面并添加商品到购物车
  await page.goto('/product/123');
  await productPage.addToCart(2);
  
  // 导航到购物车页面
  await page.goto('/cart');
  
  // 验证商品已添加
  const quantity = await cartPage.getItemQuantity('Product Name');
  expect(quantity).toBe('2');
  
  // 更新商品数量
  await cartPage.updateItemQuantity('Product Name', 3);
  
  // 验证数量已更新
  const updatedQuantity = await cartPage.getItemQuantity('Product Name');
  expect(updatedQuantity).toBe('3');
  
  // 删除商品
  await cartPage.removeItem('Product Name');
  
  // 验证商品已删除
  await expect(cartPage.cartItems).not.toContainText('Product Name');
});
```

## 4.7 最佳实践

### 4.7.1 选择器稳定性
- 优先使用data-testid属性
- 避免使用可能变化的文本内容作为选择器
- 使用结构化的CSS类名

### 4.7.2 元素交互可靠性
- 在交互前检查元素状态
- 合理使用等待机制
- 处理动态内容的变化

### 4.7.3 错误处理
- 捕获元素定位失败的异常
- 提供有意义的错误信息
- 实现重试机制

## 4.8 总结
本章深入探讨了Playwright中的高级元素操作技术，包括选择器的高级用法、定位器链式操作、动态元素处理、元素状态检查和复杂交互操作。通过电商购物车的实际案例，展示了如何将这些技术应用到真实的自动化测试场景中。
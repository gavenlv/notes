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
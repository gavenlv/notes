// tests/framework-test.spec.js
const { test, expect } = require('@playwright/test');
const { HomePage } = require('../pages/home-page');
const { UserFactory } = require('../data/user-factory');
const { TestDataProvider } = require('../data/test-data-provider');

test.describe('框架测试套件', () => {
  let homePage;

  test.beforeEach(async ({ page }) => {
    homePage = new HomePage(page);
    await homePage.navigateTo('/');
  });

  test('基础页面导航测试', async ({ page }) => {
    const title = await homePage.getTitle();
    expect(title).toContain('首页');
  });

  test('用户数据工厂测试', async ({ page }) => {
    const validUser = UserFactory.createValidUser();
    const invalidUser = UserFactory.createInvalidUser();
    
    expect(validUser.username).toMatch(/^user_\d+$/);
    expect(validUser.email).toMatch(/^user_\d+@example.com$/);
    expect(validUser.password).toBe('Password123!');
    
    expect(invalidUser.username).toBe('');
    expect(invalidUser.email).toBe('invalid-email');
    expect(invalidUser.password).toBe('123');
  });

  test('测试数据提供者测试', async ({ page }) => {
    // 创建示例JSON数据文件
    const testData = [
      { name: 'iPhone 13', price: 999 },
      { name: 'MacBook Pro', price: 1999 }
    ];
    
    // 这里只是演示数据结构，实际使用时需要创建真实的JSON文件
    expect(testData).toHaveLength(2);
    expect(testData[0].name).toBe('iPhone 13');
    expect(testData[0].price).toBe(999);
  });

  test('页面对象方法测试', async ({ page }) => {
    // 这里只是演示页面对象的方法调用
    // 实际测试中需要根据页面元素进行验证
    await homePage.search('Playwright');
    await homePage.openUserMenu();
  });
});
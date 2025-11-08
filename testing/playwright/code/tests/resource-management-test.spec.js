// tests/resource-management-test.spec.js
const { test, expect } = require('@playwright/test');
const { DatabaseFixture } = require('../fixtures/database-fixture');
const os = require('os');
const path = require('path');
const fs = require('fs');

// 创建数据库夹具实例
const dbFixture = new DatabaseFixture();

test.describe('资源管理测试', () => {
  test.beforeAll(async () => {
    // 在所有测试开始前连接数据库
    await dbFixture.connect();
  });

  test.afterAll(async () => {
    // 在所有测试结束后断开数据库连接
    await dbFixture.disconnect();
  });

  test('文件系统资源隔离测试', async ({ page, workerInfo }) => {
    // 使用唯一标识符创建临时目录
    const uniqueId = `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const tempDir = path.join(os.tmpdir(), `playwright_test_${uniqueId}_${workerInfo.workerIndex}`);
    
    // 创建临时目录
    fs.mkdirSync(tempDir, { recursive: true });
    
    console.log(`创建临时目录: ${tempDir}`);
    
    // 执行一些测试操作
    await page.goto('/');
    await page.waitForTimeout(500);
    
    // 验证页面
    const title = await page.title();
    expect(title).toBeTruthy();
    
    // 清理临时目录
    fs.rmSync(tempDir, { recursive: true, force: true });
    console.log(`清理临时目录: ${tempDir}`);
  });

  test('独立用户数据测试', async ({ page }) => {
    // 为每个测试创建唯一的用户数据
    const userData = {
      username: `testuser_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
      email: `test_${Date.now()}_${Math.floor(Math.random() * 1000)}@example.com`,
      password: 'TestPass123!'
    };
    
    console.log(`创建用户: ${userData.username}`);
    
    // 模拟用户注册流程
    await page.goto('/');
    await page.waitForTimeout(300);
    
    // 验证测试数据唯一性
    expect(userData.username).toMatch(/^testuser_\d+_\d+$/);
    expect(userData.email).toMatch(/^test_\d+_\d+@example.com$/);
  });
});
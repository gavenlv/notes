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
    await expect(timestamp).toHaveText(/\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}/); // 匹配模式而不是具体值
    
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
      await test.step(`测试用户: ${user.username}`, async () => {
        // 使用测试数据填充表单
        await page.locator('[data-testid="username-input"]').fill(user.username);
        await page.locator('[data-testid="email-input"]').fill(user.email);
        await page.locator('[data-testid="role-select"]').selectOption(user.role);
        
        // 提交表单
        await page.locator('[data-testid="submit-button"]').click();
        
        // 验证结果
        const userCard = page.locator(`[data-testid="user-card-${user.username}"]`);
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
    expect(colorValue).toMatch(/background-color: rgb\(\d+, \d+, \d+\)/);
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
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
    await expect(page).toHaveURL(/user=d+/);
    
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
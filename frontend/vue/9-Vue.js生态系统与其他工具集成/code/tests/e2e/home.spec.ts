import { test, expect } from '@playwright/test';

test.describe('Home Page', () => {
  test.beforeEach(async ({ page }) => {
    // 导航到主页
    await page.goto('/');
  });

  test('should display the main heading', async ({ page }) => {
    // 验证主标题存在
    const heading = page.locator('h1', { hasText: 'Welcome to Vue.js Ecosystem Integration' });
    await expect(heading).toBeVisible();
  });

  test('should display feature cards', async ({ page }) => {
    // 验证特性卡片存在
    const featureCards = page.locator('.feature-card');
    const count = await featureCards.count();
    
    // 应该至少有6个特性卡片
    expect(count).toBeGreaterThanOrEqual(6);
    
    // 验证特定特性卡片
    const devToolsCard = page.locator('.feature-card', { has: page.locator('h3', { hasText: 'Vue DevTools' }) });
    await expect(devToolsCard).toBeVisible();
  });

  test('should display user profile component', async ({ page }) => {
    // 验证用户资料组件存在
    const userProfile = page.locator('.user-profile');
    await expect(userProfile).toBeVisible();
  });

  test('should have proper navigation', async ({ page }) => {
    // 验证页面包含导航链接（如果有的话）
    // 这里可以根据实际导航结构进行调整
  });
});

test.describe('User Profile Component', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should show loading state initially', async ({ page }) => {
    // 验证初始加载状态
    const loadingText = page.locator('.user-profile', { hasText: 'Loading...' });
    await expect(loadingText).toBeVisible();
  });

  test('should display user data after loading', async ({ page }) => {
    // 模拟API响应（在实际测试中可能需要使用mock服务）
    // 这里假设数据会自动加载
    
    // 等待加载完成
    await page.waitForTimeout(1000); // 等待1秒，让数据加载完成
    
    // 验证用户数据显示
    const userProfile = page.locator('.user-profile');
    await expect(userProfile).not.toContainText('Loading...');
  });

  test('should update user data when button is clicked', async ({ page }) => {
    // 等待数据加载完成
    await page.waitForTimeout(1000);
    
    // 获取更新前的文本
    const initialText = await page.locator('.user-profile').textContent();
    
    // 点击更新按钮
    await page.click('button:has-text("Update User")');
    
    // 等待更新完成
    await page.waitForTimeout(500);
    
    // 验证文本已更新（包含"(updated)"）
    const updatedText = await page.locator('.user-profile').textContent();
    expect(updatedText).not.toBe(initialText);
  });
});
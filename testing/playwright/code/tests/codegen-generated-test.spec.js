// tests/codegen-generated-test.spec.js
const { test, expect } = require('@playwright/test');

/**
 * CodeGen生成的测试用例示例
 * 展示如何使用CodeGen工具生成的测试代码
 */

test.describe('CodeGen生成的测试用例', () => {
  
  test.beforeEach(async ({ page }) => {
    // 访问测试页面
    await page.goto('https://demo.playwright.dev/todomvc/');
  });

  test('基本的待办事项添加 - CodeGen风格', async ({ page }) => {
    // 这是典型的CodeGen生成的代码风格
    await page.click('[placeholder="What needs to be done?"]');
    await page.fill('[placeholder="What needs to be done?"]', 'Buy groceries');
    await page.press('[placeholder="What needs to be done?"]', 'Enter');

    // 验证待办事项已添加
    await expect(page.locator('text=Buy groceries')).toBeVisible();
  });

  test('多个待办事项管理 - CodeGen风格', async ({ page }) => {
    // 添加第一个待办事项
    await page.click('[placeholder="What needs to be done?"]');
    await page.fill('[placeholder="What needs to be done?"]', 'Task 1');
    await page.press('[placeholder="What needs to be done?"]', 'Enter');

    // 添加第二个待办事项
    await page.fill('[placeholder="What needs to be done?"]', 'Task 2');
    await page.press('[placeholder="What needs to be done?"]', 'Enter');

    // 添加第三个待办事项
    await page.fill('[placeholder="What needs to be done?"]', 'Task 3');
    await page.press('[placeholder="What needs to be done?"]', 'Enter');

    // 验证所有待办事项都已添加
    await expect(page.locator('text=Task 1')).toBeVisible();
    await expect(page.locator('text=Task 2')).toBeVisible();
    await expect(page.locator('text=Task 3')).toBeVisible();

    // 验证待办事项数量
    const todoItems = page.locator('.todo-list li');
    await expect(todoItems).toHaveCount(3);
  });

  test('待办事项完成和删除 - CodeGen风格', async ({ page }) => {
    // 添加待办事项
    await page.click('[placeholder="What needs to be done?"]');
    await page.fill('[placeholder="What needs to be done?"]', 'Complete task');
    await page.press('[placeholder="What needs to be done?"]', 'Enter');

    // 标记为完成
    await page.click('input[type="checkbox"]');

    // 验证已完成状态
    await expect(page.locator('.completed')).toBeVisible();

    // 鼠标悬停显示删除按钮
    await page.hover('.todo-list li');
    
    // 点击删除按钮
    await page.click('.destroy');

    // 验证待办事项已被删除
    await expect(page.locator('text=Complete task')).not.toBeVisible();
  });

  test('待办事项编辑 - CodeGen风格', async ({ page }) => {
    // 添加待办事项
    await page.click('[placeholder="What needs to be done?"]');
    await page.fill('[placeholder="What needs to be done?"]', 'Original task');
    await page.press('[placeholder="What needs to be done?"]', 'Enter');

    // 双击编辑待办事项
    await page.dblclick('label');

    // 清除原有文本
    await page.press('input[type="text"]', 'Control+a');
    await page.press('input[type="text"]', 'Delete');

    // 输入新文本
    await page.fill('input[type="text"]', 'Edited task');
    await page.press('input[type="text"]', 'Enter');

    // 验证编辑成功
    await expect(page.locator('text=Edited task')).toBeVisible();
    await expect(page.locator('text=Original task')).not.toBeVisible();
  });

  test('筛选待办事项 - CodeGen风格', async ({ page }) => {
    // 添加多个待办事项
    await page.click('[placeholder="What needs to be done?"]');
    await page.fill('[placeholder="What needs to be done?"]', 'Active task');
    await page.press('[placeholder="What needs to be done?"]', 'Enter');

    await page.fill('[placeholder="What needs to be done?"]', 'Completed task');
    await page.press('[placeholder="What needs to be done?"]', 'Enter');

    // 标记第二个为完成
    await page.click('.todo-list li:nth-child(2) input[type="checkbox"]');

    // 点击"Active"筛选
    await page.click('text=Active');
    
    // 验证只显示活跃待办事项
    await expect(page.locator('text=Active task')).toBeVisible();
    await expect(page.locator('text=Completed task')).not.toBeVisible();

    // 点击"Completed"筛选
    await page.click('text=Completed');
    
    // 验证只显示已完成待办事项
    await expect(page.locator('text=Active task')).not.toBeVisible();
    await expect(page.locator('text=Completed task')).toBeVisible();

    // 点击"All"筛选
    await page.click('text=All');
    
    // 验证显示所有待办事项
    await expect(page.locator('text=Active task')).toBeVisible();
    await expect(page.locator('text=Completed task')).toBeVisible();
  });

  test('清除已完成待办事项 - CodeGen风格', async ({ page }) => {
    // 添加多个待办事项
    await page.click('[placeholder="What needs to be done?"]');
    await page.fill('[placeholder="What needs to be done?"]', 'Task 1');
    await page.press('[placeholder="What needs to be done?"]', 'Enter');

    await page.fill('[placeholder="What needs to be done?"]', 'Task 2');
    await page.press('[placeholder="What needs to be done?"]', 'Enter');

    await page.fill('[placeholder="What needs to be done?"]', 'Task 3');
    await page.press('[placeholder="What needs to be done?"]', 'Enter');

    // 标记前两个为完成
    await page.click('.todo-list li:nth-child(1) input[type="checkbox"]');
    await page.click('.todo-list li:nth-child(2) input[type="checkbox"]');

    // 点击"Clear completed"按钮
    await page.click('text=Clear completed');

    // 验证只剩余未完成的待办事项
    await expect(page.locator('text=Task 1')).not.toBeVisible();
    await expect(page.locator('text=Task 2')).not.toBeVisible();
    await expect(page.locator('text=Task 3')).toBeVisible();

    // 验证待办事项数量
    const todoItems = page.locator('.todo-list li');
    await expect(todoItems).toHaveCount(1);
  });

  test('待办事项计数器 - CodeGen风格', async ({ page }) => {
    // 验证初始计数器显示
    await expect(page.locator('text="0 items left"')).toBeVisible();

    // 添加待办事项
    await page.click('[placeholder="What needs to be done?"]');
    await page.fill('[placeholder="What needs to be done?"]', 'Single task');
    await page.press('[placeholder="What needs to be done?"]', 'Enter');

    // 验证计数器更新
    await expect(page.locator('text="1 item left"')).toBeVisible();

    // 添加更多待办事项
    await page.fill('[placeholder="What needs to be done?"]', 'Multiple task');
    await page.press('[placeholder="What needs to be done?"]', 'Enter');

    // 验证计数器显示复数形式
    await expect(page.locator('text="2 items left"')).toBeVisible();
  });
});

test.describe('CodeGen生成的复杂交互测试', () => {
  
  test('键盘导航 - CodeGen风格', async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/');

    // 添加多个待办事项
    await page.click('[placeholder="What needs to be done?"]');
    await page.fill('[placeholder="What needs to be done?"]', 'Task A');
    await page.press('[placeholder="What needs to be done?"]', 'Enter');

    await page.fill('[placeholder="What needs to be done?"]', 'Task B');
    await page.press('[placeholder="What needs to be done?"]', 'Enter');

    await page.fill('[placeholder="What needs to be done?"]', 'Task C');
    await page.press('[placeholder="What needs to be done?"]', 'Enter');

    // 使用Tab键导航
    await page.press('body', 'Tab');
    await page.press('body', 'Tab');

    // 使用方向键导航
    await page.press('body', 'ArrowDown');
    await page.press('body', 'ArrowUp');

    // 使用空格键切换完成状态
    await page.press('body', ' ');

    // 验证状态变化
    await expect(page.locator('.todo-list li:first-child')).toHaveClass(/completed/);
  });

  test('批量操作 - CodeGen风格', async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/');

    // 批量添加待办事项
    const tasks = ['Task 1', 'Task 2', 'Task 3', 'Task 4', 'Task 5'];
    
    for (const task of tasks) {
      await page.click('[placeholder="What needs to be done?"]');
      await page.fill('[placeholder="What needs to be done?"]', task);
      await page.press('[placeholder="What needs to be done?"]', 'Enter');
    }

    // 验证所有待办事项都已添加
    for (const task of tasks) {
      await expect(page.locator(`text=${task}`)).toBeVisible();
    }

    // 批量标记为完成
    const checkboxes = page.locator('input[type="checkbox"]');
    const count = await checkboxes.count();
    
    for (let i = 0; i < count; i++) {
      await checkboxes.nth(i).click();
    }

    // 验证所有待办事项都已完成
    await expect(page.locator('.todo-list li')).toHaveClass(/completed/);
  });

  test('右键菜单 - CodeGen风格', async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/');

    // 添加待办事项
    await page.click('[placeholder="What needs to be done?"]');
    await page.fill('[placeholder="What needs to be done?"]', 'Context menu task');
    await page.press('[placeholder="What needs to be done?"]', 'Enter');

    // 右键点击待办事项
    await page.click('label', { button: 'right' });

    // 验证右键菜单出现（如果有的话）
    // 注意：TodoMVC应用本身没有右键菜单，这里只是演示右键操作
    await expect(page.locator('text=Context menu task')).toBeVisible();
  });

  test('拖拽排序 - CodeGen风格', async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/');

    // 添加多个待办事项
    await page.click('[placeholder="What needs to be done?"]');
    await page.fill('[placeholder="What needs to be done?"]', 'First task');
    await page.press('[placeholder="What needs to be done?"]', 'Enter');

    await page.fill('[placeholder="What needs to be done?"]', 'Second task');
    await page.press('[placeholder="What needs to be done?"]', 'Enter');

    await page.fill('[placeholder="What needs to be done?"]', 'Third task');
    await page.press('[placeholder="What needs to be done?"]', 'Enter');

    // 获取待办事项元素
    const firstTask = page.locator('.todo-list li').first();
    const thirdTask = page.locator('.todo-list li').last();

    // 拖拽第一个任务到最后
    await firstTask.dragTo(thirdTask);

    // 验证顺序变化
    const tasks = page.locator('.todo-list li');
    await expect(tasks.first()).toContainText('Second task');
    await expect(tasks.last()).toContainText('First task');
  });
});

test.describe('CodeGen生成的断言测试', () => {
  
  test('页面标题和URL断言 - CodeGen风格', async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/');

    // 验证页面标题
    await expect(page).toHaveTitle(/React • TodoMVC/);

    // 验证页面URL
    await expect(page).toHaveURL(/.*todomvc/);

    // 验证页面包含特定文本
    await expect(page.locator('body')).toContainText('todos');

    // 验证输入框存在
    await expect(page.locator('[placeholder="What needs to be done?"]')).toBeVisible();
  });

  test('元素属性断言 - CodeGen风格', async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/');

    // 添加待办事项
    await page.click('[placeholder="What needs to be done?"]');
    await page.fill('[placeholder="What needs to be done?"]', 'Test attribute');
    await page.press('[placeholder="What needs to be done?"]', 'Enter');

    // 验证复选框属性
    const checkbox = page.locator('input[type="checkbox"]');
    await expect(checkbox).not.toBeChecked();

    // 点击复选框
    await checkbox.click();

    // 验证复选框被选中
    await expect(checkbox).toBeChecked();

    // 验证待办事项有completed类
    await expect(page.locator('.todo-list li')).toHaveClass(/completed/);
  });

  test('CSS样式断言 - CodeGen风格', async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/');

    // 验证输入框的CSS属性
    const input = page.locator('[placeholder="What needs to be done?"]');
    await expect(input).toHaveCSS('font-size', '24px');

    // 添加待办事项
    await input.click();
    await input.fill('Style test');
    await input.press('Enter');

    // 标记为完成
    await page.click('input[type="checkbox"]');

    // 验证完成状态的样式
    const completedItem = page.locator('.todo-list li');
    await expect(completedItem).toHaveCSS('text-decoration-line', 'line-through');
  });
});
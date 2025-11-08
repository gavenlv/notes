# 第7章：Playwright并行执行与性能优化

## 7.1 并行执行基础

### 7.1.1 什么是并行执行
并行执行是指同时运行多个测试用例或测试套件，以减少整体测试执行时间。Playwright原生支持并行执行，可以显著提高测试效率。

### 7.1.2 Playwright并行执行机制
Playwright通过以下方式实现并行执行：
- 工作进程（Worker）：每个工作进程独立运行测试
- 浏览器上下文：每个测试在独立的浏览器上下文中运行
- 资源隔离：确保测试之间不会相互干扰

## 7.2 配置并行执行

### 7.2.1 基本并行配置
```javascript
// playwright.config.js
const config = {
  // 设置并行工作进程数
  workers: 4,
  
  // 设置每个工作进程的最大并发测试数
  maxConcurrency: 2,
  
  // 其他配置...
};

module.exports = config;
```

### 7.2.2 按浏览器并行
```javascript
// playwright.config.js
const config = {
  projects: [
    {
      name: 'Chromium',
      use: { browserName: 'chromium' },
    },
    {
      name: 'Firefox',
      use: { browserName: 'firefox' },
    },
    {
      name: 'WebKit',
      use: { browserName: 'webkit' },
    },
  ],
  workers: 3, // 每个浏览器项目一个工作进程
};

module.exports = config;
```

## 7.3 性能优化策略

### 7.3.1 测试数据优化
```javascript
// 使用固定测试数据而不是每次都生成
const TEST_USERS = [
  { username: 'user1', password: 'pass1' },
  { username: 'user2', password: 'pass2' },
];

// 在测试中复用这些数据
test('用户登录测试', async ({ page }) => {
  const user = TEST_USERS[0];
  // 执行登录操作
});
```

### 7.3.2 资源复用
```javascript
// fixture/database-fixture.js
class DatabaseFixture {
  constructor() {
    this.connection = null;
  }

  async connect() {
    if (!this.connection) {
      // 建立数据库连接
      this.connection = await createConnection();
    }
    return this.connection;
  }

  async disconnect() {
    if (this.connection) {
      await this.connection.close();
      this.connection = null;
    }
  }
}

module.exports = { DatabaseFixture };
```

## 7.4 并行执行最佳实践

### 7.4.1 独立测试设计
```javascript
// 确保每个测试都是独立的
test('用户注册测试', async ({ page }) => {
  // 创建唯一用户数据
  const userData = {
    username: `testuser_${Date.now()}`,
    email: `test_${Date.now()}@example.com`
  };
  
  // 执行注册流程
  await registerUser(page, userData);
  
  // 验证注册结果
  await expect(page).toHaveURL('/dashboard');
});
```

### 7.4.2 共享状态管理
```javascript
// 使用测试夹具管理共享状态
const test = require('@playwright/test');

test.use({
  storageState: async ({}, use) => {
    // 设置共享存储状态
    const state = await setupTestEnvironment();
    await use(state);
    // 清理测试环境
    await teardownTestEnvironment();
  },
});
```

## 7.5 实验：并行执行性能测试

### 7.5.1 实验目标
通过对比串行和并行执行，了解并行执行对测试性能的影响。

### 7.5.2 实验步骤
1. 创建多个独立的测试用例
2. 配置不同的并行级别
3. 记录执行时间
4. 分析性能提升效果

### 7.5.3 实验代码
```javascript
// tests/performance-test.spec.js
const { test, expect } = require('@playwright/test');

// 创建多个相似的测试用例
for (let i = 1; i <= 10; i++) {
  test(`性能测试用例 ${i}`, async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(1000); // 模拟耗时操作
    
    const title = await page.title();
    expect(title).toBeTruthy();
  });
}
```

```bash
# 串行执行（默认）
npx playwright test --workers=1

# 并行执行（默认4个工作进程）
npx playwright test

# 自定义并行度
npx playwright test --workers=8
```

## 7.6 监控与调试

### 7.6.1 性能监控
```javascript
// helpers/performance-monitor.js
class PerformanceMonitor {
  constructor() {
    this.metrics = [];
  }

  start(name) {
    this.metrics[name] = {
      startTime: Date.now(),
      endTime: null,
      duration: null
    };
  }

  end(name) {
    if (this.metrics[name]) {
      this.metrics[name].endTime = Date.now();
      this.metrics[name].duration = 
        this.metrics[name].endTime - this.metrics[name].startTime;
    }
  }

  getDuration(name) {
    return this.metrics[name]?.duration || 0;
  }

  report() {
    console.log('性能报告:');
    for (const [name, metric] of Object.entries(this.metrics)) {
      console.log(`${name}: ${metric.duration}ms`);
    }
  }
}

module.exports = { PerformanceMonitor };
```

### 7.6.2 调试并行问题
```javascript
// 在测试中添加调试信息
test('调试并行问题', async ({ page, workerInfo }) => {
  console.log(`工作进程ID: ${workerInfo.workerIndex}`);
  console.log(`项目名称: ${workerInfo.project.name}`);
  
  // 添加更多调试信息
  await page.goto('/');
  console.log(`页面标题: ${await page.title()}`);
});
```

## 7.7 故障排除

### 7.7.1 常见并行问题
1. **资源共享冲突**：确保每个测试使用独立的资源
2. **数据库状态污染**：使用事务或清理机制
3. **文件系统冲突**：使用临时目录或唯一文件名

### 7.7.2 解决方案
```javascript
// 使用唯一标识符避免冲突
const uniqueId = `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

// 创建临时目录
const tempDir = path.join(os.tmpdir(), uniqueId);
fs.mkdirSync(tempDir);

// 在测试后清理
test.afterAll(async () => {
  fs.rmSync(tempDir, { recursive: true });
});
```

## 7.8 性能优化技巧

### 7.8.1 减少不必要的等待
```javascript
// 避免固定的等待时间
// 不推荐
await page.waitForTimeout(5000);

// 推荐：使用智能等待
await page.waitForSelector('#element-id', { timeout: 10000 });
```

### 7.8.2 优化选择器
```javascript
// 使用高效的CSS选择器
// 不推荐：复杂XPath
await page.locator('//div[@class="container"]//button[text()="提交"]');

// 推荐：简单CSS选择器
await page.locator('button.submit-btn');
```

## 7.9 总结
本章介绍了Playwright的并行执行机制和性能优化策略。通过合理配置并行参数、优化测试数据、管理共享资源等方法，可以显著提高测试执行效率。同时，我们也探讨了并行执行中的常见问题及其解决方案，帮助构建高效稳定的自动化测试体系。
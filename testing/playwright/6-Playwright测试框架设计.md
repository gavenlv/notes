# 第6章：Playwright测试框架设计

## 6.1 测试框架架构设计

### 6.1.1 分层架构模式
采用分层架构模式来组织测试框架，提高代码的可维护性和可扩展性：
```
tests/
├── pages/          # 页面对象层
├── tests/          # 测试用例层
├── helpers/        # 辅助工具层
├── data/           # 测试数据层
└── config/         # 配置管理层
```

### 6.1.2 配置管理
```javascript
// config/test-config.js
const testConfig = {
  environments: {
    dev: {
      baseUrl: 'http://localhost:3000',
      timeout: 30000
    },
    staging: {
      baseUrl: 'https://staging.example.com',
      timeout: 60000
    },
    production: {
      baseUrl: 'https://example.com',
      timeout: 60000
    }
  },
  browsers: ['chromium', 'firefox', 'webkit'],
  headless: true
};

module.exports = { testConfig };
```

## 6.2 页面对象模型深化

### 6.2.1 基础页面类
```javascript
// pages/base-page.js
class BasePage {
  constructor(page) {
    this.page = page;
  }

  async navigateTo(url) {
    await this.page.goto(url);
  }

  async getTitle() {
    return await this.page.title();
  }

  async waitForPageLoad() {
    await this.page.waitForLoadState('networkidle');
  }
}

module.exports = { BasePage };
```

### 6.2.2 具体页面实现
```javascript
// pages/home-page.js
const { BasePage } = require('./base-page');

class HomePage extends BasePage {
  constructor(page) {
    super(page);
    this.searchInput = page.locator('#search-input');
    this.searchButton = page.locator('#search-button');
    this.userMenu = page.locator('#user-menu');
  }

  async search(keyword) {
    await this.searchInput.fill(keyword);
    await this.searchButton.click();
  }

  async openUserMenu() {
    await this.userMenu.click();
  }
}

module.exports = { HomePage };
```

## 6.3 测试数据管理

### 6.3.1 数据工厂模式
```javascript
// data/user-factory.js
class UserFactory {
  static createValidUser() {
    return {
      username: `user_${Date.now()}`,
      email: `user_${Date.now()}@example.com`,
      password: 'Password123!'
    };
  }

  static createInvalidUser() {
    return {
      username: '',
      email: 'invalid-email',
      password: '123'
    };
  }
}

module.exports = { UserFactory };
```

### 6.3.2 外部数据源
```javascript
// data/test-data-provider.js
const fs = require('fs');
const path = require('path');

class TestDataProvider {
  static loadFromJSON(filename) {
    const filePath = path.join(__dirname, filename);
    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    return data;
  }

  static loadFromCSV(filename) {
    // 实现CSV解析逻辑
    const filePath = path.join(__dirname, filename);
    // 返回解析后的数据
  }
}

module.exports = { TestDataProvider };
```

## 6.4 测试执行管理

### 6.4.1 测试套件组织
```javascript
// tests/user-management.test.js
const { test, expect } = require('@playwright/test');
const { HomePage } = require('../pages/home-page');
const { UserFactory } = require('../data/user-factory');

test.describe('用户管理测试套件', () => {
  let homePage;

  test.beforeEach(async ({ page }) => {
    homePage = new HomePage(page);
    await homePage.navigateTo('/');
  });

  test('用户登录测试', async ({ page }) => {
    const user = UserFactory.createValidUser();
    // 执行登录测试
  });

  test('用户登出测试', async ({ page }) => {
    // 执行登出测试
  });
});
```

### 6.4.2 标签和分组
```javascript
// 使用标签对测试进行分组
test('用户注册 @smoke', async ({ page }) => {
  // 冒烟测试
});

test('用户权限验证 @security', async ({ page }) => {
  // 安全测试
});
```

## 6.5 实验：构建企业级测试框架

### 6.5.1 实验目标
构建一个完整的企业级Playwright测试框架，包含配置管理、页面对象、测试数据管理、报告生成等功能。

### 6.5.2 实验步骤
1. 设计框架目录结构
2. 实现配置管理模块
3. 创建基础页面对象类
4. 实现测试数据工厂
5. 编写示例测试用例
6. 配置测试报告

### 6.5.3 实验代码
```javascript
// config/environment-config.js
class EnvironmentConfig {
  constructor() {
    this.env = process.env.TEST_ENV || 'dev';
    this.config = this.loadConfig();
  }

  loadConfig() {
    const configs = {
      dev: {
        baseUrl: 'http://localhost:3000',
        apiBaseUrl: 'http://localhost:8000/api',
        timeout: 30000
      },
      staging: {
        baseUrl: 'https://staging.example.com',
        apiBaseUrl: 'https://staging.example.com/api',
        timeout: 60000
      },
      production: {
        baseUrl: 'https://example.com',
        apiBaseUrl: 'https://example.com/api',
        timeout: 60000
      }
    };
    
    return configs[this.env];
  }

  get(key) {
    return this.config[key];
  }
}

module.exports = { EnvironmentConfig };
```

```javascript
// helpers/api-helper.js
const { EnvironmentConfig } = require('../config/environment-config');

class ApiHelper {
  constructor() {
    this.config = new EnvironmentConfig();
  }

  async createUser(userData) {
    const response = await fetch(`${this.config.get('apiBaseUrl')}/users`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(userData)
    });
    
    return await response.json();
  }

  async deleteUser(userId) {
    await fetch(`${this.config.get('apiBaseUrl')}/users/${userId}`, {
      method: 'DELETE'
    });
  }
}

module.exports = { ApiHelper };
```

## 6.6 最佳实践

### 6.6.1 代码组织
- 使用清晰的目录结构分离关注点
- 遵循命名约定提高代码可读性
- 保持页面对象的单一职责原则

### 6.6.2 可维护性
- 定期重构重复代码
- 使用配置文件管理环境变量
- 实现清晰的错误处理机制

### 6.6.3 可扩展性
- 设计可重用的组件
- 支持多环境配置
- 实现插件化架构

## 6.7 总结
本章介绍了如何设计一个企业级的Playwright测试框架，包括分层架构、页面对象模型、测试数据管理、配置管理等方面的内容。通过实际示例和实验，帮助读者掌握构建可维护、可扩展测试框架的关键技术。
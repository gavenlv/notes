# 第6章：Cypress测试组织与数据管理

## 目录
- [6.1 测试文件组织](#61-测试文件组织)
- [6.2 测试套件结构](#62-测试套件结构)
- [6.3 测试数据管理](#63-测试数据管理)
- [6.4 测试环境管理](#64-测试环境管理)
- [6.5 页面对象模型](#65-页面对象模型)
- [6.6 测试工具类](#66-测试工具类)
- [6.7 测试报告与结果分析](#67-测试报告与结果分析)
- [6.8 实验与实践](#68-实验与实践)

## 6.1 测试文件组织

### 目录结构

良好的目录结构是测试组织的基础：

```
cypress/
├── integration/          # 测试文件
│   ├── authentication/   # 认证相关测试
│   ├── dashboard/        # 仪表板测试
│   ├── profile/          # 用户资料测试
│   └── common/           # 通用测试
├── fixtures/             # 测试数据
│   ├── users.json
│   ├── products.json
│   └── responses/
├── support/              # 支持文件
│   ├── commands.js       # 自定义命令
│   ├── index.js          # 支持文件入口
│   ├── pages/            # 页面对象
│   └── utils/            # 工具函数
├── plugins/              # 插件文件
│   └── index.js
└── screenshots/          # 截图
```

### 测试文件命名规范

遵循一致的命名规范有助于测试管理：

```javascript
// 使用描述性名称
login_spec.js
user-registration_spec.js
product-search_spec.js

// 使用功能分组
authentication/login_spec.js
authentication/logout_spec.js
dashboard/widgets_spec.js
dashboard/charts_spec.js

// 使用测试类型分组
smoke/dashboard_spec.js
regression/user-profile_spec.js
integration/payment-flow_spec.js
```

### 测试文件内容组织

```javascript
// 文件头部注释
/**
 * @fileoverview 用户登录功能测试
 * @author 测试团队
 * @since 2023-01-01
 */

// 导入必要的模块和依赖
import { LoginPage } from '../support/pages/login-page';
import { TestDataGenerator } from '../support/utils/test-data-generator';

// 描述测试套件
describe('用户登录功能', () => {
  // 定义测试数据
  const validUser = {
    username: 'testuser',
    password: 'password123'
  };
  
  const invalidUser = {
    username: 'invaliduser',
    password: 'wrongpassword'
  };
  
  // 实例化页面对象
  const loginPage = new LoginPage();
  
  // 在所有测试前执行
  before(() => {
    // 执行一次性设置
    cy.log('开始登录功能测试');
  });
  
  // 在每个测试前执行
  beforeEach(() => {
    // 访问登录页面
    cy.visit('/login');
  });
  
  // 测试用例
  it('应该成功登录有效用户', () => {
    loginPage.login(validUser.username, validUser.password);
    cy.url().should('include', '/dashboard');
    cy.get('.user-name').should('contain', validUser.username);
  });
  
  it('应该拒绝无效用户登录', () => {
    loginPage.login(invalidUser.username, invalidUser.password);
    loginPage.getErrorMessage().should('contain', '用户名或密码错误');
  });
  
  // 在每个测试后执行
  afterEach(() => {
    // 清理测试状态
    cy.clearCookies();
    cy.clearLocalStorage();
  });
  
  // 在所有测试后执行
  after(() => {
    // 执行一次性清理
    cy.log('登录功能测试完成');
  });
});
```

## 6.2 测试套件结构

### 测试套件组织

```javascript
// 主套件文件
describe('用户管理模块', () => {
  // 嵌套套件
  describe('用户注册', () => {
    it('应该成功注册新用户', () => {
      // 测试代码
    });
    
    it('应该拒绝重复用户名注册', () => {
      // 测试代码
    });
  });
  
  describe('用户登录', () => {
    it('应该成功登录有效用户', () => {
      // 测试代码
    });
    
    it('应该拒绝无效用户登录', () => {
      // 测试代码
    });
  });
  
  describe('用户资料', () => {
    it('应该显示用户资料', () => {
      // 测试代码
    });
    
    it('应该更新用户资料', () => {
      // 测试代码
    });
  });
});
```

### 测试套件配置

```javascript
// 使用context和describe组合
context('当用户未登录时', () => {
  beforeEach(() => {
    // 确保用户未登录
    cy.clearCookies();
    cy.clearLocalStorage();
  });
  
  describe('访问受保护页面', () => {
    it('应该重定向到登录页面', () => {
      cy.visit('/dashboard');
      cy.url().should('include', '/login');
    });
  });
});

context('当用户已登录时', () => {
  beforeEach(() => {
    // 登录用户
    cy.login('testuser', 'password123');
  });
  
  describe('访问受保护页面', () => {
    it('应该显示受保护页面', () => {
      cy.visit('/dashboard');
      cy.url().should('include', '/dashboard');
    });
  });
});
```

### 条件测试

```javascript
describe('功能测试', () => {
  // 根据环境变量决定是否运行测试
  if (Cypress.env('skipSlowTests')) {
    it.skip('慢速测试 - 已跳过', () => {
      // 慢速测试代码
    });
  } else {
    it('慢速测试 - 运行中', () => {
      // 慢速测试代码
    });
  }
  
  // 使用only运行特定测试
  it.only('重要测试 - 只运行此测试', () => {
    // 重要测试代码
  });
  
  // 使用动态测试
  const testCases = [
    { input: 'a', expected: 'A' },
    { input: 'b', expected: 'B' },
    { input: 'c', expected: 'C' }
  ];
  
  testCases.forEach((testCase, index) => {
    it(`应该转换输入 ${testCase.input} 为 ${testCase.expected}`, () => {
      // 测试代码
      expect(testCase.input.toUpperCase()).to.eq(testCase.expected);
    });
  });
});
```

## 6.3 测试数据管理

### Fixture数据管理

```javascript
// cypress/fixtures/users.json
{
  "validUser": {
    "username": "testuser",
    "password": "password123",
    "email": "test@example.com",
    "firstName": "Test",
    "lastName": "User"
  },
  "adminUser": {
    "username": "admin",
    "password": "admin123",
    "email": "admin@example.com",
    "firstName": "Admin",
    "lastName": "User",
    "role": "admin"
  },
  "invalidUser": {
    "username": "invaliduser",
    "password": "wrongpassword"
  }
}

// 在测试中使用fixture数据
describe('使用fixture数据', () => {
  it('应该使用validUser登录', () => {
    cy.fixture('users').then((users) => {
      cy.visit('/login');
      cy.get('#username').type(users.validUser.username);
      cy.get('#password').type(users.validUser.password);
      cy.get('.login-button').click();
      cy.url().should('include', '/dashboard');
    });
  });
});
```

### 动态数据生成

```javascript
// cypress/support/utils/test-data-generator.js
export class TestDataGenerator {
  // 生成随机用户
  static generateUser(overrides = {}) {
    const randomId = Math.floor(Math.random() * 10000);
    const defaultUser = {
      username: `user_${randomId}`,
      email: `user_${randomId}@example.com`,
      password: 'Password123!',
      firstName: 'Test',
      lastName: `User${randomId}`,
      phone: `555-${randomId.toString().padStart(4, '0')}`,
      address: `${randomId} Test Street`,
      city: 'Test City',
      state: 'TS',
      zipCode: randomId.toString().padStart(5, '0'),
      active: true
    };
    
    return { ...defaultUser, ...overrides };
  }
  
  // 生成随机产品
  static generateProduct(overrides = {}) {
    const randomId = Math.floor(Math.random() * 10000);
    const defaultProduct = {
      id: randomId,
      name: `Product ${randomId}`,
      description: `Description for product ${randomId}`,
      price: (Math.random() * 100).toFixed(2),
      category: 'Electronics',
      inStock: true,
      quantity: Math.floor(Math.random() * 100) + 1
    };
    
    return { ...defaultProduct, ...overrides };
  }
  
  // 生成随机订单
  static generateOrder(overrides = {}) {
    const randomId = Math.floor(Math.random() * 10000);
    const defaultOrder = {
      id: randomId,
      userId: Math.floor(Math.random() * 1000) + 1,
      items: [
        {
          productId: Math.floor(Math.random() * 100) + 1,
          quantity: Math.floor(Math.random() * 5) + 1,
          price: (Math.random() * 100).toFixed(2)
        }
      ],
      total: (Math.random() * 500).toFixed(2),
      status: 'pending',
      date: new Date().toISOString()
    };
    
    return { ...defaultOrder, ...overrides };
  }
}

// 在测试中使用
describe('使用动态数据生成', () => {
  it('应该注册新用户', () => {
    const newUser = TestDataGenerator.generateUser({
      firstName: 'John',
      lastName: 'Doe'
    });
    
    cy.visit('/register');
    cy.get('#username').type(newUser.username);
    cy.get('#email').type(newUser.email);
    cy.get('#password').type(newUser.password);
    cy.get('#firstName').type(newUser.firstName);
    cy.get('#lastName').type(newUser.lastName);
    cy.get('.register-button').click();
    
    cy.get('.success-message').should('contain', '用户注册成功');
  });
});
```

### 数据工厂模式

```javascript
// cypress/support/factories/user-factory.js
export class UserFactory {
  static attributes(overrides = {}) {
    return {
      username: 'testuser',
      email: 'test@example.com',
      password: 'Password123!',
      firstName: 'Test',
      lastName: 'User',
      active: true,
      ...overrides
    };
  }
  
  static create(overrides = {}) {
    return cy.task('createUserInDatabase', this.attributes(overrides));
  }
  
  static createMany(count, overrides = {}) {
    const users = [];
    for (let i = 0; i < count; i++) {
      users.push(this.attributes({
        username: `user${i}`,
        email: `user${i}@example.com`,
        ...overrides
      }));
    }
    return cy.task('createUsersInDatabase', users);
  }
  
  static admin(overrides = {}) {
    return this.create({
      username: 'admin',
      email: 'admin@example.com',
      role: 'admin',
      ...overrides
    });
  }
  
  static inactive(overrides = {}) {
    return this.create({
      active: false,
      ...overrides
    });
  }
}

// 在测试中使用
describe('使用数据工厂模式', () => {
  beforeEach(() => {
    // 创建测试用户
    UserFactory.create({
      username: 'testuser',
      email: 'test@example.com'
    });
  });
  
  it('应该登录已创建的用户', () => {
    cy.visit('/login');
    cy.get('#username').type('testuser');
    cy.get('#password').type('Password123!');
    cy.get('.login-button').click();
    cy.url().should('include', '/dashboard');
  });
});
```

## 6.4 测试环境管理

### 多环境配置

```javascript
// cypress/config/environments.js
export const environments = {
  development: {
    baseUrl: 'http://localhost:3000',
    apiUrl: 'http://localhost:3001/api',
    database: {
      host: 'localhost',
      port: 5432,
      name: 'app_dev'
    }
  },
  staging: {
    baseUrl: 'https://staging.example.com',
    apiUrl: 'https://api.staging.example.com',
    database: {
      host: 'staging-db.example.com',
      port: 5432,
      name: 'app_staging'
    }
  },
  production: {
    baseUrl: 'https://example.com',
    apiUrl: 'https://api.example.com',
    database: {
      host: 'prod-db.example.com',
      port: 5432,
      name: 'app_prod'
    }
  }
};

// cypress/plugins/index.js
const { environments } = require('../config/environments');

module.exports = (on, config) => {
  // 获取环境名称
  const environment = config.env.environment || 'development';
  
  // 设置环境配置
  const envConfig = environments[environment];
  
  if (envConfig) {
    // 合并配置
    config.baseUrl = envConfig.baseUrl;
    config.env.apiUrl = envConfig.apiUrl;
    config.env.dbConfig = envConfig.database;
  }
  
  return config;
};
```

### 环境特定测试

```javascript
// cypress/integration/common/environment-tests.js
describe('环境特定测试', () => {
  it('应该使用正确的baseUrl', () => {
    cy.visit('/');
    cy.url().should('include', Cypress.config().baseUrl);
  });
  
  it('应该连接到正确的API', () => {
    const apiUrl = Cypress.env('apiUrl');
    cy.request(apiUrl + '/health').then((response) => {
      expect(response.status).to.eq(200);
    });
  });
  
  // 只在特定环境运行
  if (Cypress.env('environment') === 'staging') {
    it('应该在staging环境执行特定测试', () => {
      // Staging特定测试
    });
  }
  
  // 跳过特定环境
  if (Cypress.env('environment') === 'production') {
    it.skip('不应该在生产环境执行破坏性测试', () => {
      // 破坏性测试
    });
  }
});
```

### 环境清理

```javascript
// cypress/support/cleanup.js
export class Cleanup {
  // 清理数据库
  static cleanDatabase() {
    return cy.task('cleanDatabase');
  }
  
  // 清理测试用户
  static cleanTestUsers() {
    return cy.task('cleanTestUsers');
  }
  
  // 清理测试数据
  static cleanTestData() {
    return cy.task('cleanTestData');
  }
  
  // 重置应用状态
  static resetApplicationState() {
    cy.clearCookies();
    cy.clearLocalStorage();
    return cy.window().then((win) => {
      win.sessionStorage.clear();
    });
  }
}

// 在测试中使用
describe('使用环境清理', () => {
  before(() => {
    // 在测试套件开始前清理
    Cleanup.cleanDatabase();
  });
  
  beforeEach(() => {
    // 在每个测试前重置应用状态
    Cleanup.resetApplicationState();
  });
  
  afterEach(() => {
    // 在每个测试后清理测试数据
    Cleanup.cleanTestData();
  });
  
  after(() => {
    // 在测试套件结束后清理测试用户
    Cleanup.cleanTestUsers();
  });
});
```

## 6.5 页面对象模型

### 基本页面对象

```javascript
// cypress/support/pages/login-page.js
export class LoginPage {
  // 页面元素定位器
  get usernameInput() {
    return cy.get('#username');
  }
  
  get passwordInput() {
    return cy.get('#password');
  }
  
  get loginButton() {
    return cy.get('.login-button');
  }
  
  get errorMessage() {
    return cy.get('.error-message');
  }
  
  get successMessage() {
    return cy.get('.success-message');
  }
  
  get forgotPasswordLink() {
    return cy.get('a[href="/forgot-password"]');
  }
  
  get registerLink() {
    return cy.get('a[href="/register"]');
  }
  
  // 页面操作方法
  visit() {
    cy.visit('/login');
    return this;
  }
  
  login(username, password) {
    this.usernameInput.type(username);
    this.passwordInput.type(password);
    this.loginButton.click();
    return this;
  }
  
  getErrorText() {
    return this.errorMessage.invoke('text');
  }
  
  getSuccessText() {
    return this.successMessage.invoke('text');
  }
  
  clickForgotPassword() {
    this.forgotPasswordLink.click();
    return this;
  }
  
  clickRegister() {
    this.registerLink.click();
    return this;
  }
  
  // 页面验证方法
  verifyPageLoaded() {
    cy.url().should('include', '/login');
    this.usernameInput.should('be.visible');
    this.passwordInput.should('be.visible');
    this.loginButton.should('be.visible');
    return this;
  }
  
  verifyErrorMessage(message) {
    this.errorMessage.should('be.visible').and('contain', message);
    return this;
  }
  
  verifySuccessMessage(message) {
    this.successMessage.should('be.visible').and('contain', message);
    return this;
  }
}
```

### 高级页面对象

```javascript
// cypress/support/pages/dashboard-page.js
export class DashboardPage {
  constructor() {
    this.userMenu = cy.get('.user-menu');
    this.logoutButton = cy.get('.logout-button');
    this.widgets = cy.get('.widget');
    this.notifications = cy.get('.notification');
  }
  
  // 动态元素定位
  getWidgetByName(name) {
    return this.widgets.contains(name);
  }
  
  getNotificationByType(type) {
    return this.notifications.filter(`.${type}`);
  }
  
  // 复杂操作
  navigateToSection(sectionName) {
    cy.get('.nav-menu').contains(sectionName).click();
    return this;
  }
  
  openUserMenu() {
    this.userMenu.click();
    return this;
  }
  
  logout() {
    this.openUserMenu();
    this.logoutButton.click();
    return this;
  }
  
  // 数据获取
  getWidgetsData() {
    const widgetsData = [];
    
    this.widgets.each(($el) => {
      const widget = {};
      widget.name = $el.find('.widget-title').text();
      widget.value = $el.find('.widget-value').text();
      widgetsData.push(widget);
    });
    
    return cy.wrap(widgetsData);
  }
  
  // 状态验证
  verifyWidgetExists(name) {
    this.getWidgetByName(name).should('exist');
    return this;
  }
  
  verifyNotificationExists(type, message) {
    this.getNotificationByType(type)
      .should('be.visible')
      .and('contain', message);
    return this;
  }
}
```

### 页面对象继承

```javascript
// cypress/support/pages/base-page.js
export class BasePage {
  constructor() {
    this.header = cy.get('header');
    this.footer = cy.get('footer');
    this.mainContent = cy.get('main');
    this.loadingIndicator = cy.get('.loading-indicator');
  }
  
  // 通用方法
  visit(url) {
    cy.visit(url);
    return this;
  }
  
  waitForPageLoad() {
    this.loadingIndicator.should('not.exist');
    return this;
  }
  
  verifyHeaderExists() {
    this.header.should('be.visible');
    return this;
  }
  
  verifyFooterExists() {
    this.footer.should('be.visible');
    return this;
  }
  
  scrollToTop() {
    cy.scrollTo('top');
    return this;
  }
  
  scrollToBottom() {
    cy.scrollTo('bottom');
    return this;
  }
}

// cypress/support/pages/login-page.js
import { BasePage } from './base-page';

export class LoginPage extends BasePage {
  constructor() {
    super();
    this.usernameInput = cy.get('#username');
    this.passwordInput = cy.get('#password');
    this.loginButton = cy.get('.login-button');
  }
  
  visit() {
    return super.visit('/login');
  }
  
  login(username, password) {
    this.usernameInput.type(username);
    this.passwordInput.type(password);
    this.loginButton.click();
    return this;
  }
  
  verifyPageLoaded() {
    super.waitForPageLoad();
    cy.url().should('include', '/login');
    this.usernameInput.should('be.visible');
    this.passwordInput.should('be.visible');
    return this;
  }
}
```

### 使用页面对象

```javascript
// cypress/integration/authentication/login-spec.js
import { LoginPage } from '../../support/pages/login-page';
import { DashboardPage } from '../../support/pages/dashboard-page';

describe('用户登录', () => {
  const loginPage = new LoginPage();
  const dashboardPage = new DashboardPage();
  
  beforeEach(() => {
    loginPage.visit();
  });
  
  it('应该成功登录有效用户', () => {
    loginPage
      .verifyPageLoaded()
      .login('testuser', 'password123');
    
    dashboardPage
      .waitForPageLoad()
      .verifyHeaderExists();
    
    cy.url().should('include', '/dashboard');
  });
  
  it('应该拒绝无效用户登录', () => {
    loginPage
      .verifyPageLoaded()
      .login('invaliduser', 'wrongpassword');
    
    loginPage.verifyErrorMessage('用户名或密码错误');
  });
});
```

## 6.6 测试工具类

### 通用工具类

```javascript
// cypress/support/utils/common-utils.js
export class CommonUtils {
  // 等待元素出现
  static waitForElement(selector, timeout = 5000) {
    return cy.get(selector, { timeout }).should('be.visible');
  }
  
  // 等待元素消失
  static waitForElementToDisappear(selector, timeout = 5000) {
    return cy.get(selector, { timeout }).should('not.exist');
  }
  
  // 等待API响应
  static waitForApiResponse(alias, timeout = 10000) {
    return cy.wait(`@${alias}`, { timeout });
  }
  
  // 生成随机字符串
  static randomString(length = 10) {
    let result = '';
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const charactersLength = characters.length;
    
    for (let i = 0; i < length; i++) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    
    return result;
  }
  
  // 生成随机数字
  static randomNumber(min = 0, max = 1000) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }
  
  // 生成随机邮箱
  static randomEmail() {
    const domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'example.com'];
    const domain = domains[Math.floor(Math.random() * domains.length)];
    return `${this.randomString(8)}@${domain}`;
  }
  
  // 生成随机电话号码
  static randomPhoneNumber() {
    return `555-${this.randomNumber(100, 999)}-${this.randomNumber(1000, 9999)}`;
  }
  
  // 格式化日期
  static formatDate(date, format = 'YYYY-MM-DD') {
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    
    return format
      .replace('YYYY', year)
      .replace('MM', month)
      .replace('DD', day);
  }
  
  // 等待指定时间
  static wait(ms) {
    return cy.wait(ms);
  }
  
  // 截图
  static screenshot(name) {
    return cy.screenshot(name);
  }
  
  // 记录日志
  static log(message) {
    return cy.log(message);
  }
}
```

### API工具类

```javascript
// cypress/support/utils/api-utils.js
export class ApiUtils {
  // 发送GET请求
  static get(url, headers = {}) {
    return cy.request({
      method: 'GET',
      url,
      headers
    });
  }
  
  // 发送POST请求
  static post(url, body = {}, headers = {}) {
    return cy.request({
      method: 'POST',
      url,
      body,
      headers
    });
  }
  
  // 发送PUT请求
  static put(url, body = {}, headers = {}) {
    return cy.request({
      method: 'PUT',
      url,
      body,
      headers
    });
  }
  
  // 发送DELETE请求
  static delete(url, headers = {}) {
    return cy.request({
      method: 'DELETE',
      url,
      headers
    });
  }
  
  // 获取认证令牌
  static getAuthToken(username, password) {
    return this.post('/api/auth/login', {
      username,
      password
    }).then((response) => {
      return response.body.token;
    });
  }
  
  // 设置认证头
  static setAuthHeader(token) {
    return {
      'Authorization': `Bearer ${token}`
    };
  }
  
  // 创建用户
  static createUser(userData) {
    return this.post('/api/users', userData);
  }
  
  // 删除用户
  static deleteUser(userId, token) {
    return this.delete(`/api/users/${userId}`, this.setAuthHeader(token));
  }
  
  // 获取用户
  static getUser(userId, token) {
    return this.get(`/api/users/${userId}`, this.setAuthHeader(token));
  }
  
  // 更新用户
  static updateUser(userId, userData, token) {
    return this.put(`/api/users/${userId}`, userData, this.setAuthHeader(token));
  }
}
```

### 数据库工具类

```javascript
// cypress/support/utils/db-utils.js
export class DbUtils {
  // 执行查询
  static query(sql, params = []) {
    return cy.task('dbQuery', { sql, params });
  }
  
  // 执行插入
  static insert(table, data) {
    const columns = Object.keys(data).join(', ');
    const values = Object.values(data);
    const placeholders = values.map(() => '?').join(', ');
    
    const sql = `INSERT INTO ${table} (${columns}) VALUES (${placeholders})`;
    
    return this.query(sql, values);
  }
  
  // 执行更新
  static update(table, data, condition, conditionParams = []) {
    const setClause = Object.keys(data).map(key => `${key} = ?`).join(', ');
    const values = [...Object.values(data), ...conditionParams];
    
    const sql = `UPDATE ${table} SET ${setClause} WHERE ${condition}`;
    
    return this.query(sql, values);
  }
  
  // 执行删除
  static delete(table, condition, params = []) {
    const sql = `DELETE FROM ${table} WHERE ${condition}`;
    
    return this.query(sql, params);
  }
  
  // 查找记录
  static find(table, condition, params = []) {
    const sql = `SELECT * FROM ${table} WHERE ${condition}`;
    
    return this.query(sql, params);
  }
  
  // 查找所有记录
  static findAll(table) {
    const sql = `SELECT * FROM ${table}`;
    
    return this.query(sql);
  }
  
  // 清空表
  static truncate(table) {
    const sql = `TRUNCATE TABLE ${table}`;
    
    return this.query(sql);
  }
  
  // 创建用户
  static createUser(userData) {
    return this.insert('users', userData);
  }
  
  // 获取用户
  static getUser(userId) {
    return this.find('users', 'id = ?', [userId]).then((results) => {
      return results.length > 0 ? results[0] : null;
    });
  }
  
  // 删除用户
  static deleteUser(userId) {
    return this.delete('users', 'id = ?', [userId]);
  }
  
  // 清理测试数据
  static cleanTestData() {
    return this.query('DELETE FROM users WHERE email LIKE "%test%"');
  }
}
```

## 6.7 测试报告与结果分析

### 自定义报告器

```javascript
// cypress/plugins/index.js
const fs = require('fs');
const path = require('path');

module.exports = (on, config) => {
  // 自定义报告器
  on('after:spec', (spec, results) => {
    if (results && results.stats) {
      const reportData = {
        spec: spec.name,
        tests: results.stats.tests,
        passes: results.stats.passes,
        failures: results.stats.failures,
        pending: results.stats.pending,
        duration: results.stats.duration,
        timestamp: new Date().toISOString()
      };
      
      // 将报告数据写入文件
      const reportPath = path.join(config.projectRoot, 'cypress', 'reports');
      
      if (!fs.existsSync(reportPath)) {
        fs.mkdirSync(reportPath, { recursive: true });
      }
      
      const reportFile = path.join(reportPath, `${spec.name.replace(/\//g, '_')}.json`);
      fs.writeFileSync(reportFile, JSON.stringify(reportData, null, 2));
    }
  });
  
  return config;
};
```

### 测试结果分析

```javascript
// cypress/support/utils/test-results-analyzer.js
export class TestResultsAnalyzer {
  // 分析测试结果
  static analyzeResults(results) {
    const analysis = {
      totalTests: results.tests,
      passedTests: results.passes,
      failedTests: results.failures,
      pendingTests: results.pending,
      passRate: (results.passes / results.tests * 100).toFixed(2),
      duration: this.formatDuration(results.duration)
    };
    
    return analysis;
  }
  
  // 格式化持续时间
  static formatDuration(ms) {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes % 60}m ${seconds % 60}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds % 60}s`;
    } else {
      return `${seconds}s`;
    }
  }
  
  // 生成测试摘要
  static generateSummary(results) {
    const analysis = this.analyzeResults(results);
    
    return `
测试摘要:
- 总测试数: ${analysis.totalTests}
- 通过测试: ${analysis.passedTests}
- 失败测试: ${analysis.failedTests}
- 待定测试: ${analysis.pendingTests}
- 通过率: ${analysis.passRate}%
- 执行时间: ${analysis.duration}
    `.trim();
  }
  
  // 生成失败测试报告
  static generateFailureReport(failures) {
    if (!failures || failures.length === 0) {
      return '没有失败的测试';
    }
    
    let report = '失败测试报告:\n\n';
    
    failures.forEach((failure, index) => {
      report += `${index + 1}. ${failure.title}\n`;
      report += `   错误: ${failure.message}\n`;
      report += `   位置: ${failure.fullTitle}\n\n`;
    });
    
    return report;
  }
}
```

### 测试覆盖率

```javascript
// cypress/plugins/index.js
module.exports = (on, config) => {
  // 代码覆盖率
  if (config.env.codeCoverage) {
    require('@cypress/code-coverage/task')(on, config);
  }
  
  return config;
};

// cypress/support/index.js
// 导入代码覆盖率支持
if (Cypress.env('codeCoverage')) {
  import '@cypress/code-coverage/support';
}
```

## 6.8 实验与实践

### 实验1：测试文件组织

**目标**：练习组织测试文件和目录结构

**步骤**：
1. 创建合理的目录结构
2. 按功能模块组织测试文件
3. 使用一致的命名规范

**示例代码**：
```javascript
// cypress/integration/authentication/login-spec.js
describe('用户登录', () => {
  it('应该成功登录有效用户', () => {
    // 测试代码
  });
});

// cypress/integration/authentication/logout-spec.js
describe('用户登出', () => {
  it('应该成功登出', () => {
    // 测试代码
  });
});
```

### 实验2：页面对象模型

**目标**：练习使用页面对象模型组织测试

**步骤**：
1. 创建页面对象类
2. 实现页面对象方法
3. 在测试中使用页面对象

**示例代码**：
```javascript
// cypress/support/pages/login-page.js
export class LoginPage {
  get usernameInput() {
    return cy.get('#username');
  }
  
  get passwordInput() {
    return cy.get('#password');
  }
  
  get loginButton() {
    return cy.get('.login-button');
  }
  
  login(username, password) {
    this.usernameInput.type(username);
    this.passwordInput.type(password);
    this.loginButton.click();
    return this;
  }
}

// cypress/integration/authentication/login-spec.js
import { LoginPage } from '../../support/pages/login-page';

describe('用户登录', () => {
  const loginPage = new LoginPage();
  
  it('应该成功登录有效用户', () => {
    loginPage.login('testuser', 'password123');
    cy.url().should('include', '/dashboard');
  });
});
```

### 实验3：测试数据管理

**目标**：练习使用不同方法管理测试数据

**步骤**：
1. 使用Fixture管理静态测试数据
2. 动态生成测试数据
3. 使用工厂模式创建测试数据

**示例代码**：
```javascript
// cypress/support/utils/test-data-generator.js
export class TestDataGenerator {
  static generateUser(overrides = {}) {
    const randomId = Math.floor(Math.random() * 10000);
    const defaultUser = {
      username: `user_${randomId}`,
      email: `user_${randomId}@example.com`,
      password: 'Password123!',
      ...overrides
    };
    
    return defaultUser;
  }
}

// cypress/integration/user/registration-spec.js
import { TestDataGenerator } from '../../support/utils/test-data-generator';

describe('用户注册', () => {
  it('应该注册新用户', () => {
    const newUser = TestDataGenerator.generateUser({
      firstName: 'John',
      lastName: 'Doe'
    });
    
    cy.visit('/register');
    cy.get('#username').type(newUser.username);
    cy.get('#email').type(newUser.email);
    cy.get('#password').type(newUser.password);
    cy.get('.register-button').click();
    
    cy.get('.success-message').should('contain', '用户注册成功');
  });
});
```

## 本章小结

本章介绍了Cypress测试组织与数据管理，包括：

- 测试文件组织：目录结构，文件命名规范，文件内容组织
- 测试套件结构：测试套件组织，测试套件配置，条件测试
- 测试数据管理：Fixture数据管理，动态数据生成，数据工厂模式
- 测试环境管理：多环境配置，环境特定测试，环境清理
- 页面对象模型：基本页面对象，高级页面对象，页面对象继承
- 测试工具类：通用工具类，API工具类，数据库工具类
- 测试报告与结果分析：自定义报告器，测试结果分析，测试覆盖率

通过本章的学习，您应该能够：
- 组织和管理测试文件和目录结构
- 使用页面对象模型提高测试可维护性
- 管理和组织测试数据
- 管理不同测试环境
- 创建和使用测试工具类
- 分析测试结果和生成报告

在下一章中，我们将学习Cypress性能优化与调试，深入了解如何提高测试性能和调试测试问题。
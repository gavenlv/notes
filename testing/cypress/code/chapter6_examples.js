// 第6章：Cypress测试组织与数据管理示例代码

// 实验1：测试文件组织
describe('测试文件组织实验', () => {
  // 测试套件结构示例
  describe('用户管理模块', () => {
    // 嵌套套件示例
    describe('用户注册', () => {
      beforeEach(() => {
        cy.visit('/register');
      });
      
      it('应该成功注册新用户', () => {
        cy.get('#username').type('newuser');
        cy.get('#email').type('newuser@example.com');
        cy.get('#password').type('password123');
        cy.get('#confirmPassword').type('password123');
        cy.get('.register-button').click();
        
        cy.get('.success-message').should('contain', '用户注册成功');
      });
      
      it('应该拒绝重复用户名注册', () => {
        cy.get('#username').type('existinguser');
        cy.get('#email').type('existing@example.com');
        cy.get('#password').type('password123');
        cy.get('#confirmPassword').type('password123');
        cy.get('.register-button').click();
        
        cy.get('.error-message').should('contain', '用户名已存在');
      });
    });
    
    describe('用户登录', () => {
      beforeEach(() => {
        cy.visit('/login');
      });
      
      it('应该成功登录有效用户', () => {
        cy.get('#username').type('testuser');
        cy.get('#password').type('password123');
        cy.get('.login-button').click();
        
        cy.url().should('include', '/dashboard');
      });
      
      it('应该拒绝无效用户登录', () => {
        cy.get('#username').type('invaliduser');
        cy.get('#password').type('wrongpassword');
        cy.get('.login-button').click();
        
        cy.get('.error-message').should('contain', '用户名或密码错误');
      });
    });
  });
  
  // 条件测试示例
  describe('条件测试示例', () => {
    // 根据环境变量决定是否运行测试
    if (Cypress.env('skipSlowTests')) {
      it.skip('慢速测试 - 已跳过', () => {
        cy.wait(5000); // 模拟慢速测试
        cy.log('这是一个慢速测试');
      });
    } else {
      it('慢速测试 - 运行中', () => {
        cy.wait(1000); // 模拟慢速测试
        cy.log('这是一个慢速测试');
      });
    }
    
    // 使用动态测试
    const testCases = [
      { input: 'a', expected: 'A' },
      { input: 'b', expected: 'B' },
      { input: 'c', expected: 'C' }
    ];
    
    testCases.forEach((testCase, index) => {
      it(`应该转换输入 ${testCase.input} 为 ${testCase.expected}`, () => {
        cy.wrap(testCase.input.toUpperCase()).should('eq', testCase.expected);
      });
    });
  });
});

// 实验2：页面对象模型
describe('页面对象模型实验', () => {
  // 基本页面对象示例
  class LoginPage {
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
  }
  
  // 高级页面对象示例
  class DashboardPage {
    constructor() {
      this.userMenu = cy.get('.user-menu');
      this.logoutButton = cy.get('.logout-button');
      this.widgets = cy.get('.widget');
    }
    
    // 动态元素定位
    getWidgetByName(name) {
      return this.widgets.contains(name);
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
    
    // 状态验证
    verifyWidgetExists(name) {
      this.getWidgetByName(name).should('exist');
      return this;
    }
  }
  
  // 页面对象继承示例
  class BasePage {
    // 通用方法
    visit(url) {
      cy.visit(url);
      return this;
    }
    
    waitForPageLoad() {
      cy.get('.loading-indicator').should('not.exist');
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
  
  class ExtendedLoginPage extends BasePage {
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
  
  // 使用页面对象
  const loginPage = new LoginPage();
  const dashboardPage = new DashboardPage();
  const extendedLoginPage = new ExtendedLoginPage();
  
  it('应该使用基本页面对象登录', () => {
    loginPage
      .visit()
      .verifyPageLoaded()
      .login('testuser', 'password123');
    
    cy.url().should('include', '/dashboard');
  });
  
  it('应该使用高级页面对象操作仪表板', () => {
    // 先登录
    loginPage.visit().login('testuser', 'password123');
    
    // 使用仪表板页面对象
    dashboardPage
      .verifyWidgetExists('用户统计')
      .navigateToSection('设置');
  });
  
  it('应该使用继承页面对象登录', () => {
    extendedLoginPage
      .visit()
      .verifyPageLoaded()
      .login('testuser', 'password123');
    
    cy.url().should('include', '/dashboard');
  });
});

// 实验3：测试数据管理
describe('测试数据管理实验', () => {
  // 使用fixture数据
  it('应该使用fixture数据', () => {
    // 模拟fixture数据
    const users = {
      validUser: {
        username: 'testuser',
        password: 'password123',
        email: 'test@example.com',
        firstName: 'Test',
        lastName: 'User'
      },
      adminUser: {
        username: 'admin',
        password: 'admin123',
        email: 'admin@example.com',
        firstName: 'Admin',
        lastName: 'User',
        role: 'admin'
      },
      invalidUser: {
        username: 'invaliduser',
        password: 'wrongpassword'
      }
    };
    
    // 使用fixture数据登录
    cy.visit('/login');
    cy.get('#username').type(users.validUser.username);
    cy.get('#password').type(users.validUser.password);
    cy.get('.login-button').click();
    
    cy.url().should('include', '/dashboard');
  });
  
  // 动态数据生成
  it('应该使用动态生成的数据', () => {
    // 生成随机用户数据
    const generateRandomUser = () => {
      const randomId = Math.floor(Math.random() * 10000);
      return {
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
    };
    
    const newUser = generateRandomUser();
    
    // 验证生成的数据
    expect(newUser.username).to.match(/^user_\d+$/);
    expect(newUser.email).to.match(/^user_\d+@example\.com$/);
    expect(newUser.password).to.eq('Password123!');
    
    // 使用生成的数据注册用户
    cy.visit('/register');
    cy.get('#username').type(newUser.username);
    cy.get('#email').type(newUser.email);
    cy.get('#password').type(newUser.password);
    cy.get('#firstName').type(newUser.firstName);
    cy.get('#lastName').type(newUser.lastName);
    cy.get('.register-button').click();
    
    cy.get('.success-message').should('contain', '用户注册成功');
  });
  
  // 数据工厂模式
  it('应该使用数据工厂模式', () => {
    // 用户工厂类
    class UserFactory {
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
        // 在实际项目中，这里会调用API或数据库创建用户
        const userData = this.attributes(overrides);
        cy.log(`创建用户: ${userData.username}`);
        return cy.wrap(userData);
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
    
    // 使用工厂创建用户
    UserFactory.create({
      username: 'testuser',
      email: 'test@example.com'
    }).then((user) => {
      // 使用创建的用户登录
      cy.visit('/login');
      cy.get('#username').type(user.username);
      cy.get('#password').type(user.password);
      cy.get('.login-button').click();
      
      cy.url().should('include', '/dashboard');
    });
  });
});

// 测试工具类示例
describe('测试工具类示例', () => {
  // 通用工具类
  class CommonUtils {
    // 等待元素出现
    static waitForElement(selector, timeout = 5000) {
      return cy.get(selector, { timeout }).should('be.visible');
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
    
    // 生成随机邮箱
    static randomEmail() {
      const domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'example.com'];
      const domain = domains[Math.floor(Math.random() * domains.length)];
      return `${this.randomString(8)}@${domain}`;
    }
    
    // 记录日志
    static log(message) {
      return cy.log(message);
    }
  }
  
  // API工具类
  class ApiUtils {
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
    
    // 获取认证令牌
    static getAuthToken(username, password) {
      return this.post('/api/auth/login', {
        username,
        password
      }).then((response) => {
        return response.body.token;
      });
    }
  }
  
  it('应该使用通用工具类', () => {
    // 等待元素出现
    CommonUtils.waitForElement('h1');
    
    // 生成随机字符串
    const randomStr = CommonUtils.randomString(8);
    expect(randomStr).to.have.length(8);
    
    // 生成随机邮箱
    const randomEmail = CommonUtils.randomEmail();
    expect(randomEmail).to.include('@');
    
    // 记录日志
    CommonUtils.log('测试日志消息');
  });
  
  it('应该使用API工具类', () => {
    // 模拟API请求
    ApiUtils.get('https://jsonplaceholder.typicode.com/users/1').then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.have.property('name');
    });
    
    // 模拟API POST请求
    ApiUtils.post('https://jsonplaceholder.typicode.com/posts', {
      title: 'Test Post',
      body: 'Test body',
      userId: 1
    }).then((response) => {
      expect(response.status).to.eq(201);
      expect(response.body).to.have.property('id');
    });
  });
});

// 测试环境管理示例
describe('测试环境管理示例', () => {
  it('应该使用正确的baseUrl', () => {
    cy.visit('/');
    cy.url().should('include', Cypress.config().baseUrl);
  });
  
  it('应该连接到正确的API', () => {
    // 模拟API URL
    const apiUrl = Cypress.env('apiUrl') || 'https://jsonplaceholder.typicode.com';
    
    cy.request(apiUrl + '/posts/1').then((response) => {
      expect(response.status).to.eq(200);
    });
  });
  
  // 只在特定环境运行
  if (Cypress.env('environment') === 'staging') {
    it('应该在staging环境执行特定测试', () => {
      cy.log('在staging环境执行特定测试');
      cy.wrap('staging').should('eq', 'staging');
    });
  }
  
  // 跳过特定环境
  if (Cypress.env('environment') === 'production') {
    it.skip('不应该在生产环境执行破坏性测试', () => {
      cy.log('在生产环境跳过破坏性测试');
    });
  }
});

// 测试报告与结果分析示例
describe('测试报告与结果分析示例', () => {
  // 测试结果分析
  class TestResultsAnalyzer {
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
  }
  
  it('应该分析测试结果', () => {
    // 模拟测试结果
    const mockResults = {
      tests: 10,
      passes: 8,
      failures: 2,
      pending: 0,
      duration: 15000
    };
    
    const analysis = TestResultsAnalyzer.analyzeResults(mockResults);
    
    expect(analysis.totalTests).to.eq(10);
    expect(analysis.passedTests).to.eq(8);
    expect(analysis.failedTests).to.eq(2);
    expect(analysis.passRate).to.eq('80.00');
    expect(analysis.duration).to.eq('15s');
  });
  
  it('应该生成测试摘要', () => {
    // 模拟测试结果
    const mockResults = {
      tests: 10,
      passes: 8,
      failures: 2,
      pending: 0,
      duration: 15000
    };
    
    const summary = TestResultsAnalyzer.generateSummary(mockResults);
    
    expect(summary).to.include('总测试数: 10');
    expect(summary).to.include('通过测试: 8');
    expect(summary).to.include('失败测试: 2');
    expect(summary).to.include('通过率: 80.00%');
    expect(summary).to.include('执行时间: 15s');
    
    cy.log(summary);
  });
});

// 环境清理示例
describe('环境清理示例', () => {
  // 清理工具类
  class Cleanup {
    // 重置应用状态
    static resetApplicationState() {
      cy.clearCookies();
      cy.clearLocalStorage();
      return cy.window().then((win) => {
        win.sessionStorage.clear();
      });
    }
    
    // 清理测试数据
    static cleanTestData() {
      // 在实际项目中，这里会调用API或数据库清理
      cy.log('清理测试数据');
      return cy.wrap(null);
    }
  }
  
  beforeEach(() => {
    // 在每个测试前重置应用状态
    Cleanup.resetApplicationState();
  });
  
  afterEach(() => {
    // 在每个测试后清理测试数据
    Cleanup.cleanTestData();
  });
  
  it('应该重置应用状态', () => {
    // 设置一些状态
    cy.window().then((win) => {
      win.localStorage.setItem('testKey', 'testValue');
      win.sessionStorage.setItem('sessionKey', 'sessionValue');
    });
    
    // 验证状态已设置
    cy.window().then((win) => {
      expect(win.localStorage.getItem('testKey')).to.eq('testValue');
      expect(win.sessionStorage.getItem('sessionKey')).to.eq('sessionValue');
    });
    
    // 重置状态
    Cleanup.resetApplicationState();
    
    // 验证状态已重置
    cy.window().then((win) => {
      expect(win.localStorage.getItem('testKey')).to.be.null;
      expect(win.sessionStorage.getItem('sessionKey')).to.be.null;
    });
  });
  
  it('应该清理测试数据', () => {
    // 创建一些测试数据
    cy.window().then((win) => {
      win.localStorage.setItem('testData1', 'value1');
      win.localStorage.setItem('testData2', 'value2');
    });
    
    // 验证数据已创建
    cy.window().then((win) => {
      expect(win.localStorage.getItem('testData1')).to.eq('value1');
      expect(win.localStorage.getItem('testData2')).to.eq('value2');
    });
    
    // 清理测试数据
    Cleanup.cleanTestData();
    
    // 验证数据已清理
    cy.window().then((win) => {
      expect(win.localStorage.getItem('testData1')).to.be.null;
      expect(win.localStorage.getItem('testData2')).to.be.null;
    });
  });
});
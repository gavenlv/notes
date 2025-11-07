# 第5章：Cypress高级特性与自定义命令

## 目录
- [5.1 环境变量与配置](#51-环境变量与配置)
- [5.2 插件系统](#52-插件系统)
- [5.3 任务与文件操作](#53-任务与文件操作)
- [5.4 自定义命令](#54-自定义命令)
- [5.5 测试运行器扩展](#55-测试运行器扩展)
- [5.6 高级选择器技巧](#56-高级选择器技巧)
- [5.7 测试数据管理](#57-测试数据管理)
- [5.8 实验与实践](#58-实验与实践)

## 5.1 环境变量与配置

### 环境变量

Cypress支持多种方式设置环境变量：

#### 通过cypress.json配置

```json
{
  "env": {
    "username": "testuser",
    "password": "password123",
    "apiUrl": "https://api.example.com"
  }
}
```

#### 通过命令行传递

```bash
# 设置单个环境变量
cypress run --env username=admin

# 设置多个环境变量
cypress run --env username=admin,password=admin123
```

#### 通过.env文件

创建`.env`文件：
```
CYPRESS_username=testuser
CYPRESS_password=password123
CYPRESS_apiUrl=https://api.example.com
```

#### 在测试中使用环境变量

```javascript
// 访问环境变量
const username = Cypress.env('username');
const password = Cypress.env('password');
const apiUrl = Cypress.env('apiUrl');

// 在测试中使用
it('should login with environment variables', () => {
  cy.visit('/login');
  cy.get('#username').type(username);
  cy.get('#password').type(password);
  cy.get('.login-button').click();
});
```

### 配置选项

Cypress提供了丰富的配置选项：

```json
{
  "baseUrl": "http://localhost:3000",
  "defaultCommandTimeout": 5000,
  "requestTimeout": 5000,
  "responseTimeout": 30000,
  "viewportWidth": 1280,
  "viewportHeight": 720,
  "video": true,
  "screenshotOnRunFailure": true,
  "trashAssetsBeforeRuns": true,
  "chromeWebSecurity": false,
  "testFiles": "**/*.{js,jsx,ts,tsx}",
  "ignoreTestFiles": "*.hot-update.js",
  "supportFile": "cypress/support/index.js",
  "pluginsFile": "cypress/plugins/index.js",
  "fixturesFolder": "cypress/fixtures",
  "integrationFolder": "cypress/integration",
  "screenshotsFolder": "cypress/screenshots",
  "videosFolder": "cypress/videos",
  "downloadsFolder": "cypress/downloads"
}
```

### 条件配置

```javascript
// cypress/plugins/index.js
module.exports = (on, config) => {
  // 根据环境设置不同配置
  if (config.env === 'production') {
    config.baseUrl = 'https://prod.example.com';
  } else if (config.env === 'staging') {
    config.baseUrl = 'https://staging.example.com';
  } else {
    config.baseUrl = 'http://localhost:3000';
  }
  
  return config;
};
```

## 5.2 插件系统

### 插件基础

Cypress插件系统允许扩展测试运行器的功能：

```javascript
// cypress/plugins/index.js
module.exports = (on, config) => {
  // on函数用于注册事件监听器
  // config对象包含Cypress配置
  
  return config;
};
```

### 常用插件

#### cypress-file-upload

用于文件上传测试：

```javascript
// 安装
npm install --save-dev cypress-file-upload

// 在cypress/support/commands.js中导入
import 'cypress-file-upload';

// 在测试中使用
cy.get('input[type="file"]').selectFile('file.json');
```

#### cypress-iframe

用于处理iframe：

```javascript
// 安装
npm install --save-dev cypress-iframe

// 在cypress/support/commands.js中导入
import 'cypress-iframe';

// 在测试中使用
cy.frameLoaded('#my-iframe');
cy.iframe().find('.button').click();
```

#### cypress-real-events

用于模拟真实事件：

```javascript
// 安装
npm install --save-dev cypress-real-events

// 在cypress/support/commands.js中导入
import 'cypress-real-events/support';

// 在测试中使用
cy.get('button').realClick();
cy.get('input').realType('Hello');
```

### 自定义插件

```javascript
// cypress/plugins/index.js
const fs = require('fs');
const path = require('path');

module.exports = (on, config) => {
  // 自定义任务
  on('task', {
    // 读取文件
    readFile(filename) {
      if (fs.existsSync(filename)) {
        return fs.readFileSync(filename, 'utf8');
      }
      return null;
    },
    
    // 写入文件
    writeFile({ filename, content }) {
      fs.writeFileSync(filename, content, 'utf8');
      return null;
    },
    
    // 删除文件
    deleteFile(filename) {
      if (fs.existsSync(filename)) {
        fs.unlinkSync(filename);
      }
      return null;
    },
    
    // 检查文件是否存在
    fileExists(filename) {
      return fs.existsSync(filename);
    },
    
    // 获取目录列表
    getDirectoryList(dirPath) {
      return fs.readdirSync(dirPath);
    }
  });
  
  return config;
};
```

## 5.3 任务与文件操作

### 使用任务

```javascript
// 在测试中调用任务
it('should read file content', () => {
  cy.task('readFile', 'cypress/fixtures/test-data.json').then((content) => {
    const data = JSON.parse(content);
    expect(data).to.have.property('users');
  });
});

it('should write file content', () => {
  const testData = { name: 'Test User', email: 'test@example.com' };
  cy.task('writeFile', {
    filename: 'output.json',
    content: JSON.stringify(testData, null, 2)
  });
});

it('should check if file exists', () => {
  cy.task('fileExists', 'cypress/fixtures/test-data.json').should('be.true');
});
```

### 文件操作

```javascript
// 读取fixture文件
cy.fixture('users.json').then((users) => {
  cy.log(users.length);
});

// 读取特定fixture文件
cy.fixture('data', 'json').then((data) => {
  // 使用数据
});

// 动态生成fixture数据
beforeEach(() => {
  cy.task('readFile', 'cypress/fixtures/template.json').then((template) => {
    const data = JSON.parse(template);
    data.timestamp = new Date().toISOString();
    cy.writeFile('cypress/fixtures/generated.json', data);
  });
});
```

### 数据库操作

```javascript
// cypress/plugins/index.js
const mysql = require('mysql2/promise');

module.exports = (on, config) => {
  on('task', {
    // 查询数据库
    queryDatabase(query) {
      const connection = mysql.createConnection({
        host: 'localhost',
        user: 'root',
        password: '',
        database: 'test_db'
      });
      
      return connection.execute(query)
        .then(([rows, fields]) => {
          connection.end();
          return rows;
        })
        .catch(error => {
          connection.end();
          throw error;
        });
    },
    
    // 清理数据库
    cleanDatabase() {
      const connection = mysql.createConnection({
        host: 'localhost',
        user: 'root',
        password: '',
        database: 'test_db'
      });
      
      return connection.execute('DELETE FROM users WHERE email LIKE "%test%"')
        .then(() => {
          connection.end();
          return null;
        })
        .catch(error => {
          connection.end();
          throw error;
        });
    }
  });
  
  return config;
};

// 在测试中使用
it('should query database', () => {
  cy.task('queryDatabase', 'SELECT * FROM users WHERE active = 1').then((users) => {
    expect(users).to.have.length.greaterThan(0);
  });
});
```

## 5.4 自定义命令

### 创建自定义命令

在`cypress/support/commands.js`中添加自定义命令：

```javascript
// 登录命令
Cypress.Commands.add('login', (username, password) => {
  cy.visit('/login');
  cy.get('#username').type(username);
  cy.get('#password').type(password);
  cy.get('.login-button').click();
  cy.url().should('include', '/dashboard');
});

// 添加商品到购物车命令
Cypress.Commands.add('addToCart', (productId) => {
  cy.get(`[data-product-id="${productId}"]`).find('.add-to-cart').click();
  cy.get('.cart-count').should('contain', /\d+/);
});

// 等待加载完成命令
Cypress.Commands.add('waitForLoading', () => {
  cy.get('.loading-indicator').should('not.exist');
});

// 数据库清理命令
Cypress.Commands.add('cleanDatabase', () => {
  cy.task('cleanDatabase');
});

// 设置API令牌命令
Cypress.Commands.add('setApiToken', (token) => {
  window.localStorage.setItem('auth_token', token);
});
```

### 使用自定义命令

```javascript
describe('使用自定义命令', () => {
  beforeEach(() => {
    // 使用自定义登录命令
    cy.login('testuser', 'password123');
  });

  it('should add product to cart', () => {
    // 使用自定义添加到购物车命令
    cy.addToCart('product-123');
    
    // 验证购物车更新
    cy.get('.cart-count').should('contain', '1');
  });

  it('should wait for loading', () => {
    cy.visit('/slow-page');
    
    // 使用自定义等待加载命令
    cy.waitForLoading();
    
    // 验证内容已加载
    cy.get('.content').should('be.visible');
  });

  it('should use API token', () => {
    // 设置API令牌
    cy.setApiToken('fake-jwt-token');
    
    // 访问需要认证的页面
    cy.visit('/protected-page');
    cy.get('.protected-content').should('be.visible');
  });
});
```

### 高级自定义命令

```javascript
// 带回调的自定义命令
Cypress.Commands.add('getData', (url, callback) => {
  cy.request(url).then((response) => {
    callback(response.body);
  });
});

// 带选项的自定义命令
Cypress.Commands.add('typeSlow', { prevSubject: 'element' }, (subject, text, options = {}) => {
  const { delay = 100 } = options;
  cy.wrap(subject).type(text, { delay });
});

// 带验证的自定义命令
Cypress.Commands.add('loginAndVerify', (username, password) => {
  cy.visit('/login');
  cy.get('#username').type(username);
  cy.get('#password').type(password);
  cy.get('.login-button').click();
  
  // 验证登录成功
  cy.url().should('include', '/dashboard');
  cy.get('.user-name').should('contain', username);
  
  // 返回用户信息供后续使用
  return cy.get('.user-info').then(($info) => {
    return {
      name: $info.find('.user-name').text(),
      email: $info.find('.user-email').text()
    };
  });
});
```

## 5.5 测试运行器扩展

### 自定义报告器

```javascript
// 安装自定义报告器
npm install --save-dev cypress-mochawesome-reporter

// cypress/plugins/index.js
const { report } = require('cypress-mochawesome-reporter');

module.exports = (on, config) => {
  report(on, config);
  
  return config;
};

// cypress.json
{
  "reporter": "cypress-mochawesome-reporter",
  "reporterOptions": {
    "reportDir": "cypress/results",
    "charts": true,
    "reportPageTitle": "Cypress Test Report"
  }
}
```

### 自定义测试运行器事件

```javascript
// cypress/plugins/index.js
module.exports = (on, config) => {
  // 测试开始前
  on('before:run', (details) => {
    console.log('Starting test run:', details.specs);
  });
  
  // 测试结束后
  on('after:run', (results) => {
    console.log('Test run completed:', results.totalPassed, 'passed');
  });
  
  // 测试用例开始前
  on('before:spec', (spec, results) => {
    console.log('Running spec:', spec.name);
  });
  
  // 测试用例结束后
  on('after:spec', (spec, results) => {
    console.log('Spec completed:', spec.name, results.stats.passes, 'passed');
  });
  
  return config;
};
```

### 自定义浏览器配置

```javascript
// cypress/plugins/index.js
module.exports = (on, config) => {
  // 自定义Chrome启动参数
  on('before:browser:launch', (browser, launchOptions) => {
    if (browser.name === 'chrome') {
      launchOptions.args.push('--disable-dev-shm-usage');
      launchOptions.args.push('--no-sandbox');
      launchOptions.args.push('--disable-gpu');
    }
    
    return launchOptions;
  });
  
  return config;
};
```

## 5.6 高级选择器技巧

### 使用jQuery选择器

```javascript
// 使用jQuery选择器
cy.get(':input:not([type=hidden])').should('have.length', 5);
cy.get('div:has(.active)').should('have.class', 'container');
cy.get('li:contains("Item")').should('have.length', 3);
cy.get('input[name^="user"]').should('have.length', 2);
```

### 使用XPath选择器

```javascript
// 安装XPath插件
npm install --save-dev cypress-xpath

// 在cypress/support/commands.js中导入
require('cypress-xpath');

// 在测试中使用XPath
cy.xpath('//button[contains(text(), "Submit")]').click();
cy.xpath('//div[@class="container"]//p[1]').should('contain', 'First paragraph');
```

### 使用contains和filter

```javascript
// 使用contains查找包含特定文本的元素
cy.contains('button', 'Submit').click();
cy.contains('.error', 'Invalid email').should('be.visible');

// 使用filter过滤元素
cy.get('.list-item').filter(':even').should('have.length', 3);
cy.get('.list-item').filter(':contains("Important")').should('have.class', 'highlight');
```

### 使用within限定作用域

```javascript
// 使用within限定命令作用域
cy.get('.form').within(() => {
  cy.get('#username').type('testuser');
  cy.get('#password').type('password123');
  cy.get('.submit').click();
});

// 使用within验证特定区域
cy.get('.user-card').within(() => {
  cy.get('.name').should('contain', 'John Doe');
  cy.get('.email').should('contain', 'john@example.com');
});
```

## 5.7 测试数据管理

### 使用Fixture管理测试数据

```javascript
// cypress/fixtures/users.json
{
  "admin": {
    "username": "admin",
    "password": "admin123",
    "email": "admin@example.com"
  },
  "user": {
    "username": "testuser",
    "password": "password123",
    "email": "user@example.com"
  }
}

// 在测试中使用
it('should login with admin credentials', () => {
  cy.fixture('users').then((users) => {
    cy.visit('/login');
    cy.get('#username').type(users.admin.username);
    cy.get('#password').type(users.admin.password);
    cy.get('.login-button').click();
    cy.url().should('include', '/admin');
  });
});
```

### 动态生成测试数据

```javascript
// 生成随机用户数据
const generateRandomUser = () => {
  const randomId = Math.floor(Math.random() * 1000);
  return {
    username: `user${randomId}`,
    email: `user${randomId}@example.com`,
    password: 'password123',
    firstName: 'Test',
    lastName: `User${randomId}`
  };
};

// 在测试中使用
it('should create a new user', () => {
  const user = generateRandomUser();
  
  cy.visit('/register');
  cy.get('#username').type(user.username);
  cy.get('#email').type(user.email);
  cy.get('#password').type(user.password);
  cy.get('#firstName').type(user.firstName);
  cy.get('#lastName').type(user.lastName);
  cy.get('.register-button').click();
  
  cy.get('.success-message').should('contain', 'User created successfully');
});
```

### 使用工厂模式创建测试数据

```javascript
// cypress/support/factories/userFactory.js
class UserFactory {
  static create(overrides = {}) {
    const defaultUser = {
      username: 'testuser',
      email: 'test@example.com',
      password: 'password123',
      firstName: 'Test',
      lastName: 'User',
      active: true
    };
    
    return { ...defaultUser, ...overrides };
  }
  
  static createAdmin(overrides = {}) {
    return this.create({
      username: 'admin',
      email: 'admin@example.com',
      role: 'admin',
      ...overrides
    });
  }
  
  static createInactive(overrides = {}) {
    return this.create({
      active: false,
      ...overrides
    });
  }
}

// 在测试中使用
it('should handle admin user', () => {
  const admin = UserFactory.createAdmin();
  
  cy.visit('/login');
  cy.get('#username').type(admin.username);
  cy.get('#password').type(admin.password);
  cy.get('.login-button').click();
  
  cy.url().should('include', '/admin');
});
```

## 5.8 实验与实践

### 实验1：环境变量与配置

**目标**：练习使用环境变量和配置管理不同环境的测试

**步骤**：
1. 创建不同环境的配置文件
2. 设置环境变量
3. 在测试中使用环境变量

**示例代码**：
```javascript
describe('环境变量与配置实验', () => {
  it('should use environment variables', () => {
    const apiUrl = Cypress.env('apiUrl');
    const username = Cypress.env('username');
    const password = Cypress.env('password');
    
    cy.request('POST', `${apiUrl}/login`, {
      username,
      password
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.have.property('token');
    });
  });
});
```

### 实验2：自定义命令

**目标**：练习创建和使用自定义命令

**步骤**：
1. 创建自定义命令
2. 在测试中使用自定义命令
3. 验证自定义命令的功能

**示例代码**：
```javascript
describe('自定义命令实验', () => {
  it('should use custom login command', () => {
    cy.login('testuser', 'password123');
    cy.url().should('include', '/dashboard');
  });
  
  it('should use custom add to cart command', () => {
    cy.addToCart('product-123');
    cy.get('.cart-count').should('contain', '1');
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
describe('测试数据管理实验', () => {
  it('should use fixture data', () => {
    cy.fixture('users').then((users) => {
      const user = users.user;
      cy.visit('/login');
      cy.get('#username').type(user.username);
      cy.get('#password').type(user.password);
      cy.get('.login-button').click();
      cy.url().should('include', '/dashboard');
    });
  });
  
  it('should use dynamically generated data', () => {
    const user = generateRandomUser();
    cy.visit('/register');
    // 使用生成的用户数据填写表单
    // ...
  });
});
```

## 本章小结

本章介绍了Cypress的高级特性与自定义命令，包括：

- 环境变量与配置：设置和使用环境变量，配置选项，条件配置
- 插件系统：常用插件，自定义插件，插件开发
- 任务与文件操作：使用任务，文件操作，数据库操作
- 自定义命令：创建自定义命令，使用自定义命令，高级自定义命令
- 测试运行器扩展：自定义报告器，自定义测试运行器事件，自定义浏览器配置
- 高级选择器技巧：jQuery选择器，XPath选择器，contains和filter，within
- 测试数据管理：使用Fixture，动态生成测试数据，工厂模式

通过本章的学习，您应该能够：
- 熟练使用环境变量和配置管理不同环境的测试
- 创建和使用自定义命令扩展Cypress功能
- 使用插件系统增强测试能力
- 管理和组织测试数据
- 使用高级选择器技巧定位元素

在下一章中，我们将学习Cypress测试组织与数据管理，深入了解如何组织测试结构和管理测试数据。
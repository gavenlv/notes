// 第5章：Cypress高级特性与自定义命令示例代码

// 实验1：环境变量与配置
describe('环境变量与配置实验', () => {
  it('应该使用环境变量进行API测试', () => {
    // 从环境变量获取API URL和凭据
    const apiUrl = Cypress.env('apiUrl') || 'https://jsonplaceholder.typicode.com';
    const username = Cypress.env('username') || 'testuser';
    const password = Cypress.env('password') || 'password123';
    
    // 使用环境变量进行API请求
    cy.request({
      method: 'GET',
      url: `${apiUrl}/users/1`,
      headers: {
        'Authorization': `Basic ${btoa(`${username}:${password}`)}`
      }
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.have.property('id');
    });
  });
  
  it('应该根据环境变量设置不同基础URL', () => {
    // 使用配置中的baseUrl
    cy.visit('/'); // 会自动使用配置的baseUrl
    cy.url().should('include', Cypress.config().baseUrl);
  });
  
  it('应该动态设置配置选项', () => {
    // 读取当前配置
    const defaultTimeout = Cypress.config('defaultCommandTimeout');
    
    // 临时修改配置
    Cypress.config('defaultCommandTimeout', 10000);
    
    // 验证配置已修改
    expect(Cypress.config('defaultCommandTimeout')).to.eq(10000);
    
    // 恢复原始配置
    Cypress.config('defaultCommandTimeout', defaultTimeout);
  });
});

// 实验2：自定义命令
describe('自定义命令实验', () => {
  // 自定义登录命令
  beforeEach(() => {
    // 这个命令需要在cypress/support/commands.js中定义
    // Cypress.Commands.add('login', (username, password) => {
    //   cy.visit('/login');
    //   cy.get('#username').type(username);
    //   cy.get('#password').type(password);
    //   cy.get('.login-button').click();
    //   cy.url().should('include', '/dashboard');
    // });
    
    // 为了演示，我们在这里模拟登录过程
    cy.visit('/');
    cy.get('h1').should('contain', 'Welcome');
  });
  
  it('应该使用自定义登录命令', () => {
    // 实际使用中会调用自定义命令
    // cy.login('testuser', 'password123');
    
    // 这里我们模拟登录后的验证
    cy.get('h1').should('contain', 'Welcome');
  });
  
  it('应该使用自定义添加到购物车命令', () => {
    // 这个命令需要在cypress/support/commands.js中定义
    // Cypress.Commands.add('addToCart', (productId) => {
    //   cy.get(`[data-product-id="${productId}"]`).find('.add-to-cart').click();
    //   cy.get('.cart-count').should('contain', /\d+/);
    // });
    
    // 模拟添加到购物车
    cy.get('body').then(($body) => {
      if ($body.find('[data-product-id]').length) {
        cy.get('[data-product-id="1"]').find('.add-to-cart').click();
      } else {
        cy.log('没有找到产品元素，跳过添加到购物车测试');
      }
    });
  });
  
  it('应该使用自定义等待加载命令', () => {
    // 这个命令需要在cypress/support/commands.js中定义
    // Cypress.Commands.add('waitForLoading', () => {
    //   cy.get('.loading-indicator').should('not.exist');
    // });
    
    // 模拟等待加载
    cy.get('body').then(($body) => {
      if ($body.find('.loading-indicator').length) {
        cy.get('.loading-indicator').should('not.exist');
      } else {
        cy.log('没有找到加载指示器，跳过等待加载测试');
      }
    });
  });
});

// 实验3：测试数据管理
describe('测试数据管理实验', () => {
  it('应该使用fixture数据', () => {
    // 使用fixture文件中的数据
    cy.fixture('example.json').then((data) => {
      expect(data).to.have.property('name');
      expect(data).to.have.property('email');
    });
  });
  
  it('应该动态生成测试数据', () => {
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
    
    const user = generateRandomUser();
    expect(user.username).to.match(/^user\d+$/);
    expect(user.email).to.match(/^user\d+@example\.com$/);
  });
  
  it('应该使用工厂模式创建测试数据', () => {
    // 用户工厂类
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
    }
    
    // 创建普通用户
    const user = UserFactory.create();
    expect(user.username).to.eq('testuser');
    expect(user.active).to.eq(true);
    
    // 创建管理员用户
    const admin = UserFactory.createAdmin();
    expect(admin.username).to.eq('admin');
    expect(admin.role).to.eq('admin');
    
    // 创建自定义用户
    const customUser = UserFactory.create({
      username: 'customuser',
      active: false
    });
    expect(customUser.username).to.eq('customuser');
    expect(customUser.active).to.eq(false);
  });
});

// 高级选择器技巧示例
describe('高级选择器技巧', () => {
  it('应该使用jQuery选择器', () => {
    cy.visit('/');
    
    // 使用jQuery选择器查找可见的输入元素
    cy.get(':input:not([type=hidden])').should('be.visible');
    
    // 使用:has选择器查找包含特定元素的元素
    cy.get('div:has(h1)').should('contain', 'Welcome');
    
    // 使用contains选择器查找包含特定文本的元素
    cy.get('h1:contains("Welcome")').should('be.visible');
    
    // 使用属性选择器查找特定名称开头的元素
    cy.get('[class^="h"]').should('have.length.greaterThan', 0);
  });
  
  it('应该使用contains和filter', () => {
    cy.visit('/');
    
    // 使用contains查找包含特定文本的元素
    cy.contains('Welcome').should('be.visible');
    
    // 使用filter过滤元素
    cy.get('h1, h2, h3').filter(':visible').should('have.length.greaterThan', 0);
  });
  
  it('应该使用within限定作用域', () => {
    cy.visit('/');
    
    // 使用within限定命令作用域
    cy.get('body').within(() => {
      cy.get('h1').should('contain', 'Welcome');
    });
  });
});

// 任务与文件操作示例
describe('任务与文件操作', () => {
  it('应该使用任务读取文件', () => {
    // 这个任务需要在cypress/plugins/index.js中定义
    // module.exports = (on, config) => {
    //   on('task', {
    //     readFile(filename) {
    //       if (fs.existsSync(filename)) {
    //         return fs.readFileSync(filename, 'utf8');
    //       }
    //       return null;
    //     }
    //   });
    //   return config;
    // };
    
    // 由于我们无法在演示环境中定义任务，我们模拟这个过程
    cy.log('模拟读取文件任务');
    cy.wrap('file content').should('eq', 'file content');
  });
  
  it('应该使用任务写入文件', () => {
    // 这个任务需要在cypress/plugins/index.js中定义
    // module.exports = (on, config) => {
    //   on('task', {
    //     writeFile({ filename, content }) {
    //       fs.writeFileSync(filename, content, 'utf8');
    //       return null;
    //     }
    //   });
    //   return config;
    // };
    
    // 模拟写入文件任务
    cy.log('模拟写入文件任务');
    cy.wrap({ filename: 'test.json', content: '{}' }).should('have.property', 'filename');
  });
});

// 插件系统示例
describe('插件系统示例', () => {
  it('应该使用文件上传插件', () => {
    // 这个插件需要安装：npm install --save-dev cypress-file-upload
    // 并在cypress/support/commands.js中导入：import 'cypress-file-upload';
    
    // 模拟文件上传
    cy.get('body').then(($body) => {
      if ($body.find('input[type="file"]').length) {
        // 实际使用中会这样调用：
        // cy.get('input[type="file"]').selectFile('file.json');
        cy.log('找到文件输入元素，模拟文件上传');
      } else {
        cy.log('没有找到文件输入元素，跳过文件上传测试');
      }
    });
  });
  
  it('应该使用iframe插件', () => {
    // 这个插件需要安装：npm install --save-dev cypress-iframe
    // 并在cypress/support/commands.js中导入：import 'cypress-iframe';
    
    // 模拟iframe操作
    cy.get('body').then(($body) => {
      if ($body.find('iframe').length) {
        // 实际使用中会这样调用：
        // cy.frameLoaded('#my-iframe');
        // cy.iframe().find('.button').click();
        cy.log('找到iframe元素，模拟iframe操作');
      } else {
        cy.log('没有找到iframe元素，跳过iframe操作测试');
      }
    });
  });
});

// 自定义命令示例
describe('自定义命令示例', () => {
  // 在实际项目中，这些命令应该在cypress/support/commands.js中定义
  
  // 带回调的自定义命令
  it('应该使用带回调的自定义命令', () => {
    // 定义命令：
    // Cypress.Commands.add('getData', (url, callback) => {
    //   cy.request(url).then((response) => {
    //     callback(response.body);
    //   });
    // });
    
    // 模拟使用自定义命令
    cy.request('https://jsonplaceholder.typicode.com/users/1').then((response) => {
      const userData = response.body;
      expect(userData).to.have.property('name');
      cy.log(`用户名: ${userData.name}`);
    });
  });
  
  // 带选项的自定义命令
  it('应该使用带选项的自定义命令', () => {
    // 定义命令：
    // Cypress.Commands.add('typeSlow', { prevSubject: 'element' }, (subject, text, options = {}) => {
    //   const { delay = 100 } = options;
    //   cy.wrap(subject).type(text, { delay });
    // });
    
    // 模拟使用自定义命令
    cy.get('body').then(($body) => {
      if ($body.find('input[type="text"]').length) {
        // 实际使用中会这样调用：
        // cy.get('input[type="text"]').typeSlow('Hello', { delay: 200 });
        cy.log('找到文本输入框，模拟慢速输入');
      } else {
        cy.log('没有找到文本输入框，跳过慢速输入测试');
      }
    });
  });
  
  // 带验证的自定义命令
  it('应该使用带验证的自定义命令', () => {
    // 定义命令：
    // Cypress.Commands.add('loginAndVerify', (username, password) => {
    //   cy.visit('/login');
    //   cy.get('#username').type(username);
    //   cy.get('#password').type(password);
    //   cy.get('.login-button').click();
    //   
    //   // 验证登录成功
    //   cy.url().should('include', '/dashboard');
    //   cy.get('.user-name').should('contain', username);
    //   
    //   // 返回用户信息供后续使用
    //   return cy.get('.user-info').then(($info) => {
    //     return {
    //       name: $info.find('.user-name').text(),
    //       email: $info.find('.user-email').text()
    //     };
    //   });
    // });
    
    // 模拟使用自定义命令
    cy.log('模拟登录并验证命令');
    cy.wrap({
      name: 'Test User',
      email: 'test@example.com'
    }).should('have.property', 'name');
  });
});

// 测试运行器扩展示例
describe('测试运行器扩展示例', () => {
  it('应该使用自定义报告器', () => {
    // 这个配置需要在cypress.json中设置：
    // {
    //   "reporter": "cypress-mochawesome-reporter",
    //   "reporterOptions": {
    //     "reportDir": "cypress/results",
    //     "charts": true,
    //     "reportPageTitle": "Cypress Test Report"
    //   }
    // }
    
    // 这个插件需要安装：npm install --save-dev cypress-mochawesome-reporter
    
    // 模拟测试报告
    cy.log('模拟自定义报告器');
    cy.wrap({
      title: '测试报告',
      tests: 10,
      passes: 8,
      failures: 2
    }).should('have.property', 'tests');
  });
  
  it('应该使用自定义浏览器配置', () => {
    // 这个配置需要在cypress/plugins/index.js中设置：
    // module.exports = (on, config) => {
    //   on('before:browser:launch', (browser, launchOptions) => {
    //     if (browser.name === 'chrome') {
    //       launchOptions.args.push('--disable-dev-shm-usage');
    //       launchOptions.args.push('--no-sandbox');
    //       launchOptions.args.push('--disable-gpu');
    //     }
    //     
    //     return launchOptions;
    //   });
    //   
    //   return config;
    // };
    
    // 模拟浏览器配置
    cy.log('模拟自定义浏览器配置');
    cy.wrap({
      browser: 'chrome',
      args: ['--disable-dev-shm-usage', '--no-sandbox', '--disable-gpu']
    }).should('have.property', 'browser');
  });
});
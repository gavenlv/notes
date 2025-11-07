// 第7章：Cypress性能优化与调试示例代码

// 实验1：性能优化实践
describe('性能优化实践实验', () => {
  // 不优化的测试示例
  describe('未优化的测试', () => {
    it('未优化的测试示例', () => {
      // 使用固定等待而不是条件等待
      cy.wait(3000);
      
      // 使用复杂的选择器
      cy.get('div.container > ul:nth-child(2) > li:nth-child(3) > a').click();
      
      // 重复访问页面
      cy.visit('/dashboard');
      cy.get('.widget').should('be.visible');
      
      // 多次单独操作
      cy.get('#input1').type('value1');
      cy.get('#input2').type('value2');
      cy.get('#input3').type('value3');
      
      // 重复查找元素
      cy.get('.user-menu').click();
      cy.get('.user-menu').should('have.class', 'active');
      cy.get('.user-menu').find('.profile-link').click();
    });
  });
  
  // 优化后的测试示例
  describe('优化后的测试', () => {
    beforeEach(() => {
      // 在beforeEach中访问页面，避免重复访问
      cy.visit('/dashboard');
    });
    
    it('优化后的测试示例', () => {
      // 使用条件等待而不是固定等待
      cy.get('.loading-spinner', { timeout: 5000 }).should('not.exist');
      
      // 使用简单的选择器
      cy.get('[data-cy=submit-link]').click();
      
      // 使用别名缓存元素
      cy.get('.user-menu').as('userMenu');
      cy.get('@userMenu').click();
      cy.get('@userMenu').should('have.class', 'active');
      cy.get('@userMenu').find('.profile-link').click();
      
      // 批量操作
      cy.get('#input1, #input2, #input3').each(($el, index) => {
        cy.wrap($el).type(`value${index + 1}`);
      });
    });
  });
  
  // 性能对比测试
  describe('性能对比测试', () => {
    let unoptimizedTime;
    let optimizedTime;
    
    it('测量未优化测试的执行时间', () => {
      const startTime = Date.now();
      
      // 执行未优化的操作
      cy.wait(3000);
      cy.get('div.container > ul:nth-child(2) > li:nth-child(3) > a').click();
      cy.visit('/dashboard');
      cy.get('.widget').should('be.visible');
      cy.get('#input1').type('value1');
      cy.get('#input2').type('value2');
      cy.get('#input3').type('value3');
      cy.get('.user-menu').click();
      cy.get('.user-menu').should('have.class', 'active');
      cy.get('.user-menu').find('.profile-link').click();
      
      cy.then(() => {
        unoptimizedTime = Date.now() - startTime;
        cy.log(`未优化测试执行时间: ${unoptimizedTime}ms`);
      });
    });
    
    it('测量优化测试的执行时间', () => {
      const startTime = Date.now();
      
      // 执行优化的操作
      cy.visit('/dashboard');
      cy.get('.loading-spinner', { timeout: 5000 }).should('not.exist');
      cy.get('[data-cy=submit-link]').click();
      cy.get('.widget').should('be.visible');
      cy.get('.user-menu').as('userMenu');
      cy.get('@userMenu').click();
      cy.get('@userMenu').should('have.class', 'active');
      cy.get('@userMenu').find('.profile-link').click();
      cy.get('#input1, #input2, #input3').each(($el, index) => {
        cy.wrap($el).type(`value${index + 1}`);
      });
      
      cy.then(() => {
        optimizedTime = Date.now() - startTime;
        cy.log(`优化测试执行时间: ${optimizedTime}ms`);
        
        // 计算性能提升百分比
        const improvement = ((unoptimizedTime - optimizedTime) / unoptimizedTime * 100).toFixed(2);
        cy.log(`性能提升: ${improvement}%`);
      });
    });
  });
});

// 实验2：网络请求优化
describe('网络请求优化实验', () => {
  // 拦截和模拟网络请求
  describe('网络请求拦截与模拟', () => {
    beforeEach(() => {
      // 拦截API请求并返回模拟数据
      cy.intercept('GET', '/api/users', { fixture: 'users.json' }).as('getUsers');
      cy.intercept('GET', '/api/products', { fixture: 'products.json' }).as('getProducts');
      cy.intercept('GET', '/api/orders', { fixture: 'orders.json' }).as('getOrders');
      
      // 禁用不必要的资源加载
      cy.intercept('GET', '**/analytics.js', { statusCode: 204 }).as('analytics');
      cy.intercept('GET', '**/tracking.js', { statusCode: 204 }).as('tracking');
      cy.intercept('GET', '**/ads.js', { statusCode: 204 }).as('ads');
    });
    
    it('应该并行处理多个API请求', () => {
      cy.visit('/dashboard');
      
      // 并行等待所有请求完成
      cy.wait(['@getUsers', '@getProducts', '@getOrders']);
      
      // 验证页面已加载
      cy.get('.dashboard').should('be.visible');
      cy.get('.user-list').should('have.length.greaterThan', 0);
      cy.get('.product-list').should('have.length.greaterThan', 0);
      cy.get('.order-list').should('have.length.greaterThan', 0);
    });
    
    it('应该禁用不必要的资源加载', () => {
      cy.visit('/dashboard');
      
      // 验证不必要的资源被拦截
      cy.wait(['@analytics', '@tracking', '@ads']);
      
      // 验证页面仍然正常加载
      cy.get('.dashboard').should('be.visible');
    });
  });
  
  // 网络性能分析
  describe('网络性能分析', () => {
    let requestTimes = {};
    
    beforeEach(() => {
      // 记录请求开始时间
      cy.intercept('GET', '/api/users', (req) => {
        requestTimes.users = { start: Date.now() };
      }).as('getUsers');
      
      cy.intercept('/api/users', (res) => {
        requestTimes.users.end = Date.now();
        requestTimes.users.duration = requestTimes.users.end - requestTimes.users.start;
      });
      
      cy.intercept('GET', '/api/products', (req) => {
        requestTimes.products = { start: Date.now() };
      }).as('getProducts');
      
      cy.intercept('/api/products', (res) => {
        requestTimes.products.end = Date.now();
        requestTimes.products.duration = requestTimes.products.end - requestTimes.products.start;
      });
    });
    
    it('应该分析API响应时间', () => {
      cy.visit('/dashboard');
      cy.wait(['@getUsers', '@getProducts']);
      
      // 分析并记录API响应时间
      cy.then(() => {
        cy.log(`用户API响应时间: ${requestTimes.users.duration}ms`);
        cy.log(`产品API响应时间: ${requestTimes.products.duration}ms`);
        
        // 如果响应时间过长，记录警告
        if (requestTimes.users.duration > 1000) {
          cy.log('警告: 用户API响应时间过长!');
        }
        
        if (requestTimes.products.duration > 1000) {
          cy.log('警告: 产品API响应时间过长!');
        }
      });
    });
  });
});

// 实验3：测试数据优化
describe('测试数据优化实验', () => {
  // 使用轻量级测试数据
  describe('轻量级测试数据', () => {
    it('应该使用最小必要数据', () => {
      // 不好的做法：使用大量真实数据
      const largeDataSet = Array.from({ length: 1000 }, (_, i) => ({
        id: i,
        name: `User ${i}`,
        email: `user${i}@example.com`,
        address: `${i} Test Street`,
        city: 'Test City',
        state: 'TS',
        zipCode: i.toString().padStart(5, '0'),
        phone: `555-${i.toString().padStart(4, '0')}`,
        active: true,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }));
      
      // 好的做法：使用最小必要数据
      const minimalDataSet = [
        { id: 1, name: 'User 1', email: 'user1@example.com' },
        { id: 2, name: 'User 2', email: 'user2@example.com' }
      ];
      
      // 模拟API返回最小数据集
      cy.intercept('GET', '/api/users', { body: minimalDataSet }).as('getUsers');
      
      cy.visit('/users');
      cy.wait('@getUsers');
      
      // 验证页面只显示必要数据
      cy.get('.user-list').should('have.length', 2);
      cy.get('.user-item').eq(0).should('contain', 'User 1');
      cy.get('.user-item').eq(1).should('contain', 'User 2');
    });
  });
  
  // 重用测试数据
  describe('重用测试数据', () => {
    let testData;
    
    before(() => {
      // 创建共享测试数据
      testData = {
        users: [
          { id: 1, name: 'User 1', email: 'user1@example.com' },
          { id: 2, name: 'User 2', email: 'user2@example.com' },
          { id: 3, name: 'User 3', email: 'user3@example.com' }
        ],
        products: [
          { id: 1, name: 'Product 1', price: 10.99 },
          { id: 2, name: 'Product 2', price: 20.99 }
        ],
        orders: [
          { id: 1, userId: 1, productId: 1, quantity: 2 },
          { id: 2, userId: 2, productId: 2, quantity: 1 }
        ]
      };
    });
    
    beforeEach(() => {
      // 拦截API请求并返回共享数据
      cy.intercept('GET', '/api/users', { body: testData.users }).as('getUsers');
      cy.intercept('GET', '/api/products', { body: testData.products }).as('getProducts');
      cy.intercept('GET', '/api/orders', { body: testData.orders }).as('getOrders');
    });
    
    it('应该显示用户列表', () => {
      cy.visit('/users');
      cy.wait('@getUsers');
      
      cy.get('.user-list').should('have.length', testData.users.length);
    });
    
    it('应该显示产品列表', () => {
      cy.visit('/products');
      cy.wait('@getProducts');
      
      cy.get('.product-list').should('have.length', testData.products.length);
    });
    
    it('应该显示订单列表', () => {
      cy.visit('/orders');
      cy.wait('@getOrders');
      
      cy.get('.order-list').should('have.length', testData.orders.length);
    });
  });
});

// 实验4：调试技巧应用
describe('调试技巧应用实验', () => {
  // 使用调试命令
  describe('调试命令使用', () => {
    it('应该使用debug命令', () => {
      cy.visit('/');
      
      // 使用debug命令暂停测试并打开调试器
      cy.get('.button').debug();
      
      // 继续执行测试
      cy.get('.button').click();
      cy.get('.message').should('be.visible');
    });
    
    it('应该使用log命令', () => {
      cy.visit('/');
      
      // 使用log命令记录信息
      cy.get('.button').log('按钮元素');
      cy.get('.button').click();
      cy.get('.message').log('消息元素').should('be.visible');
    });
    
    it('应该使用pause命令', () => {
      cy.visit('/');
      
      cy.get('.button').click();
      
      // 使用pause命令暂停测试
      cy.pause();
      
      // 用户可以手动恢复测试
      cy.get('.message').should('be.visible');
    });
  });
  
  // 测试运行器调试
  describe('测试运行器调试', () => {
    // 只运行这个测试
    it.only('只运行这个测试', () => {
      cy.visit('/');
      cy.get('.button').click();
      cy.get('.message').should('be.visible');
    });
    
    // 跳过这个测试
    it.skip('跳过这个测试', () => {
      cy.visit('/');
      cy.get('.button').click();
      cy.get('.message').should('be.visible');
    });
  });
  
  // 自定义调试命令
  describe('自定义调试命令', () => {
    // 在实际项目中，这些命令应该定义在cypress/support/commands.js中
    beforeEach(() => {
      Cypress.Commands.add('debugElement', (selector) => {
        cy.get(selector).then(($el) => {
          console.log('Element:', $el);
          console.log('Text:', $el.text());
          console.log('Classes:', $el.attr('class'));
          console.log('Attributes:', $el[0].attributes);
        });
      });
      
      Cypress.Commands.add('debugNetwork', (alias) => {
        cy.get(alias).then((interception) => {
          console.log('Request URL:', interception.request.url);
          console.log('Request Method:', interception.request.method);
          console.log('Request Headers:', interception.request.headers);
          console.log('Response Status:', interception.response.statusCode);
          console.log('Response Body:', interception.response.body);
        });
      });
    });
    
    it('应该使用自定义调试命令', () => {
      cy.visit('/');
      
      // 使用自定义调试命令
      cy.debugElement('.button');
      
      // 拦截网络请求
      cy.intercept('GET', '/api/data', { fixture: 'data.json' }).as('getData');
      
      cy.get('.load-data-button').click();
      cy.wait('@getData');
      
      // 使用自定义网络调试命令
      cy.debugNetwork('@getData');
    });
  });
});

// 实验5：性能监控与分析
describe('性能监控与分析实验', () => {
  // 测试执行时间监控
  describe('测试执行时间监控', () => {
    let testTimes = [];
    
    beforeEach(() => {
      // 记录测试开始时间
      cy.then(() => {
        Cypress.currentTest.startTime = Date.now();
      });
    });
    
    afterEach(() => {
      // 记录测试结束时间并计算执行时间
      cy.then(() => {
        const duration = Date.now() - Cypress.currentTest.startTime;
        testTimes.push({
          test: Cypress.currentTest.title,
          duration: duration
        });
        
        cy.log(`测试 "${Cypress.currentTest.title}" 执行时间: ${duration}ms`);
        
        // 如果执行时间过长，记录警告
        if (duration > 5000) {
          cy.log(`警告: 测试 "${Cypress.currentTest.title}" 执行时间过长!`);
        }
      });
    });
    
    after(() => {
      // 生成测试执行时间报告
      cy.then(() => {
        const totalTime = testTimes.reduce((sum, test) => sum + test.duration, 0);
        const averageTime = totalTime / testTimes.length;
        const maxTime = Math.max(...testTimes.map(t => t.duration));
        const slowestTest = testTimes.find(t => t.duration === maxTime);
        
        cy.log(`测试执行时间报告:`);
        cy.log(`总执行时间: ${totalTime}ms`);
        cy.log(`平均执行时间: ${averageTime.toFixed(2)}ms`);
        cy.log(`最慢测试: "${slowestTest.test}" (${maxTime}ms)`);
        
        testTimes.forEach(test => {
          cy.log(`- ${test.test}: ${test.duration}ms`);
        });
      });
    });
    
    it('快速测试', () => {
      cy.visit('/');
      cy.get('.title').should('contain', 'Welcome');
    });
    
    it('中等速度测试', () => {
      cy.visit('/');
      cy.get('.load-data-button').click();
      cy.get('.data-container', { timeout: 3000 }).should('be.visible');
    });
    
    it('慢速测试', () => {
      cy.visit('/');
      cy.get('.load-heavy-data-button').click();
      cy.get('.heavy-data-container', { timeout: 5000 }).should('be.visible');
    });
  });
  
  // 内存使用监控
  describe('内存使用监控', () => {
    it('应该监控内存使用', () => {
      cy.visit('/');
      
      // 获取初始内存使用
      cy.window().then((win) => {
        if (win.performance && win.performance.memory) {
          const initialMemory = win.performance.memory.usedJSHeapSize;
          cy.log(`初始内存使用: ${(initialMemory / 1024 / 1024).toFixed(2)}MB`);
          
          // 执行一些操作
          cy.get('.load-data-button').click();
          cy.wait(1000);
          
          // 获取操作后内存使用
          cy.window().then((win) => {
            const finalMemory = win.performance.memory.usedJSHeapSize;
            const memoryIncrease = finalMemory - initialMemory;
            
            cy.log(`最终内存使用: ${(finalMemory / 1024 / 1024).toFixed(2)}MB`);
            cy.log(`内存增加: ${(memoryIncrease / 1024 / 1024).toFixed(2)}MB`);
            
            // 如果内存增加过多，记录警告
            if (memoryIncrease > 10 * 1024 * 1024) { // 10MB
              cy.log('警告: 内存使用增加过多!');
            }
          });
        } else {
          cy.log('浏览器不支持内存监控');
        }
      });
    });
  });
  
  // 性能指标收集
  describe('性能指标收集', () => {
    it('应该收集页面加载性能指标', () => {
      cy.visit('/');
      
      // 等待页面完全加载
      cy.window().then((win) => {
        return new Promise((resolve) => {
          if (win.performance && win.performance.timing) {
            const timing = win.performance.timing;
            
            // 计算各种性能指标
            const dnsLookup = timing.domainLookupEnd - timing.domainLookupStart;
            const tcpConnect = timing.connectEnd - timing.connectStart;
            const serverResponse = timing.responseEnd - timing.requestStart;
            const domLoad = timing.domContentLoadedEventEnd - timing.navigationStart;
            const pageLoad = timing.loadEventEnd - timing.navigationStart;
            
            // 记录性能指标
            cy.log(`DNS查询时间: ${dnsLookup}ms`);
            cy.log(`TCP连接时间: ${tcpConnect}ms`);
            cy.log(`服务器响应时间: ${serverResponse}ms`);
            cy.log(`DOM加载时间: ${domLoad}ms`);
            cy.log(`页面加载时间: ${pageLoad}ms`);
            
            // 如果某些指标过高，记录警告
            if (pageLoad > 3000) {
              cy.log('警告: 页面加载时间过长!');
            }
            
            if (serverResponse > 1000) {
              cy.log('警告: 服务器响应时间过长!');
            }
          } else {
            cy.log('浏览器不支持性能指标收集');
          }
          
          resolve();
        });
      });
    });
  });
});

// 实验6：测试并行化
describe('测试并行化实验', () => {
  // 测试标签和分组
  describe('测试标签和分组', () => {
    // 使用标签标记测试
    it('应该成功登录', { tags: ['@smoke', '@regression'] }, () => {
      cy.visit('/login');
      cy.get('#username').type('testuser');
      cy.get('#password').type('password123');
      cy.get('.login-button').click();
      cy.url().should('include', '/dashboard');
    });
    
    it('应该更新用户资料', { tags: ['@regression'] }, () => {
      cy.visit('/login');
      cy.get('#username').type('testuser');
      cy.get('#password').type('password123');
      cy.get('.login-button').click();
      
      cy.url().should('include', '/dashboard');
      cy.get('.profile-link').click();
      cy.get('#firstName').clear().type('Updated');
      cy.get('.save-button').click();
      cy.get('.success-message').should('contain', '资料已更新');
    });
    
    it('应该显示用户列表', { tags: ['@smoke'] }, () => {
      cy.visit('/login');
      cy.get('#username').type('testuser');
      cy.get('#password').type('password123');
      cy.get('.login-button').click();
      
      cy.url().should('include', '/dashboard');
      cy.get('.users-link').click();
      cy.get('.user-list').should('be.visible');
    });
  });
  
  // 测试文件组织
  describe('测试文件组织示例', () => {
    // 在实际项目中，这些测试应该放在不同的文件中
    // e2e/login/login_spec.js
    describe('登录模块', () => {
      it('应该成功登录', () => {
        cy.visit('/login');
        cy.get('#username').type('testuser');
        cy.get('#password').type('password123');
        cy.get('.login-button').click();
        cy.url().should('include', '/dashboard');
      });
    });
    
    // e2e/profile/profile_spec.js
    describe('用户资料模块', () => {
      beforeEach(() => {
        // 登录
        cy.visit('/login');
        cy.get('#username').type('testuser');
        cy.get('#password').type('password123');
        cy.get('.login-button').click();
        cy.url().should('include', '/dashboard');
      });
      
      it('应该查看用户资料', () => {
        cy.get('.profile-link').click();
        cy.get('.profile-page').should('be.visible');
      });
      
      it('应该更新用户资料', () => {
        cy.get('.profile-link').click();
        cy.get('#firstName').clear().type('Updated');
        cy.get('.save-button').click();
        cy.get('.success-message').should('contain', '资料已更新');
      });
    });
  });
});
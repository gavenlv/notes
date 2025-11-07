// 第3章：Cypress交互操作与命令 - 示例代码

describe('Cypress交互操作与命令示例', () => {

  // 实验1：表单交互
  describe('表单交互实验', () => {
    beforeEach(() => {
      // 假设有一个表单测试页面
      cy.visit('/form-test-page');
    });

    it('应该填写并提交表单', () => {
      // 填写文本输入框
      cy.get('#username').type('testuser');
      cy.get('#email').type('test@example.com');
      cy.get('#password').type('password123');
      
      // 选择下拉菜单
      cy.get('select#country').select('USA');
      
      // 选中复选框
      cy.get('input[type="checkbox"][name="terms"]').check();
      
      // 选择单选按钮
      cy.get('input[type="radio"][value="newsletter"]').check();
      
      // 提交表单
      cy.get('button[type="submit"]').click();
      
      // 验证提交结果
      cy.get('.success-message').should('be.visible');
      cy.url().should('include', '/success');
    });

    it('应该处理表单验证', () => {
      // 直接提交空表单
      cy.get('button[type="submit"]').click();
      
      // 验证错误消息
      cy.get('.error-message').should('be.visible');
      cy.get('#username-error').should('contain', '用户名是必填的');
      cy.get('#email-error').should('contain', '请输入有效的邮箱地址');
      
      // 填写无效数据
      cy.get('#email').type('invalid-email');
      cy.get('button[type="submit"]').click();
      cy.get('#email-error').should('contain', '请输入有效的邮箱地址');
      
      // 修正数据
      cy.get('#email').clear().type('valid@example.com');
      cy.get('#email-error').should('not.exist');
    });

    it('应该处理文件上传', () => {
      // 上传单个文件
      cy.get('input[type="file"]').selectFile('cypress/fixtures/sample.pdf');
      
      // 验证文件已选择
      cy.get('.file-name').should('contain', 'sample.pdf');
      
      // 上传多个文件
      cy.get('input[type="file"][multiple]').selectFile([
        'cypress/fixtures/file1.jpg',
        'cypress/fixtures/file2.png'
      ]);
      
      // 验证多个文件已选择
      cy.get('.selected-files').children().should('have.length', 2);
    });
  });

  // 实验2：鼠标交互
  describe('鼠标交互实验', () => {
    beforeEach(() => {
      cy.visit('/mouse-interaction-page');
    });

    it('应该执行各种点击操作', () => {
      // 基本点击
      cy.get('.button').click();
      cy.get('.click-result').should('contain', '按钮被点击');
      
      // 双击
      cy.get('.double-click-button').dblclick();
      cy.get('.double-click-result').should('contain', '双击成功');
      
      // 右键点击
      cy.get('.right-click-button').rightclick();
      cy.get('.context-menu').should('be.visible');
      
      // 按住修饰键点击
      cy.get('.shift-click-button').click({ shiftKey: true });
      cy.get('.shift-click-result').should('contain', 'Shift+点击成功');
      
      // 点击特定位置
      cy.get('.position-button').click('topLeft');
      cy.get('.position-result').should('contain', '左上角被点击');
    });

    it('应该处理悬停和拖放', () => {
      // 鼠标悬停
      cy.get('.menu-item').trigger('mouseover');
      cy.get('.submenu').should('be.visible');
      
      // 鼠标移出
      cy.get('.menu-item').trigger('mouseout');
      cy.get('.submenu').should('not.be.visible');
      
      // 拖放操作
      cy.get('#draggable').drag('#droppable');
      cy.get('#droppable').should('contain', '拖放成功');
      
      // 使用原生事件模拟拖放
      cy.get('#draggable2')
        .trigger('mousedown', { which: 1, clientX: 100, clientY: 100 })
        .trigger('mousemove', { clientX: 200, clientY: 200 })
        .trigger('mouseup', { force: true });
      
      cy.get('#droppable2').should('contain', '拖放成功');
    });

    it('应该处理滚动操作', () => {
      // 滚动到元素
      cy.get('.footer').scrollIntoView();
      cy.get('.footer').should('be.visible');
      
      // 滚动到特定位置
      cy.get('.container').scrollTo('bottom');
      cy.get('.bottom-indicator').should('be.visible');
      
      // 水平滚动
      cy.get('.horizontal-container').scrollTo('right');
      cy.get('.right-content').should('be.visible');
    });
  });

  // 实验3：键盘交互
  describe('键盘交互实验', () => {
    beforeEach(() => {
      cy.visit('/keyboard-interaction-page');
    });

    it('应该处理文本输入', () => {
      // 基本输入
      cy.get('#text-input').type('Hello World');
      cy.get('#text-input').should('have.value', 'Hello World');
      
      // 输入特殊字符
      cy.get('#text-input').type('{selectall}{del}New Text');
      cy.get('#text-input').should('have.value', 'New Text');
      
      // 模拟输入速度
      cy.get('#slow-input').type('Slow typing', { delay: 100 });
      cy.get('#slow-input').should('have.value', 'Slow typing');
      
      // 清空输入
      cy.get('#text-input').clear();
      cy.get('#text-input').should('have.value', '');
    });

    it('应该处理键盘事件', () => {
      // Enter键
      cy.get('#search-input').type('Cypress{enter}');
      cy.get('.search-results').should('be.visible');
      
      // Tab键导航
      cy.get('#input1').type('Value1{tab}');
      cy.focused().should('have.id', 'input2');
      
      // 组合键
      cy.get('#text-area').type('Some text{ctrl}a');
      cy.get('#text-area').should('have.prop', 'selectionStart', 0);
      cy.get('#text-area').should('have.prop', 'selectionEnd', 9);
      
      // 使用trigger触发键盘事件
      cy.get('#custom-input').trigger('keydown', { keyCode: 65 }); // 'a'键
      cy.get('.key-display').should('contain', 'a');
    });
  });

  // 实验4：导航操作
  describe('导航操作实验', () => {
    it('应该处理页面导航', () => {
      // 访问URL
      cy.visit('/home');
      cy.url().should('include', '/home');
      
      // 点击链接导航
      cy.get('[data-cy="about-link"]').click();
      cy.url().should('include', '/about');
      
      // 浏览器导航
      cy.go('back');
      cy.url().should('include', '/home');
      
      cy.go('forward');
      cy.url().should('include', '/about');
      
      // 刷新页面
      cy.reload();
      cy.get('.page-title').should('contain', 'About Us');
    });

    it('应该处理URL操作', () => {
      cy.visit('/search?q=cypress');
      
      // 获取当前URL
      cy.url().should('include', '/search');
      cy.url().should('include', 'q=cypress');
      
      // 获取URL的不同部分
      cy.location().should((loc) => {
        expect(loc.pathname).to.eq('/search');
        expect(loc.search).to.include('q=cypress');
      });
      
      // 获取特定URL部分
      cy.location('search').should('include', 'q=cypress');
    });
  });

  // 实验5：窗口和视口操作
  describe('窗口和视口操作实验', () => {
    it('应该处理视口大小变化', () => {
      // 设置视口大小
      cy.viewport(1280, 720);
      cy.get('.desktop-menu').should('be.visible');
      cy.get('.mobile-menu').should('not.be.visible');
      
      // 切换到移动视口
      cy.viewport('iphone-x');
      cy.get('.desktop-menu').should('not.be.visible');
      cy.get('.mobile-menu').should('be.visible');
      
      // 验证视口大小
      cy.window().its('innerWidth').should('be.lessThan', 500);
    });

    it('应该访问窗口对象', () => {
      cy.visit('/window-test');
      
      // 获取窗口对象
      cy.window().then((win) => {
        // 访问窗口属性
        expect(win.innerWidth).to.be.a('number');
        
        // 调用窗口方法
        win.scrollTo(0, 500);
      });
      
      // 获取文档对象
      cy.document().then((doc) => {
        expect(doc.title).to.be.a('string');
      });
      
      // 获取元素对象
      cy.get('.element').then(($el) => {
        // 访问jQuery对象
        $el.css('color', 'red');
      });
    });
  });

  // 实验6：网络请求控制
  describe('网络请求控制实验', () => {
    beforeEach(() => {
      cy.visit('/api-test-page');
    });

    it('应该拦截并模拟API响应', () => {
      // 拦截GET请求
      cy.intercept('GET', '/api/users', { fixture: 'users.json' }).as('getUsers');
      
      cy.get('.load-users').click();
      cy.wait('@getUsers');
      
      // 验证数据已加载
      cy.get('.user-list').should('contain', 'John Doe');
      cy.get('.user-list').should('contain', 'Jane Smith');
    });

    it('应该拦截POST请求', () => {
      // 拦截POST请求
      cy.intercept('POST', '/api/login', (req) => {
        expect(req.body).to.include('username');
        expect(req.body).to.include('password');
        
        req.reply({
          statusCode: 200,
          body: { token: 'fake-jwt-token', user: { id: 1, name: 'Test User' } }
        });
      }).as('loginRequest');
      
      // 填写登录表单
      cy.get('#username').type('testuser');
      cy.get('#password').type('password123');
      cy.get('.login-button').click();
      
      // 等待请求并验证响应
      cy.wait('@loginRequest').then((interception) => {
        expect(interception.response.statusCode).to.eq(200);
        expect(interception.response.body.token).to.exist;
      });
      
      // 验证登录成功
      cy.get('.user-info').should('contain', 'Test User');
    });

    it('应该模拟网络错误', () => {
      // 模拟网络错误
      cy.intercept('GET', '/api/error', { statusCode: 500 }).as('errorRequest');
      
      cy.get('.trigger-error').click();
      cy.wait('@errorRequest');
      
      // 验证错误处理
      cy.get('.error-message').should('contain', '服务器错误');
    });

    it('应该模拟慢速网络', () => {
      // 模拟慢速网络
      cy.intercept('GET', '/api/slow', { delay: 2000 }).as('slowRequest');
      
      cy.get('.load-slow-data').click();
      
      // 验证加载状态
      cy.get('.loading-indicator').should('be.visible');
      
      // 等待请求完成
      cy.wait('@slowRequest');
      
      // 验证加载完成
      cy.get('.loading-indicator').should('not.exist');
      cy.get('.data-content').should('be.visible');
    });
  });

  // 实验7：自定义命令
  describe('自定义命令实验', () => {
    // 假设已在cypress/support/commands.js中定义了以下自定义命令：
    // Cypress.Commands.add('login', (username, password) => { ... });
    // Cypress.Commands.add('addToCart', (productId) => { ... });
    // Cypress.Commands.add('waitForLoading', () => { ... });

    it('应该使用自定义登录命令', () => {
      // 使用自定义登录命令
      cy.login('testuser', 'password123');
      
      // 验证登录成功
      cy.url().should('include', '/dashboard');
      cy.get('.user-name').should('contain', 'testuser');
    });

    it('应该使用自定义添加到购物车命令', () => {
      cy.visit('/products');
      
      // 使用自定义添加到购物车命令
      cy.addToCart('product-123');
      
      // 验证商品已添加
      cy.get('.cart-count').should('contain', '1');
      cy.get('.cart-item').should('contain', 'Product 123');
    });

    it('应该使用自定义等待加载命令', () => {
      cy.visit('/slow-page');
      
      // 使用自定义等待加载命令
      cy.waitForLoading();
      
      // 验证页面已加载完成
      cy.get('.content').should('be.visible');
    });
  });

  // 额外示例：复杂交互场景
  describe('复杂交互场景', () => {
    it('应该完成完整的购物流程', () => {
      // 访问首页
      cy.visit('/');
      
      // 搜索商品
      cy.get('.search-input').type('Laptop{enter}');
      
      // 等待搜索结果
      cy.intercept('GET', '/api/search?q=Laptop').as('search');
      cy.wait('@search');
      
      // 选择第一个商品
      cy.get('.product-item').first().click();
      
      // 添加到购物车
      cy.get('.add-to-cart').click();
      
      // 查看购物车
      cy.get('.cart-icon').click();
      
      // 验证商品在购物车中
      cy.get('.cart-item').should('have.length', 1);
      
      // 结账
      cy.get('.checkout-button').click();
      
      // 填写结账信息
      cy.get('#first-name').type('John');
      cy.get('#last-name').type('Doe');
      cy.get('#email').type('john.doe@example.com');
      cy.get('#address').type('123 Main St');
      cy.get('#city').type('New York');
      cy.get('#zip').type('10001');
      
      // 提交订单
      cy.get('.place-order').click();
      
      // 验证订单成功
      cy.get('.order-confirmation').should('contain', 'Order Placed Successfully');
    });

    it('应该处理动态内容加载', () => {
      cy.visit('/dynamic-content');
      
      // 点击加载更多按钮
      cy.get('.load-more').click();
      
      // 等待新内容加载
      cy.intercept('GET', '/api/more-content').as('moreContent');
      cy.wait('@moreContent');
      
      // 验证新内容已加载
      cy.get('.content-item').should('have.length.greaterThan', 10);
      
      // 滚动到页面底部
      cy.scrollTo('bottom');
      
      // 验证自动加载更多内容
      cy.intercept('GET', '/api/infinite-scroll').as('infiniteScroll');
      cy.wait('@infiniteScroll');
      
      // 验证更多内容已加载
      cy.get('.content-item').should('have.length.greaterThan', 20);
    });
  });
});
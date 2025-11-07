// 第4章：Cypress断言与验证 - 示例代码

describe('Cypress断言与验证示例', () => {

  // 实验1：基本断言
  describe('基本断言实验', () => {
    beforeEach(() => {
      // 假设有一个断言测试页面
      cy.visit('/assertion-test-page');
    });

    it('应该验证元素可见性', () => {
      // 元素可见性断言
      cy.get('.visible-element').should('be.visible');
      cy.get('.hidden-element').should('not.be.visible');
      cy.get('.non-existent-element').should('not.exist');
      cy.get('.element').should('exist');
      
      // 元素显示状态
      cy.get('.hidden-element').should('be.hidden');
      cy.get('.visible-element').should('not.be.hidden');
    });

    it('应该验证元素状态', () => {
      // 元素启用/禁用状态
      cy.get('#enabled-input').should('be.enabled');
      cy.get('#disabled-input').should('be.disabled');
      
      // 元素选中状态
      cy.get('#checked-checkbox').should('be.checked');
      cy.get('#unchecked-checkbox').should('not.be.checked');
      cy.get('#selected-radio').should('be.checked');
      
      // 元素焦点状态
      cy.get('#focused-input').should('be.focused');
      cy.get('#unfocused-input').should('not.be.focused');
    });

    it('应该验证元素属性', () => {
      // 类名断言
      cy.get('.element').should('have.class', 'active');
      cy.get('.element').should('not.have.class', 'inactive');
      cy.get('.elements').should('have.length', 3);
      
      // ID断言
      cy.get('#my-id').should('have.id', 'my-id');
      
      // 属性值断言
      cy.get('input[type="text"]').should('have.attr', 'type', 'text');
      cy.get('input[type="text"]').should('have.prop', 'disabled', false);
      
      // CSS属性断言
      cy.get('.red-text').should('have.css', 'color', 'rgb(255, 0, 0)');
      cy.get('.large-text').should('have.css', 'font-size', '20px');
    });

    it('应该验证文本内容', () => {
      // 文本内容
      cy.get('.title').should('have.text', 'Page Title');
      cy.get('.description').should('contain', 'This is a description');
      cy.get('.description').should('not.contain', 'Absent Text');
      
      // HTML内容
      cy.get('.html-content').should('have.html', '<span>Content</span>');
      cy.get('.html-content').should('include.html', '<span>');
      
      // 值断言
      cy.get('#input-field').should('have.value', 'Default Value');
      cy.get('#select-field').should('have.value', 'option1');
    });

    it('应该验证数值', () => {
      // 数值比较
      cy.get('.count').should('have.text', '5');
      
      cy.get('.price').invoke('text').then(parseFloat).should('be.gt', 10);
      cy.get('.price').invoke('text').then(parseFloat).should('be.gte', 10);
      cy.get('.price').invoke('text').then(parseFloat).should('be.lt', 20);
      cy.get('.price').invoke('text').then(parseFloat).should('be.lte', 20);
      
      // 数值范围
      cy.get('.temperature').invoke('text').then(parseFloat).should('be.within', 10, 30);
    });
  });

  // 实验2：链式断言
  describe('链式断言实验', () => {
    beforeEach(() => {
      cy.visit('/chain-assertion-test-page');
    });

    it('应该使用链式断言验证用户卡片', () => {
      cy.get('.user-card')
        .should('be.visible')
        .and('have.class', 'active')
        .and('contain', 'John Doe')
        .and('have.attr', 'data-user-id', '123');
    });

    it('应该使用链式断言验证产品列表', () => {
      cy.get('.product-list')
        .should('have.length', 5)
        .and('have.class', 'grid')
        .each(($product, index) => {
          cy.wrap($product)
            .find('.product-name')
            .should('not.be.empty')
            .and('match', /^Product \d+$/);
        });
    });

    it('应该使用回调函数进行复杂断言', () => {
      cy.get('.users').should(($users) => {
        expect($users).to.have.length(3);
        expect($users.eq(0)).to.contain('John');
        expect($users.eq(1)).to.contain('Jane');
        expect($users.eq(2)).to.contain('Bob');
      });
    });

    it('应该使用then获取元素进行断言', () => {
      cy.get('.data').then(($data) => {
        const text = $data.text();
        expect(text).to.match(/^[A-Z]/);  // 以大写字母开头
        expect(text.length).to.be.greaterThan(10);
      });
    });
  });

  // 实验3：自定义断言
  describe('自定义断言实验', () => {
    beforeEach(() => {
      cy.visit('/custom-assertion-test-page');
    });

    // 自定义断言：验证邮箱格式
    const assertValidEmail = (email) => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      expect(email).to.match(emailRegex);
    };

    // 自定义断言：验证电话号码格式
    const assertValidPhoneNumber = (phone) => {
      const phoneRegex = /^\d{3}-\d{3}-\d{4}$/;
      expect(phone).to.match(phoneRegex);
    };

    // 自定义断言：验证URL格式
    const assertValidUrl = (url) => {
      try {
        new URL(url);
        return true;
      } catch (e) {
        return false;
      }
    };

    it('应该使用自定义断言验证表单数据', () => {
      cy.get('#email').invoke('val').then((email) => {
        assertValidEmail(email);
      });

      cy.get('#phone').invoke('val').then((phone) => {
        assertValidPhoneNumber(phone);
      });

      cy.get('#website').invoke('val').then((url) => {
        expect(assertValidUrl(url)).to.be.true;
      });
    });

    it('应该使用自定义断言验证API响应', () => {
      cy.request('/api/user').then((response) => {
        expect(response.status).to.eq(200);
        
        const user = response.body;
        assertValidEmail(user.email);
        assertValidPhoneNumber(user.phone);
        expect(assertValidUrl(user.website)).to.be.true;
      });
    });

    it('应该使用expect进行复杂断言', () => {
      cy.get('.user-data').then(($userData) => {
        const userData = JSON.parse($userData.text());
        
        expect(userData).to.have.property('name');
        expect(userData.name).to.be.a('string');
        expect(userData.age).to.be.a('number').and.to.be.above(0);
        assertValidEmail(userData.email);
      });
    });
  });

  // 实验4：重试机制
  describe('重试机制实验', () => {
    it('应该自动重试直到元素可见', () => {
      cy.visit('/slow-loading-page');
      
      // Cypress会自动重试直到元素可见
      cy.get('.slow-element', { timeout: 5000 }).should('be.visible');
    });

    it('应该自动重试直到文本出现', () => {
      cy.visit('/dynamic-content-page');
      
      // 点击按钮触发内容加载
      cy.get('.load-content').click();
      
      // Cypress会自动重试直到文本出现
      cy.get('.message').should('contain', 'Success');
    });

    it('应该自动重试直到属性值改变', () => {
      cy.visit('/state-change-page');
      
      // 点击按钮改变输入框值
      cy.get('.change-value').click();
      
      // Cypress会自动重试直到属性值改变
      cy.get('input').should('have.value', 'New Value');
    });

    it('应该配置自定义超时时间', () => {
      cy.visit('/very-slow-page');
      
      // 为特定命令设置超时
      cy.get('.very-slow-element', { timeout: 10000 }).should('be.visible');
      
      // 为特定断言设置超时
      cy.get('.element').should('be.visible', { timeout: 8000 });
    });
  });

  // 实验5：等待策略
  describe('等待策略实验', () => {
    it('应该使用显式等待', () => {
      cy.visit('/wait-test-page');
      
      // 等待特定时间
      cy.wait(1000);  // 等待1秒
      
      // 等待别名请求
      cy.intercept('GET', '/api/users').as('getUsers');
      cy.get('.load-users').click();
      cy.wait('@getUsers');  // 等待请求完成
      
      // 验证请求结果
      cy.get('.user-list').should('be.visible');
    });

    it('应该使用隐式等待', () => {
      cy.visit('/implicit-wait-page');
      
      // Cypress自动等待元素出现
      cy.get('.element').should('be.visible');  // 自动等待元素可见
      
      // Cypress自动等待请求完成
      cy.get('.submit').click();  // 自动等待页面加载完成
      cy.get('.success-message').should('be.visible');
    });

    it('应该使用条件等待', () => {
      cy.visit('/conditional-wait-page');
      
      // 使用should进行条件等待
      cy.get('.element').should(($el) => {
        expect($el.text()).to.match(/Success|Error/);
      });
      
      // 使用until插件（需要安装）
      cy.get('.element').should('not.contain', 'Loading');
      cy.get('.element').should('contain', 'Complete');
    });
  });

  // 实验6：条件断言
  describe('条件断言实验', () => {
    it('应该使用条件语句进行断言', () => {
      cy.visit('/conditional-assertion-page');
      
      // 使用if语句进行条件断言
      cy.get('.element').then(($el) => {
        if ($el.length > 0) {
          cy.get('.element').should('be.visible');
        } else {
          cy.get('.alternative-element').should('be.visible');
        }
      });
      
      // 使用jQuery的is方法
      cy.get('.element').then(($el) => {
        if ($el.is(':visible')) {
          cy.get('.element').should('have.class', 'active');
        }
      });
    });

    it('应该使用可选链处理可能不存在的元素', () => {
      cy.visit('/optional-chain-page');
      
      // 使用可选链处理可能不存在的元素
      cy.get('.optional-element').then(($el) => {
        if ($el.length) {
          cy.get('.optional-element').should('contain', 'Expected Text');
        }
      });
      
      // 使用jQuery的find方法
      cy.get('.container').then(($container) => {
        const $optionalElement = $container.find('.optional-element');
        if ($optionalElement.length) {
          cy.wrap($optionalElement).should('be.visible');
        }
      });
    });

    it('应该使用Cypress条件命令', () => {
      cy.visit('/cypress-conditional-page');
      
      // 使用its命令进行条件断言
      cy.get('.element').its('length').then((length) => {
        if (length > 0) {
          cy.get('.element').first().should('be.visible');
        }
      });
      
      // 使用invoke命令进行条件断言
      cy.get('.element').invoke('is', ':visible').then((isVisible) => {
        if (isVisible) {
          cy.get('.element').should('have.class', 'active');
        }
      });
    });
  });

  // 额外示例：复杂断言场景
  describe('复杂断言场景', () => {
    it('应该验证复杂表单提交', () => {
      cy.visit('/complex-form');
      
      // 填写表单
      cy.get('#name').type('John Doe');
      cy.get('#email').type('john.doe@example.com');
      cy.get('#phone').type('123-456-7890');
      cy.get('#password').type('Password123');
      cy.get('#confirm-password').type('Password123');
      
      // 同意条款
      cy.get('#terms').check();
      
      // 提交表单
      cy.get('.submit').click();
      
      // 验证成功消息
      cy.get('.success-message').should('be.visible').and('contain', 'Form submitted successfully');
      
      // 验证重定向
      cy.url().should('include', '/success');
      
      // 验证用户信息显示
      cy.get('.user-name').should('contain', 'John Doe');
      cy.get('.user-email').should('contain', 'john.doe@example.com');
    });

    it('应该验证动态加载的内容', () => {
      cy.visit('/dynamic-content');
      
      // 点击加载更多按钮
      cy.get('.load-more').click();
      
      // 等待新内容加载
      cy.intercept('GET', '/api/more-content').as('moreContent');
      cy.wait('@moreContent');
      
      // 验证新内容已加载
      cy.get('.content-item').should('have.length.greaterThan', 10);
      
      // 验证每个内容项的结构
      cy.get('.content-item').each(($item) => {
        cy.wrap($item)
          .find('.title')
          .should('not.be.empty');
        cy.wrap($item)
          .find('.description')
          .should('not.be.empty');
        cy.wrap($item)
          .find('.date')
          .should('not.be.empty');
      });
    });

    it('应该验证API响应数据', () => {
      cy.intercept('GET', '/api/products').as('getProducts');
      cy.visit('/products-page');
      cy.wait('@getProducts');
      
      // 验证API响应
      cy.get('@getProducts').then((interception) => {
        expect(interception.response.statusCode).to.eq(200);
        expect(interception.response.body).to.be.an('array');
        expect(interception.response.body).to.have.length.greaterThan(0);
        
        // 验证每个产品对象的结构
        interception.response.body.forEach((product) => {
          expect(product).to.have.property('id');
          expect(product).to.have.property('name');
          expect(product).to.have.property('price');
          expect(product).to.have.property('description');
          
          expect(product.name).to.be.a('string').and.not.be.empty;
          expect(product.price).to.be.a('number').and.be.above(0);
          expect(product.description).to.be.a('string').and.not.be.empty;
        });
      });
      
      // 验证页面上的产品显示
      cy.get('.product').should('have.length.greaterThan', 0);
      cy.get('.product').each(($product) => {
        cy.wrap($product)
          .find('.product-name')
          .should('not.be.empty');
        cy.wrap($product)
          .find('.product-price')
          .should('match', /\$\d+\.\d{2}/);
      });
    });
  });
});
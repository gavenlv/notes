# 第4章：Cypress断言与验证

## 目录
- [4.1 断言基础](#41-断言基础)
- [4.2 内置断言](#42-内置断言)
- [4.3 断言链](#43-断言链)
- [4.4 自定义断言](#44-自定义断言)
- [4.5 重试机制](#45-重试机制)
- [4.6 等待策略](#46-等待策略)
- [4.7 条件断言](#47-条件断言)
- [4.8 实验与实践](#48-实验与实践)

## 4.1 断言基础

### 什么是断言

断言是测试中用于验证实际结果是否符合预期结果的关键机制。在Cypress中，断言用于检查应用程序的状态、行为和属性是否符合预期。

```javascript
// 基本断言语法
cy.get('.element').should('have.text', 'Expected Text');
cy.get('.element').should('have.class', 'active');
cy.get('.element').should('be.visible');
```

### 断言的重要性

断言在测试中起到以下关键作用：

1. **验证预期行为**：确保应用程序按预期工作
2. **提供反馈**：当测试失败时，提供明确的错误信息
3. **文档化行为**：作为应用程序行为的文档
4. **回归检测**：在代码变更后检测是否引入了问题

### 断言库

Cypress内置了以下断言库：

1. **Chai**：提供BDD（行为驱动开发）和TDD（测试驱动开发）风格的断言
2. **Chai-jQuery**：扩展Chai以支持jQuery断言
3. **Sinon-Chai**：扩展Chai以支持Sinon间谍和存根断言

## 4.2 内置断言

### 元素可见性断言

```javascript
// 元素可见性
cy.get('.visible-element').should('be.visible');      // 元素可见
cy.get('.hidden-element').should('not.be.visible');  // 元素不可见
cy.get('.element').should('exist');                 // 元素存在于DOM中
cy.get('.element').should('not.exist');              // 元素不存在于DOM中

// 元素显示状态
cy.get('.element').should('be.hidden');              // 元素隐藏
cy.get('.element').should('not.be.hidden');          // 元素不隐藏
```

### 元素状态断言

```javascript
// 元素启用/禁用状态
cy.get('input').should('be.enabled');               // 元素启用
cy.get('input').should('be.disabled');              // 元素禁用

// 元素选中状态
cy.get('input[type="checkbox"]').should('be.checked');     // 复选框选中
cy.get('input[type="checkbox"]').should('not.be.checked'); // 复选框未选中
cy.get('input[type="radio"]').should('be.checked');        // 单选按钮选中

// 元素焦点状态
cy.get('input').should('be.focused');               // 元素获得焦点
cy.get('input').should('not.be.focused');           // 元素未获得焦点
```

### 元素属性断言

```javascript
// 类名断言
cy.get('.element').should('have.class', 'active');          // 包含指定类
cy.get('.element').should('not.have.class', 'inactive');    // 不包含指定类
cy.get('.element').should('have.length', 3);               // 元素数量

// ID断言
cy.get('.element').should('have.id', 'my-id');              // 具有指定ID

// 属性值断言
cy.get('input').should('have.attr', 'type', 'text');        // 属性值
cy.get('input').should('have.prop', 'disabled', false);     // 属性值

// CSS属性断言
cy.get('.element').should('have.css', 'color', 'rgb(255, 0, 0)');
cy.get('.element').should('have.css', 'font-size', '16px');
```

### 文本内容断言

```javascript
// 文本内容
cy.get('.element').should('have.text', 'Expected Text');    // 完全匹配
cy.get('.element').should('contain', 'Partial Text');       // 包含文本
cy.get('.element').should('not.contain', 'Absent Text');    // 不包含文本

// HTML内容
cy.get('.element').should('have.html', '<span>Content</span>');
cy.get('.element').should('include.html', '<span>');

// 值断言
cy.get('input').should('have.value', 'Expected Value');     // 输入框值
cy.get('select').should('have.value', 'option1');           // 下拉框选中值
```

### 数值断言

```javascript
// 数值比较
cy.get('.count').should('have.text', '5');                 // 文本转数值
cy.get('.element').invoke('text').then(parseFloat).should('be.gt', 10);  // 大于
cy.get('.element').invoke('text').then(parseFloat).should('be.gte', 10); // 大于等于
cy.get('.element').invoke('text').then(parseFloat).should('be.lt', 20);  // 小于
cy.get('.element').invoke('text').then(parseFloat).should('be.lte', 20); // 小于等于

// 数值范围
cy.get('.element').invoke('text').then(parseFloat).should('be.within', 10, 20);
```

## 4.3 断言链

### 链式断言

Cypress支持链式断言，可以在一个命令中添加多个断言：

```javascript
// 链式断言
cy.get('.user-card')
  .should('be.visible')
  .and('have.class', 'active')
  .and('contain', 'John Doe')
  .and('have.attr', 'data-id', '123');

// 使用and替代should
cy.get('.user-card')
  .should('be.visible')
  .and('have.class', 'active')
  .and('contain', 'John Doe');
```

### 多个元素断言

```javascript
// 多个元素断言
cy.get('.list-item')
  .should('have.length', 5)
  .and('have.class', 'item')
  .each(($el, index) => {
    expect($el).to.contain.text(`Item ${index + 1}`);
  });

// 使用each遍历元素
cy.get('.product')
  .each(($product) => {
    cy.wrap($product)
      .find('.price')
      .should('not.be.empty')
      .and('match', /\$\d+\.\d{2}/);
  });
```

### 回调函数断言

```javascript
// 使用回调函数进行复杂断言
cy.get('.users').should(($users) => {
  expect($users).to.have.length(3);
  expect($users.eq(0)).to.contain('John');
  expect($users.eq(1)).to.contain('Jane');
  expect($users.eq(2)).to.contain('Bob');
});

// 使用then获取元素进行断言
cy.get('.data').then(($data) => {
  const text = $data.text();
  expect(text).to.match(/^[A-Z]/);  // 以大写字母开头
  expect(text.length).to.be.greaterThan(10);
});
```

## 4.4 自定义断言

### 使用Chai自定义断言

```javascript
// 在cypress/support/commands.js中添加自定义断言
chai.use((_chai, utils) => {
  function assertIsEmail(str) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const isEmail = emailRegex.test(str);
    
    if (!isEmail) {
      throw new chai.AssertionError(
        `expected ${str} to be a valid email address`,
        null,
        assertIsEmail
      );
    }
  }
  
  _chai.Assertion.addMethod('email', function() {
    const obj = utils.flag(this, 'object');
    new _chai.Assertion(obj).to.be.a('string');
    assertIsEmail(obj);
  });
});

// 使用自定义断言
cy.get('#email').should('have.value').and('be.email');
```

### 使用Cypress自定义命令

```javascript
// 在cypress/support/commands.js中添加自定义命令
Cypress.Commands.add('shouldBeValidEmail', { prevSubject: true }, (subject) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  expect(subject).to.match(emailRegex);
});

// 使用自定义命令
cy.get('#email').invoke('val').shouldBeValidEmail();
```

### 使用expect进行自定义断言

```javascript
// 使用expect进行复杂断言
cy.get('.user-data').then(($userData) => {
  const userData = JSON.parse($userData.text());
  
  expect(userData).to.have.property('name');
  expect(userData.name).to.be.a('string');
  expect(userData.age).to.be.a('number').and.to.be.above(0);
  expect(userData.email).to.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/);
});

// 使用expect进行异步断言
cy.request('/api/users').then((response) => {
  expect(response.status).to.eq(200);
  expect(response.body).to.be.an('array');
  expect(response.body).to.have.length.greaterThan(0);
});
```

## 4.5 重试机制

### 自动重试

Cypress具有内置的自动重试机制，当断言失败时会自动重试，直到超时或成功：

```javascript
// Cypress会自动重试直到元素可见
cy.get('.loading-indicator').should('not.be.visible');

// Cypress会自动重试直到文本出现
cy.get('.message').should('contain', 'Success');

// Cypress会自动重试直到属性值改变
cy.get('input').should('have.value', 'New Value');
```

### 重试配置

```javascript
// 在cypress.json中配置默认超时时间
{
  "defaultCommandTimeout": 5000,
  "requestTimeout": 5000,
  "responseTimeout": 30000
}

// 在测试中覆盖默认超时时间
cy.get('.slow-element', { timeout: 10000 }).should('be.visible');

// 为特定断言设置超时
cy.get('.element').should('be.visible', { timeout: 8000 });
```

### 重试限制

```javascript
// 使用should不会重试
cy.get('.element').then(($el) => {
  expect($el).to.be.visible;  // 不会重试
});

// 使用should会重试
cy.get('.element').should('be.visible');  // 会重试
```

## 4.6 等待策略

### 显式等待

```javascript
// 等待特定时间
cy.wait(1000);  // 等待1秒

// 等待别名请求
cy.intercept('GET', '/api/users').as('getUsers');
cy.get('.load-users').click();
cy.wait('@getUsers');  // 等待请求完成

// 等待多个请求
cy.wait(['@getUsers', '@getProducts']);
```

### 隐式等待

```javascript
// Cypress自动等待元素出现
cy.get('.element').should('be.visible');  // 自动等待元素可见

// Cypress自动等待请求完成
cy.get('.submit').click();  // 自动等待页面加载完成
cy.get('.success-message').should('be.visible');
```

### 条件等待

```javascript
// 使用should进行条件等待
cy.get('.element').should(($el) => {
  expect($el.text()).to.match(/Success|Error/);
});

// 使用until插件（需要安装）
cy.get('.element').should('not.contain', 'Loading');
cy.get('.element').should('contain', 'Complete');
```

## 4.7 条件断言

### 使用条件语句

```javascript
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
```

### 使用可选链

```javascript
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
```

### 使用Cypress条件命令

```javascript
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
```

## 4.8 实验与实践

### 实验1：基本断言

**目标**：练习使用各种基本断言验证页面元素

**步骤**：
1. 创建一个包含各种元素的测试页面
2. 使用不同的断言验证这些元素
3. 观察断言失败时的错误信息

**示例代码**：
```javascript
describe('基本断言实验', () => {
  beforeEach(() => {
    cy.visit('/assertion-test-page');
  });

  it('应该验证元素可见性', () => {
    cy.get('.visible-element').should('be.visible');
    cy.get('.hidden-element').should('not.be.visible');
    cy.get('.non-existent-element').should('not.exist');
  });

  it('应该验证元素状态', () => {
    cy.get('#enabled-input').should('be.enabled');
    cy.get('#disabled-input').should('be.disabled');
    cy.get('#checked-checkbox').should('be.checked');
    cy.get('#unchecked-checkbox').should('not.be.checked');
  });

  it('应该验证元素属性', () => {
    cy.get('.element').should('have.class', 'active');
    cy.get('.element').should('have.attr', 'data-id', '123');
    cy.get('.element').should('have.css', 'color', 'rgb(255, 0, 0)');
  });

  it('应该验证文本内容', () => {
    cy.get('.title').should('have.text', 'Page Title');
    cy.get('.description').should('contain', 'This is a description');
    cy.get('#input-field').should('have.value', 'Default Value');
  });
});
```

### 实验2：链式断言

**目标**：练习使用链式断言提高测试可读性

**步骤**：
1. 创建一个包含复杂元素的测试页面
2. 使用链式断言验证多个属性
3. 比较链式断言与分离断言的差异

**示例代码**：
```javascript
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
});
```

### 实验3：自定义断言

**目标**：练习创建和使用自定义断言

**步骤**：
1. 创建自定义断言函数
2. 在测试中使用自定义断言
3. 比较自定义断言与内置断言的差异

**示例代码**：
```javascript
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

  it('应该使用自定义断言验证表单数据', () => {
    cy.get('#email').invoke('val').then((email) => {
      assertValidEmail(email);
    });

    cy.get('#phone').invoke('val').then((phone) => {
      assertValidPhoneNumber(phone);
    });
  });

  it('应该使用自定义断言验证API响应', () => {
    cy.request('/api/user').then((response) => {
      expect(response.status).to.eq(200);
      
      const user = response.body;
      assertValidEmail(user.email);
      assertValidPhoneNumber(user.phone);
    });
  });
});
```

## 本章小结

本章介绍了Cypress的断言与验证机制，包括：

- 断言基础：什么是断言、断言的重要性和断言库
- 内置断言：元素可见性、状态、属性、文本内容和数值断言
- 断言链：链式断言、多个元素断言和回调函数断言
- 自定义断言：使用Chai、Cypress自定义命令和expect
- 重试机制：自动重试、重试配置和重试限制
- 等待策略：显式等待、隐式等待和条件等待
- 条件断言：使用条件语句、可选链和Cypress条件命令

通过本章的学习，您应该能够：
- 熟练使用各种内置断言验证应用程序状态
- 使用链式断言提高测试可读性
- 创建和使用自定义断言
- 理解Cypress的重试机制和等待策略
- 使用条件断言处理复杂场景

在下一章中，我们将学习Cypress的高级特性与自定义命令，深入了解如何扩展Cypress的功能。
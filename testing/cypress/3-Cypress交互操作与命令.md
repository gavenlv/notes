# 第3章：Cypress交互操作与命令

## 目录
- [3.1 鼠标交互操作](#31-鼠标交互操作)
- [3.2 键盘交互操作](#32-键盘交互操作)
- [3.3 表单操作](#33-表单操作)
- [3.4 导航操作](#34-导航操作)
- [3.5 窗口和视口操作](#35-窗口和视口操作)
- [3.6 网络请求控制](#36-网络请求控制)
- [3.7 自定义命令](#37-自定义命令)
- [3.8 实验与实践](#38-实验与实践)

## 3.1 鼠标交互操作

### 点击操作

Cypress提供了多种点击相关的方法：

```javascript
// 基本点击
cy.get('button').click();

// 点击特定位置
cy.get('button').click('topLeft');
cy.get('button').click('bottomRight');

// 按住修饰键点击
cy.get('button').click({ altKey: true });
cy.get('button').click({ ctrlKey: true });
cy.get('button').click({ metaKey: true });
cy.get('button').click({ shiftKey: true });

// 多次点击
cy.get('button').dblclick();  // 双击
cy.get('button').click({ multiple: true });  // 多个元素
cy.get('button').click({ force: true });  // 强制点击（即使不可见）
```

### 悬停操作

```javascript
// 鼠标悬停
cy.get('.menu-item').trigger('mouseover');

// 使用realHover插件（需要安装）
cy.get('.menu-item').realHover();

// 模拟鼠标移动
cy.get('.canvas').trigger('mousemove', 100, 100);
```

### 拖放操作

```javascript
// 拖放元素
cy.get('#draggable').drag('#droppable');

// 使用原生事件模拟拖放
cy.get('#draggable')
  .trigger('mousedown', { which: 1 })
  .trigger('mousemove', { clientX: 100, clientY: 100 })
  .trigger('mouseup', { force: true });
```

### 右键操作

```javascript
// 右键点击
cy.get('.context-menu-target').rightclick();

// 触发上下文菜单事件
cy.get('.context-menu-target').trigger('contextmenu');
```

### 滚动操作

```javascript
// 滚动到元素
cy.get('.footer').scrollIntoView();

// 滚动到特定位置
cy.get('.container').scrollTo('bottom');
cy.get('.container').scrollTo('center');
cy.get('.container').scrollTo(0, 500);  // 滚动到x=0, y=500

// 水平滚动
cy.get('.horizontal-container').scrollTo('right');
```

## 3.2 键盘交互操作

### 文本输入

```javascript
// 基本输入
cy.get('input[type="text"]').type('Hello World');

// 输入特殊字符
cy.get('input[type="text"]').type('Hello{enter}World');
cy.get('input[type="text"]').type('Hello{shift}World');  // 按住Shift键

// 输入延迟（模拟真实输入速度）
cy.get('input[type="text"]').type('Hello World', { delay: 100 });

// 清空并输入
cy.get('input[type="text"]').clear().type('New Text');

// 追加文本
cy.get('input[type="text"]').type('{selectall}{del}New Text');
```

### 键盘事件

```javascript
// 触发键盘事件
cy.get('input').type('{enter}');
cy.get('input').type('{esc}');
cy.get('input').type('{tab}');
cy.get('input').type('{backspace}');
cy.get('input').type('{del}');
cy.get('input').type('{selectall}');

// 组合键
cy.get('input').type('{ctrl}a');  // 全选
cy.get('input').type('{ctrl}c');  // 复制
cy.get('input').type('{ctrl}v');  // 粘贴

// 使用trigger触发键盘事件
cy.get('input').trigger('keydown', { keyCode: 13 });  // Enter键
cy.get('input').trigger('keypress', { which: 65 });    // 'a'键
cy.get('input').trigger('keyup', { keyCode: 13 });     // Enter键释放
```

## 3.3 表单操作

### 输入框操作

```javascript
// 文本输入框
cy.get('#username').type('testuser');
cy.get('#password').type('password123');

// 清空输入框
cy.get('#username').clear();

// 获取输入框值
cy.get('#username').invoke('val').should('eq', 'testuser');
```

### 下拉菜单操作

```javascript
// 选择下拉选项
cy.get('select#country').select('USA');
cy.get('select#country').select(0);  // 通过索引选择
cy.get('select#country').select(['USA', 'Canada']);  // 多选

// 验证选中值
cy.get('select#country').should('have.value', 'USA');
```

### 复选框和单选按钮

```javascript
// 复选框
cy.get('input[type="checkbox"]').check();
cy.get('input[type="checkbox"]').uncheck();
cy.get('input[type="checkbox"]').check({ force: true });  // 强制选中

// 验证复选框状态
cy.get('input[type="checkbox"]').should('be.checked');
cy.get('input[type="checkbox"]').should('not.be.checked');

// 单选按钮
cy.get('input[type="radio"][value="male"]').check();
cy.get('input[type="radio"][value="male"]').should('be.checked');
```

### 文件上传

```javascript
// 上传文件
cy.get('input[type="file"]').selectFile('path/to/file.jpg');
cy.get('input[type="file"]').selectFile(['file1.jpg', 'file2.pdf']);  // 多文件

// 从fixture上传文件
cy.fixture('example.json').as('jsonData');
cy.get('input[type="file"]').selectFile('@jsonData');

// 验证文件已选择
cy.get('input[type="file"]').should('have.prop', 'files').and('have.length', 1);
```

### 表单提交

```javascript
// 提交表单
cy.get('form').submit();

// 点击提交按钮
cy.get('button[type="submit"]').click();
cy.get('input[type="submit"]').click();
```

## 3.4 导航操作

### 页面导航

```javascript
// 访问URL
cy.visit('https://example.com');
cy.visit('/login');  // 相对于baseUrl

// 带参数访问
cy.visit('/search?q=cypress');

// 带选项访问
cy.visit('/login', {
  auth: {
    username: 'user',
    password: 'pass'
  },
  onBeforeLoad: (win) => {
    // 页面加载前的操作
  },
  onLoad: (win) => {
    // 页面加载完成后的操作
  }
});
```

### 浏览器导航

```javascript
// 前进和后退
cy.go('back');
cy.go('forward');
cy.go(-1);  // 后退一页
cy.go(1);   // 前进一页

// 刷新页面
cy.reload();
cy.reload(true);  // 强制刷新（清除缓存）
```

### URL操作

```javascript
// 获取当前URL
cy.url().should('include', '/dashboard');
cy.url().should('eq', 'https://example.com/dashboard');

// 获取URL的不同部分
cy.location().should((loc) => {
  expect(loc.href).to.include('/dashboard');
  expect(loc.pathname).to.eq('/dashboard');
  expect(loc.search).to.include('id=123');
  expect(loc.hash).to.eq('#section1');
});

// 获取特定URL部分
cy.location('pathname').should('eq', '/dashboard');
cy.location('search').should('include', 'id=123');
```

## 3.5 窗口和视口操作

### 视口大小

```javascript
// 设置视口大小
cy.viewport(1280, 720);
cy.viewport('macbook-15');
cy.viewport('ipad-2');
cy.viewport('iphone-x');

// 验证视口大小
cy.window().its('innerWidth').should('eq', 1280);
cy.window().its('innerHeight').should('eq', 720);
```

### 窗口操作

```javascript
// 获取窗口对象
cy.window().then((win) => {
  // 访问窗口属性和方法
  win.scrollTo(0, 500);
});

// 获取文档对象
cy.document().then((doc) => {
  // 访问文档属性和方法
  console.log(doc.title);
});

// 获取元素对象
cy.get('.element').then(($el) => {
  // 访问jQuery对象
  $el.css('color', 'red');
});
```

## 3.6 网络请求控制

### 拦截请求

```javascript
// 拦截所有请求
cy.intercept('GET', '/api/**').as('apiRequests');

// 拦截特定请求
cy.intercept('POST', '/api/login', { fixture: 'login-success.json' }).as('loginRequest');

// 使用正则表达式拦截
cy.intercept('GET', /\/api\/users\/\d+/).as('userRequest');

// 拦截并修改响应
cy.intercept('GET', '/api/users', (req) => {
  req.reply({
    statusCode: 200,
    body: [{ id: 1, name: 'Test User' }]
  });
}).as('usersRequest');
```

### 等待请求

```javascript
// 等待请求完成
cy.wait('@apiRequests');

// 等待特定请求
cy.wait('@loginRequest');

// 验证请求
cy.wait('@loginRequest').then((interception) => {
  expect(interception.request.body).to.include('username');
  expect(interception.response.statusCode).to.eq(200);
});
```

### 模拟网络条件

```javascript
// 模拟慢速网络
cy.intercept('GET', '/api/slow', { delay: 1000 }).as('slowRequest');

// 模拟网络错误
cy.intercept('GET', '/api/error', { statusCode: 500 }).as('errorRequest');

// 模拟网络超时
cy.intercept('GET', '/api/timeout', { delay: 30000, statusCode: 200 }).as('timeoutRequest');
```

## 3.7 自定义命令

### 创建自定义命令

在`cypress/support/commands.js`文件中添加自定义命令：

```javascript
// 登录命令
Cypress.Commands.add('login', (username, password) => {
  cy.visit('/login');
  cy.get('#username').type(username);
  cy.get('#password').type(password);
  cy.get('button[type="submit"]').click();
});

// 添加商品到购物车命令
Cypress.Commands.add('addToCart', (productId) => {
  cy.get(`[data-product-id="${productId}"]`).find('.add-to-cart').click();
});

// 等待加载完成命令
Cypress.Commands.add('waitForLoading', () => {
  cy.get('.loading-indicator').should('not.exist');
});
```

### 使用自定义命令

```javascript
// 使用自定义命令
it('should login successfully', () => {
  cy.login('testuser', 'password123');
  cy.url().should('include', '/dashboard');
});

it('should add product to cart', () => {
  cy.addToCart('product-123');
  cy.get('.cart-count').should('contain', '1');
});
```

### 覆盖现有命令

```javascript
// 覆盖type命令以添加默认延迟
Cypress.Commands.overwrite('type', (originalFn, subject, text, options = {}) => {
  options.delay = options.delay || 50;
  return originalFn(subject, text, options);
});
```

## 3.8 实验与实践

### 实验1：表单交互

**目标**：练习各种表单元素的交互操作

**步骤**：
1. 创建一个包含各种表单元素的测试页面
2. 使用Cypress与这些元素进行交互
3. 验证交互结果

**示例代码**：
```javascript
describe('表单交互实验', () => {
  beforeEach(() => {
    cy.visit('/form-test-page');
  });

  it('应该填写并提交表单', () => {
    cy.get('#username').type('testuser');
    cy.get('#email').type('test@example.com');
    cy.get('#password').type('password123');
    cy.get('select#country').select('USA');
    cy.get('input[type="checkbox"][name="terms"]').check();
    cy.get('button[type="submit"]').click();
    cy.get('.success-message').should('be.visible');
  });
});
```

### 实验2：鼠标交互

**目标**：练习各种鼠标交互操作

**步骤**：
1. 创建一个包含可交互元素的页面
2. 使用Cypress模拟各种鼠标操作
3. 验证交互结果

**示例代码**：
```javascript
describe('鼠标交互实验', () => {
  beforeEach(() => {
    cy.visit('/mouse-interaction-page');
  });

  it('应该执行各种鼠标操作', () => {
    cy.get('.button').click();
    cy.get('.button').dblclick();
    cy.get('.button').rightclick();
    cy.get('.menu-item').trigger('mouseover');
    cy.get('.draggable').drag('.droppable');
  });
});
```

### 实验3：网络请求控制

**目标**：练习拦截和控制网络请求

**步骤**：
1. 创建一个发起网络请求的页面
2. 使用Cypress拦截这些请求
3. 模拟不同的响应情况

**示例代码**：
```javascript
describe('网络请求控制实验', () => {
  beforeEach(() => {
    cy.visit('/api-test-page');
  });

  it('应该拦截并模拟API响应', () => {
    cy.intercept('GET', '/api/users', { fixture: 'users.json' }).as('getUsers');
    cy.get('.load-users').click();
    cy.wait('@getUsers');
    cy.get('.user-list').should('contain', 'John Doe');
  });
});
```

## 本章小结

本章介绍了Cypress的交互操作和命令，包括：

- 鼠标交互操作：点击、悬停、拖放、右键、滚动等
- 键盘交互操作：文本输入、键盘事件、组合键等
- 表单操作：输入框、下拉菜单、复选框、单选按钮、文件上传等
- 导航操作：页面导航、浏览器导航、URL操作等
- 窗口和视口操作：视口大小设置、窗口对象访问等
- 网络请求控制：拦截请求、等待请求、模拟网络条件等
- 自定义命令：创建和使用自定义命令

通过本章的学习，您应该能够：
- 熟练使用各种鼠标和键盘交互操作
- 处理各种表单元素
- 控制页面导航和窗口操作
- 拦截和控制网络请求
- 创建和使用自定义命令

在下一章中，我们将学习Cypress的断言与验证，深入了解如何验证应用程序的行为和状态。
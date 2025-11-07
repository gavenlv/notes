# 第2章：Cypress核心概念与选择器

## 目录
- [2.1 Cypress核心概念](#21-cypress核心概念)
- [2.2 选择器基础](#22-选择器基础)
- [2.3 常用选择器方法](#23-常用选择器方法)
- [2.4 元素定位策略](#24-元素定位策略)
- [2.5 处理动态元素](#25-处理动态元素)
- [2.6 选择器最佳实践](#26-选择器最佳实践)
- [2.7 实验与实践](#27-实验与实践)

## 2.1 Cypress核心概念

### 命令链

Cypress的核心是命令链（Command Chaining），允许将多个操作链接在一起：

```javascript
cy.get('#button')  // 获取元素
  .click()         // 点击元素
  .should('be.visible');  // 验证元素可见
```

### 命令类型

1. **查询命令**：获取DOM元素
   - `cy.get()`
   - `cy.contains()`
   - `cy.find()`

2. **操作命令**：与元素交互
   - `.click()`
   - `.type()`
   - `.select()`

3. **断言命令**：验证状态
   - `.should()`
   - `.expect()`

4. **控制命令**：控制测试流程
   - `.then()`
   - `.each()`
   - `.its()`

### 自动等待机制

Cypress内置智能等待机制，会自动等待以下条件：
- 元素出现在DOM中
- 元素变为可见
- 元素可交互
- 动画完成
- 网络请求完成

### 命令队列

Cypress将命令放入队列中异步执行，而不是立即执行：

```javascript
// 这些命令不会立即执行，而是被添加到队列中
cy.get('#button');
cy.click();
cy.should('be.visible');
// 测试运行时，Cypress会按顺序执行队列中的命令
```

## 2.2 选择器基础

### 什么是选择器

选择器是用来定位HTML元素的模式或规则。Cypress支持多种选择器类型：

1. **CSS选择器**：使用CSS语法定位元素
2. **属性选择器**：基于元素属性定位
3. **文本选择器**：基于元素内容定位
4. **自定义选择器**：使用特定条件定位元素

### 基本CSS选择器

```javascript
// 通过ID选择
cy.get('#element-id');

// 通过类名选择
cy.get('.element-class');

// 通过标签名选择
cy.get('div');

// 通过属性选择
cy.get('[data-testid="submit-button"]');

// 组合选择器
cy.get('div.container .button.primary');
```

### 属性选择器

```javascript
// 存在特定属性
cy.get('[required]');

// 属性值等于特定值
cy.get('[type="email"]');

// 属性值包含特定字符串
cy.get('[class*="button"]');

// 属性值以特定字符串开头
cy.get('[class^="btn-"]');

// 属性值以特定字符串结尾
cy.get('[class$="-primary"]');
```

## 2.3 常用选择器方法

### cy.get()

最常用的选择器方法，接受CSS选择器作为参数：

```javascript
// 通过ID选择
cy.get('#username');

// 通过类名选择
cy.get('.form-control');

// 通过属性选择
cy.get('[data-cy="submit-form"]');

// 通过标签和属性组合选择
cy.get('input[type="password"]');
```

### cy.contains()

根据元素内容选择元素：

```javascript
// 选择包含特定文本的元素
cy.contains('Submit');

// 选择包含特定文本的特定类型元素
cy.contains('button', 'Submit');

// 使用正则表达式匹配文本
cy.contains(/submit/i);  // 不区分大小写

// 选择包含多个文本的元素
cy.contains(['First', 'Second']);
```

### cy.find()

在已选择的元素内查找子元素：

```javascript
// 先选择父元素，再查找子元素
cy.get('.form-group').find('input');

// 链式查找
cy.get('form').find('.username-field').find('input');
```

### cy.parent()和cy.parents()

选择父元素：

```javascript
// 选择直接父元素
cy.get('button').parent();

// 选择所有匹配的父元素
cy.get('button').parents('form');

// 选择直到特定父元素
cy.get('button').parentsUntil('.container');
```

### cy.siblings()和cy.next()、cy.prev()

选择兄弟元素：

```javascript
// 选择所有兄弟元素
cy.get('.active').siblings();

// 选择下一个兄弟元素
cy.get('.active').next();

// 选择上一个兄弟元素
cy.get('.active').prev();
```

### cy.children()

选择直接子元素：

```javascript
// 选择所有直接子元素
cy.get('.container').children();

// 选择特定类型的直接子元素
cy.get('.container').children('div');
```

## 2.4 元素定位策略

### 使用测试专用属性

最佳实践是为测试添加专用属性，如`data-testid`、`data-cy`或`data-test`：

```html
<!-- 不推荐：使用业务属性 -->
<button class="btn btn-primary" id="submit-btn">Submit</button>

<!-- 推荐：使用测试专用属性 -->
<button class="btn btn-primary" data-testid="submit-button">Submit</button>
```

```javascript
// 使用测试专用属性选择
cy.get('[data-testid="submit-button"]');
```

### 避免使用易变的选择器

避免使用可能随业务逻辑变化的选择器：

```javascript
// 不推荐：使用CSS类名（可能变化）
cy.get('.btn-primary');

// 不推荐：使用文本（可能变化）
cy.contains('Submit');

// 推荐：使用测试专用属性
cy.get('[data-testid="submit-button"]');
```

### 使用语义化选择器

选择具有语义意义的选择器：

```javascript
// 不推荐：使用通用选择器
cy.get('div:nth-child(3) > button');

// 推荐：使用语义化选择器
cy.get('[data-testid="user-profile-save-button"]');
```

### 组合选择器

组合多个条件创建更精确的选择器：

```javascript
// 组合类名和属性
cy.get('.btn[data-testid="submit-button"]');

// 组合标签名和属性
cy.get('button[data-testid="submit-button"]');

// 组合多个属性
cy.get('[data-testid="submit-button"][type="submit"]');
```

## 2.5 处理动态元素

### 处理动态ID

```javascript
// 不推荐：使用动态ID
cy.get('#user-12345-profile');

// 推荐：使用稳定的属性
cy.get('[data-testid="user-profile"]');
```

### 处理动态类名

```javascript
// 不推荐：使用动态类名
cy.get('.active-item-12345');

// 推荐：使用稳定的属性或部分匹配
cy.get('[data-testid="item"].active');
cy.get('[class*="active-item"]');
```

### 处理延迟加载元素

Cypress会自动等待元素出现，但有时需要额外的等待：

```javascript
// 等待元素出现
cy.get('[data-testid="lazy-loaded-content"]').should('be.visible');

// 使用超时设置
cy.get('[data-testid="slow-loading-element"]', { timeout: 10000 });
```

### 处理条件性元素

```javascript
// 检查元素是否存在
cy.get('body').then(($body) => {
  if ($body.find('[data-testid="conditional-element"]').length > 0) {
    cy.get('[data-testid="conditional-element"]').click();
  }
});

// 使用jQuery方法
cy.get('[data-testid="conditional-element"]').should(($el) => {
  expect($el).to.have.length.greaterThan(0);
});
```

## 2.6 选择器最佳实践

### 1. 使用测试专用属性

```html
<!-- 推荐：添加测试专用属性 -->
<button data-testid="submit-form-button" class="btn btn-primary">Submit</button>
```

```javascript
// 推荐：使用测试专用属性
cy.get('[data-testid="submit-form-button"]');
```

### 2. 避免使用CSS选择器进行功能测试

```javascript
// 不推荐：使用CSS类名
cy.get('.btn-primary');

// 不推荐：使用元素层级
cy.get('div > form > button');

// 推荐：使用测试专用属性
cy.get('[data-testid="submit-button"]');
```

### 3. 保持选择器简洁

```javascript
// 不推荐：过于复杂的选择器
cy.get('div.container > form.user-form > div.form-group > button.btn.btn-primary');

// 推荐：简洁的选择器
cy.get('[data-testid="submit-button"]');
```

### 4. 使用有意义的选择器名称

```javascript
// 不推荐：无意义的选择器
cy.get('#el-123');

// 推荐：有意义的选择器
cy.get('[data-testid="user-login-form"]');
```

### 5. 避免使用文本内容选择元素

```javascript
// 不推荐：使用文本内容（可能变化）
cy.contains('Click here to submit');

// 推荐：使用测试专用属性
cy.get('[data-testid="submit-button"]');
```

### 6. 使用相对选择器

```javascript
// 不推荐：使用绝对路径
cy.get('body > div > div > form > button');

// 推荐：从最近的稳定元素开始
cy.get('[data-testid="user-form"]').find('button');
```

## 2.7 实验与实践

### 实验1：基本选择器使用

**目标**：练习使用各种基本选择器

**步骤**：
1. 创建一个简单的HTML页面，包含各种元素和属性
2. 使用不同的选择器定位这些元素
3. 验证选择器是否正确选择了目标元素

**示例代码**：
```javascript
describe('基本选择器使用', () => {
  beforeEach(() => {
    cy.visit('path/to/test/page.html');
  });

  it('使用ID选择器', () => {
    cy.get('#username').should('exist');
  });

  it('使用类名选择器', () => {
    cy.get('.form-control').should('have.length', 3);
  });

  it('使用属性选择器', () => {
    cy.get('[data-testid="submit-button"]').should('be.visible');
  });
});
```

### 实验2：复杂选择器组合

**目标**：练习组合多个选择器条件

**步骤**：
1. 创建包含嵌套元素的复杂页面
2. 使用组合选择器定位特定元素
3. 验证选择器的准确性

**示例代码**：
```javascript
describe('复杂选择器组合', () => {
  beforeEach(() => {
    cy.visit('path/to/complex/page.html');
  });

  it('组合类名和属性', () => {
    cy.get('.btn[data-testid="primary-action"]').should('be.visible');
  });

  it('使用父子关系', () => {
    cy.get('.user-form').find('[data-testid="submit-button"]').should('exist');
  });

  it('使用兄弟关系', () => {
    cy.get('.active').siblings('.inactive').should('have.length', 2);
  });
});
```

### 实验3：处理动态元素

**目标**：练习处理动态生成的元素

**步骤**：
1. 创建一个页面，其中包含动态生成的元素
2. 使用适当的选择器定位这些元素
3. 处理元素加载延迟和条件性显示

**示例代码**：
```javascript
describe('处理动态元素', () => {
  beforeEach(() => {
    cy.visit('path/to/dynamic/page.html');
  });

  it('处理延迟加载元素', () => {
    cy.get('[data-testid="lazy-content"]', { timeout: 10000 }).should('be.visible');
  });

  it('处理条件性元素', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-testid="conditional-element"]').length > 0) {
        cy.get('[data-testid="conditional-element"]').click();
      }
    });
  });
});
```

## 本章小结

本章介绍了Cypress的核心概念和选择器使用方法，包括：

- Cypress的核心概念：命令链、命令类型、自动等待机制和命令队列
- 基本选择器类型：CSS选择器、属性选择器等
- 常用选择器方法：cy.get()、cy.contains()、cy.find()等
- 元素定位策略：使用测试专用属性、避免易变选择器等
- 处理动态元素的方法
- 选择器最佳实践

通过本章的学习，您应该能够：
- 理解Cypress的核心概念和工作原理
- 熟练使用各种选择器定位页面元素
- 处理动态生成的元素
- 遵循选择器最佳实践，编写可维护的测试代码

在下一章中，我们将学习Cypress的交互操作和命令，深入了解如何与页面元素进行交互。
// 第2章示例代码：Cypress核心概念与选择器

// 实验1：基本选择器使用
describe('基本选择器使用', () => {
  beforeEach(() => {
    // 访问测试页面（这里使用Cypress官网作为示例）
    cy.visit('https://www.cypress.io');
  });

  it('使用ID选择器', () => {
    // 在实际测试中，应该使用测试专用属性
    // 这里仅作为示例展示ID选择器
    cy.get('body').should('exist');
  });

  it('使用类名选择器', () => {
    // 查找包含特定类名的元素
    cy.get('.navbar').should('be.visible');
  });

  it('使用标签名选择器', () => {
    // 查找特定标签的元素
    cy.get('nav').should('exist');
  });

  it('使用属性选择器', () => {
    // 查找包含特定属性的元素
    cy.get('[href="/features"]').should('exist');
  });

  it('使用组合选择器', () => {
    // 组合多个条件
    cy.get('nav a[href="/features"]').should('exist');
  });
});

// 实验2：复杂选择器组合
describe('复杂选择器组合', () => {
  beforeEach(() => {
    cy.visit('https://www.cypress.io');
  });

  it('组合类名和属性', () => {
    // 组合类名和属性选择器
    cy.get('a[href="/features"]').should('exist');
  });

  it('使用父子关系', () => {
    // 使用find方法查找子元素
    cy.get('nav').find('a').should('have.length.greaterThan', 0);
  });

  it('使用兄弟关系', () => {
    // 获取元素后查找兄弟元素
    cy.get('nav').then(($nav) => {
      if ($nav.find('a').length > 0) {
        cy.get('nav a').first().siblings().should('have.length.greaterThan', 0);
      }
    });
  });

  it('使用contains方法', () => {
    // 使用contains查找包含特定文本的元素
    cy.contains('Features').should('be.visible');
  });

  it('使用正则表达式', () => {
    // 使用正则表达式匹配文本
    cy.contains(/features/i).should('be.visible');
  });
});

// 实验3：处理动态元素
describe('处理动态元素', () => {
  beforeEach(() => {
    cy.visit('https://www.cypress.io');
  });

  it('处理延迟加载元素', () => {
    // 设置超时时间，等待元素出现
    cy.get('body', { timeout: 10000 }).should('be.visible');
  });

  it('处理条件性元素', () => {
    // 检查元素是否存在
    cy.get('body').then(($body) => {
      if ($body.find('img').length > 0) {
        cy.get('img').first().should('be.visible');
      }
    });
  });

  it('使用should等待元素', () => {
    // 使用should等待元素满足特定条件
    cy.get('body').should('contain', 'Cypress');
  });
});

// 额外示例：选择器最佳实践
describe('选择器最佳实践', () => {
  beforeEach(() => {
    cy.visit('https://www.cypress.io');
  });

  it('使用稳定的属性而非CSS类', () => {
    // 不推荐：使用可能变化的CSS类
    // cy.get('.btn-primary');
    
    // 推荐：使用稳定的属性（这里使用href作为示例）
    cy.get('a[href="/features"]').should('exist');
  });

  it('使用相对选择器而非绝对路径', () => {
    // 不推荐：使用绝对路径
    // cy.get('body > div > header > nav > a');
    
    // 推荐：从最近的稳定元素开始
    cy.get('nav').find('a[href="/features"]').should('exist');
  });

  it('使用有意义的选择器名称', () => {
    // 不推荐：使用无意义的选择器
    // cy.get('div:nth-child(2) > a');
    
    // 推荐：使用有意义的选择器
    cy.get('a[href="/features"]').should('contain', 'Features');
  });
});

// 示例：处理表单元素
describe('表单元素选择', () => {
  beforeEach(() => {
    // 访问一个包含表单的页面（这里使用Cypress官网作为示例）
    cy.visit('https://www.cypress.io');
  });

  it('选择输入框', () => {
    // 在实际应用中，应该使用测试专用属性
    // 这里仅作为示例
    cy.get('body').then(($body) => {
      if ($body.find('input').length > 0) {
        cy.get('input').first().should('exist');
      } else {
        cy.log('页面上没有输入框元素');
      }
    });
  });

  it('选择按钮', () => {
    // 查找按钮元素
    cy.get('body').then(($body) => {
      if ($body.find('button').length > 0) {
        cy.get('button').first().should('exist');
      } else if ($body.find('a').length > 0) {
        cy.log('页面上没有按钮，但有链接元素');
      } else {
        cy.log('页面上没有按钮或链接元素');
      }
    });
  });

  it('选择下拉菜单', () => {
    // 查找下拉菜单元素
    cy.get('body').then(($body) => {
      if ($body.find('select').length > 0) {
        cy.get('select').first().should('exist');
      } else {
        cy.log('页面上没有下拉菜单元素');
      }
    });
  });
});

// 示例：处理列表和表格
describe('列表和表格选择', () => {
  beforeEach(() => {
    cy.visit('https://www.cypress.io');
  });

  it('选择列表项', () => {
    // 查找列表元素
    cy.get('body').then(($body) => {
      if ($body.find('ul').length > 0) {
        cy.get('ul').first().find('li').should('have.length.greaterThan', 0);
      } else if ($body.find('ol').length > 0) {
        cy.get('ol').first().find('li').should('have.length.greaterThan', 0);
      } else {
        cy.log('页面上没有列表元素');
      }
    });
  });

  it('选择表格行和列', () => {
    // 查找表格元素
    cy.get('body').then(($body) => {
      if ($body.find('table').length > 0) {
        cy.get('table').first().find('tr').should('have.length.greaterThan', 0);
      } else {
        cy.log('页面上没有表格元素');
      }
    });
  });
});

// 主函数：用于运行所有实验
function runAllExperiments() {
  console.log('运行第2章所有实验...');
  
  // 注意：这些测试需要在Cypress环境中运行
  // 使用以下命令运行测试：
  // npx cypress open
  // 然后选择对应的测试文件
  
  console.log('实验1：基本选择器使用');
  console.log('实验2：复杂选择器组合');
  console.log('实验3：处理动态元素');
  console.log('额外示例：选择器最佳实践');
  console.log('示例：处理表单元素');
  console.log('示例：处理列表和表格');
}

// 导出主函数（如果在Node.js环境中使用）
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { runAllExperiments };
}
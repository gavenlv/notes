// 第1章示例代码：Cypress基础入门

// 实验1：安装和配置Cypress
// 这个实验不需要代码，只需要按照文档中的步骤进行安装和配置

// 实验2：创建简单测试
describe('我的第一个测试', () => {
  it('访问示例网站并验证标题', () => {
    // 访问网站
    cy.visit('https://example.com');
    
    // 验证页面标题
    cy.title().should('eq', 'Example Domain');
    
    // 验证页面内容
    cy.get('h1').should('contain', 'Example Domain');
  });

  it('访问Cypress官网并验证标题', () => {
    // 访问Cypress官网
    cy.visit('https://www.cypress.io');
    
    // 验证页面标题包含"Cypress"
    cy.title().should('contain', 'Cypress');
    
    // 验证页面包含特定文本
    cy.contains('Fast, easy and reliable testing for anything that runs in a browser').should('be.visible');
  });
});

// 实验3：探索测试运行器
describe('测试运行器探索', () => {
  beforeEach(() => {
    // 在每个测试前访问示例网站
    cy.visit('https://example.com');
  });

  it('使用调试命令', () => {
    // 使用debug命令暂停执行
    cy.get('h1').debug();
    
    // 验证标题元素存在
    cy.get('h1').should('exist');
  });

  it('使用控制台输出', () => {
    // 使用console.log输出调试信息
    cy.get('h1').then(($h1) => {
      console.log('标题文本:', $h1.text());
    });
    
    // 验证标题元素可见
    cy.get('h1').should('be.visible');
  });

  it('使用cy.log()输出信息', () => {
    // 使用cy.log()在测试运行器中输出信息
    cy.log('开始测试标题元素');
    
    // 获取标题元素
    cy.get('h1').should('contain', 'Example Domain');
    
    cy.log('标题元素验证完成');
  });
});

// 额外示例：基本命令使用
describe('基本命令使用示例', () => {
  it('访问网站并验证URL', () => {
    // 访问网站
    cy.visit('https://example.com');
    
    // 验证URL
    cy.url().should('include', 'example.com');
  });

  it('验证页面元素', () => {
    // 访问网站
    cy.visit('https://example.com');
    
    // 验证h1元素存在
    cy.get('h1').should('exist');
    
    // 验证h1元素可见
    cy.get('h1').should('be.visible');
    
    // 验证h1元素包含特定文本
    cy.get('h1').should('contain', 'Example Domain');
  });

  it('使用contains查找元素', () => {
    // 访问网站
    cy.visit('https://example.com');
    
    // 使用contains查找包含特定文本的元素
    cy.contains('Example Domain').should('be.visible');
    
    // 使用contains查找特定元素内的文本
    cy.contains('h1', 'Example Domain').should('be.visible');
  });
});

// 主函数：用于运行所有实验
function runAllExperiments() {
  console.log('运行第1章所有实验...');
  
  // 注意：这些测试需要在Cypress环境中运行
  // 使用以下命令运行测试：
  // npx cypress open
  // 然后选择对应的测试文件
  
  console.log('实验1：安装和配置Cypress');
  console.log('实验2：创建简单测试');
  console.log('实验3：探索测试运行器');
  console.log('额外示例：基本命令使用');
}

// 导出主函数（如果在Node.js环境中使用）
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { runAllExperiments };
}
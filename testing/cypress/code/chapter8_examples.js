// 第8章：Cypress CI/CD集成与最佳实践示例代码

// 实验1：CI/CD集成实践

// 示例1：GitHub Actions工作流配置
// 文件路径：.github/workflows/cypress.yml
const githubActionsWorkflow = `
name: Cypress Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  cypress-run:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        node-version: [16.x, 18.x]
        
    steps:
      - name: Checkout
        uses: actions/checkout@v3
        
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: \${{ matrix.node-version }}
          
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: |
            ~/.npm
            node_modules
          key: \${{ runner.os }}-node-\${{ matrix.node-version }}-\${{ hashFiles('**/package-lock.json') }}
          
      - name: Install dependencies
        run: npm ci
        
      - name: Start application
        run: npm start &
        
      - name: Wait for application
        run: npx wait-on http://localhost:3000
        
      - name: Run Cypress tests
        uses: cypress-io/github-action@v5
        with:
          start: npm start
          wait-on: 'http://localhost:3000'
          browser: chrome
          record: true
        env:
          CYPRESS_RECORD_KEY: \${{ secrets.CYPRESS_RECORD_KEY }}
          GITHUB_TOKEN: \${{ secrets.GITHUB_TOKEN }}
          
      - name: Upload screenshots
        uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: cypress-screenshots
          path: cypress/screenshots
          
      - name: Upload videos
        uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: cypress-videos
          path: cypress/videos
`;

// 示例2：Jenkins Pipeline配置
// 文件路径：Jenkinsfile
const jenkinsPipeline = `
pipeline {
    agent any
    
    environment {
        CYPRESS_RECORD_KEY = credentials('cypress-record-key')
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup') {
            steps {
                sh 'npm ci'
            }
        }
        
        stage('Start App') {
            steps {
                sh 'npm start &'
                sh 'npx wait-on http://localhost:3000'
            }
        }
        
        stage('Test') {
            steps {
                sh 'npx cypress run --record --key $CYPRESS_RECORD_KEY'
            }
        }
    }
    
    post {
        always {
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'cypress/reports/html',
                reportFiles: 'index.html',
                reportName: 'Cypress Report'
            ])
        }
        
        failure {
            archiveArtifacts artifacts: 'cypress/screenshots/**/*,cypress/videos/**/*', fingerprint: true
        }
    }
}
`;

// 示例3：GitLab CI配置
// 文件路径：.gitlab-ci.yml
const gitlabCI = `
stages:
  - test
  - deploy

variables:
  CYPRESS_CACHE_FOLDER: "$CI_PROJECT_DIR/cache/Cypress"

cache:
  paths:
    - cache/Cypress
    - node_modules/

cypress:e2e:
  stage: test
  image: cypress/included:13.6.1
  
  before_script:
    - npm ci
    
  script:
    - npm run start:ci &
    - npx wait-on http://localhost:3000
    - npx cypress run --record --key $CYPRESS_RECORD_KEY
    
  artifacts:
    when: always
    paths:
      - cypress/screenshots
      - cypress/videos
    expire_in: 1 day
    
  only:
    - merge_requests
    - main
    - develop
`;

// 实验2：测试报告定制

// 示例1：Mochawesome报告配置
// 文件路径：cypress.config.js
const mochawesomeConfig = `
const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    // Mochawesome报告配置
    reporter: 'mochawesome',
    reporterOptions: {
      reportDir: 'cypress/results/mochawesome',
      overwrite: false,
      html: true,
      json: true,
      charts: true,
      reportPageTitle: 'Cypress Test Report',
      embeddedScreenshots: true,
      inlineAssets: true
    },
    
    // 视频录制配置
    video: true,
    videoCompression: 32,
    videosFolder: 'cypress/videos',
    videoUploadOnPasses: false,
    
    // 截图配置
    screenshotOnRunFailure: true,
    screenshotsFolder: 'cypress/screenshots',
    trashAssetsBeforeRuns: true
  }
});
`;

// 示例2：自定义报告生成器
// 文件路径：cypress/plugins/index.js
const customReporter = `
const fse = require('fs-extra');
const path = require('path');

module.exports = (on, config) => {
  on('after:run', (results) => {
    if (results) {
      // 生成自定义报告
      generateCustomReport(results);
    }
  });
};

function generateCustomReport(results) {
  const reportPath = path.join(__dirname, '..', 'results', 'custom-report.json');
  
  // 确保目录存在
  fse.ensureDirSync(path.dirname(reportPath));
  
  // 生成报告数据
  const reportData = {
    date: new Date().toISOString(),
    totalTests: results.totalTests,
    totalPassed: results.totalPassed,
    totalFailed: results.totalFailed,
    totalPending: results.totalPending,
    totalSkipped: results.totalSkipped,
    duration: results.totalDuration,
    tests: results.tests.map(test => ({
      title: test.title.join(' '),
      state: test.state,
      duration: test.duration,
      error: test.err ? test.err.message : null
    }))
  };
  
  // 写入报告文件
  fse.writeFileSync(reportPath, JSON.stringify(reportData, null, 2));
}
`;

// 示例3：测试报告合并脚本
// 文件路径：scripts/merge-reports.js
const mergeReportsScript = `
const { merge } = require('mochawesome-merge');
const { create } = require('mochawesome-report-generator');

async function mergeReports() {
  try {
    // 合并所有JSON报告
    const report = await merge({
      files: ['cypress/results/mochawesome/*.json']
    });
    
    // 生成HTML报告
    await create(report, {
      reportDir: 'cypress/results/mochawesome',
      reportFilename: 'merged-report.html'
    });
    
    console.log('报告合并完成');
  } catch (err) {
    console.error('报告合并失败:', err);
  }
}

mergeReports();
`;

// 实验3：并行测试实现

// 示例1：测试分片脚本
// 文件路径：scripts/split-tests.js
const splitTestsScript = `
const { globSync } = require('glob');
const path = require('path');

// 获取所有测试文件
const allSpecs = globSync('cypress/e2e/**/*.cy.{js,jsx,ts,tsx}');

// 获取分片参数
const totalSplits = parseInt(process.env.SPLIT) || 1;
const currentSplit = parseInt(process.env.SPLIT_INDEX) || 0;

// 计算每个分片应该包含的测试文件
const specsPerSplit = Math.ceil(allSpecs.length / totalSplits);
const startIndex = currentSplit * specsPerSplit;
const endIndex = Math.min(startIndex + specsPerSplit, allSpecs.length);

// 获取当前分片的测试文件
const currentSpecs = allSpecs.slice(startIndex, endIndex);

// 输出测试文件列表
console.log(currentSpecs.join(','));
`;

// 示例2：并行测试配置
// 文件路径：cypress.config.js
const parallelTestConfig = `
const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    // 并行测试配置
    experimentalRunAllSpecs: true,
    numTestsKeptInMemory: 50,
    
    // 分片配置
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    
    // 视频和截图配置
    video: true,
    videoCompression: 32,
    screenshotOnRunFailure: true,
    
    // 报告配置
    reporter: 'cypress-mochawesome-reporter',
    reporterOptions: {
      reportDir: 'cypress/results/mochawesome',
      charts: true,
      reportPageTitle: 'Cypress Test Report',
      embeddedScreenshots: true,
      inlineAssets: true
    }
  },
  
  setupNodeEvents(on, config) {
    // 并行测试插件
    require('cypress-mochawesome-reporter/plugin')(on);
    
    // 分片配置
    on('before:run', (details) => {
      console.log('Starting test run with config:', details.config);
    });
    
    return config;
  }
});
`;

// 示例3：并行测试GitHub Actions工作流
// 文件路径：.github/workflows/parallel-tests.yml
const parallelTestsWorkflow = `
name: Cypress Parallel Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        containers: [1, 2, 3, 4, 5]
        
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Start application
        run: npm start &
        
      - name: Wait for application
        run: npx wait-on http://localhost:3000
        
      - name: Run Cypress tests
        uses: cypress-io/github-action@v5
        with:
          start: npm start
          wait-on: 'http://localhost:3000'
          browser: chrome
          record: true
          parallel: true
          group: 'Chrome'
          spec: cypress/e2e/**/*.cy.js
        env:
          CYPRESS_RECORD_KEY: \${{ secrets.CYPRESS_RECORD_KEY }}
          GITHUB_TOKEN: \${{ secrets.GITHUB_TOKEN }}
          SPLIT: \${{ strategy.job-total }}
          SPLIT_INDEX: \${{ strategy.job-index }}
          
      - name: Upload test results
        uses: actions/upload-artifact@v3
        with:
          name: test-results-\${{ matrix.containers }}
          path: cypress/results/mochawesome/*.json
          
  merge-reports:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Download all test results
        uses: actions/download-artifact@v3
        with:
          path: artifacts
          
      - name: Merge test reports
        run: |
          mkdir -p cypress/results/mochawesome
          cp artifacts/test-results-*/cypress/results/mochawesome/*.json cypress/results/mochawesome/
          node scripts/merge-reports.js
          
      - name: Upload merged report
        uses: actions/upload-artifact@v3
        with:
          name: merged-test-report
          path: cypress/results/mochawesome/merged-report.html
`;

// 测试环境管理示例

// 示例1：多环境配置
// 文件路径：cypress.config.js
const multiEnvironmentConfig = `
const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    // 根据环境变量配置不同环境
    baseUrl: process.env.CYPRESS_BASE_URL || 'http://localhost:3000',
    
    // 环境特定配置
    env: {
      // 开发环境
      development: {
        apiUrl: 'http://localhost:3001/api',
        username: 'dev_user',
        password: 'dev_password'
      },
      
      // 测试环境
      testing: {
        apiUrl: 'https://test-api.example.com',
        username: 'test_user',
        password: 'test_password'
      },
      
      // 生产环境
      production: {
        apiUrl: 'https://api.example.com',
        username: 'prod_user',
        password: 'prod_password'
      }
    },
    
    setupNodeEvents(on, config) {
      // 根据环境变量加载不同配置
      const environment = config.env.environment || 'development';
      const environmentConfig = config.env[environment];
      
      if (environmentConfig) {
        Object.assign(config.env, environmentConfig);
      }
      
      return config;
    }
  }
});
`;

// 示例2：环境变量配置文件
// 文件路径：cypress.env.json
const environmentVariables = `
{
  "development": {
    "apiUrl": "http://localhost:3001/api",
    "username": "dev_user",
    "password": "dev_password"
  },
  "testing": {
    "apiUrl": "https://test-api.example.com",
    "username": "test_user",
    "password": "test_password"
  },
  "production": {
    "apiUrl": "https://api.example.com",
    "username": "prod_user",
    "password": "prod_password"
  }
}
`;

// 示例3：测试数据管理命令
// 文件路径：cypress/support/commands.js
const testDataManagement = `
// 加载测试数据命令
Cypress.Commands.add('loadTestData', (fixtureName) => {
  return cy.fixture(fixtureName).then((data) => {
    // 根据环境处理测试数据
    const environment = Cypress.env('environment') || 'development';
    
    if (data[environment]) {
      return data[environment];
    }
    
    return data;
  });
});

// 创建隔离的测试数据命令
Cypress.Commands.add('createUser', (userData = {}) => {
  const defaultUserData = {
    username: \`user_\${Date.now()}\`,
    email: \`user_\${Date.now()}@example.com\`,
    password: 'Password123!',
    firstName: 'Test',
    lastName: 'User'
  };
  
  const finalUserData = { ...defaultUserData, ...userData };
  
  // 通过API创建用户
  return cy.request({
    method: 'POST',
    url: '/api/users',
    body: finalUserData
  }).then((response) => {
    return response.body;
  });
});

// 清理测试数据命令
Cypress.Commands.add('cleanupTestData', () => {
  return cy.task('cleanupTestData').then((result) => {
    cy.log(\`清理了 \${result.deletedCount} 条测试数据\`);
  });
});
`;

// 测试策略与最佳实践示例

// 示例1：E2E测试最佳实践
// 文件路径：cypress/e2e/user-purchase-flow.cy.js
const e2eTestBestPractice = `
describe('用户购买流程', () => {
  beforeEach(() => {
    // 登录用户
    cy.login('testuser@example.com', 'password123');
  });
  
  it('应该允许用户浏览产品并完成购买', () => {
    // 访问首页
    cy.visit('/');
    
    // 搜索产品
    cy.get('[data-cy=search-input]').type('laptop');
    cy.get('[data-cy=search-button]').click();
    
    // 选择产品
    cy.get('[data-cy=product-card]').first().click();
    
    // 添加到购物车
    cy.get('[data-cy=add-to-cart-button]').click();
    
    // 查看购物车
    cy.get('[data-cy=cart-icon]').click();
    
    // 结账
    cy.get('[data-cy=checkout-button]').click();
    
    // 填写配送信息
    cy.get('[data-cy=shipping-form]').within(() => {
      cy.get('[data-cy=first-name]').type('John');
      cy.get('[data-cy=last-name]').type('Doe');
      cy.get('[data-cy=address]').type('123 Main St');
      cy.get('[data-cy=city]').type('Anytown');
      cy.get('[data-cy=zip-code]').type('12345');
    });
    
    // 提交订单
    cy.get('[data-cy=submit-order-button]').click();
    
    // 验证订单成功
    cy.get('[data-cy=order-confirmation]').should('contain', 'Thank you for your order');
  });
  
  it('应该显示用户订单历史', () => {
    // 创建测试订单
    cy.createTestOrder().then((order) => {
      // 访问订单历史页面
      cy.visit('/orders');
      
      // 验证订单显示
      cy.get('[data-cy=order-list]').should('contain', order.id);
      cy.get('[data-cy=order-item]').first().within(() => {
        cy.get('[data-cy=order-date]').should('contain', order.date);
        cy.get('[data-cy=order-total]').should('contain', order.total);
      });
    });
  });
  
  afterEach(() => {
    // 清理测试数据
    cy.cleanupTestData();
  });
});
`;

// 示例2：测试数据隔离
// 文件路径：cypress/e2e/user-management.cy.js
const testDataIsolation = `
describe('用户管理', () => {
  let testUser;
  
  beforeEach(() => {
    // 创建测试用户
    cy.createUser({
      firstName: 'John',
      lastName: 'Doe',
      email: 'john.doe@example.com'
    }).then((user) => {
      testUser = user;
    });
  });
  
  it('应该显示用户列表', () => {
    cy.visit('/users');
    cy.get('[data-cy=user-list]').should('contain', testUser.firstName);
  });
  
  it('应该允许编辑用户信息', () => {
    cy.visit(\`/users/\${testUser.id}/edit\`);
    
    cy.get('[data-cy=first-name]').clear().type('Jane');
    cy.get('[data-cy=last-name]').clear().type('Smith');
    cy.get('[data-cy=save-button]').click();
    
    cy.get('[data-cy=notification]').should('contain', 'User updated successfully');
    cy.get('[data-cy=user-details]').should('contain', 'Jane Smith');
  });
  
  afterEach(() => {
    // 删除测试用户
    if (testUser) {
      cy.request({
        method: 'DELETE',
        url: \`/api/users/\${testUser.id}\`
      });
    }
  });
});
`;

// 示例3：选择器最佳实践
// 文件路径：cypress/e2e/selector-best-practices.cy.js
const selectorBestPractices = `
describe('选择器最佳实践', () => {
  it('应该使用data-cy属性选择器', () => {
    // 好的选择器示例
    cy.get('[data-cy=submit-button]').click(); // 最佳
    cy.get('#user-profile').click(); // 较好
    cy.get('.btn-primary').click(); // 一般
    cy.get('button').click(); // 不推荐
    cy.contains('Submit').click(); // 不推荐
  });
  
  it('应该使用语义化的data-cy属性', () => {
    // 选择器命名约定
    // data-cy-element-type-element-name
    
    cy.get('[data-cy-input-username]').type('testuser');
    cy.get('[data-cy-button-submit]').click();
    cy.get('[data-cy-link-home]').click();
    cy.get('[data-cy-dropdown-menu]').click();
    cy.get('[data-cy-modal-dialog]').should('be.visible');
    cy.get('[data-cy-table-users]').should('contain', 'testuser');
    cy.get('[data-cy-notification-success]').should('contain', 'Success');
  });
});
`;

// 导出所有示例代码
module.exports = {
  githubActionsWorkflow,
  jenkinsPipeline,
  gitlabCI,
  mochawesomeConfig,
  customReporter,
  mergeReportsScript,
  splitTestsScript,
  parallelTestConfig,
  parallelTestsWorkflow,
  multiEnvironmentConfig,
  environmentVariables,
  testDataManagement,
  e2eTestBestPractice,
  testDataIsolation,
  selectorBestPractices
};
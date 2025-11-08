# 第8章：Playwright CI/CD集成与企业级应用

## 8.1 CI/CD基础概念

### 8.1.1 什么是CI/CD
CI/CD（持续集成/持续部署）是现代软件开发中的重要实践，它通过自动化流程确保代码质量和快速交付。

### 8.1.2 Playwright在CI/CD中的作用
Playwright作为端到端测试工具，在CI/CD流水线中扮演着质量守门员的角色，确保每次代码变更都不会破坏现有功能。

## 8.2 GitHub Actions集成

### 8.2.1 基本工作流配置
```yaml
# .github/workflows/playwright.yml
name: Playwright Tests
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-node@v3
      with:
        node-version: 18
    - name: Install dependencies
      run: npm ci
    - name: Install Playwright Browsers
      run: npx playwright install --with-deps
    - name: Run Playwright tests
      run: npx playwright test
    - uses: actions/upload-artifact@v3
      if: always()
      with:
        name: playwright-report
        path: playwright-report/
        retention-days: 30
```

### 8.2.2 并行测试配置
```yaml
# 并行执行多个测试作业
jobs:
  test-chrome:
    runs-on: ubuntu-latest
    steps:
      # ... 安装步骤
      - name: Run Chrome tests
        run: npx playwright test --project=chromium

  test-firefox:
    runs-on: ubuntu-latest
    steps:
      # ... 安装步骤
      - name: Run Firefox tests
        run: npx playwright test --project=firefox

  test-webkit:
    runs-on: ubuntu-latest
    steps:
      # ... 安装步骤
      - name: Run WebKit tests
        run: npx playwright test --project=webkit
```

## 8.3 Jenkins集成

### 8.3.1 Jenkins Pipeline配置
```groovy
// Jenkinsfile
pipeline {
    agent any
    
    tools {
        nodejs "NodeJS-18"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                sh 'npm ci'
            }
        }
        
        stage('Install Playwright') {
            steps {
                sh 'npx playwright install --with-deps'
            }
        }
        
        stage('Run Tests') {
            steps {
                sh 'npx playwright test'
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'playwright-report',
                        reportFiles: 'index.html',
                        reportName: 'Playwright Report'
                    ])
                }
            }
        }
    }
}
```

## 8.4 Docker化测试环境

### 8.4.1 Dockerfile配置
```dockerfile
# Dockerfile
FROM mcr.microsoft.com/playwright:v1.38.0-jammy

WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制应用代码
COPY . .

# 安装浏览器
RUN npx playwright install --with-deps

# 暴露端口
EXPOSE 3000

# 启动命令
CMD ["npm", "start"]
```

### 8.4.2 docker-compose配置
```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "3000:3000"
    depends_on:
      - db
      
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: testdb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
      
  playwright-tests:
    build: .
    command: npx playwright test
    depends_on:
      - app
    environment:
      BASE_URL: http://app:3000
```

## 8.5 测试报告与可视化

### 8.5.1 HTML报告配置
```javascript
// playwright.config.js
const config = {
  reporter: [
    ['html', { 
      outputFolder: 'playwright-report',
      open: 'never'
    }],
    ['json', { 
      outputFile: 'test-results.json' 
    }],
    ['list']
  ],
  // 其他配置...
};

module.exports = config;
```

### 8.5.2 自定义报告器
```javascript
// reporters/slack-reporter.js
class SlackReporter {
  constructor(options) {
    this.options = options;
  }

  async onEnd(result) {
    if (result.status === 'failed') {
      await this.sendSlackNotification(result);
    }
  }

  async sendSlackNotification(result) {
    // 发送失败通知到Slack
    const failedTests = result.failures.length;
    const passedTests = result.passes.length;
    
    const message = `
:test_tube: Playwright测试报告
通过: ${passedTests} :white_check_mark:
失败: ${failedTests} :x:
总执行时间: ${result.duration}ms
    `;
    
    // 发送到Slack webhook
    await fetch(this.options.webhookUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ text: message })
    });
  }
}

module.exports = { SlackReporter };
```

## 8.6 企业级最佳实践

### 8.6.1 测试环境管理
```javascript
// config/environment-manager.js
class EnvironmentManager {
  constructor() {
    this.environments = {
      development: {
        url: 'http://localhost:3000',
        database: 'dev_db'
      },
      staging: {
        url: process.env.STAGING_URL || 'https://staging.example.com',
        database: 'staging_db'
      },
      production: {
        url: process.env.PROD_URL || 'https://example.com',
        database: 'prod_db'
      }
    };
  }

  getEnvironment() {
    return this.environments[process.env.TEST_ENV] || this.environments.development;
  }

  isCI() {
    return !!process.env.CI;
  }
}

module.exports = { EnvironmentManager };
```

### 8.6.2 安全测试集成
```javascript
// tests/security-test.spec.js
const { test, expect } = require('@playwright/test');

test.describe('安全测试', () => {
  test('XSS防护测试', async ({ page }) => {
    await page.goto('/search');
    
    // 尝试注入恶意脚本
    await page.fill('#search-input', '<script>alert("xss")</script>');
    await page.click('#search-button');
    
    // 验证脚本未执行
    const content = await page.content();
    expect(content).not.toContain('alert("xss")');
  });

  test('CSRF防护测试', async ({ page, request }) => {
    // 尝试无令牌请求
    const response = await request.post('/api/delete-account', {
      data: { userId: '123' }
    });
    
    // 验证请求被拒绝
    expect(response.status()).toBe(403);
  });
});
```

## 8.7 实验：构建完整的CI/CD流水线

### 8.7.1 实验目标
构建一个完整的CI/CD流水线，包含代码检出、依赖安装、测试执行、报告生成和通知推送。

### 8.7.2 实验步骤
1. 配置GitHub Actions工作流
2. 设置并行测试执行
3. 集成测试报告
4. 配置失败通知
5. 验证整个流程

### 8.7.3 实验代码
```yaml
# .github/workflows/complete-pipeline.yml
name: 完整CI/CD流水线
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  NODE_VERSION: 18

jobs:
  setup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: ${{ env.NODE_VERSION }}
      - name: Cache node modules
        uses: actions/cache@v3
        with:
          path: ~/.npm
          key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
      - name: Install dependencies
        run: npm ci

  test:
    needs: setup
    strategy:
      matrix:
        browser: [chromium, firefox, webkit]
        os: [ubuntu-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: ${{ env.NODE_VERSION }}
      - name: Restore cache
        uses: actions/cache@v3
        with:
          path: ~/.npm
          key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
      - name: Install dependencies
        run: npm ci
      - name: Install Playwright browsers
        run: npx playwright install --with-deps
      - name: Run tests
        run: npx playwright test --project=${{ matrix.browser }}
        env:
          TEST_ENV: staging
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results-${{ matrix.browser }}-${{ matrix.os }}
          path: |
            test-results/
            playwright-report/

  report:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Download all test results
        uses: actions/download-artifact@v3
      - name: Generate summary report
        run: |
          echo "## 测试报告摘要" >> $GITHUB_STEP_SUMMARY
          echo "所有测试已完成" >> $GITHUB_STEP_SUMMARY
```

## 8.8 监控与告警

### 8.8.1 测试指标收集
```javascript
// helpers/metrics-collector.js
class MetricsCollector {
  constructor() {
    this.metrics = {
      totalTests: 0,
      passedTests: 0,
      failedTests: 0,
      skippedTests: 0,
      duration: 0
    };
  }

  recordTestResult(status) {
    this.metrics.totalTests++;
    switch (status) {
      case 'passed':
        this.metrics.passedTests++;
        break;
      case 'failed':
        this.metrics.failedTests++;
        break;
      case 'skipped':
        this.metrics.skippedTests++;
        break;
    }
  }

  recordDuration(duration) {
    this.metrics.duration += duration;
  }

  getMetrics() {
    return {
      ...this.metrics,
      passRate: this.metrics.totalTests > 0 ? 
        (this.metrics.passedTests / this.metrics.totalTests * 100).toFixed(2) + '%' : '0%'
    };
  }

  async sendToMonitoringSystem(metrics) {
    // 发送到Prometheus、Datadog等监控系统
    console.log('发送指标到监控系统:', metrics);
  }
}

module.exports = { MetricsCollector };
```

## 8.9 故障排除

### 8.9.1 常见CI/CD问题
1. **浏览器安装失败**：使用`npx playwright install --with-deps`
2. **内存不足**：增加runner内存或减少并行度
3. **超时问题**：调整timeout设置
4. **报告生成失败**：检查权限和路径

### 8.9.2 调试技巧
```bash
# 在CI环境中启用调试日志
DEBUG=pw:api npx playwright test

# 生成详细的跟踪文件
npx playwright test --trace on

# 查看浏览器控制台输出
npx playwright test --headed
```

## 8.10 总结
本章介绍了如何将Playwright集成到CI/CD流水线中，包括GitHub Actions和Jenkins的配置方法，以及Docker化测试环境的搭建。通过实际示例和实验，展示了如何构建完整的企业级自动化测试体系，并提供了监控、告警和故障排除的最佳实践。
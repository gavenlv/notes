// examples/codegen-integration-demo.js
/**
 * CodeGen集成演示
 * 展示CodeGen与其他工具和框架的集成
 */

const { CodegenCommandBuilder } = require('./codegen-custom-commands');
const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

/**
 * CodeGen集成管理器
 */
class CodegenIntegrationManager {
  constructor(config = {}) {
    this.config = {
      projectRoot: config.projectRoot || process.cwd(),
      testDir: config.testDir || './tests',
      outputDir: config.outputDir || './codegen-output',
      reportsDir: config.reportsDir || './reports',
      ...config
    };
    
    this.setupDirectories();
  }

  setupDirectories() {
    const dirs = [this.config.testDir, this.config.outputDir, this.config.reportsDir];
    dirs.forEach(dir => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    });
  }

  /**
   * 与CI/CD管道集成
   */
  async integrateWithCICD(options = {}) {
    console.log('集成CodeGen到CI/CD管道...');
    
    const {
      pipeline = 'github-actions',
      environment = 'staging',
      browsers = ['chromium'],
      devices = ['desktop'],
      parallel = true
    } = options;

    // 创建CI/CD配置文件
    const cicdConfig = this.createCICDConfig(pipeline, environment);
    
    // 生成CI/CD脚本
    const scriptContent = this.generateCICDScript(pipeline, {
      environment,
      browsers,
      devices,
      parallel
    });

    // 保存配置文件
    const configPath = path.join(this.config.projectRoot, '.github', 'workflows', 'codegen-ci.yml');
    fs.writeFileSync(configPath, scriptContent);
    
    console.log(`CI/CD配置文件已创建: ${configPath}`);
    
    return {
      configPath,
      pipeline,
      environment,
      browsers,
      devices
    };
  }

  createCICDConfig(pipeline, environment) {
    const configs = {
      'github-actions': {
        name: 'CodeGen CI/CD',
        on: {
          push: { branches: ['main', 'develop'] },
          pull_request: { branches: ['main'] },
          schedule: [{ cron: '0 2 * * *' }] // 每天凌晨2点运行
        },
        jobs: {
          codegen: {
            'runs-on': 'ubuntu-latest',
            strategy: {
              matrix: {
                browser: ['chromium', 'firefox', 'webkit'],
                device: ['desktop', 'iPhone 12']
              }
            },
            steps: [
              { name: 'Checkout', uses: 'actions/checkout@v3' },
              { name: 'Setup Node.js', uses: 'actions/setup-node@v3', with: { 'node-version': '18' } },
              { name: 'Install dependencies', run: 'npm ci' },
              { name: 'Install Playwright', run: 'npx playwright install --with-deps ${{ matrix.browser }}' },
              { name: 'Run CodeGen', run: 'npm run codegen:ci' },
              { name: 'Upload artifacts', uses: 'actions/upload-artifact@v3', with: { 
                name: 'codegen-results-${{ matrix.browser }}-${{ matrix.device }}',
                path: 'codegen-output/'
              }}
            ]
          }
        }
      }
    };

    return configs[pipeline] || configs['github-actions'];
  }

  generateCICDScript(pipeline, options) {
    const { environment, browsers, devices, parallel } = options;
    
    if (pipeline === 'github-actions') {
      return `
name: CodeGen CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'

jobs:
  codegen:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        browser: [${browsers.map(b => `'${b}'`).join(', ')}]
        device: [${devices.map(d => `'${d}'`).join(', ')}]
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Install Playwright browsers
      run: npx playwright install --with-deps \${{ matrix.browser }}
    
    - name: Run CodeGen tests
      run: |
        npm run codegen:batch -- \\
          --browser \${{ matrix.browser }} \\
          --device "\${{ matrix.device }}" \\
          --env ${environment} \\
          ${parallel ? '--parallel' : ''}
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: codegen-results-\${{ matrix.browser }}-\${{ matrix.device }}
        path: |
          codegen-output/
          reports/
      `;
    }
  }

  /**
   * 与测试管理工具集成
   */
  async integrateWithTestManagement(options = {}) {
    console.log('集成CodeGen与测试管理工具...');
    
    const {
      tool = 'testrail',
      projectId,
      suiteId,
      apiKey
    } = options;

    // 创建测试用例映射
    const testCaseMapping = await this.createTestCaseMapping(tool, {
      projectId,
      suiteId,
      apiKey
    });

    // 生成同步脚本
    const syncScript = this.generateTestManagementSyncScript(tool, {
      projectId,
      suiteId,
      apiKey,
      testCaseMapping
    });

    // 保存同步脚本
    const scriptPath = path.join(this.config.outputDir, `sync-with-${tool}.js`);
    fs.writeFileSync(scriptPath, syncScript);
    
    console.log(`测试管理工具集成脚本已创建: ${scriptPath}`);
    
    return {
      scriptPath,
      tool,
      testCaseMapping
    };
  }

  createTestCaseMapping(tool, config) {
    // 模拟创建测试用例映射
    return {
      tool,
      mapping: {
        'generated-test-1.spec.js': { id: 'TC001', title: '用户登录测试' },
        'generated-test-2.spec.js': { id: 'TC002', title: '产品搜索测试' },
        'generated-test-3.spec.js': { id: 'TC003', title: '购物车测试' }
      },
      config
    };
  }

  generateTestManagementSyncScript(tool, options) {
    const { projectId, suiteId, apiKey, testCaseMapping } = options;
    
    return `
// 测试管理工具同步脚本
const axios = require('axios');
const fs = require('fs');

/**
 * 同步CodeGen生成的测试到${tool}
 */
async function syncTestsWithTestManagement() {
  const testResults = JSON.parse(fs.readFileSync('test-results.json', 'utf8'));
  
  for (const result of testResults) {
    const testCase = testCaseMapping.mapping[result.file];
    if (testCase) {
      try {
        // 更新测试用例状态
        await updateTestCaseStatus(tool, {
          projectId: '${projectId}',
          suiteId: '${suiteId}',
          caseId: testCase.id,
          status: result.status,
          apiKey: '${apiKey}'
        });
        
        console.log(\`已更新测试用例: \${testCase.title} (\${testCase.id})\`);
      } catch (error) {
        console.error(\`更新测试用例失败: \${testCase.title}\`, error);
      }
    }
  }
}

async function updateTestCaseStatus(tool, config) {
  // 实现具体的API调用逻辑
  console.log(\`更新 \${tool} 中的测试用例 \${config.caseId} 状态为 \${config.status}\`);
}

// 执行同步
syncTestsWithTestManagement().catch(console.error);
    `;
  }

  /**
   * 与性能测试工具集成
   */
  async integrateWithPerformanceTesting(options = {}) {
    console.log('集成CodeGen与性能测试工具...');
    
    const {
      tool = 'lighthouse',
      url,
      performanceBudget = {}
    } = options;

    // 创建性能测试配置
    const performanceConfig = this.createPerformanceConfig(tool, performanceBudget);
    
    // 生成性能测试脚本
    const performanceScript = this.generatePerformanceTestScript(tool, {
      url,
      config: performanceConfig
    });

    // 保存性能测试脚本
    const scriptPath = path.join(this.config.outputDir, `performance-test-with-${tool}.js`);
    fs.writeFileSync(scriptPath, performanceScript);
    
    console.log(`性能测试集成脚本已创建: ${scriptPath}`);
    
    return {
      scriptPath,
      tool,
      config: performanceConfig
    };
  }

  createPerformanceConfig(tool, budget) {
    const defaultBudget = {
      performance: 90,
      accessibility: 90,
      'best-practices': 90,
      seo: 90,
      pwa: 90
    };

    return {
      ...defaultBudget,
      ...budget
    };
  }

  generatePerformanceTestScript(tool, options) {
    const { url, config } = options;
    
    return `
// 性能测试集成脚本
const { codegenCommandBuilder } = require('./codegen-custom-commands');
const lighthouse = require('lighthouse');
const chromeLauncher = require('chrome-launcher');

/**
 * 使用CodeGen和Lighthouse进行性能测试
 */
async function runPerformanceTestWithCodegen() {
  // 1. 使用CodeGen录制用户交互
  console.log('步骤1: 使用CodeGen录制用户交互...');
  const codegenBuilder = new CodegenCommandBuilder()
    .url('${url}')
    .output('performance-test.spec.js')
    .slowMo(500); // 减慢速度以更好地测量性能
  
  // 执行CodeGen录制
  await codegenBuilder.execute();
  
  // 2. 使用Lighthouse进行性能测试
  console.log('步骤2: 使用Lighthouse进行性能测试...');
  const chrome = await chromeLauncher.launch({ chromeFlags: ['--headless'] });
  
  const options = {
    logLevel: 'info',
    output: 'json',
    onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
    port: chrome.port
  };
  
  const runnerResult = await lighthouse('${url}', options);
  
  // 3. 分析结果
  console.log('步骤3: 分析性能测试结果...');
  const { lhr } = runnerResult;
  
  const results = {
    performance: Math.round(lhr.categories.performance.score * 100),
    accessibility: Math.round(lhr.categories.accessibility.score * 100),
    bestPractices: Math.round(lhr.categories['best-practices'].score * 100),
    seo: Math.round(lhr.categories.seo.score * 100),
    metrics: {
      firstContentfulPaint: lhr.audits['first-contentful-paint'].displayValue,
      largestContentfulPaint: lhr.audits['largest-contentful-paint'].displayValue,
      firstMeaningfulPaint: lhr.audits['first-meaningful-paint'].displayValue,
      speedIndex: lhr.audits['speed-index'].displayValue,
      interactive: lhr.audits['interactive'].displayValue
    }
  };
  
  // 4. 检查性能预算
  const budget = ${JSON.stringify(config, null, 2)};
  const budgetCheck = checkPerformanceBudget(results, budget);
  
  // 5. 生成报告
  const report = {
    url: '${url}',
    timestamp: new Date().toISOString(),
    results,
    budgetCheck,
    passed: budgetCheck.allPassed
  };
  
  fs.writeFileSync('performance-report.json', JSON.stringify(report, null, 2));
  
  console.log('性能测试完成！');
  console.log('结果:', results);
  console.log('预算检查:', budgetCheck);
  
  await chrome.kill();
}

function checkPerformanceBudget(results, budget) {
  const checks = {};
  let allPassed = true;
  
  Object.entries(budget).forEach(([metric, threshold]) => {
    const actual = results[metric] || results[metric.replace('-', '')];
    const passed = actual >= threshold;
    checks[metric] = { actual, threshold, passed };
    if (!passed) allPassed = false;
  });
  
  return { checks, allPassed };
}

// 执行性能测试
runPerformanceTestWithCodegen().catch(console.error);
    `;
  }

  /**
   * 与监控工具集成
   */
  async integrateWithMonitoring(options = {}) {
    console.log('集成CodeGen与监控工具...');
    
    const {
      tool = 'datadog',
      apiKey,
      appKey,
      metrics = []
    } = options;

    // 创建监控配置
    const monitoringConfig = this.createMonitoringConfig(tool, metrics);
    
    // 生成监控脚本
    const monitoringScript = this.generateMonitoringScript(tool, {
      apiKey,
      appKey,
      config: monitoringConfig
    });

    // 保存监控脚本
    const scriptPath = path.join(this.config.outputDir, `monitoring-with-${tool}.js`);
    fs.writeFileSync(scriptPath, monitoringScript);
    
    console.log(`监控工具集成脚本已创建: ${scriptPath}`);
    
    return {
      scriptPath,
      tool,
      config: monitoringConfig
    };
  }

  createMonitoringConfig(tool, metrics) {
    const defaultMetrics = [
      'test_execution_time',
      'test_success_rate',
      'codegen_coverage',
      'browser_performance',
      'error_count'
    ];

    return {
      metrics: metrics.length > 0 ? metrics : defaultMetrics,
      interval: 60000, // 1分钟
      thresholds: {
        test_execution_time: 300000, // 5分钟
        test_success_rate: 0.95, // 95%
        error_count: 5
      }
    };
  }

  generateMonitoringScript(tool, options) {
    const { apiKey, appKey, config } = options;
    
    return `
// 监控工具集成脚本
const { CodegenCommandBuilder } = require('./codegen-custom-commands');
const axios = require('axios');

/**
 * 使用CodeGen进行持续监控
 */
class CodegenMonitoringService {
  constructor(config) {
    this.config = config;
    this.metrics = {
      test_execution_time: [],
      test_success_rate: [],
      codegen_coverage: [],
      browser_performance: [],
      error_count: 0
    };
  }

  async startMonitoring() {
    console.log('启动CodeGen监控服务...');
    
    // 定期执行CodeGen测试
    setInterval(async () => {
      await this.runMonitoringTest();
    }, this.config.interval);
  }

  async runMonitoringTest() {
    const startTime = Date.now();
    
    try {
      // 1. 运行CodeGen测试
      const builder = new CodegenCommandBuilder()
        .url('https://demo.monitoring.com')
        .output(\`monitoring-test-\${Date.now()}.spec.js\`)
        .headless();
      
      const result = await builder.execute();
      
      // 2. 收集指标
      const executionTime = Date.now() - startTime;
      const success = result.success;
      
      this.collectMetrics({
        executionTime,
        success,
        timestamp: new Date().toISOString()
      });
      
      // 3. 检查阈值
      this.checkThresholds();
      
      // 4. 发送到监控工具
      await this.sendMetricsToMonitoringTool();
      
    } catch (error) {
      console.error('监控测试失败:', error);
      this.metrics.error_count++;
    }
  }

  collectMetrics(data) {
    this.metrics.test_execution_time.push(data.executionTime);
    this.metrics.test_success_rate.push(data.success ? 1 : 0);
    
    // 保持最近100个数据点
    Object.keys(this.metrics).forEach(key => {
      if (Array.isArray(this.metrics[key]) && this.metrics[key].length > 100) {
        this.metrics[key] = this.metrics[key].slice(-100);
      }
    });
  }

  checkThresholds() {
    const thresholds = this.config.thresholds;
    
    // 检查执行时间
    const avgExecutionTime = this.metrics.test_execution_time.reduce((a, b) => a + b, 0) / this.metrics.test_execution_time.length;
    if (avgExecutionTime > thresholds.test_execution_time) {
      this.sendAlert('执行时间超过阈值', \`平均执行时间: \${avgExecutionTime}ms\`);
    }
    
    // 检查成功率
    const successRate = this.metrics.test_success_rate.reduce((a, b) => a + b, 0) / this.metrics.test_success_rate.length;
    if (successRate < thresholds.test_success_rate) {
      this.sendAlert('成功率低于阈值', \`成功率: \${(successRate * 100).toFixed(2)}%\`);
    }
    
    // 检查错误数量
    if (this.metrics.error_count > thresholds.error_count) {
      this.sendAlert('错误数量超过阈值', \`错误数量: \${this.metrics.error_count}\`);
    }
  }

  async sendMetricsToMonitoringTool() {
    const payload = {
      series: [
        {
          metric: 'codegen.test_execution_time',
          points: [[Date.now(), this.metrics.test_execution_time[this.metrics.test_execution_time.length - 1]]],
          type: 'gauge',
          tags: ['tool:codegen', 'environment:production']
        },
        {
          metric: 'codegen.test_success_rate',
          points: [[Date.now(), this.metrics.test_success_rate[this.metrics.test_success_rate.length - 1]]],
          type: 'gauge',
          tags: ['tool:codegen', 'environment:production']
        }
      ]
    };
    
    try {
      await axios.post(\`https://api.datadoghq.com/api/v1/series?api_key=${apiKey}\`, payload);
      console.log('指标已发送到监控工具');
    } catch (error) {
      console.error('发送指标失败:', error);
    }
  }

  sendAlert(title, message) {
    console.log(\`[ALERT] \${title}: \${message}\`);
    // 这里可以集成更多的告警机制，如邮件、Slack等
  }
}

// 启动监控服务
const monitoringService = new CodegenMonitoringService(${JSON.stringify(config, null, 2)});
monitoringService.startMonitoring();
    `;
  }

  /**
   * 与容器化平台集成
   */
  async integrateWithContainerization(options = {}) {
    console.log('集成CodeGen与容器化平台...');
    
    const {
      platform = 'docker',
      baseImage = 'mcr.microsoft.com/playwright:v1.38.0-jammy',
      browsers = ['chromium', 'firefox', 'webkit']
    } = options;

    // 创建Dockerfile
    const dockerfileContent = this.generateDockerfile(baseImage, browsers);
    
    // 创建Docker Compose配置
    const dockerComposeContent = this.generateDockerCompose(browsers);
    
    // 创建Kubernetes配置（如果指定）
    let kubernetesContent = null;
    if (platform === 'kubernetes') {
      kubernetesContent = this.generateKubernetesConfig(browsers);
    }

    // 保存配置文件
    const dockerfilePath = path.join(this.config.projectRoot, 'Dockerfile.codegen');
    const dockerComposePath = path.join(this.config.projectRoot, 'docker-compose.codegen.yml');
    
    fs.writeFileSync(dockerfilePath, dockerfileContent);
    fs.writeFileSync(dockerComposePath, dockerComposeContent);
    
    if (kubernetesContent) {
      const kubernetesPath = path.join(this.config.projectRoot, 'k8s-codegen.yml');
      fs.writeFileSync(kubernetesPath, kubernetesContent);
    }
    
    console.log('容器化配置文件已创建');
    
    return {
      dockerfilePath,
      dockerComposePath,
      kubernetesPath: kubernetesContent ? path.join(this.config.projectRoot, 'k8s-codegen.yml') : null,
      platform,
      browsers
    };
  }

  generateDockerfile(baseImage, browsers) {
    return `
# CodeGen容器化Dockerfile
FROM ${baseImage}

# 设置工作目录
WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制应用代码
COPY . .

# 安装额外的浏览器（如果需要）
${browsers.includes('chrome') ? 'RUN npx playwright install chrome' : ''}
${browsers.includes('edge') ? 'RUN npx playwright install msedge' : ''}

# 创建输出目录
RUN mkdir -p /app/codegen-output /app/reports

# 设置环境变量
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

# 暴露端口（用于报告服务）
EXPOSE 8080

# 默认命令
CMD ["npm", "run", "codegen:docker"]
    `;
  }

  generateDockerCompose(browsers) {
    const services = browsers.map(browser => `
  codegen-${browser}:
    build:
      context: .
      dockerfile: Dockerfile.codegen
    environment:
      - BROWSER=${browser}
      - NODE_ENV=production
    volumes:
      - ./codegen-output:/app/codegen-output
      - ./reports:/app/reports
    ports:
      - "808${browsers.indexOf(browser) + 1}:8080"
    command: npm run codegen:browser -- --browser ${browser}
`).join('');

    return `
version: '3.8'

services:${services}

volumes:
  codegen-output:
  reports:
    `;
  }

  generateKubernetesConfig(browsers) {
    return `
apiVersion: apps/v1
kind: Deployment
metadata:
  name: codegen-deployment
spec:
  replicas: ${browsers.length}
  selector:
    matchLabels:
      app: codegen
  template:
    metadata:
      labels:
        app: codegen
    spec:
      containers:
${browsers.map(browser => `
      - name: codegen-${browser}
        image: codegen:latest
        env:
        - name: BROWSER
          value: "${browser}"
        - name: NODE_ENV
          value: "production"
        volumeMounts:
        - name: codegen-storage
          mountPath: /app/codegen-output
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
`).join('')}
      volumes:
      - name: codegen-storage
        persistentVolumeClaim:
          claimName: codegen-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: codegen-service
spec:
  selector:
    app: codegen
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 8080
  type: LoadBalancer
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: codegen-pvc
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
    `;
  }
}

/**
 * 演示所有集成
 */
async function demonstrateAllIntegrations() {
  console.log('=== CodeGen集成演示 ===\n');

  const integrationManager = new CodegenIntegrationManager();

  // 示例1: CI/CD集成
  console.log('1. CI/CD集成演示');
  const cicdResult = await integrationManager.integrateWithCICD({
    pipeline: 'github-actions',
    environment: 'staging',
    browsers: ['chromium', 'firefox'],
    devices: ['desktop', 'iPhone 12'],
    parallel: true
  });

  // 示例2: 测试管理工具集成
  console.log('\n2. 测试管理工具集成演示');
  const testManagementResult = await integrationManager.integrateWithTestManagement({
    tool: 'testrail',
    projectId: '123',
    suiteId: '456',
    apiKey: 'your-api-key'
  });

  // 示例3: 性能测试集成
  console.log('\n3. 性能测试集成演示');
  const performanceResult = await integrationManager.integrateWithPerformanceTesting({
    tool: 'lighthouse',
    url: 'https://example.com',
    performanceBudget: {
      performance: 85,
      accessibility: 90,
      'best-practices': 90,
      seo: 80
    }
  });

  // 示例4: 监控工具集成
  console.log('\n4. 监控工具集成演示');
  const monitoringResult = await integrationManager.integrateWithMonitoring({
    tool: 'datadog',
    apiKey: 'your-api-key',
    appKey: 'your-app-key',
    metrics: ['test_execution_time', 'test_success_rate', 'error_count']
  });

  // 示例5: 容器化集成
  console.log('\n5. 容器化集成演示');
  const containerResult = await integrationManager.integrateWithContainerization({
    platform: 'docker',
    baseImage: 'mcr.microsoft.com/playwright:v1.38.0-jammy',
    browsers: ['chromium', 'firefox', 'webkit']
  });

  console.log('\n=== 所有集成演示完成 ===');
  
  return {
    cicd: cicdResult,
    testManagement: testManagementResult,
    performance: performanceResult,
    monitoring: monitoringResult,
    containerization: containerResult
  };
}

// 导出所有功能
module.exports = {
  CodegenIntegrationManager,
  demonstrateAllIntegrations
};

// 如果直接运行此文件，执行演示
if (require.main === module) {
  demonstrateAllIntegrations().catch(console.error);
}
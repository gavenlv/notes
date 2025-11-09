# 第4章：k6最佳实践与生产环境部署

## 4.1 k6脚本最佳实践

### 代码组织和模块化

```javascript
// utils/http-utils.js - HTTP工具函数
import http from 'k6/http';

export function makeRequest(method, url, data = null, options = {}) {
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'k6-performance-test/1.0',
      ...options.headers,
    },
    tags: {
      method: method.toUpperCase(),
      url: url,
      ...options.tags,
    },
    timeout: '30s',
    ...options,
  };
  
  switch (method.toUpperCase()) {
    case 'GET':
      return http.get(url, defaultOptions);
    case 'POST':
      return http.post(url, JSON.stringify(data), defaultOptions);
    case 'PUT':
      return http.put(url, JSON.stringify(data), defaultOptions);
    case 'DELETE':
      return http.del(url, defaultOptions);
    default:
      throw new Error(`Unsupported HTTP method: ${method}`);
  }
}

export function withRetry(requestFn, maxRetries = 3, baseDelay = 1000) {
  return async function (...args) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await requestFn(...args);
      } catch (error) {
        if (attempt === maxRetries) throw error;
        await sleep((baseDelay * Math.pow(2, attempt - 1)) / 1000);
      }
    }
  };
}

// utils/validation-utils.js - 验证工具函数
import { check } from 'k6';

export function validateResponse(response, expectations) {
  const results = check(response, expectations);
  
  // 记录验证结果
  if (!results) {
    console.warn('Response validation failed:', {
      url: response.url,
      status: response.status,
      expectations: Object.keys(expectations),
    });
  }
  
  return results;
}

export function createApiValidator(apiName) {
  return function (response, customExpectations = {}) {
    const baseExpectations = {
      [`${apiName} status is 2xx`]: (r) => r.status >= 200 && r.status < 300,
      [`${apiName} response time < 5s`]: (r) => r.timings.duration < 5000,
      ...customExpectations,
    };
    
    return validateResponse(response, baseExpectations);
  };
}

// config/test-config.js - 测试配置
const environments = {
  development: {
    baseUrl: 'https://httpbin.test.k6.io',
    users: {
      min: 1,
      max: 10,
    },
    timeout: '30s',
  },
  
  staging: {
    baseUrl: 'https://staging-api.example.com',
    users: {
      min: 10,
      max: 100,
    },
    timeout: '60s',
  },
  
  production: {
    baseUrl: 'https://api.example.com',
    users: {
      min: 50,
      max: 1000,
    },
    timeout: '120s',
  },
};

export function getConfig(env = __ENV.ENV || 'development') {
  return environments[env] || environments.development;
}

// 主测试脚本
import { makeRequest, withRetry, createApiValidator } from './utils/http-utils.js';
import { getConfig } from './config/test-config.js';

const config = getConfig();
const validateApi = createApiValidator('test-api');

// 配置测试参数
export const options = {
  stages: [
    { duration: '2m', target: config.users.min },
    { duration: '5m', target: config.users.max },
    { duration: '2m', target: 0 },
  ],
  
  thresholds: {
    http_req_duration: [`p(95)<${config.timeout}`],
    http_req_failed: ['rate<0.01'],
    checks: ['rate>0.99'],
  },
};

export default function () {
  // 使用工具函数进行测试
  const response = withRetry(makeRequest)('GET', `${config.baseUrl}/get`);
  validateApi(response, {
    'response contains expected data': (r) => {
      const data = r.json();
      return data.url === `${config.baseUrl}/get`;
    },
  });
}
```

### 性能优化技巧

```javascript
// 避免内存泄漏
import { group } from 'k6';

export default function () {
  // 正确：在函数作用域内创建变量
  group('efficient_memory_usage', function () {
    const localData = { timestamp: Date.now() };
    
    // 使用后及时清理引用
    const response = http.get('https://api.example.com/data');
    
    // 处理完成后清除大对象引用
    localData.processed = true;
    // localData 会在函数结束时自动垃圾回收
  });
  
  // 错误：在全局作用域累积数据
  // globalData.push(someLargeObject); // 这会导致内存泄漏
}

// 优化HTTP请求
import http from 'k6/http';

export default function () {
  // 使用连接池
  const params = {
    headers: {
      'Connection': 'keep-alive',
    },
  };
  
  // 批量请求（如果API支持）
  const batchRequests = [
    { method: 'GET', url: 'https://api.example.com/users/1' },
    { method: 'GET', url: 'https://api.example.com/users/2' },
    { method: 'GET', url: 'https://api.example.com/users/3' },
  ];
  
  // 并行执行（如果逻辑允许）
  const responses = http.batch(batchRequests);
  
  // 使用HTTP/2（如果服务器支持）
  const http2Params = {
    http2: true,
  };
  
  const http2Response = http.get('https://api.example.com/http2-endpoint', http2Params);
}
```

## 4.2 CI/CD集成

### GitLab CI集成

```yaml
# .gitlab-ci.yml
stages:
  - test
  - performance

variables:
  K6_CLOUD_TOKEN: $K6_CLOUD_TOKEN

performance_tests:
  stage: performance
  image: grafana/k6:latest
  script:
    - echo "Running performance tests..."
    - k6 run --out cloud scripts/smoke-test.js
    - k6 run --out cloud scripts/load-test.js
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  artifacts:
    when: always
    reports:
      junit: reports/junit-*.xml
    paths:
      - reports/
    expire_in: 1 week

performance_tests_on_demand:
  stage: performance
  image: grafana/k6:latest
  script:
    - echo "Running on-demand performance tests..."
    - k6 cloud scripts/stress-test.js
  when: manual
  allow_failure: true
```

### Jenkins集成

```groovy
// Jenkinsfile
pipeline {
  agent any
  
  environment {
    K6_CLOUD_TOKEN = credentials('k6-cloud-token')
  }
  
  stages {
    stage('Build') {
      steps {
        sh 'npm install'
        sh 'npm run build'
      }
    }
    
    stage('Unit Tests') {
      steps {
        sh 'npm test'
      }
    }
    
    stage('Performance Tests') {
      parallel {
        stage('Smoke Test') {
          steps {
            sh 'k6 run scripts/smoke-test.js --out json=reports/smoke-results.json'
          }
          post {
            always {
              junit 'reports/*-results.xml'
              archiveArtifacts artifacts: 'reports/', fingerprint: true
            }
          }
        }
        
        stage('Load Test') {
          steps {
            sh 'k6 run scripts/load-test.js --out influxdb=http://influxdb:8086/k6'
          }
        }
      }
    }
  }
  
  post {
    always {
      // 清理工作
      sh 'rm -rf reports/'
    }
    
    success {
      // 发送成功通知
      emailext (
        subject: "SUCCESS: Performance Tests - ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
        body: "Performance tests passed successfully.\n\nCheck details: ${env.BUILD_URL}",
        to: "devops@example.com"
      )
    }
    
    failure {
      // 发送失败通知
      emailext (
        subject: "FAILED: Performance Tests - ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
        body: "Performance tests failed. Please check the logs.\n\nBuild URL: ${env.BUILD_URL}",
        to: "devops@example.com"
      )
    }
  }
}
```

### GitHub Actions集成

```yaml
# .github/workflows/performance-tests.yml
name: Performance Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'  # 每天凌晨2点运行

jobs:
  performance-tests:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        test-type: [smoke, load, stress]
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Setup k6
      uses: grafana/setup-k6-action@v1
      with:
        k6-version: '0.45.0'
    
    - name: Run ${{ matrix.test-type }} test
      run: |
        k6 run scripts/${{ matrix.test-type }}-test.js \
          --out json=reports/${{ matrix.test-type }}-results.json \
          --summary-export=reports/${{ matrix.test-type }}-summary.json
      env:
        K6_CLOUD_TOKEN: ${{ secrets.K6_CLOUD_TOKEN }}
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      with:
        name: ${{ matrix.test-type }}-test-results
        path: reports/
    
    - name: Notify on failure
      if: failure()
      uses: 8398a7/action-slack@v3
      with:
        status: failure
        text: Performance test ${{ matrix.test-type }} failed
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

## 4.3 监控和告警

### 与Prometheus集成

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'k6'
    static_configs:
      - targets: ['localhost:6565']
    scrape_interval: 15s
    metrics_path: /metrics

# k6脚本配置Prometheus输出
import { prometheus } from 'k6/metrics';

// 创建自定义指标
export const customMetrics = {
  transactionDuration: new prometheus.Summary('k6_transaction_duration_seconds'),
  errorRate: new prometheus.Gauge('k6_error_rate'),
  activeUsers: new prometheus.Gauge('k6_active_users'),
};

export const options = {
  // 启用Prometheus远程写入
  ext: {
    loadimpact: {
      name: 'Production Load Test',
      projectID: 123456,
    },
  },
  
  // 配置输出
  outputs: {
    prometheus: {
      url: 'http://localhost:9090/api/v1/write',
    },
  },
};

export default function () {
  const startTime = Date.now();
  
  try {
    const response = http.get('https://api.example.com/data');
    
    // 记录指标
    customMetrics.transactionDuration.observe((Date.now() - startTime) / 1000);
    customMetrics.errorRate.set(0);
    customMetrics.activeUsers.set(__VU);
    
  } catch (error) {
    customMetrics.errorRate.set(1);
  }
}
```

### Grafana仪表板配置

```json
{
  "dashboard": {
    "title": "K6 Performance Dashboard",
    "panels": [
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(k6_http_req_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "singlestat",
        "targets": [
          {
            "expr": "rate(k6_http_req_failed[5m]) * 100",
            "format": "percent"
          }
        ],
        "thresholds": "0,1,5"
      }
    ]
  }
}
```

## 4.4 生产环境部署策略

### Docker化部署

```dockerfile
# Dockerfile
FROM grafana/k6:latest

WORKDIR /app

# 复制测试脚本和资源
COPY scripts/ ./scripts/
COPY data/ ./data/
COPY config/ ./config/

# 设置环境变量
ENV K6_CLOUD_TOKEN=""
ENV K6_OUT="influxdb=http://influxdb:8086/k6"

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD k6 version || exit 1

# 设置入口点
ENTRYPOINT ["k6"]
CMD ["run", "scripts/smoke-test.js"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  k6-runner:
    build: .
    environment:
      - K6_CLOUD_TOKEN=${K6_CLOUD_TOKEN}
      - K6_OUT=influxdb=http://influxdb:8086/k6
    volumes:
      - ./reports:/app/reports
    depends_on:
      - influxdb
    networks:
      - k6-network

  influxdb:
    image: influxdb:2.0
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=admin
      - DOCKER_INFLUXDB_INIT_PASSWORD=password
      - DOCKER_INFLUXDB_INIT_ORG=k6
      - DOCKER_INFLUXDB_INIT_BUCKET=k6
    ports:
      - "8086:8086"
    networks:
      - k6-network

  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    ports:
      - "3000:3000"
    depends_on:
      - influxdb
    networks:
      - k6-network

networks:
  k6-network:
    driver: bridge
```

### Kubernetes部署

```yaml
# k6-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: k6-test-runner
  labels:
    app: k6
spec:
  replicas: 3
  selector:
    matchLabels:
      app: k6
  template:
    metadata:
      labels:
        app: k6
    spec:
      containers:
      - name: k6
        image: my-registry/k6-runner:latest
        env:
        - name: K6_CLOUD_TOKEN
          valueFrom:
            secretKeyRef:
              name: k6-secrets
              key: cloud-token
        - name: K6_TEST_SCRIPT
          value: "scripts/load-test.js"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        volumeMounts:
        - name: test-scripts
          mountPath: /app/scripts
        - name: config
          mountPath: /app/config
      volumes:
      - name: test-scripts
        configMap:
          name: k6-scripts
      - name: config
        secret:
          secretName: k6-config
      restartPolicy: Always
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: k6-scripts
data:
  smoke-test.js: |
    import http from 'k6/http';
    
    export const options = {
      vus: 1,
      duration: '1m',
    };
    
    export default function () {
      http.get('https://api.example.com/health');
    }
  load-test.js: |
    import http from 'k6/http';
    
    export const options = {
      stages: [
        { duration: '2m', target: 10 },
        { duration: '5m', target: 10 },
        { duration: '2m', target: 0 },
      ],
    };
    
    export default function () {
      http.get('https://api.example.com/api');
    }
```

## 4.5 安全考虑

### 敏感信息管理

```javascript
// 使用环境变量管理敏感信息
const config = {
  apiKey: __ENV.API_KEY || 'default-key',
  baseUrl: __ENV.BASE_URL || 'https://test.example.com',
  databaseUrl: __ENV.DATABASE_URL,
};

// 安全的认证处理
function getAuthHeaders() {
  const token = __ENV.API_TOKEN;
  
  if (!token) {
    throw new Error('API token is required');
  }
  
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
}

// 避免在日志中记录敏感信息
console.log = (function(originalLog) {
  return function(...args) {
    // 过滤敏感信息
    const filteredArgs = args.map(arg => {
      if (typeof arg === 'string') {
        return arg
          .replace(/Bearer\s+\w+/g, 'Bearer [REDACTED]')
          .replace(/apikey=\w+/g, 'apikey=[REDACTED]');
      }
      return arg;
    });
    
    originalLog.apply(console, filteredArgs);
  };
})(console.log);
```

## 4.6 实验：生产级性能测试框架

### 实验目标
创建一个可用于生产环境的完整性能测试框架。

### 实验代码

```javascript
// 实验4：生产级性能测试框架

// config/production-config.js
const environments = {
  development: {
    baseUrl: 'https://httpbin.test.k6.io',
    thresholds: {
      http_req_duration: ['p(95)<1000'],
      http_req_failed: ['rate<0.01'],
    },
    users: { min: 1, max: 10 },
  },
  
  production: {
    baseUrl: 'https://api.example.com',
    thresholds: {
      http_req_duration: ['p(95)<2000'],
      http_req_failed: ['rate<0.005'],
    },
    users: { min: 50, max: 1000 },
  },
};

export function getEnvironmentConfig() {
  const env = __ENV.ENV || 'development';
  return environments[env] || environments.development;
}

// utils/metrics-collector.js
import { Counter, Trend, Rate } from 'k6/metrics';

export class MetricsCollector {
  constructor(prefix = '') {
    this.prefix = prefix;
    this.metrics = {};
  }
  
  createMetric(type, name, options = {}) {
    const fullName = this.prefix ? `${this.prefix}_${name}` : name;
    
    switch (type) {
      case 'counter':
        this.metrics[name] = new Counter(fullName);
        break;
      case 'trend':
        this.metrics[name] = new Trend(fullName, options.timestamp);
        break;
      case 'rate':
        this.metrics[name] = new Rate(fullName);
        break;
      default:
        throw new Error(`Unknown metric type: ${type}`);
    }
    
    return this.metrics[name];
  }
  
  record(name, value, tags = {}) {
    if (!this.metrics[name]) {
      throw new Error(`Metric not found: ${name}`);
    }
    
    this.metrics[name].add(value, tags);
  }
}

// tests/api-test-suite.js
import { getEnvironmentConfig } from '../config/production-config.js';
import { MetricsCollector } from '../utils/metrics-collector.js';

const config = getEnvironmentConfig();
const metrics = new MetricsCollector('api');

// 创建测试指标
const responseTimeMetric = metrics.createMetric('trend', 'response_time', { timestamp: true });
const errorRateMetric = metrics.createMetric('rate', 'error_rate');
const requestCountMetric = metrics.createMetric('counter', 'request_count');

export const options = {
  stages: [
    { duration: '2m', target: config.users.min },
    { duration: '10m', target: config.users.max },
    { duration: '2m', target: 0 },
  ],
  
  thresholds: config.thresholds,
  
  // 生产环境额外配置
  noConnectionReuse: false,
  userAgent: 'k6-production-test/1.0',
  
  // 输出配置
  summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(95)', 'p(99)'],
};

// 测试套件
export function setup() {
  console.log(`Starting test in ${__ENV.ENV || 'development'} environment`);
  console.log(`Base URL: ${config.baseUrl}`);
  
  return {
    startTime: Date.now(),
    environment: __ENV.ENV || 'development',
  };
}

export default function (data) {
  const testStartTime = Date.now();
  
  try {
    // 记录测试开始
    requestCountMetric.add(1, { endpoint: 'health' });
    
    // 健康检查
    const healthResponse = http.get(`${config.baseUrl}/health`);
    
    // 记录响应时间
    const responseTime = Date.now() - testStartTime;
    responseTimeMetric.add(responseTime, { endpoint: 'health' });
    
    // 验证响应
    const healthCheck = check(healthResponse, {
      'health check status is 200': (r) => r.status === 200,
      'health check response time < 5s': (r) => r.timings.duration < 5000,
    });
    
    // 记录错误率
    errorRateMetric.add(healthCheck);
    
    if (!healthCheck) {
      console.error(`Health check failed: ${healthResponse.status}`);
    }
    
  } catch (error) {
    // 记录错误
    errorRateMetric.add(false);
    console.error(`Test execution failed: ${error.message}`);
  }
}

export function teardown(data) {
  const totalDuration = Date.now() - data.startTime;
  
  console.log(`Test completed in ${data.environment} environment`);
  console.log(`Total duration: ${totalDuration}ms`);
  
  // 生成测试报告摘要
  console.log('=== TEST SUMMARY ===');
  console.log(`Environment: ${data.environment}`);
  console.log(`Base URL: ${config.baseUrl}`);
  console.log(`Test duration: ${Math.round(totalDuration / 1000)} seconds`);
}

// 运行不同测试类型的脚本
// scripts/run-smoke-test.js
import { getEnvironmentConfig } from '../config/production-config.js';

export const options = {
  vus: 1,
  duration: '1m',
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

const config = getEnvironmentConfig();

export default function () {
  // 简单烟雾测试逻辑
  http.get(`${config.baseUrl}/health`);
}

// scripts/run-load-test.js
import { getEnvironmentConfig } from '../config/production-config.js';

export const options = {
  stages: [
    { duration: '5m', target: 50 },
    { duration: '15m', target: 50 },
    { duration: '5m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000'],
    http_req_failed: ['rate<0.005'],
  },
};

const config = getEnvironmentConfig();

export default function () {
  // 负载测试逻辑
  http.get(`${config.baseUrl}/api/v1/data`);
}
```

### 部署和运行

```bash
# 设置环境变量
export ENV=production
export BASE_URL=https://api.example.com
export K6_CLOUD_TOKEN=your-token-here

# 运行烟雾测试
k6 run scripts/run-smoke-test.js --out cloud

# 运行负载测试
k6 run scripts/run-load-test.js --out cloud

# 使用Docker运行
docker run -i --rm \
  -e ENV=production \
  -e K6_CLOUD_TOKEN=your-token \
  -v $(pwd)/scripts:/scripts \
  grafana/k6 run /scripts/run-load-test.js
```

## 总结

本章我们学习了k6在生产环境中的最佳实践：

1. **代码组织和模块化**：创建可维护的测试代码结构
2. **CI/CD集成**：与GitLab、Jenkins、GitHub Actions等工具的无缝集成
3. **监控和告警**：与Prometheus和Grafana的集成
4. **生产环境部署**：Docker和Kubernetes部署策略
5. **安全考虑**：敏感信息管理和安全最佳实践
6. **完整测试框架**：创建可用于生产环境的性能测试框架

通过本课程的学习，您已经掌握了从k6基础到专家级别的完整知识体系，能够设计、实施和维护专业的性能测试方案。
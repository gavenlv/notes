// 第4章：生产级测试框架示例
// 演示如何在生产环境中使用k6进行性能测试

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Rate, Trend, Gauge } from 'k6/metrics';
import { htmlReport } from 'https://jslib.k6.io/k6-summary/0.0.1/index.js';

// 生产环境配置
const ENV = __ENV.ENV || 'production';
const BASE_URL = __ENV.BASE_URL || 'https://httpbin.test.k6.io';
const API_KEY = __ENV.API_KEY || 'test-key';

// 生产环境指标
const customMetrics = {
  // 业务指标
  successfulTransactions: new Counter('successful_transactions'),
  failedTransactions: new Counter('failed_transactions'),
  transactionRate: new Rate('transaction_rate'),
  
  // 性能指标
  responseTimeTrend: new Trend('response_time_trend'),
  throughputGauge: new Gauge('throughput_gauge'),
  
  // 错误指标
  errorRate: new Rate('error_rate'),
  timeoutRate: new Rate('timeout_rate'),
  
  // 资源指标
  memoryUsage: new Gauge('memory_usage'),
  cpuUsage: new Gauge('cpu_usage'),
};

// 生产级HTTP客户端
class ProductionHttpClient {
  constructor(baseUrl, apiKey) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
    this.requestCounter = 0;
  }
  
  createHeaders() {
    return {
      'Authorization': `Bearer ${this.apiKey}`,
      'Content-Type': 'application/json',
      'User-Agent': 'k6-production-framework/1.0',
      'X-Request-ID': this.generateRequestId(),
      'X-Environment': ENV,
    };
  }
  
  generateRequestId() {
    return `req_${Date.now()}_${this.requestCounter++}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  async request(method, endpoint, data = null, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = { ...this.createHeaders(), ...options.headers };
    
    const params = {
      headers,
      tags: {
        environment: ENV,
        endpoint: endpoint,
        method: method.toUpperCase(),
        ...options.tags,
      },
      timeout: options.timeout || '30s',
    };
    
    const startTime = Date.now();
    
    try {
      let response;
      
      switch (method.toUpperCase()) {
        case 'GET':
          response = http.get(url, params);
          break;
        case 'POST':
          response = http.post(url, JSON.stringify(data), params);
          break;
        case 'PUT':
          response = http.put(url, JSON.stringify(data), params);
          break;
        case 'PATCH':
          response = http.patch(url, JSON.stringify(data), params);
          break;
        case 'DELETE':
          response = http.del(url, params);
          break;
        default:
          throw new Error(`Unsupported HTTP method: ${method}`);
      }
      
      const responseTime = Date.now() - startTime;
      
      // 记录指标
      customMetrics.responseTimeTrend.add(responseTime);
      customMetrics.memoryUsage.add(__VU * 100); // 模拟内存使用
      customMetrics.cpuUsage.add(Math.random() * 100); // 模拟CPU使用
      
      return {
        success: response.status >= 200 && response.status < 300,
        status: response.status,
        data: response.json(),
        responseTime,
        headers: response.headers,
      };
      
    } catch (error) {
      const responseTime = Date.now() - startTime;
      
      // 记录错误指标
      customMetrics.errorRate.add(false);
      
      if (error.message.includes('timeout')) {
        customMetrics.timeoutRate.add(false);
      }
      
      return {
        success: false,
        error: error.message,
        responseTime,
      };
    }
  }
}

// 测试场景管理器
class TestScenarioManager {
  constructor() {
    this.scenarios = new Map();
    this.results = [];
  }
  
  registerScenario(name, scenario) {
    this.scenarios.set(name, scenario);
  }
  
  async runScenario(name, iterations = 1) {
    const scenario = this.scenarios.get(name);
    if (!scenario) {
      throw new Error(`Scenario '${name}' not found`);
    }
    
    const scenarioResults = [];
    
    for (let i = 0; i < iterations; i++) {
      try {
        const result = await scenario.execute(i);
        scenarioResults.push(result);
        
        if (result.success) {
          customMetrics.successfulTransactions.add(1);
          customMetrics.transactionRate.add(true);
        } else {
          customMetrics.failedTransactions.add(1);
          customMetrics.transactionRate.add(false);
        }
        
      } catch (error) {
        console.error(`Scenario ${name} iteration ${i} failed:`, error);
        scenarioResults.push({ success: false, error: error.message });
        customMetrics.failedTransactions.add(1);
        customMetrics.transactionRate.add(false);
      }
      
      sleep(0.1); // 避免过快的请求
    }
    
    this.results.push({
      scenario: name,
      results: scenarioResults,
      successRate: scenarioResults.filter(r => r.success).length / scenarioResults.length
    };
    
    return scenarioResults;
  }
  
  getSummary() {
    return {
      totalScenarios: this.scenarios.size,
      totalIterations: this.results.reduce((sum, r) => sum + r.results.length, 0),
      successRate: this.results.reduce((sum, r) => sum + r.successRate, 0) / this.results.length,
      scenarios: this.results
    };
  }
}

// 基础测试场景
class BaseScenario {
  constructor(name, httpClient) {
    this.name = name;
    this.httpClient = httpClient;
  }
  
  async execute(iteration) {
    throw new Error('execute method must be implemented');
  }
  
  validateResponse(response, expectedStatus = 200) {
    return response.status === expectedStatus && response.data;
  }
  
  logResult(result, iteration) {
    if (result.success) {
      console.log(`[${this.name}] Iteration ${iteration}: SUCCESS (${result.responseTime}ms)`);
    } else {
      console.error(`[${this.name}] Iteration ${iteration}: FAILED - ${result.error}`);
    }
  }
}

// 具体测试场景实现
class UserManagementScenario extends BaseScenario {
  constructor(httpClient) {
    super('UserManagement', httpClient);
  }
  
  async execute(iteration) {
    const userData = {
      username: `testuser_${iteration}_${Date.now()}`,
      email: `testuser_${iteration}@example.com`,
      password: 'SecurePassword123!'
    };
    
    // 1. 创建用户
    const createResult = await this.httpClient.request('POST', '/post', userData);
    
    if (!this.validateResponse(createResult, 200)) {
      return { ...createResult, step: 'user_creation' };
    }
    
    sleep(0.5);
    
    // 2. 获取用户信息
    const getUserResult = await this.httpClient.request('GET', '/get');
    
    if (!this.validateResponse(getUserResult, 200)) {
      return { ...getUserResult, step: 'get_user' };
    }
    
    sleep(0.5);
    
    // 3. 更新用户信息
    const updateData = { updated: true, timestamp: Date.now() };
    const updateResult = await this.httpClient.request('PUT', '/put', updateData);
    
    if (!this.validateResponse(updateResult, 200)) {
      return { ...updateResult, step: 'update_user' };
    }
    
    return { success: true, responseTime: createResult.responseTime + getUserResult.responseTime + updateResult.responseTime };
  }
}

class ProductCatalogScenario extends BaseScenario {
  constructor(httpClient) {
    super('ProductCatalog', httpClient);
  }
  
  async execute(iteration) {
    // 1. 获取产品列表
    const listResult = await this.httpClient.request('GET', '/get');
    
    if (!this.validateResponse(listResult, 200)) {
      return { ...listResult, step: 'list_products' };
    }
    
    sleep(0.3);
    
    // 2. 搜索产品
    const searchData = { query: `product_${iteration}` };
    const searchResult = await this.httpClient.request('POST', '/post', searchData);
    
    if (!this.validateResponse(searchResult, 200)) {
      return { ...searchResult, step: 'search_products' };
    }
    
    sleep(0.3);
    
    // 3. 获取产品详情
    const detailResult = await this.httpClient.request('GET', `/get?product_id=${iteration}`);
    
    if (!this.validateResponse(detailResult, 200)) {
      return { ...detailResult, step: 'product_detail' };
    }
    
    return { success: true, responseTime: listResult.responseTime + searchResult.responseTime + detailResult.responseTime };
  }
}

class OrderProcessingScenario extends BaseScenario {
  constructor(httpClient) {
    super('OrderProcessing', httpClient);
  }
  
  async execute(iteration) {
    const orderData = {
      items: [
        { productId: iteration, quantity: 1, price: 99.99 },
        { productId: iteration + 1, quantity: 2, price: 49.99 }
      ],
      total: 199.97,
      customerId: `customer_${iteration}`
    };
    
    // 1. 创建订单
    const createResult = await this.httpClient.request('POST', '/post', orderData);
    
    if (!this.validateResponse(createResult, 200)) {
      return { ...createResult, step: 'create_order' };
    }
    
    sleep(0.5);
    
    // 2. 支付订单
    const paymentData = { orderId: iteration, amount: orderData.total, method: 'credit_card' };
    const paymentResult = await this.httpClient.request('POST', '/post', paymentData);
    
    if (!this.validateResponse(paymentResult, 200)) {
      return { ...paymentResult, step: 'process_payment' };
    }
    
    sleep(0.5);
    
    // 3. 确认订单
    const confirmResult = await this.httpClient.request('PUT', '/put', { status: 'confirmed' };
    
    if (!this.validateResponse(confirmResult, 200)) {
      return { ...confirmResult, step: 'confirm_order' };
    }
    
    return { success: true, responseTime: createResult.responseTime + paymentResult.responseTime + confirmResult.responseTime };
  }
}

// 生产环境配置
export const options = {
  scenarios: {
    smoke_test: {
      executor: 'constant-vus',
      vus: 1,
      duration: '1m',
      gracefulStop: '30s',
      tags: { test_type: 'smoke' },
    },
    load_test: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '2m', target: 10 },  // 逐步增加
        { duration: '3m', target: 10 },  // 保持稳定
        { duration: '2m', target: 0 },   // 逐步减少
      ],
      gracefulRampDown: '30s',
      tags: { test_type: 'load' },
    },
    stress_test: {
      executor: 'ramping-arrival-rate',
      startRate: 10,
      timeUnit: '1s',
      preAllocatedVUs: 5,
      maxVUs: 50,
      stages: [
        { duration: '2m', target: 50 },   // 逐步增加
        { duration: '3m', target: 50 },   // 保持稳定
        { duration: '1m', target: 10 },   // 逐步减少
      ],
      tags: { test_type: 'stress' },
    },
  },
  
  thresholds: {
    // 全局阈值
    http_req_duration: ['p(95)<2000', 'p(99)<5000'],
    http_req_failed: ['rate<0.01'],  // 错误率小于1%
    
    // 自定义指标阈值
    'successful_transactions': ['count>100'],
    'transaction_rate': ['rate>0.95'],  // 成功率大于95%
    'error_rate': ['rate<0.05'],
    'response_time_trend': ['p(95)<1500'],
  },
  
  discardResponseBodies: false,
  
  // 性能优化
  noConnectionReuse: false,
  batch: 20,
  
  // 环境变量
  env: {
    ENV: ENV,
    BASE_URL: BASE_URL,
  },
};

// 全局测试管理器
const httpClient = new ProductionHttpClient(BASE_URL, API_KEY);
const scenarioManager = new TestScenarioManager();

// 注册测试场景
scenarioManager.registerScenario('user_management', new UserManagementScenario(httpClient));
scenarioManager.registerScenario('product_catalog', new ProductCatalogScenario(httpClient));
scenarioManager.registerScenario('order_processing', new OrderProcessingScenario(httpClient));

export default function () {
  // 根据测试类型执行不同的场景组合
  const testType = __ENV.TEST_TYPE || 'load';
  
  let scenarioConfig;
  
  switch (testType) {
    case 'smoke':
      scenarioConfig = { iterations: 1 };
      break;
    case 'load':
      scenarioConfig = { iterations: 3 };
      break;
    case 'stress':
      scenarioConfig = { iterations: 5 };
      break;
    default:
      scenarioConfig = { iterations: 2 };
  }
  
  // 并行执行所有场景
  const scenarios = ['user_management', 'product_catalog', 'order_processing'];
  
  scenarios.forEach(async (scenarioName) => {
    await scenarioManager.runScenario(scenarioName, scenarioConfig.iterations);
  });
  
  // 记录吞吐量
  customMetrics.throughputGauge.add(__VU);
}

// 测试结束后的报告生成
export function handleSummary(data) {
  const summary = scenarioManager.getSummary();
  
  // 生成HTML报告
  const htmlReportContent = htmlReport(data);
  
  // 自定义报告内容
  const customSummary = {
    'production_test_summary.json': JSON.stringify({
      timestamp: new Date().toISOString(),
      environment: ENV,
      test_duration: data.state.testRunDurationMs,
      vus: data.metrics.vus.values,
      ...summary,
      custom_metrics: {
        successful_transactions: customMetrics.successfulTransactions,
        failed_transactions: customMetrics.failedTransactions,
        average_response_time: customMetrics.responseTimeTrend.values.avg,
      }
    }, null, 2),
    'production_test_report.html': htmlReportContent,
  };
  
  return customSummary;
}

// 测试环境检查
export function setup() {
  console.log(`=== 生产环境性能测试 ===`);
  console.log(`环境: ${ENV}`);
  console.log(`目标URL: ${BASE_URL}`);
  console.log(`开始时间: ${new Date().toISOString()}`);
  
  // 环境验证
  if (!BASE_URL.startsWith('https://')) {
    console.warn('⚠ 警告: 生产环境测试应使用HTTPS');
  }
  
  if (ENV === 'production' && BASE_URL.includes('test')) {
    console.warn('⚠ 警告: 生产环境不应使用测试URL');
  }
  
  return { environment: ENV, baseUrl: BASE_URL, startTime: Date.now() };
}

// 测试清理
export function teardown(data) {
  const duration = Date.now() - data.startTime;
  const summary = scenarioManager.getSummary();
  
  console.log(`\n=== 测试完成 ===`);
  console.log(`总运行时间: ${(duration / 1000).toFixed(2)}秒`);
  console.log(`测试场景数: ${summary.totalScenarios}`);
  console.log(`总迭代次数: ${summary.totalIterations}`);
  console.log(`成功率: ${(summary.successRate * 100).toFixed(2)}%`);
  
  if (summary.successRate < 0.95) {
    console.error('❌ 测试失败: 成功率低于95%阈值');
  } else {
    console.log('✅ 测试通过: 所有指标符合预期');
  }
}
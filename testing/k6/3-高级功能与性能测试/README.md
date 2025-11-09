# 第3章：k6高级功能与性能测试

## 3.1 自定义指标（Metrics）

### 内置指标类型

k6提供了多种内置指标类型，可以满足不同的监控需求：

```javascript
import { Counter, Gauge, Rate, Trend } from 'k6/metrics';

// 计数器 - 用于计数
const myCounter = new Counter('my_counter');

// 仪表 - 用于记录当前值
const myGauge = new Gauge('my_gauge');

// 比率 - 用于记录成功率等比率
const myRate = new Rate('my_rate');

// 趋势 - 用于记录数值分布（如响应时间）
const myTrend = new Trend('my_trend');

// 使用自定义指标
export default function () {
  // 计数器：每次调用加1
  myCounter.add(1);
  
  // 仪表：记录当前活跃用户数
  myGauge.add(__VU);
  
  // 比率：记录请求是否成功
  const response = http.get('https://httpbin.test.k6.io/get');
  myRate.add(response.status === 200);
  
  // 趋势：记录响应时间
  myTrend.add(response.timings.duration);
}
```

### 自定义指标最佳实践

```javascript
import { Counter, Trend } from 'k6/metrics';

// 业务指标
const businessTransactions = new Counter('business_transactions');
const apiResponseTimes = new Trend('api_response_times', true); // true启用时间戳

// 错误指标
const errorCount = new Counter('error_count');
const errorTypes = new Counter('error_types');

export default function () {
  try {
    // 业务操作1
    const response1 = http.get('https://api.example.com/order');
    businessTransactions.add(1, { type: 'get_order' });
    apiResponseTimes.add(response1.timings.duration, { endpoint: '/order' });
    
    // 业务操作2
    const response2 = http.post('https://api.example.com/order', {});
    businessTransactions.add(1, { type: 'create_order' });
    apiResponseTimes.add(response2.timings.duration, { endpoint: '/order' });
    
  } catch (error) {
    errorCount.add(1);
    errorTypes.add(1, { error_type: error.name });
  }
}
```

## 3.2 场景（Scenarios）和执行器（Executors）

### 复杂场景配置

```javascript
export const options = {
  scenarios: {
    // 场景1：烟雾测试
    smoke_test: {
      executor: 'shared-iterations',
      vus: 1,
      iterations: 10,
      maxDuration: '5m',
      exec: 'smokeTest', // 指定执行的函数
      tags: { test_type: 'smoke' },
    },
    
    // 场景2：负载测试
    load_test: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 50 },
        { duration: '5m', target: 50 },
        { duration: '2m', target: 0 },
      ],
      gracefulRampDown: '30s',
      exec: 'loadTest',
      tags: { test_type: 'load' },
    },
    
    // 场景3：压力测试
    stress_test: {
      executor: 'constant-arrival-rate',
      rate: 100,
      timeUnit: '1s',
      duration: '10m',
      preAllocatedVUs: 50,
      maxVUs: 200,
      exec: 'stressTest',
      tags: { test_type: 'stress' },
    },
  },
  
  thresholds: {
    // 针对不同场景设置不同阈值
    'http_req_duration{scenario:smoke_test}': ['p(95)<500'],
    'http_req_duration{scenario:load_test}': ['p(95)<1000'],
    'http_req_duration{scenario:stress_test}': ['p(95)<2000'],
  },
};

// 场景专用函数
export function smokeTest() {
  // 简单功能验证
  const response = http.get('https://api.example.com/health');
  check(response, { 'health check passed': (r) => r.status === 200 });
}

export function loadTest() {
  // 正常负载测试
  const response = http.get('https://api.example.com/api/v1/users');
  check(response, { 'users api working': (r) => r.status === 200 });
}

export function stressTest() {
  // 高压测试
  const response = http.get('https://api.example.com/api/v1/complex-query');
  check(response, { 'complex query working': (r) => r.status === 200 });
}
```

### 执行器类型详解

| 执行器 | 用途 | 适用场景 |
|--------|------|----------|
| shared-iterations | 共享迭代 | 功能测试 |
| per-vu-iterations | 每VU独立迭代 | 并发测试 |
| constant-vus | 固定VU数 | 稳定性测试 |
| ramping-vus | 渐变VU数 | 负载测试 |
| constant-arrival-rate | 固定到达率 | 压力测试 |
| ramping-arrival-rate | 渐变到达率 | 尖峰测试 |
| externally-controlled | 外部控制 | 分布式测试 |

## 3.3 测试数据管理

### 外部数据文件

```javascript
import { SharedArray } from 'k6/data';

// 使用CSV文件
const users = new SharedArray('users', function () {
  return open('./data/users.csv').split('\n').slice(1).map(line => {
    const [id, username, email] = line.split(',');
    return { id: parseInt(id), username, email };
  });
});

// 使用JSON文件
const testData = new SharedArray('test_data', function () {
  return JSON.parse(open('./data/test-data.json'));
});

export default function () {
  // 从共享数组中随机选择数据
  const user = users[Math.floor(Math.random() * users.length)];
  
  // 使用测试数据
  const response = http.post('https://api.example.com/login', {
    username: user.username,
    email: user.email,
  });
}
```

### 动态数据生成

```javascript
import { faker } from 'https://cdnjs.cloudflare.com/ajax/libs/Faker/3.1.0/faker.min.js';

// 自定义数据生成器
function generateUser() {
  return {
    firstName: faker.name.firstName(),
    lastName: faker.name.lastName(),
    email: faker.internet.email(),
    phone: faker.phone.phoneNumber(),
    address: {
      street: faker.address.streetAddress(),
      city: faker.address.city(),
      zipCode: faker.address.zipCode(),
    },
  };
}

function generateProduct() {
  return {
    name: faker.commerce.productName(),
    price: faker.commerce.price(10, 1000, 2),
    category: faker.commerce.department(),
    description: faker.lorem.sentence(),
  };
}

export default function () {
  // 生成测试数据
  const user = generateUser();
  const product = generateProduct();
  
  // 使用生成的数据进行测试
  const createUserResponse = http.post('https://api.example.com/users', user);
  const createProductResponse = http.post('https://api.example.com/products', product);
}
```

## 3.4 性能测试类型

### 负载测试（Load Testing）

```javascript
// 负载测试：验证系统在正常负载下的性能
export const options = {
  scenarios: {
    load_test: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '5m', target: 100 },  // 5分钟增加到100用户
        { duration: '30m', target: 100 }, // 保持30分钟
        { duration: '5m', target: 0 },    // 5分钟减少到0
      ],
      gracefulRampDown: '0s',
    },
  },
  
  thresholds: {
    http_req_duration: ['p(95)<1000'],
    http_req_failed: ['rate<0.01'],
    'iteration_duration{scenario:load_test}': ['p(95)<5000'],
  },
};

export default function () {
  // 模拟真实用户行为
  group('browse_products', function () {
    const products = http.get('https://api.example.com/products');
    sleep(Math.random() * 3 + 1); // 随机等待1-4秒
  });
  
  group('view_product_details', function () {
    const productId = Math.floor(Math.random() * 1000) + 1;
    const details = http.get(`https://api.example.com/products/${productId}`);
    sleep(Math.random() * 2 + 1); // 随机等待1-3秒
  });
  
  group('add_to_cart', function () {
    const cartResponse = http.post('https://api.example.com/cart', {
      productId: Math.floor(Math.random() * 1000) + 1,
      quantity: Math.floor(Math.random() * 3) + 1,
    });
    sleep(1);
  });
}
```

### 压力测试（Stress Testing）

```javascript
// 压力测试：验证系统在极限负载下的表现
export const options = {
  scenarios: {
    stress_test: {
      executor: 'ramping-arrival-rate',
      startRate: 10,
      timeUnit: '1s',
      preAllocatedVUs: 50,
      maxVUs: 500,
      stages: [
        { target: 50, duration: '2m' },   // 2分钟增加到50请求/秒
        { target: 100, duration: '2m' },  // 2分钟增加到100请求/秒
        { target: 200, duration: '2m' },  // 2分钟增加到200请求/秒
        { target: 500, duration: '5m' },  // 保持500请求/秒5分钟
        { target: 0, duration: '2m' },    // 2分钟减少到0
      ],
    },
  },
  
  thresholds: {
    http_req_duration: ['p(95)<5000'], // 压力测试允许更长的响应时间
    http_req_failed: ['rate<0.05'],    // 允许更高的失败率
  },
};

export default function () {
  // 高压力场景：频繁的API调用
  const endpoints = [
    '/api/v1/search',
    '/api/v1/products',
    '/api/v1/users',
    '/api/v1/orders',
  ];
  
  const endpoint = endpoints[Math.floor(Math.random() * endpoints.length)];
  const response = http.get(`https://api.example.com${endpoint}`);
  
  // 记录压力测试特定指标
  if (response.status !== 200) {
    console.log(`Stress test failure: ${endpoint} returned ${response.status}`);
  }
}
```

### 尖峰测试（Spike Testing）

```javascript
// 尖峰测试：验证系统对突然流量激增的处理能力
export const options = {
  scenarios: {
    spike_test: {
      executor: 'constant-arrival-rate',
      rate: 1000, // 突然增加到1000请求/秒
      timeUnit: '1s',
      duration: '2m',      // 持续2分钟
      preAllocatedVUs: 200,
      maxVUs: 1000,
    },
  },
  
  thresholds: {
    http_req_duration: ['p(95)<3000'],
    http_req_failed: ['rate<0.1'], // 尖峰测试允许更高的失败率
  },
};

export default function () {
  // 模拟尖峰场景：所有用户同时执行相同操作
  const response = http.get('https://api.example.com/flash-sale');
  
  check(response, {
    'flash sale accessible': (r) => r.status === 200,
    'response contains sale items': (r) => {
      const data = r.json();
      return data.items && data.items.length > 0;
    },
  });
}
```

## 3.5 高级错误处理

### 重试机制

```javascript
function httpRequestWithRetry(url, options = {}, maxRetries = 3) {
  let attempts = 0;
  
  while (attempts < maxRetries) {
    try {
      const response = http.get(url, options);
      
      if (response.status >= 200 && response.status < 300) {
        return response;
      }
      
      // 如果是服务器错误，重试
      if (response.status >= 500) {
        attempts++;
        sleep(Math.pow(2, attempts)); // 指数退避
        continue;
      }
      
      // 客户端错误，不重试
      return response;
      
    } catch (error) {
      attempts++;
      if (attempts >= maxRetries) {
        throw error;
      }
      sleep(Math.pow(2, attempts)); // 指数退避
    }
  }
  
  throw new Error(`Max retries (${maxRetries}) exceeded`);
}

export default function () {
  try {
    const response = httpRequestWithRetry('https://api.example.com/unstable-endpoint');
    check(response, { 'request succeeded after retry': (r) => r.status === 200 });
    
  } catch (error) {
    console.log(`Request failed after retries: ${error.message}`);
    // 记录失败指标
  }
}
```

### 断路器模式

```javascript
class CircuitBreaker {
  constructor(failureThreshold = 5, timeout = 60000) {
    this.failureThreshold = failureThreshold;
    this.timeout = timeout;
    this.failureCount = 0;
    this.lastFailureTime = null;
    this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
  }
  
  async call(url, options) {
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFailureTime > this.timeout) {
        this.state = 'HALF_OPEN';
      } else {
        throw new Error('Circuit breaker is OPEN');
      }
    }
    
    try {
      const response = http.get(url, options);
      
      if (response.status >= 200 && response.status < 300) {
        this.success();
        return response;
      } else {
        this.failure();
        return response;
      }
      
    } catch (error) {
      this.failure();
      throw error;
    }
  }
  
  success() {
    this.failureCount = 0;
    if (this.state === 'HALF_OPEN') {
      this.state = 'CLOSED';
    }
  }
  
  failure() {
    this.failureCount++;
    this.lastFailureTime = Date.now();
    
    if (this.failureCount >= this.failureThreshold) {
      this.state = 'OPEN';
    }
  }
}

// 使用断路器
const breaker = new CircuitBreaker();

export default function () {
  try {
    const response = await breaker.call('https://api.example.com/unstable-api');
    check(response, { 'circuit breaker protected call': (r) => r.status === 200 });
    
  } catch (error) {
    console.log(`Circuit breaker prevented call: ${error.message}`);
  }
}
```

## 3.6 实验：综合性能测试场景

### 实验目标
创建一个综合的电商网站性能测试场景，包含多种用户行为模式。

### 实验代码

```javascript
// 实验3：电商网站综合性能测试
import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// 自定义指标
const successRate = new Rate('success_rate');
const transactionTime = new Trend('transaction_time');
const errorCount = new Counter('error_count');

const BASE_URL = 'https://httpbin.test.k6.io';

// 测试配置
export const options = {
  scenarios: {
    // 浏览型用户（80%流量）
    browser_users: {
      executor: 'constant-vus',
      vus: 40,
      duration: '10m',
      exec: 'browseBehavior',
      tags: { user_type: 'browser' },
    },
    
    // 购买型用户（15%流量）
    buyer_users: {
      executor: 'constant-arrival-rate',
      rate: 2,
      timeUnit: '1s',
      duration: '10m',
      preAllocatedVUs: 10,
      maxVUs: 20,
      exec: 'buyerBehavior',
      tags: { user_type: 'buyer' },
    },
    
    // 搜索型用户（5%流量）
    searcher_users: {
      executor: 'per-vu-iterations',
      vus: 5,
      iterations: 20,
      maxDuration: '10m',
      exec: 'searcherBehavior',
      tags: { user_type: 'searcher' },
    },
  },
  
  thresholds: {
    // 全局阈值
    http_req_duration: ['p(95)<2000'],
    http_req_failed: ['rate<0.05'],
    
    // 用户类型特定阈值
    'http_req_duration{user_type:browser}': ['p(95)<1500'],
    'http_req_duration{user_type:buyer}': ['p(95)<3000'],
    'http_req_duration{user_type:searcher}': ['p(95)<1000'],
    
    // 自定义指标阈值
    success_rate: ['rate>0.95'],
    'transaction_time{user_type:buyer}': ['p(95)<5000'],
  },
};

// 浏览型用户行为
export function browseBehavior() {
  group('browse_website', function () {
    // 浏览首页
    const homeResponse = http.get(`${BASE_URL}/get`);
    check(homeResponse, { 'homepage loaded': (r) => r.status === 200 });
    successRate.add(homeResponse.status === 200);
    sleep(Math.random() * 5 + 2); // 浏览2-7秒
    
    // 浏览产品列表
    const productsResponse = http.get(`${BASE_URL}/get?page=products`);
    check(productsResponse, { 'products page loaded': (r) => r.status === 200 });
    successRate.add(productsResponse.status === 200);
    sleep(Math.random() * 10 + 5); // 浏览5-15秒
    
    // 查看随机产品详情
    const productId = Math.floor(Math.random() * 100) + 1;
    const productResponse = http.get(`${BASE_URL}/get?product=${productId}`);
    check(productResponse, { 'product page loaded': (r) => r.status === 200 });
    successRate.add(productResponse.status === 200);
    sleep(Math.random() * 8 + 3); // 浏览3-11秒
  });
}

// 购买型用户行为
export function buyerBehavior() {
  const startTime = Date.now();
  
  group('purchase_flow', function () {
    try {
      // 搜索产品
      const searchResponse = http.get(`${BASE_URL}/get?q=test+product`);
      check(searchResponse, { 'search successful': (r) => r.status === 200 });
      sleep(1);
      
      // 查看产品详情
      const productResponse = http.get(`${BASE_URL}/get?product=123`);
      check(productResponse, { 'product details loaded': (r) => r.status === 200 });
      sleep(2);
      
      // 添加到购物车
      const cartResponse = http.post(`${BASE_URL}/post`, {
        productId: 123,
        quantity: 1,
      });
      check(cartResponse, { 'item added to cart': (r) => r.status === 200 });
      sleep(1);
      
      // 查看购物车
      const cartViewResponse = http.get(`${BASE_URL}/get?cart=view`);
      check(cartViewResponse, { 'cart viewed': (r) => r.status === 200 });
      sleep(1);
      
      // 结算
      const checkoutResponse = http.post(`${BASE_URL}/post`, {
        paymentMethod: 'credit_card',
        shippingAddress: 'test address',
      });
      check(checkoutResponse, { 'checkout successful': (r) => r.status === 200 });
      
      // 记录交易时间
      const endTime = Date.now();
      transactionTime.add(endTime - startTime, { user_type: 'buyer' });
      successRate.add(true);
      
    } catch (error) {
      errorCount.add(1);
      successRate.add(false);
      console.log(`Purchase flow failed: ${error.message}`);
    }
  });
}

// 搜索型用户行为
export function searcherBehavior() {
  group('search_behavior', function () {
    // 执行多个搜索
    const searchTerms = ['laptop', 'phone', 'tablet', 'accessories'];
    
    searchTerms.forEach(term => {
      const searchResponse = http.get(`${BASE_URL}/get?q=${term}`);
      check(searchResponse, { 
        [`search for ${term} successful`]: (r) => r.status === 200 
      });
      successRate.add(searchResponse.status === 200);
      sleep(Math.random() * 2 + 1); // 等待1-3秒
    });
    
    // 高级搜索
    const advancedSearchResponse = http.post(`${BASE_URL}/post`, {
      category: 'electronics',
      priceRange: '100-500',
      brand: 'test brand',
    });
    check(advancedSearchResponse, { 'advanced search successful': (r) => r.status === 200 });
    successRate.add(advancedSearchResponse.status === 200);
  });
}

// 设置和清理
export function setup() {
  console.log('Setting up test data...');
  return { testData: 'ready' };
}

export function teardown(data) {
  console.log('Test completed. Performing cleanup...');
}
```

### 实验结果分析

1. **用户行为分析**：比较不同类型用户的性能表现
2. **系统瓶颈识别**：找出响应时间最长的操作
3. **容量规划**：基于测试结果评估系统容量需求
4. **优化建议**：提出具体的性能优化建议

## 总结

本章我们深入学习了：
- 自定义指标的使用和最佳实践
- 复杂场景配置和执行器选择
- 测试数据管理策略
- 各种性能测试类型的设计和实施
- 高级错误处理机制

下一章我们将学习k6在生产环境中的最佳实践和部署策略。
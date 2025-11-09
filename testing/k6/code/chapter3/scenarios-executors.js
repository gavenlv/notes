// 第3章：场景和执行器示例
// 演示各种执行器和复杂场景配置

import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = 'https://httpbin.test.k6.io';

// 复杂场景配置
export const options = {
  scenarios: {
    // 场景1：烟雾测试 - 验证基本功能
    smoke_test: {
      executor: 'shared-iterations',
      vus: 1,
      iterations: 10,
      maxDuration: '5m',
      exec: 'smokeTest',
      tags: { 
        test_type: 'smoke',
        priority: 'high'
      },
    },
    
    // 场景2：负载测试 - 正常负载下的性能
    load_test: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 50 },   // 2分钟增加到50用户
        { duration: '5m', target: 50 },   // 保持50用户5分钟
        { duration: '2m', target: 0 },     // 2分钟减少到0用户
      ],
      gracefulRampDown: '30s',
      exec: 'loadTest',
      tags: { 
        test_type: 'load',
        priority: 'medium'
      },
    },
    
    // 场景3：压力测试 - 极限负载下的表现
    stress_test: {
      executor: 'constant-arrival-rate',
      rate: 100,
      timeUnit: '1s',
      duration: '10m',
      preAllocatedVUs: 50,
      maxVUs: 200,
      exec: 'stressTest',
      tags: { 
        test_type: 'stress',
        priority: 'low'
      },
    },
    
    // 场景4：尖峰测试 - 突然流量激增
    spike_test: {
      executor: 'ramping-arrival-rate',
      startRate: 10,
      timeUnit: '1s',
      stages: [
        { target: 500, duration: '1m' },  // 1分钟增加到500请求/秒
        { target: 500, duration: '3m' },  // 保持3分钟
        { target: 0, duration: '1m' },    // 1分钟减少到0
      ],
      preAllocatedVUs: 100,
      maxVUs: 500,
      exec: 'spikeTest',
      tags: { 
        test_type: 'spike',
        priority: 'medium'
      },
    },
    
    // 场景5：浸泡测试 - 长时间运行稳定性
    soak_test: {
      executor: 'constant-vus',
      vus: 20,
      duration: '2h',
      exec: 'soakTest',
      tags: { 
        test_type: 'soak',
        priority: 'low'
      },
    },
  },
  
  // 全局阈值
  thresholds: {
    http_req_duration: ['p(95)<2000'],
    http_req_failed: ['rate<0.05'],
    
    // 场景特定阈值
    'http_req_duration{scenario:smoke_test}': ['p(95)<500'],
    'http_req_duration{scenario:load_test}': ['p(95)<1000'],
    'http_req_duration{scenario:stress_test}': ['p(95)<5000'],
    'http_req_duration{scenario:spike_test}': ['p(95)<3000'],
    'http_req_duration{scenario:soak_test}': ['p(95)<1500'],
    
    'http_req_failed{scenario:smoke_test}': ['rate<0.01'],
    'http_req_failed{scenario:load_test}': ['rate<0.02'],
    'http_req_failed{scenario:stress_test}': ['rate<0.1'],
    'http_req_failed{scenario:spike_test}': ['rate<0.05'],
    'http_req_failed{scenario:soak_test}': ['rate<0.01'],
  },
  
  // 其他配置
  noConnectionReuse: false,
  userAgent: 'k6-scenario-test/1.0',
};

// 烟雾测试函数
export function smokeTest() {
  console.log('Running smoke test - basic functionality verification');
  
  // 基本健康检查
  const healthResponse = http.get(`${BASE_URL}/status/200`);
  check(healthResponse, {
    'health check passed': (r) => r.status === 200,
    'response time acceptable': (r) => r.timings.duration < 1000,
  });
  
  // 基本API功能测试
  const apiResponse = http.get(`${BASE_URL}/get`);
  check(apiResponse, {
    'api basic functionality': (r) => r.status === 200,
    'response contains data': (r) => r.json().url !== undefined,
  });
  
  sleep(1);
}

// 负载测试函数
export function loadTest() {
  console.log('Running load test - normal load performance');
  
  // 模拟正常用户行为
  const endpoints = [
    '/get',
    '/post',
    '/put',
    '/delete'
  ];
  
  const randomEndpoint = endpoints[Math.floor(Math.random() * endpoints.length)];
  
  let response;
  if (randomEndpoint === '/post' || randomEndpoint === '/put') {
    const data = {
      test: 'load test data',
      timestamp: Date.now(),
      user: `user_${Math.floor(Math.random() * 1000)}`
    };
    response = http.post(`${BASE_URL}${randomEndpoint}`, data);
  } else {
    response = http.get(`${BASE_URL}${randomEndpoint}`);
  }
  
  check(response, {
    'load test request successful': (r) => r.status === 200,
    'reasonable response time': (r) => r.timings.duration < 2000,
  });
  
  // 模拟用户思考时间
  sleep(Math.random() * 3 + 1);
}

// 压力测试函数
export function stressTest() {
  console.log('Running stress test - extreme load conditions');
  
  // 高压力场景：频繁的API调用
  const complexEndpoints = [
    '/delay/1',      // 1秒延迟
    '/delay/2',      // 2秒延迟
    '/bytes/1024',   // 1KB数据
    '/bytes/2048',   // 2KB数据
  ];
  
  const endpoint = complexEndpoints[Math.floor(Math.random() * complexEndpoints.length)];
  
  const response = http.get(`${BASE_URL}${endpoint}`);
  
  // 压力测试允许更高的失败率和更长的响应时间
  check(response, {
    'stress test request completed': (r) => r.status >= 200 && r.status < 500,
    'extreme condition handled': (r) => r.timings.duration < 10000,
  });
  
  // 较短的等待时间以增加压力
  sleep(Math.random() * 0.5);
}

// 尖峰测试函数
export function spikeTest() {
  console.log('Running spike test - sudden traffic spike');
  
  // 模拟突然的大量请求
  const responses = http.batch([
    ['GET', `${BASE_URL}/get`],
    ['GET', `${BASE_URL}/status/200`],
    ['GET', `${BASE_URL}/status/404`],
  ]);
  
  // 检查批量请求的结果
  responses.forEach((response, index) => {
    check(response, {
      [`spike test request ${index} handled`]: (r) => r.status !== 0,
    });
  });
  
  // 非常短的等待时间模拟尖峰流量
  sleep(Math.random() * 0.2);
}

// 浸泡测试函数
export function soakTest() {
  console.log('Running soak test - long-term stability');
  
  // 长时间运行的稳定性测试
  const soakEndpoints = [
    '/get',
    '/status/200',
    '/status/201',
    '/status/204',
  ];
  
  const endpoint = soakEndpoints[Math.floor(Math.random() * soakEndpoints.length)];
  
  const response = http.get(`${BASE_URL}${endpoint}`);
  
  // 浸泡测试关注稳定性和资源使用
  check(response, {
    'soak test stability': (r) => r.status === 200,
    'consistent response time': (r) => r.timings.duration < 3000,
  });
  
  // 正常的用户思考时间
  sleep(Math.random() * 5 + 2);
}

// 自定义执行器示例
function createCustomExecutor() {
  // 这里可以创建自定义的执行逻辑
  // 例如基于业务指标的动态调整
  
  return {
    execute: function(testFunction) {
      // 自定义执行逻辑
      const startTime = Date.now();
      
      try {
        testFunction();
        const endTime = Date.now();
        
        // 记录执行指标
        console.log(`Custom executor completed in ${endTime - startTime}ms`);
        
      } catch (error) {
        console.error('Custom executor error:', error);
      }
    }
  };
}

// 使用自定义执行器
export function customExecutorTest() {
  const executor = createCustomExecutor();
  
  executor.execute(function() {
    const response = http.get(`${BASE_URL}/get`);
    check(response, { 'custom executor test': (r) => r.status === 200 });
  });
}
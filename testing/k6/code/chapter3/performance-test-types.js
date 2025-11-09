// 第3章：性能测试类型示例
// 演示各种性能测试类型的设计和实施

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';

const BASE_URL = 'https://httpbin.test.k6.io';

// 自定义指标用于不同类型的测试
const loadTestMetrics = {
  successfulRequests: new Counter('load_successful_requests'),
  failedRequests: new Counter('load_failed_requests'),
  responseTimes: new Trend('load_response_times'),
  errorRate: new Rate('load_error_rate')
};

const stressTestMetrics = {
  successfulRequests: new Counter('stress_successful_requests'),
  failedRequests: new Counter('stress_failed_requests'),
  responseTimes: new Trend('stress_response_times'),
  timeoutCount: new Counter('stress_timeout_count')
};

const spikeTestMetrics = {
  successfulRequests: new Counter('spike_successful_requests'),
  failedRequests: new Counter('spike_failed_requests'),
  peakResponseTimes: new Trend('spike_peak_response_times'),
  recoveryTime: new Trend('spike_recovery_time')
};

const soakTestMetrics = {
  successfulRequests: new Counter('soak_successful_requests'),
  memoryUsage: new Trend('soak_memory_usage'),
  throughput: new Trend('soak_throughput'),
  stabilityRate: new Rate('soak_stability_rate')
};

// 1. 负载测试配置
export const options_load = {
  scenarios: {
    load_test: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 50 },   // 2分钟增加到50用户
        { duration: '5m', target: 50 },   // 保持50用户5分钟
        { duration: '2m', target: 0 },    // 2分钟减少到0用户
      ],
      gracefulRampDown: '30s',
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<1000'],
    http_req_failed: ['rate<0.01'],
    'load_error_rate': ['rate<0.05'],
  },
};

// 负载测试函数
export function loadTest() {
  console.log('Running load test - normal operating conditions');
  
  const startTime = Date.now();
  
  // 模拟正常用户行为
  const userActions = [
    'browse_homepage',
    'search_products', 
    'view_product_details',
    'add_to_cart',
    'view_cart'
  ];
  
  const action = userActions[Math.floor(Math.random() * userActions.length)];
  
  const response = http.get(`${BASE_URL}/get?action=${action}`);
  
  const responseTime = Date.now() - startTime;
  
  const success = check(response, {
    'load test request successful': (r) => r.status === 200,
    'reasonable response time': (r) => r.timings.duration < 2000,
  });
  
  // 记录负载测试指标
  if (success) {
    loadTestMetrics.successfulRequests.add(1);
    loadTestMetrics.responseTimes.add(responseTime);
    loadTestMetrics.errorRate.add(true);
  } else {
    loadTestMetrics.failedRequests.add(1);
    loadTestMetrics.errorRate.add(false);
  }
  
  // 模拟用户思考时间
  sleep(Math.random() * 3 + 1);
}

// 2. 压力测试配置
export const options_stress = {
  scenarios: {
    stress_test: {
      executor: 'constant-arrival-rate',
      rate: 200,
      timeUnit: '1s',
      duration: '10m',
      preAllocatedVUs: 100,
      maxVUs: 500,
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<5000'], // 允许更长的响应时间
    http_req_failed: ['rate<0.1'],     // 允许更高的失败率
  },
};

// 压力测试函数
export function stressTest() {
  console.log('Running stress test - extreme conditions');
  
  const startTime = Date.now();
  
  // 高压力场景：复杂的API调用
  const stressEndpoints = [
    '/delay/3',           // 3秒延迟
    '/bytes/4096',        // 4KB数据
    '/status/500',        // 服务器错误
    '/status/200',
    '/status/404'
  ];
  
  const endpoint = stressEndpoints[Math.floor(Math.random() * stressEndpoints.length)];
  
  const params = {
    timeout: '10s', // 更长的超时时间
  };
  
  const response = http.get(`${BASE_URL}${endpoint}`, params);
  
  const responseTime = Date.now() - startTime;
  
  // 压力测试的检查更加宽松
  const success = check(response, {
    'stress test request handled': (r) => r.status !== 0,
    'system under stress responded': (r) => r.timings.duration < 10000,
  });
  
  // 记录压力测试指标
  if (success) {
    stressTestMetrics.successfulRequests.add(1);
    stressTestMetrics.responseTimes.add(responseTime);
  } else {
    stressTestMetrics.failedRequests.add(1);
    if (response.timings.duration >= 10000) {
      stressTestMetrics.timeoutCount.add(1);
    }
  }
  
  // 非常短的等待时间以增加压力
  sleep(Math.random() * 0.5);
}

// 3. 尖峰测试配置
export const options_spike = {
  scenarios: {
    spike_test: {
      executor: 'ramping-arrival-rate',
      startRate: 10,
      timeUnit: '1s',
      stages: [
        { target: 1000, duration: '1m' },  // 1分钟增加到1000请求/秒
        { target: 1000, duration: '2m' },  // 保持2分钟
        { target: 10, duration: '1m' },    // 1分钟减少到10请求/秒
      ],
      preAllocatedVUs: 200,
      maxVUs: 1000,
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<3000'],
    http_req_failed: ['rate<0.2'], // 尖峰测试允许更高的失败率
  },
};

// 尖峰测试函数
export function spikeTest() {
  console.log('Running spike test - sudden traffic spike');
  
  const startTime = Date.now();
  
  // 模拟尖峰场景：大量用户同时执行相同操作
  const spikeActions = [
    'flash_sale',
    'product_launch', 
    'event_registration',
    'limited_offer'
  ];
  
  const action = spikeActions[Math.floor(Math.random() * spikeActions.length)];
  
  // 批量请求模拟并发
  const batchRequests = [
    ['GET', `${BASE_URL}/get?action=${action}`],
    ['GET', `${BASE_URL}/status/200`],
    ['GET', `${BASE_URL}/delay/1`]
  ];
  
  const responses = http.batch(batchRequests);
  
  const peakResponseTime = Date.now() - startTime;
  
  // 检查批量响应
  let successfulCount = 0;
  responses.forEach((response, index) => {
    const success = check(response, {
      [`spike batch request ${index} handled`]: (r) => r.status !== 0,
    });
    
    if (success) successfulCount++;
  });
  
  // 记录尖峰测试指标
  if (successfulCount === batchRequests.length) {
    spikeTestMetrics.successfulRequests.add(1);
  } else {
    spikeTestMetrics.failedRequests.add(1);
  }
  
  spikeTestMetrics.peakResponseTimes.add(peakResponseTime);
  
  // 测量恢复时间
  const recoveryStart = Date.now();
  const recoveryResponse = http.get(`${BASE_URL}/status/200`);
  const recoveryTime = Date.now() - recoveryStart;
  
  spikeTestMetrics.recoveryTime.add(recoveryTime);
  
  // 短暂的等待时间
  sleep(Math.random() * 0.2);
}

// 4. 浸泡测试配置
export const options_soak = {
  scenarios: {
    soak_test: {
      executor: 'constant-vus',
      vus: 20,
      duration: '2h', // 2小时浸泡测试
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<2000'],
    http_req_failed: ['rate<0.01'], // 浸泡测试要求高稳定性
  },
};

// 浸泡测试函数
export function soakTest() {
  console.log('Running soak test - long-term stability');
  
  const startTime = Date.now();
  
  // 长时间运行的稳定性测试
  const soakActions = [
    'health_check',
    'api_status',
    'data_query',
    'cache_check'
  ];
  
  const action = soakActions[Math.floor(Math.random() * soakActions.length)];
  
  const response = http.get(`${BASE_URL}/get?action=${action}`);
  
  const responseTime = Date.now() - startTime;
  
  // 浸泡测试关注稳定性和一致性
  const stability = check(response, {
    'soak test stability': (r) => r.status === 200,
    'consistent performance': (r) => {
      // 检查响应时间是否在合理范围内
      return r.timings.duration > 0 && r.timings.duration < 5000;
    },
    'data integrity': (r) => {
      // 简单的数据完整性检查
      return r.body && r.body.length > 0;
    }
  });
  
  // 记录浸泡测试指标
  if (stability) {
    soakTestMetrics.successfulRequests.add(1);
    soakTestMetrics.throughput.add(1);
    soakTestMetrics.stabilityRate.add(true);
    
    // 模拟内存使用监控（实际中需要通过其他方式获取）
    const simulatedMemoryUsage = Math.random() * 100 + 50; // 50-150 MB
    soakTestMetrics.memoryUsage.add(simulatedMemoryUsage);
  } else {
    soakTestMetrics.stabilityRate.add(false);
  }
  
  // 正常的操作间隔
  sleep(Math.random() * 10 + 5); // 5-15秒间隔
}

// 5. 综合测试：结合多种测试类型
function comprehensiveTest() {
  // 根据测试阶段执行不同的测试逻辑
  const testPhase = __VU < 10 ? 'load' : 
                   __VU < 30 ? 'stress' : 
                   'spike';
  
  switch (testPhase) {
    case 'load':
      loadTest();
      break;
    case 'stress':
      stressTest();
      break;
    case 'spike':
      spikeTest();
      break;
    default:
      soakTest();
  }
}

// 测试结果分析函数
function analyzeTestResults() {
  // 在实际环境中，这里可以连接到监控系统进行分析
  console.log('Analyzing test results...');
  
  // 模拟分析逻辑
  const analysis = {
    loadTest: {
      avgResponseTime: 'Calculating...',
      errorRate: 'Calculating...',
      recommendations: ['Optimize database queries', 'Add caching layer']
    },
    stressTest: {
      breakingPoint: 'Calculating...',
      recoveryTime: 'Calculating...',
      recommendations: ['Implement rate limiting', 'Add auto-scaling']
    },
    spikeTest: {
      peakPerformance: 'Calculating...',
      recoveryAbility: 'Calculating...',
      recommendations: ['Prepare for traffic spikes', 'Use CDN']
    },
    soakTest: {
      memoryLeaks: 'None detected',
      stability: 'High',
      recommendations: ['Monitor memory usage', 'Regular health checks']
    }
  };
  
  return analysis;
}

// 默认导出函数（用于简单测试）
export default function () {
  // 根据环境变量选择测试类型
  const testType = __ENV.TEST_TYPE || 'load';
  
  switch (testType) {
    case 'load':
      loadTest();
      break;
    case 'stress':
      stressTest();
      break;
    case 'spike':
      spikeTest();
      break;
    case 'soak':
      soakTest();
      break;
    default:
      comprehensiveTest();
  }
}
// 第3章：自定义指标示例
// 演示如何使用自定义指标进行高级监控

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Gauge, Rate, Trend } from 'k6/metrics';

// 创建自定义指标
const myCounter = new Counter('my_custom_counter');
const myGauge = new Gauge('my_custom_gauge');
const myRate = new Rate('my_custom_rate');
const myTrend = new Trend('my_custom_trend');

// 业务指标
const successfulTransactions = new Counter('successful_transactions');
const failedTransactions = new Counter('failed_transactions');
const transactionDuration = new Trend('transaction_duration', true); // 启用时间戳
const errorRate = new Rate('error_rate');

// API特定指标
const apiResponseTimes = new Trend('api_response_times');
const apiErrorCount = new Counter('api_error_count');
const apiSuccessRate = new Rate('api_success_rate');

const BASE_URL = 'https://httpbin.test.k6.io';

export const options = {
  vus: 10,
  duration: '2m',
  
  thresholds: {
    // 内置指标阈值
    http_req_duration: ['p(95)<1000'],
    http_req_failed: ['rate<0.01'],
    
    // 自定义指标阈值
    'successful_transactions': ['count>100'],
    'failed_transactions': ['count<5'],
    'error_rate': ['rate<0.05'],
    'transaction_duration': ['p(95)<2000'],
    'api_success_rate': ['rate>0.95'],
  },
};

export default function () {
  const transactionStart = Date.now();
  
  try {
    // 业务操作1：获取用户信息
    const userResponse = http.get(`${BASE_URL}/get?action=user`);
    
    // 记录API指标
    apiResponseTimes.add(userResponse.timings.duration);
    
    const userCheck = check(userResponse, {
      'user api success': (r) => r.status === 200,
    });
    
    apiSuccessRate.add(userCheck);
    if (!userCheck) {
      apiErrorCount.add(1);
    }
    
    // 业务操作2：获取产品列表
    const productsResponse = http.get(`${BASE_URL}/get?action=products`);
    
    apiResponseTimes.add(productsResponse.timings.duration);
    
    const productsCheck = check(productsResponse, {
      'products api success': (r) => r.status === 200,
    });
    
    apiSuccessRate.add(productsCheck);
    if (!productsCheck) {
      apiErrorCount.add(1);
    }
    
    // 业务操作3：模拟下单
    const orderData = {
      productId: Math.floor(Math.random() * 100) + 1,
      quantity: Math.floor(Math.random() * 3) + 1,
      userId: Math.floor(Math.random() * 1000) + 1
    };
    
    const orderResponse = http.post(`${BASE_URL}/post`, orderData);
    
    apiResponseTimes.add(orderResponse.timings.duration);
    
    const orderCheck = check(orderResponse, {
      'order api success': (r) => r.status === 200,
      'order contains correct data': (r) => {
        const json = r.json();
        return json.form.productId == orderData.productId;
      },
    });
    
    apiSuccessRate.add(orderCheck);
    
    // 记录业务指标
    const transactionEnd = Date.now();
    const transactionTime = transactionEnd - transactionStart;
    
    if (userCheck && productsCheck && orderCheck) {
      // 事务成功
      successfulTransactions.add(1);
      transactionDuration.add(transactionTime);
      errorRate.add(true);
      
      // 记录成功指标
      myCounter.add(1);
      myGauge.add(__VU); // 记录当前VU数量
      myRate.add(true);
      myTrend.add(transactionTime);
      
      console.log(`Transaction completed successfully in ${transactionTime}ms`);
      
    } else {
      // 事务失败
      failedTransactions.add(1);
      errorRate.add(false);
      
      // 记录失败指标
      myRate.add(false);
      
      console.log('Transaction failed');
    }
    
    // 模拟思考时间
    sleep(Math.random() * 2 + 1);
    
  } catch (error) {
    // 处理异常
    failedTransactions.add(1);
    errorRate.add(false);
    apiErrorCount.add(1);
    
    console.error('Transaction error:', error.message);
  }
}

// 带标签的自定义指标示例
const taggedCounter = new Counter('tagged_counter');
const taggedTrend = new Trend('tagged_trend');

// 带标签的API测试函数
function testApiWithTags(endpoint, method = 'GET') {
  const startTime = Date.now();
  
  try {
    let response;
    if (method === 'GET') {
      response = http.get(`${BASE_URL}${endpoint}`);
    } else if (method === 'POST') {
      response = http.post(`${BASE_URL}${endpoint}`, {});
    }
    
    const duration = Date.now() - startTime;
    
    // 使用标签记录指标
    taggedCounter.add(1, { 
      endpoint: endpoint, 
      method: method, 
      status: response.status 
    });
    
    taggedTrend.add(duration, { 
      endpoint: endpoint, 
      method: method,
      status_group: response.status < 300 ? '2xx' : 
                   response.status < 400 ? '3xx' : 
                   response.status < 500 ? '4xx' : '5xx'
    });
    
    return response;
    
  } catch (error) {
    const duration = Date.now() - startTime;
    
    taggedCounter.add(1, { 
      endpoint: endpoint, 
      method: method, 
      status: 'error',
      error_type: error.name
    });
    
    taggedTrend.add(duration, { 
      endpoint: endpoint, 
      method: method,
      status_group: 'error'
    });
    
    throw error;
  }
}

// 使用带标签的API测试
export function taggedApiTest() {
  // 测试不同的API端点
  const endpoints = [
    '/get',
    '/post', 
    '/put',
    '/delete'
  ];
  
  endpoints.forEach(endpoint => {
    try {
      testApiWithTags(endpoint, endpoint === '/post' || endpoint === '/put' ? 'POST' : 'GET');
    } catch (error) {
      console.log(`API test failed for ${endpoint}:`, error.message);
    }
    
    sleep(0.5);
  });
}
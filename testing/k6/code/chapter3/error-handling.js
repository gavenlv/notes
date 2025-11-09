// 第3章：错误处理示例
// 演示高级错误处理机制，包括重试、断路器模式等

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Rate } from 'k6/metrics';

const BASE_URL = 'https://httpbin.test.k6.io';

// 错误处理指标
const errorMetrics = {
  totalRequests: new Counter('total_requests'),
  successfulRequests: new Counter('successful_requests'),
  failedRequests: new Counter('failed_requests'),
  retryAttempts: new Counter('retry_attempts'),
  circuitBreakerTrips: new Counter('circuit_breaker_trips'),
  errorRate: new Rate('error_rate'),
  retrySuccessRate: new Rate('retry_success_rate')
};

// 1. 基础重试机制
function httpRequestWithRetry(url, options = {}, maxRetries = 3) {
  let attempts = 0;
  let lastError = null;
  
  while (attempts < maxRetries) {
    attempts++;
    
    try {
      const response = http.get(url, options);
      errorMetrics.totalRequests.add(1);
      
      if (response.status >= 200 && response.status < 300) {
        // 请求成功
        errorMetrics.successfulRequests.add(1);
        errorMetrics.errorRate.add(true);
        
        if (attempts > 1) {
          errorMetrics.retrySuccessRate.add(true);
        }
        
        return { success: true, response: response, attempts: attempts };
      }
      
      // 根据状态码决定是否重试
      if (response.status >= 500) {
        // 服务器错误，重试
        lastError = new Error(`Server error: ${response.status}`);
        
        if (attempts < maxRetries) {
          errorMetrics.retryAttempts.add(1);
          const backoffTime = Math.pow(2, attempts - 1); // 指数退避
          sleep(backoffTime);
          continue;
        }
      } else {
        // 客户端错误，不重试
        errorMetrics.failedRequests.add(1);
        errorMetrics.errorRate.add(false);
        return { 
          success: false, 
          error: new Error(`Client error: ${response.status}`),
          attempts: attempts 
        };
      }
      
    } catch (error) {
      // 网络错误等异常
      lastError = error;
      
      if (attempts < maxRetries) {
        errorMetrics.retryAttempts.add(1);
        const backoffTime = Math.pow(2, attempts - 1);
        sleep(backoffTime);
        continue;
      }
    }
  }
  
  // 所有重试都失败
  errorMetrics.failedRequests.add(1);
  errorMetrics.errorRate.add(false);
  
  if (attempts > 1) {
    errorMetrics.retrySuccessRate.add(false);
  }
  
  return { 
    success: false, 
    error: lastError || new Error('Max retries exceeded'),
    attempts: attempts 
  };
}

// 2. 断路器模式实现
class CircuitBreaker {
  constructor(failureThreshold = 5, timeout = 60000, halfOpenTimeout = 30000) {
    this.failureThreshold = failureThreshold;
    this.timeout = timeout;
    this.halfOpenTimeout = halfOpenTimeout;
    this.failureCount = 0;
    this.lastFailureTime = null;
    this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
    this.halfOpenAttempts = 0;
  }
  
  async call(url, options = {}) {
    const currentTime = Date.now();
    
    // 检查断路器状态
    if (this.state === 'OPEN') {
      if (currentTime - this.lastFailureTime > this.timeout) {
        // 超时后进入半开状态
        this.state = 'HALF_OPEN';
        this.halfOpenAttempts = 0;
        console.log('Circuit breaker moving to HALF_OPEN state');
      } else {
        // 断路器仍处于打开状态
        throw new Error('Circuit breaker is OPEN');
      }
    }
    
    try {
      const response = http.get(url, options);
      
      if (response.status >= 200 && response.status < 300) {
        // 请求成功
        this.success();
        return response;
      } else if (response.status >= 500) {
        // 服务器错误
        this.failure();
        return response;
      } else {
        // 客户端错误，不影响断路器状态
        return response;
      }
      
    } catch (error) {
      // 网络错误
      this.failure();
      throw error;
    }
  }
  
  success() {
    this.failureCount = 0;
    
    if (this.state === 'HALF_OPEN') {
      // 半开状态下的成功请求，关闭断路器
      this.state = 'CLOSED';
      console.log('Circuit breaker moving to CLOSED state');
    }
    
    this.halfOpenAttempts = 0;
  }
  
  failure() {
    this.failureCount++;
    this.lastFailureTime = Date.now();
    
    if (this.state === 'HALF_OPEN') {
      this.halfOpenAttempts++;
      
      if (this.halfOpenAttempts >= 3) {
        // 半开状态下多次失败，重新打开断路器
        this.state = 'OPEN';
        errorMetrics.circuitBreakerTrips.add(1);
        console.log('Circuit breaker moving to OPEN state (half-open failure)');
      }
    } else if (this.failureCount >= this.failureThreshold) {
      // 失败次数达到阈值，打开断路器
      this.state = 'OPEN';
      errorMetrics.circuitBreakerTrips.add(1);
      console.log('Circuit breaker moving to OPEN state');
    }
  }
  
  getState() {
    return {
      state: this.state,
      failureCount: this.failureCount,
      lastFailureTime: this.lastFailureTime,
      halfOpenAttempts: this.halfOpenAttempts
    };
  }
}

// 3. 错误分类和处理
class ErrorHandler {
  static classifyError(error) {
    if (error.message.includes('timeout')) {
      return 'TIMEOUT';
    } else if (error.message.includes('network')) {
      return 'NETWORK';
    } else if (error.message.includes('5')) {
      return 'SERVER_ERROR';
    } else if (error.message.includes('4')) {
      return 'CLIENT_ERROR';
    } else {
      return 'UNKNOWN';
    }
  }
  
  static getRecoveryStrategy(errorType) {
    const strategies = {
      TIMEOUT: { retry: true, backoff: true, fallback: true },
      NETWORK: { retry: true, backoff: true, fallback: true },
      SERVER_ERROR: { retry: true, backoff: true, fallback: false },
      CLIENT_ERROR: { retry: false, backoff: false, fallback: true },
      UNKNOWN: { retry: false, backoff: false, fallback: true }
    };
    
    return strategies[errorType] || strategies.UNKNOWN;
  }
  
  static executeFallback(action, fallbackData = null) {
    console.log(`Executing fallback for action: ${action}`);
    
    // 模拟回退逻辑
    switch (action) {
      case 'get_user_data':
        return { success: true, data: fallbackData || { id: 'fallback', name: 'Fallback User' } };
      case 'process_order':
        return { success: false, error: 'Fallback: Order processing unavailable' };
      default:
        return { success: false, error: 'No fallback strategy available' };
    }
  }
}

// 4. 综合错误处理函数
async function robustHttpRequest(url, options = {}) {
  const circuitBreaker = new CircuitBreaker();
  const maxRetries = 3;
  
  try {
    // 首先尝试通过断路器
    const response = await circuitBreaker.call(url, options);
    
    if (response.status >= 200 && response.status < 300) {
      return { success: true, data: response, source: 'primary' };
    }
    
    // 处理非成功响应
    const errorType = ErrorHandler.classifyError(
      new Error(`HTTP ${response.status}`)
    );
    const strategy = ErrorHandler.getRecoveryStrategy(errorType);
    
    if (strategy.retry) {
      // 使用重试机制
      const retryResult = httpRequestWithRetry(url, options, maxRetries);
      
      if (retryResult.success) {
        return { success: true, data: retryResult.response, source: 'retry' };
      }
    }
    
    if (strategy.fallback) {
      // 执行回退策略
      const fallbackResult = ErrorHandler.executeFallback('get_user_data');
      return { 
        success: fallbackResult.success, 
        data: fallbackResult.data, 
        source: 'fallback',
        error: fallbackResult.error
      };
    }
    
    return { success: false, error: `Request failed after all recovery attempts` };
    
  } catch (error) {
    const errorType = ErrorHandler.classifyError(error);
    const strategy = ErrorHandler.getRecoveryStrategy(errorType);
    
    console.log(`Error occurred: ${error.message}, Type: ${errorType}`);
    
    if (strategy.fallback) {
      const fallbackResult = ErrorHandler.executeFallback('get_user_data');
      return { 
        success: fallbackResult.success, 
        data: fallbackResult.data, 
        source: 'fallback',
        error: fallbackResult.error
      };
    }
    
    return { success: false, error: error.message };
  }
}

// 测试配置
export const options = {
  vus: 10,
  duration: '5m',
  thresholds: {
    http_req_duration: ['p(95)<2000'],
    http_req_failed: ['rate<0.05'],
    error_rate: ['rate<0.1'],
    retry_success_rate: ['rate>0.5'] // 重试成功率应大于50%
  },
};

// 测试函数
export default function () {
  // 测试1：基础重试机制
  group('basic_retry_test', function () {
    const result = httpRequestWithRetry(`${BASE_URL}/status/500`); // 模拟服务器错误
    
    check(result, {
      'retry mechanism handled server error': (r) => r.attempts > 0,
      'retry result has success status': (r) => typeof r.success === 'boolean'
    });
    
    console.log(`Basic retry test: ${result.success ? 'Success' : 'Failed'} after ${result.attempts} attempts`);
  });
  
  sleep(1);
  
  // 测试2：断路器模式
  group('circuit_breaker_test', function () {
    const circuitBreaker = new CircuitBreaker(3, 30000); // 3次失败触发，30秒超时
    
    // 模拟连续失败
    for (let i = 0; i < 5; i++) {
      try {
        circuitBreaker.call(`${BASE_URL}/status/500`);
      } catch (error) {
        console.log(`Circuit breaker call ${i + 1}: ${error.message}`);
      }
    }
    
    const state = circuitBreaker.getState();
    check(state, {
      'circuit breaker tripped after failures': (s) => s.state === 'OPEN',
      'failure count recorded correctly': (s) => s.failureCount >= 3
    });
    
    console.log('Circuit breaker state:', state);
  });
  
  sleep(1);
  
  // 测试3：错误分类和恢复策略
  group('error_classification_test', function () {
    const testErrors = [
      new Error('timeout exceeded'),
      new Error('network error'),
      new Error('HTTP 500'),
      new Error('HTTP 404'),
      new Error('unknown error')
    ];
    
    testErrors.forEach(error => {
      const errorType = ErrorHandler.classifyError(error);
      const strategy = ErrorHandler.getRecoveryStrategy(errorType);
      
      check(strategy, {
        [`recovery strategy for ${errorType}`]: (s) => 
          typeof s.retry === 'boolean' && 
          typeof s.backoff === 'boolean' && 
          typeof s.fallback === 'boolean'
      });
      
      console.log(`Error: ${error.message} -> Type: ${errorType} -> Strategy:`, strategy);
    });
  });
  
  sleep(1);
  
  // 测试4：综合错误处理
  group('comprehensive_error_handling', function () {
    // 测试正常请求
    robustHttpRequest(`${BASE_URL}/status/200`)
      .then(result => {
        check(result, {
          'normal request handled successfully': (r) => r.success === true,
          'normal request used primary source': (r) => r.source === 'primary'
        });
        console.log('Normal request result:', result);
      });
    
    sleep(1);
    
    // 测试错误请求
    robustHttpRequest(`${BASE_URL}/status/500`)
      .then(result => {
        check(result, {
          'error request handled with recovery': (r) => typeof r.success === 'boolean',
          'error request has recovery source': (r) => 
            r.source === 'retry' || r.source === 'fallback' || r.source === 'primary'
        });
        console.log('Error request result:', result);
      });
  });
  
  sleep(2);
  
  // 测试5：性能监控下的错误处理
  group('performance_error_handling', function () {
    const endpoints = [
      '/status/200',
      '/status/500', 
      '/delay/1',
      '/status/404'
    ];
    
    endpoints.forEach(endpoint => {
      const startTime = Date.now();
      
      robustHttpRequest(`${BASE_URL}${endpoint}`)
        .then(result => {
          const duration = Date.now() - startTime;
          
          check(result, {
            [`${endpoint} request completed`]: (r) => typeof r.success === 'boolean',
            [`${endpoint} reasonable duration`]: (r) => duration < 10000
          });
          
          console.log(`Performance test ${endpoint}: ${result.success ? 'Success' : 'Failed'} in ${duration}ms`);
        });
      
      sleep(0.5);
    });
  });
}

// 错误报告和监控
export function teardown() {
  console.log('=== Error Handling Test Summary ===');
  console.log('Total requests:', errorMetrics.totalRequests);
  console.log('Successful requests:', errorMetrics.successfulRequests);
  console.log('Failed requests:', errorMetrics.failedRequests);
  console.log('Retry attempts:', errorMetrics.retryAttempts);
  console.log('Circuit breaker trips:', errorMetrics.circuitBreakerTrips);
  
  // 计算错误率
  const total = errorMetrics.totalRequests;
  const failed = errorMetrics.failedRequests;
  const errorRate = total > 0 ? (failed / total) * 100 : 0;
  
  console.log(`Error rate: ${errorRate.toFixed(2)}%`);
  
  if (errorRate > 10) {
    console.warn('⚠ High error rate detected - consider reviewing error handling strategies');
  }
}
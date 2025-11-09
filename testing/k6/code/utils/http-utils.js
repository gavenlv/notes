// 第4章：HTTP工具类
// 提供生产环境级别的HTTP请求工具

import http from 'k6/http';
import { check, sleep } from 'k6';

/**
 * 创建HTTP请求配置
 * @param Object options - 请求选项
 * @returns Object 请求配置
 */
export function createRequestConfig(options = {}) {
  const config = {
    headers: {
      'User-Agent': 'k6-performance-test/1.0',
      'X-Request-ID': generateRequestId(),
      ...options.headers
    },
    tags: {
      environment: __ENV.ENV || 'development',
      test_type: 'performance',
      ...options.tags
    },
    timeout: options.timeout || '30s',
    noConnectionReuse: false
  };
  
  return config;
}

/**
 * 生成唯一的请求ID
 * @returns String 请求ID
 */
export function generateRequestId() {
  return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * 安全执行HTTP请求
 * @param String method - HTTP方法
 * @param String url - 请求URL
 * @param Object data - 请求数据
 * @param Object options - 请求选项
 * @returns Object 请求结果
 */
export function safeHttpRequest(method, url, data = null, options = {}) {
  const config = createRequestConfig(options);
  
  try {
    let response;
    
    switch (method.toUpperCase()) {
      case 'GET':
        response = http.get(url, config);
        break;
      case 'POST':
        response = http.post(url, data, config);
        break;
      case 'PUT':
        response = http.put(url, data, config);
        break;
      case 'PATCH':
        response = http.patch(url, data, config);
        break;
      case 'DELETE':
        response = http.del(url, config);
        break;
      default:
        throw new Error(`Unsupported HTTP method: ${method}`);
    }
    
    return {
      success: response.status >= 200 && response.status < 300,
      response: response,
      status: response.status,
      duration: response.timings.duration
    };
    
  } catch (error) {
    return {
      success: false,
      error: error,
      status: 0,
      duration: 0
    };
  }
}

/**
 * 重试HTTP请求
 * @param String method - HTTP方法
 * @param String url - 请求URL
 * @param Object data - 请求数据
 * @param Object options - 请求选项
 * @param Number maxAttempts - 最大重试次数
 * @returns Object 请求结果
 */
export function retryHttpRequest(method, url, data = null, options = {}, maxAttempts = 3) {
  let lastError;
  let attempts = 0;
  
  while (attempts < maxAttempts) {
    attempts++;
    const result = safeHttpRequest(method, url, data, options);
    
    if (result.success) {
      return { ...result, attempts };
    }
    
    lastError = result.error;
    
    // 指数退避策略
    const backoffTime = Math.pow(2, attempts) * 1000;
    console.log(`请求失败，${backoffTime}ms后重试... (尝试 ${attempts}/${maxAttempts})`);
    sleep(backoffTime / 1000);
  }
  
  return {
    success: false,
    error: lastError || new Error('Max retries exceeded'),
    status: 0,
    duration: 0,
    attempts: attempts
  };
}

/**
 * 创建检查点配置
 * @param String apiName - API名称
 * @param Array customExpectations - 自定义期望
 * @returns Object 检查配置
 */
export function createCheckConfig(apiName, customExpectations = []) {
  const baseExpectations = {
    [`${apiName} status is 2xx`]: (r) => r.status >= 200 && r.status < 300,
    [`${apiName} response time < 5s`]: (r) => r.timings.duration < 5000,
    [`${apiName} has valid response`]: (r) => r.body && r.body.length > 0
  };
  
  // 合并自定义期望
  const expectations = { ...baseExpectations };
  customExpectations.forEach((expectation, index) => {
    expectations[`${apiName} custom_${index}`] = expectation;
  });
  
  return expectations;
}

/**
 * 安全地解析JSON响应
 * @param Object response - HTTP响应
 * @returns Object 解析后的JSON或null
 */
export function safeJsonParse(response) {
  try {
    return response.json();
  } catch (error) {
    console.warn('JSON parse failed:', error.message);
    return null;
  }
}

/**
 * 批量执行HTTP请求
 * @param Array requests - 请求数组
 * @returns Array 请求结果数组
 */
export function batchHttpRequests(requests) {
  const results = [];
  
  requests.forEach((request, index) => {
    const result = safeHttpRequest(
      request.method,
      request.url,
      request.data,
      request.options
    );
    
    results.push({
      index,
      name: request.name || `Request ${index}`,
      ...result
    });
    
    // 添加间隔，避免请求过密
    if (index < requests.length - 1) {
      sleep(0.1);
    }
  });
  
  return results;
}
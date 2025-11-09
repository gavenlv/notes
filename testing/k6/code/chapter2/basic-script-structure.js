// 第2章：k6脚本基本结构示例
// 演示完整的k6脚本结构

import http from 'k6/http';
import { check, sleep } from 'k6';

// 测试配置
export const options = {
  // 虚拟用户配置
  vus: 10,
  duration: '30s',
  
  // 阈值配置
  thresholds: {
    http_req_duration: ['p(95)<500'],
  },
};

// 初始化代码（可选）
export function setup() {
  console.log('Setup: 测试开始前的准备工作');
  // 这里可以执行测试前的准备工作
  // 比如：创建测试数据、获取认证令牌等
  return { 
    testData: '准备就绪',
    timestamp: Date.now()
  };
}

// 默认函数 - 每个虚拟用户执行的主逻辑
export default function (data) {
  // 测试逻辑
  const response = http.get('https://httpbin.test.k6.io/get');
  
  // 验证响应
  check(response, { 
    'status is 200': (r) => r.status === 200,
    'response time < 1s': (r) => r.timings.duration < 1000
  });
  
  // 等待1秒
  sleep(1);
}

// 清理代码（可选）
export function teardown(data) {
  console.log('Teardown: 测试结束后的清理工作');
  console.log(`测试数据: ${data.testData}`);
  console.log(`测试时长: ${Date.now() - data.timestamp}ms`);
}
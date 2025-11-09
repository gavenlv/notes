// 第1章：第一个k6测试脚本
// 这个脚本演示了最基本的k6测试结构

import http from 'k6/http';
import { check, sleep } from 'k6';

// 测试配置
export const options = {
  vus: 1,          // 1个虚拟用户
  duration: '30s', // 测试持续30秒
};

// 默认函数 - 每个虚拟用户都会执行
export default function () {
  // 发送HTTP GET请求到测试服务器
  const response = http.get('https://httpbin.test.k6.io/get');
  
  // 验证响应
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  // 等待1秒
  sleep(1);
}
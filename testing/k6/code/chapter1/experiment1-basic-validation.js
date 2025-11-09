// 实验1：基础环境验证
// 验证k6安装是否成功，理解基本测试流程

import http from 'k6/http';
import { check } from 'k6';

export const options = {
  stages: [
    { duration: '10s', target: 5 },  // 10秒内增加到5个用户
    { duration: '20s', target: 5 },  // 保持5个用户20秒
    { duration: '10s', target: 0 },  // 10秒内减少到0个用户
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95%的请求响应时间小于500ms
    http_req_failed: ['rate<0.01'],   // 请求失败率小于1%
  },
};

export default function () {
  const response = http.get('https://httpbin.test.k6.io/get');
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'has request headers': (r) => r.json().headers !== undefined,
  });
}
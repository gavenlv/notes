// 第2章：HTTP请求示例
// 演示各种HTTP请求方法

import http from 'k6/http';
import { check } from 'k6';

const BASE_URL = 'https://httpbin.test.k6.io';

export const options = {
  vus: 5,
  duration: '1m',
};

export default function () {
  // 1. GET请求示例
  const getResponse = http.get(`${BASE_URL}/get`);
  check(getResponse, {
    'GET status is 200': (r) => r.status === 200,
    'GET response contains headers': (r) => r.json().headers !== undefined,
  });
  
  // 2. POST请求 - 表单数据
  const formData = {
    username: 'testuser',
    password: 'testpass',
    email: 'test@example.com'
  };
  
  const postResponse = http.post(`${BASE_URL}/post`, formData);
  check(postResponse, {
    'POST status is 200': (r) => r.status === 200,
    'POST contains form data': (r) => {
      const json = r.json();
      return json.form.username === 'testuser';
    },
  });
  
  // 3. POST请求 - JSON数据
  const jsonData = JSON.stringify({
    title: 'Test Post',
    body: 'This is a test post content',
    userId: 1
  });
  
  const jsonParams = {
    headers: { 'Content-Type': 'application/json' },
  };
  
  const jsonPostResponse = http.post(`${BASE_URL}/post`, jsonData, jsonParams);
  check(jsonPostResponse, {
    'JSON POST status is 200': (r) => r.status === 200,
    'JSON POST contains data': (r) => {
      const json = r.json();
      return json.data === jsonData;
    },
  });
  
  // 4. PUT请求
  const putData = { 
    id: 1, 
    name: 'Updated Name',
    status: 'active'
  };
  
  const putResponse = http.put(`${BASE_URL}/put`, putData);
  check(putResponse, {
    'PUT status is 200': (r) => r.status === 200,
  });
  
  // 5. PATCH请求
  const patchData = { status: 'inactive' };
  const patchResponse = http.patch(`${BASE_URL}/patch`, patchData);
  check(patchResponse, {
    'PATCH status is 200': (r) => r.status === 200,
  });
  
  // 6. DELETE请求
  const deleteResponse = http.del(`${BASE_URL}/delete`);
  check(deleteResponse, {
    'DELETE status is 200': (r) => r.status === 200,
  });
  
  // 7. 带参数的请求
  const params = {
    headers: {
      'User-Agent': 'k6-test/1.0',
      'X-Custom-Header': 'custom-value'
    },
    tags: {
      name: 'custom-request',
      type: 'api-call'
    },
    timeout: '30s',
  };
  
  const customResponse = http.get(`${BASE_URL}/headers`, params);
  check(customResponse, {
    'Custom request status is 200': (r) => r.status === 200,
    'Custom headers received': (r) => {
      const json = r.json();
      return json.headers['X-Custom-Header'] === 'custom-value';
    },
  });
}
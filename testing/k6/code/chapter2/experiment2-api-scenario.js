// 实验2：完整API测试场景
// 创建一个完整的用户注册、登录、操作的API测试场景

import http from 'k6/http';
import { check, group, sleep } from 'k6';

const BASE_URL = 'https://httpbin.test.k6.io';

// 测试配置
export const options = {
  stages: [
    { duration: '30s', target: 5 },
    { duration: '1m', target: 5 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000'],
    http_req_failed: ['rate<0.05'],
    'group_duration{group:authentication}': ['avg<2000'],
    checks: ['rate>0.9'],
  },
  tags: {
    environment: 'test',
    test_type: 'api-scenario',
  },
};

// 测试数据
export function setup() {
  console.log('Setting up test data...');
  
  return {
    testUser: {
      username: `testuser_${Date.now()}`,
      email: `test_${Date.now()}@example.com`,
      password: 'TestPass123!',
    },
    startTime: Date.now(),
  };
}

export default function (data) {
  let authToken = '';
  let sessionId = '';
  
  // 分组1：用户注册
  group('user_registration', function () {
    console.log('Starting user registration for:', data.testUser.username);
    
    const registerResponse = http.post(`${BASE_URL}/post`, {
      username: data.testUser.username,
      email: data.testUser.email,
      password: data.testUser.password,
    });
    
    check(registerResponse, {
      'registration successful': (r) => r.status === 200,
      'registration response contains data': (r) => {
        const json = r.json();
        return json.form.username === data.testUser.username;
      },
    });
    
    // 模拟注册后处理时间
    sleep(1);
    
    console.log('User registration completed');
  });
  
  // 分组2：用户登录
  group('user_authentication', function () {
    console.log('Starting user authentication');
    
    const loginResponse = http.post(`${BASE_URL}/post`, {
      username: data.testUser.username,
      password: data.testUser.password,
    });
    
    check(loginResponse, {
      'login successful': (r) => r.status === 200,
      'login returns session data': (r) => {
        const json = r.json();
        // 模拟获取认证令牌和会话ID
        authToken = `token_${Date.now()}`;
        sessionId = `session_${Date.now()}`;
        return authToken !== '' && sessionId !== '';
      },
    });
    
    sleep(1);
    console.log('User authentication completed');
  });
  
  // 分组3：用户操作（需要认证）
  if (authToken && sessionId) {
    group('authenticated_operations', function () {
      console.log('Starting authenticated operations');
      
      const headers = {
        'Authorization': `Bearer ${authToken}`,
        'X-Session-ID': sessionId,
        'Content-Type': 'application/json',
      };
      
      // 获取用户信息
      const profileResponse = http.get(`${BASE_URL}/get`, { headers });
      check(profileResponse, {
        'profile access successful': (r) => r.status === 200,
        'profile contains user data': (r) => {
          const json = r.json();
          return json.headers && json.headers.Authorization !== undefined;
        },
      });
      
      sleep(1);
      
      // 更新用户设置
      const settingsResponse = http.put(`${BASE_URL}/put`, 
        JSON.stringify({ 
          theme: 'dark',
          language: 'en',
          notifications: true 
        }), 
        { headers }
      );
      check(settingsResponse, {
        'settings update successful': (r) => r.status === 200,
      });
      
      sleep(2);
      
      // 执行用户操作
      group('user_actions', function () {
        // 浏览内容
        const browseResponse = http.get(`${BASE_URL}/get?action=browse`, { headers });
        check(browseResponse, { 'browse successful': (r) => r.status === 200 });
        
        sleep(Math.random() * 2 + 1);
        
        // 搜索内容
        const searchResponse = http.get(`${BASE_URL}/get?q=test+search`, { headers });
        check(searchResponse, { 'search successful': (r) => r.status === 200 });
        
        sleep(1);
        
        // 创建内容
        const createData = {
          title: `Test Post ${Date.now()}`,
          content: 'This is a test post created during performance testing',
          category: 'test'
        };
        
        const createResponse = http.post(`${BASE_URL}/post`, 
          JSON.stringify(createData), 
          { headers }
        );
        check(createResponse, { 'content creation successful': (r) => r.status === 200 });
        
        sleep(2);
      });
      
      console.log('Authenticated operations completed');
    });
  }
  
  // 分组4：用户登出
  group('user_logout', function () {
    console.log('Starting user logout');
    
    const logoutResponse = http.post(`${BASE_URL}/post`, {
      action: 'logout',
      token: authToken,
      sessionId: sessionId
    });
    
    check(logoutResponse, {
      'logout successful': (r) => r.status === 200,
    });
    
    sleep(1);
    console.log('User logout completed');
  });
  
  // 分组5：清理测试数据（可选）
  group('cleanup', function () {
    console.log('Starting cleanup operations');
    
    // 模拟清理测试数据
    const cleanupResponse = http.post(`${BASE_URL}/post`, {
      action: 'cleanup',
      testUser: data.testUser.username
    });
    
    check(cleanupResponse, {
      'cleanup successful': (r) => r.status === 200,
    });
    
    console.log('Cleanup operations completed');
  });
}

// 清理函数
export function teardown(data) {
  const totalDuration = Date.now() - data.startTime;
  
  console.log('=== TEST COMPLETED ===');
  console.log(`Test environment: ${__ENV.ENV || 'development'}`);
  console.log(`Base URL: ${BASE_URL}`);
  console.log(`Total test duration: ${Math.round(totalDuration / 1000)} seconds`);
  console.log(`Test user: ${data.testUser.username}`);
  console.log('Cleanup completed successfully');
}
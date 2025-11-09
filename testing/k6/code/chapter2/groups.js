// 第2章：分组功能示例
// 演示如何使用分组组织测试逻辑

import http from 'k6/http';
import { group, check, sleep } from 'k6';

const BASE_URL = 'https://httpbin.test.k6.io';

export const options = {
  vus: 5,
  duration: '3m',
  thresholds: {
    'group_duration{group:user_registration}': ['avg < 2000'],
    'group_duration{group:user_authentication}': ['avg < 3000'],
    'group_duration{group:user_operations}': ['avg < 5000'],
  },
};

export default function () {
  // 用户注册流程分组
  group('user_registration', function () {
    console.log('Starting user registration flow');
    
    // 1. 检查注册页面可用性
    const registerPageResponse = http.get(`${BASE_URL}/get?page=register`);
    check(registerPageResponse, {
      'registration page available': (r) => r.status === 200,
    });
    
    sleep(1);
    
    // 2. 提交注册表单
    const registrationData = {
      username: `testuser_${Date.now()}`,
      email: `test_${Date.now()}@example.com`,
      password: 'TestPass123!',
      confirmPassword: 'TestPass123!'
    };
    
    const registerResponse = http.post(`${BASE_URL}/post`, registrationData);
    check(registerResponse, {
      'registration successful': (r) => r.status === 200,
      'registration response contains data': (r) => {
        const json = r.json();
        return json.form.username === registrationData.username;
      },
    });
    
    sleep(2);
    
    // 3. 验证邮箱（模拟）
    const verifyResponse = http.get(`${BASE_URL}/get?action=verify`);
    check(verifyResponse, {
      'verification successful': (r) => r.status === 200,
    });
    
    console.log('User registration completed');
  });
  
  // 用户认证流程分组
  group('user_authentication', function () {
    console.log('Starting user authentication flow');
    
    // 1. 登录
    const loginData = {
      username: 'testuser',
      password: 'testpass'
    };
    
    const loginResponse = http.post(`${BASE_URL}/post`, loginData);
    check(loginResponse, {
      'login successful': (r) => r.status === 200,
    });
    
    sleep(1);
    
    // 2. 获取用户信息（需要认证）
    const userInfoResponse = http.get(`${BASE_URL}/get?action=userinfo`);
    check(userInfoResponse, {
      'user info retrieved': (r) => r.status === 200,
    });
    
    // 3. 检查权限
    const permissionsResponse = http.get(`${BASE_URL}/get?action=permissions`);
    check(permissionsResponse, {
      'permissions checked': (r) => r.status === 200,
    });
    
    console.log('User authentication completed');
  });
  
  // 用户操作分组
  group('user_operations', function () {
    console.log('Starting user operations');
    
    // 1. 浏览产品
    group('browse_products', function () {
      const productsResponse = http.get(`${BASE_URL}/get?action=products`);
      check(productsResponse, {
        'products page loaded': (r) => r.status === 200,
      });
      sleep(Math.random() * 3 + 1); // 随机浏览时间
    });
    
    // 2. 搜索产品
    group('search_products', function () {
      const searchTerms = ['laptop', 'phone', 'tablet'];
      const randomTerm = searchTerms[Math.floor(Math.random() * searchTerms.length)];
      
      const searchResponse = http.get(`${BASE_URL}/get?q=${randomTerm}`);
      check(searchResponse, {
        'search successful': (r) => r.status === 200,
      });
      sleep(1);
    });
    
    // 3. 查看产品详情
    group('view_product_details', function () {
      const productId = Math.floor(Math.random() * 100) + 1;
      const productResponse = http.get(`${BASE_URL}/get?product=${productId}`);
      check(productResponse, {
        'product details loaded': (r) => r.status === 200,
      });
      sleep(Math.random() * 2 + 1);
    });
    
    // 4. 添加到购物车
    group('add_to_cart', function () {
      const cartData = {
        productId: Math.floor(Math.random() * 100) + 1,
        quantity: Math.floor(Math.random() * 3) + 1
      };
      
      const cartResponse = http.post(`${BASE_URL}/post`, cartData);
      check(cartResponse, {
        'item added to cart': (r) => r.status === 200,
      });
      sleep(1);
    });
    
    // 5. 查看购物车
    group('view_cart', function () {
      const cartResponse = http.get(`${BASE_URL}/get?action=cart`);
      check(cartResponse, {
        'cart viewed': (r) => r.status === 200,
      });
      sleep(1);
    });
    
    console.log('User operations completed');
  });
  
  // 用户登出流程
  group('user_logout', function () {
    console.log('Starting user logout');
    
    const logoutResponse = http.get(`${BASE_URL}/get?action=logout`);
    check(logoutResponse, {
      'logout successful': (r) => r.status === 200,
    });
    
    console.log('User logout completed');
  });
  
  // 嵌套分组示例
  group('complex_workflow', function () {
    group('step_1_initialization', function () {
      const initResponse = http.get(`${BASE_URL}/get?step=init`);
      check(initResponse, { 'initialization complete': (r) => r.status === 200 });
    });
    
    group('step_2_processing', function () {
      group('substep_2a', function () {
        const response = http.get(`${BASE_URL}/get?step=2a`);
        check(response, { 'substep 2a complete': (r) => r.status === 200 });
      });
      
      group('substep_2b', function () {
        const response = http.get(`${BASE_URL}/get?step=2b`);
        check(response, { 'substep 2b complete': (r) => r.status === 200 });
      });
    });
    
    group('step_3_finalization', function () {
      const finalResponse = http.get(`${BASE_URL}/get?step=final`);
      check(finalResponse, { 'finalization complete': (r) => r.status === 200 });
    });
  });
}
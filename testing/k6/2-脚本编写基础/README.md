# 第2章：k6脚本编写基础

## 2.1 k6脚本结构

一个完整的k6脚本包含以下几个核心部分：

### 基本结构

```javascript
// 1. 导入模块
import http from 'k6/http';
import { check, sleep } from 'k6';

// 2. 测试配置
export const options = {
  // 虚拟用户配置
  vus: 10,
  duration: '30s',
  
  // 阈值配置
  thresholds: {
    http_req_duration: ['p(95)<500'],
  },
};

// 3. 初始化代码（可选）
export function setup() {
  // 测试前的准备工作
  return { data: 'test data' };
}

// 4. 默认函数 - 每个虚拟用户执行的主逻辑
export default function (data) {
  // 测试逻辑
  const response = http.get('https://test.k6.io');
  check(response, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}

// 5. 清理代码（可选）
export function teardown(data) {
  // 测试后的清理工作
}
```

## 2.2 HTTP请求详解

### 基本HTTP方法

#### GET请求

```javascript
import http from 'k6/http';

// 简单GET请求
const response = http.get('https://httpbin.test.k6.io/get');

// 带查询参数的GET请求
const params = {
  headers: { 'X-My-Header': 'value' },
  tags: { name: 'get-request' },
};
const response = http.get('https://httpbin.test.k6.io/get?param1=value1', params);
```

#### POST请求

```javascript
// 表单数据
const formData = {
  username: 'testuser',
  password: 'testpass',
};
const response = http.post('https://httpbin.test.k6.io/post', formData);

// JSON数据
const jsonData = JSON.stringify({
  title: 'Test Post',
  body: 'This is a test post',
  userId: 1,
});

const params = {
  headers: { 'Content-Type': 'application/json' },
};
const response = http.post('https://httpbin.test.k6.io/post', jsonData, params);

// 文件上传
const fileData = http.file('data.csv', 'id,name\n1,John\n2,Jane');
const multipartData = {
  file: fileData,
  description: 'Test file upload',
};
const response = http.post('https://httpbin.test.k6.io/post', multipartData);
```

#### PUT、PATCH、DELETE请求

```javascript
// PUT请求 - 完整更新
const putData = { id: 1, name: 'Updated Name' };
const response = http.put('https://httpbin.test.k6.io/put', putData);

// PATCH请求 - 部分更新
const patchData = { name: 'Partial Update' };
const response = http.patch('https://httpbin.test.k6.io/patch', patchData);

// DELETE请求
const response = http.del('https://httpbin.test.k6.io/delete');
```

### 请求参数配置

```javascript
const params = {
  // 头信息
  headers: {
    'User-Agent': 'k6-test/1.0',
    'Authorization': 'Bearer token123',
    'Content-Type': 'application/json',
  },
  
  // 标签（用于结果分析）
  tags: {
    name: 'api-call',
    endpoint: '/users',
    method: 'GET',
  },
  
  // 超时设置
  timeout: '30s',
  
  // Cookies
  cookies: {
    session_id: 'abc123',
  },
  
  // 认证信息
  auth: 'user:pass',
  
  // 重定向配置
  redirects: 5,
  
  // 响应类型
  responseType: 'text', // 'text', 'binary', 'none'
};
```

## 2.3 响应处理

### 响应对象结构

```javascript
const response = http.get('https://httpbin.test.k6.io/get');

// 响应状态
console.log('Status:', response.status);
console.log('Status Text:', response.status_text);

// 响应头
console.log('Content-Type:', response.headers['Content-Type']);

// 响应体
console.log('Body:', response.body);

// 响应时间指标
console.log('Duration:', response.timings.duration);
console.log('Waiting:', response.timings.waiting);
console.log('Receiving:', response.timings.receiving);

// Cookies
console.log('Cookies:', response.cookies);
```

### JSON响应处理

```javascript
const response = http.get('https://httpbin.test.k6.io/json');

// 解析JSON
const json = response.json();

// 安全解析（避免解析错误导致测试失败）
const json = JSON.parse(response.body);

// 处理嵌套数据
if (json && json.slideshow && json.slideshow.slides) {
  const slides = json.slideshow.slides;
  console.log('Number of slides:', slides.length);
}
```

### 二进制响应处理

```javascript
// 下载文件
const response = http.get('https://httpbin.test.k6.io/bytes/1024');

// 处理二进制数据
const buffer = response.body;
console.log('File size:', buffer.length);

// 保存到文件（在k6云中）
// 注意：本地运行无法直接保存文件
```

## 2.4 检查点（Checks）

### 基本检查

```javascript
import { check } from 'k6';

const response = http.get('https://httpbin.test.k6.io/get');

// 单个检查
check(response, {
  'status is 200': (r) => r.status === 200,
});

// 多个检查
check(response, {
  'status is 200': (r) => r.status === 200,
  'response time < 500ms': (r) => r.timings.duration < 500,
  'has content type': (r) => r.headers['Content-Type'] === 'application/json',
  'response contains data': (r) => r.json().url !== undefined,
});
```

### 复杂检查逻辑

```javascript
// 检查数组长度
check(response, {
  'array has items': (r) => {
    const data = r.json();
    return Array.isArray(data.items) && data.items.length > 0;
  },
});

// 检查特定字段值
check(response, {
  'user id is correct': (r) => {
    const user = r.json();
    return user.id === 1 && user.name === 'Test User';
  },
});

// 检查正则表达式匹配
check(response, {
  'contains expected text': (r) => {
    return /expected pattern/i.test(r.body);
  },
});
```

### 检查分组

```javascript
// 对不同的API端点使用不同的检查组
const apiCheck = (response, endpoint) => {
  return check(response, {
    [`${endpoint} status is 200`]: (r) => r.status === 200,
    [`${endpoint} response time < 1s`]: (r) => r.timings.duration < 1000,
  });
};

// 使用检查组
const userResponse = http.get('https://api.example.com/users');
apiCheck(userResponse, 'get-users');

const productResponse = http.get('https://api.example.com/products');
apiCheck(productResponse, 'get-products');
```

## 2.5 分组（Groups）

### 基本分组

```javascript
import { group } from 'k6';

export default function () {
  // 用户登录流程分组
  group('user authentication', function () {
    const loginResponse = http.post('https://api.example.com/login', {
      username: 'testuser',
      password: 'testpass',
    });
    
    check(loginResponse, {
      'login successful': (r) => r.status === 200,
    });
  });
  
  // 用户操作分组
  group('user actions', function () {
    const profileResponse = http.get('https://api.example.com/profile');
    const settingsResponse = http.get('https://api.example.com/settings');
    
    check(profileResponse, { 'profile loaded': (r) => r.status === 200 });
    check(settingsResponse, { 'settings loaded': (r) => r.status === 200 });
  });
}
```

### 异步分组

```javascript
import { group } from 'k6';

export default function () {
  // 并行执行多个分组
  group('parallel operations', function () {
    // 这些操作会并行执行
    const promises = [
      http.getAsync('https://api.example.com/users'),
      http.getAsync('https://api.example.com/products'),
      http.getAsync('https://api.example.com/orders'),
    ];
    
    // 等待所有请求完成
    const responses = Promise.all(promises);
    
    // 处理响应
    responses.forEach((response, index) => {
      check(response, {
        [`request ${index} successful`]: (r) => r.status === 200,
      });
    });
  });
}
```

## 2.6 测试配置详解

### 虚拟用户配置

```javascript
export const options = {
  // 固定虚拟用户数
  vus: 10,
  duration: '5m',
  
  // 或者使用阶段式配置
  stages: [
    { duration: '2m', target: 100 },  // 2分钟内增加到100用户
    { duration: '5m', target: 100 },  // 保持100用户5分钟
    { duration: '2m', target: 0 },    // 2分钟内减少到0用户
  ],
  
  // 或者使用执行器
  executor: 'ramping-vus',
  startVUs: 0,
  stages: [
    { duration: '30s', target: 10 },
    { duration: '1m', target: 10 },
    { duration: '30s', target: 0 },
  ],
};
```

### 阈值配置

```javascript
export const options = {
  thresholds: {
    // HTTP请求相关阈值
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.01'],
    http_reqs: ['count>1000'],
    
    // 自定义指标阈值
    'my_custom_metric': ['avg<1000'],
    
    // 分组阈值
    'group_duration{group:auth}': ['avg<2000'],
    
    // 检查点阈值
    checks: ['rate>0.95'],
  },
};
```

### 环境变量和标签

```javascript
export const options = {
  // 环境变量
  env: {
    BASE_URL: __ENV.BASE_URL || 'https://test.k6.io',
    API_KEY: __ENV.API_KEY || 'default-key',
  },
  
  // 标签
  tags: {
    environment: __ENV.ENV || 'development',
    test_type: 'smoke',
    version: '1.0',
  },
};
```

## 2.7 实验：完整API测试场景

### 实验目标
创建一个完整的用户注册、登录、操作的API测试场景。

### 实验代码

```javascript
// 实验2：完整API测试场景
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
  return {
    testUser: {
      username: `testuser_${Date.now()}`,
      email: `test_${Date.now()}@example.com`,
      password: 'TestPass123!',
    },
  };
}

export default function (data) {
  let authToken = '';
  
  // 分组1：用户注册
  group('user registration', function () {
    const registerResponse = http.post(`${BASE_URL}/post`, {
      username: data.testUser.username,
      email: data.testUser.email,
      password: data.testUser.password,
    });
    
    check(registerResponse, {
      'registration successful': (r) => r.status === 200,
      'registration response contains data': (r) => {
        const json = r.json();
        return json.json.username === data.testUser.username;
      },
    });
    
    // 模拟注册后处理时间
    sleep(1);
  });
  
  // 分组2：用户登录
  group('user authentication', function () {
    const loginResponse = http.post(`${BASE_URL}/post`, {
      username: data.testUser.username,
      password: data.testUser.password,
    });
    
    check(loginResponse, {
      'login successful': (r) => r.status === 200,
      'login returns token': (r) => {
        const json = r.json();
        // 模拟获取token
        authToken = `token_${Date.now()}`;
        return authToken !== '';
      },
    });
    
    sleep(1);
  });
  
  // 分组3：用户操作（需要认证）
  if (authToken) {
    group('authenticated operations', function () {
      const headers = {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      };
      
      // 获取用户信息
      const profileResponse = http.get(`${BASE_URL}/get`, { headers });
      check(profileResponse, {
        'profile access successful': (r) => r.status === 200,
      });
      
      // 更新用户设置
      const settingsResponse = http.put(`${BASE_URL}/put`, 
        JSON.stringify({ theme: 'dark' }), 
        { headers }
      );
      check(settingsResponse, {
        'settings update successful': (r) => r.status === 200,
      });
      
      sleep(2);
    });
  }
  
  // 分组4：用户登出
  group('user logout', function () {
    const logoutResponse = http.post(`${BASE_URL}/post`, {});
    check(logoutResponse, {
      'logout successful': (r) => r.status === 200,
    });
    
    sleep(1);
  });
}

// 清理（可选）
export function teardown(data) {
  console.log('Test completed. Cleanup can be done here.');
}
```

### 实验结果分析

1. 观察不同分组的执行时间和成功率
2. 分析认证操作对整体性能的影响
3. 验证阈值配置是否合理
4. 检查标签系统是否正常工作

## 总结

本章我们深入学习了：
- k6脚本的完整结构
- HTTP请求的各种方法和参数配置
- 响应处理和检查点的使用
- 分组功能的使用
- 详细的测试配置选项

下一章我们将学习k6的高级功能和性能测试的最佳实践。
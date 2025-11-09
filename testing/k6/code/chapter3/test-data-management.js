// 第3章：测试数据管理示例
// 演示如何使用外部数据文件和动态数据生成

import http from 'k6/http';
import { check, sleep } from 'k6';
import { SharedArray } from 'k6/data';

// 使用外部数据文件（模拟）
// 注意：在实际使用中，需要创建对应的数据文件

// 模拟CSV数据
const mockUsers = [
  { id: 1, username: 'user1', email: 'user1@example.com', role: 'admin' },
  { id: 2, username: 'user2', email: 'user2@example.com', role: 'user' },
  { id: 3, username: 'user3', email: 'user3@example.com', role: 'user' },
  { id: 4, username: 'user4', email: 'user4@example.com', role: 'moderator' },
  { id: 5, username: 'user5', email: 'user5@example.com', role: 'user' }
];

// 模拟产品数据
const mockProducts = [
  { id: 1, name: 'Laptop', category: 'Electronics', price: 999.99 },
  { id: 2, name: 'Phone', category: 'Electronics', price: 699.99 },
  { id: 3, name: 'Tablet', category: 'Electronics', price: 399.99 },
  { id: 4, name: 'Headphones', category: 'Audio', price: 199.99 },
  { id: 5, name: 'Keyboard', category: 'Accessories', price: 89.99 }
];

// 使用SharedArray共享数据（模拟文件读取）
const users = new SharedArray('users', function () {
  // 模拟从CSV文件读取数据
  return mockUsers;
});

const products = new SharedArray('products', function () {
  // 模拟从JSON文件读取数据
  return mockProducts;
});

const BASE_URL = 'https://httpbin.test.k6.io';

export const options = {
  vus: 5,
  duration: '3m',
};

// 动态数据生成函数
function generateUser() {
  const firstNames = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace'];
  const lastNames = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller'];
  const domains = ['example.com', 'test.com', 'demo.org'];
  
  const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
  const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
  const domain = domains[Math.floor(Math.random() * domains.length)];
  
  return {
    firstName: firstName,
    lastName: lastName,
    email: `${firstName.toLowerCase()}.${lastName.toLowerCase()}@${domain}`,
    username: `${firstName}${lastName}${Math.floor(Math.random() * 1000)}`,
    password: `Pass${Math.floor(Math.random() * 10000)}!`,
    phone: `+1-555-${Math.floor(100 + Math.random() * 900)}-${Math.floor(1000 + Math.random() * 9000)}`
  };
}

function generateProduct() {
  const categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports', 'Beauty'];
  const adjectives = ['Amazing', 'Premium', 'Professional', 'Luxury', 'Standard', 'Economy'];
  const nouns = ['Product', 'Item', 'Goods', 'Merchandise', 'Commodity'];
  
  const category = categories[Math.floor(Math.random() * categories.length)];
  const adjective = adjectives[Math.floor(Math.random() * adjectives.length)];
  const noun = nouns[Math.floor(Math.random() * nouns.length)];
  
  return {
    name: `${adjective} ${noun}`,
    category: category,
    price: Math.round((Math.random() * 1000 + 10) * 100) / 100, // $10-$1010
    description: `High-quality ${category.toLowerCase()} product for everyday use`,
    inStock: Math.random() > 0.1 // 90% chance of being in stock
  };
}

export default function () {
  // 方法1：使用预定义数据
  group('predefined_data_test', function () {
    // 随机选择一个用户
    const user = users[Math.floor(Math.random() * users.length)];
    
    // 使用用户数据进行测试
    const userResponse = http.post(`${BASE_URL}/post`, {
      action: 'login',
      username: user.username,
      email: user.email,
      role: user.role
    });
    
    check(userResponse, {
      'user login with predefined data': (r) => r.status === 200,
      'response contains user data': (r) => {
        const json = r.json();
        return json.form.username === user.username;
      }
    });
    
    sleep(1);
    
    // 随机选择一个产品
    const product = products[Math.floor(Math.random() * products.length)];
    
    const productResponse = http.post(`${BASE_URL}/post`, {
      action: 'view_product',
      productId: product.id,
      productName: product.name,
      category: product.category,
      price: product.price
    });
    
    check(productResponse, {
      'product view with predefined data': (r) => r.status === 200
    });
    
    sleep(1);
  });
  
  // 方法2：使用动态生成的数据
  group('dynamic_data_test', function () {
    // 生成动态用户数据
    const dynamicUser = generateUser();
    
    const registerResponse = http.post(`${BASE_URL}/post`, {
      action: 'register',
      userData: dynamicUser
    });
    
    check(registerResponse, {
      'user registration with dynamic data': (r) => r.status === 200,
      'dynamic user data processed': (r) => {
        const json = r.json();
        return json.form.userData !== undefined;
      }
    });
    
    sleep(1);
    
    // 生成动态产品数据
    const dynamicProduct = generateProduct();
    
    const createProductResponse = http.post(`${BASE_URL}/post`, {
      action: 'create_product',
      productData: dynamicProduct
    });
    
    check(createProductResponse, {
      'product creation with dynamic data': (r) => r.status === 200
    });
    
    sleep(1);
  });
  
  // 方法3：混合使用预定义和动态数据
  group('mixed_data_test', function () {
    // 使用预定义用户
    const user = users[Math.floor(Math.random() * users.length)];
    
    // 生成动态订单数据
    const orderItems = [];
    const numItems = Math.floor(Math.random() * 3) + 1; // 1-3个商品
    
    for (let i = 0; i < numItems; i++) {
      const product = products[Math.floor(Math.random() * products.length)];
      orderItems.push({
        productId: product.id,
        productName: product.name,
        quantity: Math.floor(Math.random() * 3) + 1,
        price: product.price
      });
    }
    
    const orderData = {
      userId: user.id,
      username: user.username,
      items: orderItems,
      totalAmount: orderItems.reduce((sum, item) => sum + (item.price * item.quantity), 0),
      orderDate: new Date().toISOString()
    };
    
    const orderResponse = http.post(`${BASE_URL}/post`, {
      action: 'create_order',
      orderData: orderData
    });
    
    check(orderResponse, {
      'order creation with mixed data': (r) => r.status === 200,
      'order contains correct items': (r) => {
        const json = r.json();
        return json.form.orderData.items.length === numItems;
      }
    });
    
    sleep(2);
  });
  
  // 方法4：数据驱动测试
  group('data_driven_test', function () {
    // 测试不同的用户角色
    const testCases = [
      { role: 'admin', expectedAccess: 'full' },
      { role: 'moderator', expectedAccess: 'partial' },
      { role: 'user', expectedAccess: 'limited' },
      { role: 'guest', expectedAccess: 'minimal' }
    ];
    
    testCases.forEach(testCase => {
      const accessResponse = http.post(`${BASE_URL}/post`, {
        action: 'check_access',
        role: testCase.role,
        expectedAccess: testCase.expectedAccess
      });
      
      check(accessResponse, {
        [`access check for ${testCase.role} role`]: (r) => r.status === 200
      });
      
      sleep(0.5);
    });
  });
  
  // 方法5：性能测试数据生成
  group('performance_data_test', function () {
    // 生成大量测试数据用于性能测试
    const batchSize = 10;
    const batchRequests = [];
    
    for (let i = 0; i < batchSize; i++) {
      const user = generateUser();
      batchRequests.push([
        'POST',
        `${BASE_URL}/post`,
        {
          action: 'batch_user_creation',
          userIndex: i,
          userData: user
        }
      ]);
    }
    
    // 批量发送请求
    const batchResponses = http.batch(batchRequests);
    
    // 验证批量响应
    batchResponses.forEach((response, index) => {
      check(response, {
        [`batch request ${index} successful`]: (r) => r.status === 200
      });
    });
    
    sleep(1);
  });
}

// 数据验证函数
function validateUserData(user) {
  return user && 
         user.username && 
         user.email && 
         user.email.includes('@') &&
         user.password &&
         user.password.length >= 8;
}

function validateProductData(product) {
  return product &&
         product.name &&
         product.category &&
         product.price > 0 &&
         typeof product.inStock === 'boolean';
}

// 数据清理函数（模拟）
export function teardown() {
  console.log('Cleaning up test data...');
  
  // 在实际环境中，这里可以执行数据库清理操作
  const cleanupResponse = http.post(`${BASE_URL}/post`, {
    action: 'cleanup_test_data',
    timestamp: Date.now()
  });
  
  console.log('Test data cleanup completed');
}
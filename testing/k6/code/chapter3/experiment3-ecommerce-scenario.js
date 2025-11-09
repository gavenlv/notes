// 实验3：电商网站综合性能测试
// 创建一个完整的电商网站性能测试场景

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Counter, Trend, Rate } from 'k6/metrics';

// 自定义指标
const metrics = {
  // 业务指标
  successfulTransactions: new Counter('successful_transactions'),
  failedTransactions: new Counter('failed_transactions'),
  transactionDuration: new Trend('transaction_duration'),
  
  // 用户行为指标
  pageViews: new Counter('page_views'),
  productViews: new Counter('product_views'),
  cartAdditions: new Counter('cart_additions'),
  purchases: new Counter('purchases'),
  
  // 性能指标
  apiResponseTimes: new Trend('api_response_times'),
  errorRate: new Rate('error_rate'),
  conversionRate: new Rate('conversion_rate'),
  
  // 用户体验指标
  pageLoadTime: new Trend('page_load_time'),
  searchResponseTime: new Trend('search_response_time'),
  checkoutDuration: new Trend('checkout_duration')
};

const BASE_URL = 'https://httpbin.test.k6.io';

// 测试配置
export const options = {
  scenarios: {
    // 浏览型用户（70%流量）
    browser_users: {
      executor: 'constant-vus',
      vus: 35,
      duration: '10m',
      exec: 'browseBehavior',
      tags: { user_type: 'browser' },
    },
    
    // 搜索型用户（15%流量）
    searcher_users: {
      executor: 'constant-arrival-rate',
      rate: 3,
      timeUnit: '1s',
      duration: '10m',
      preAllocatedVUs: 10,
      maxVUs: 15,
      exec: 'searcherBehavior',
      tags: { user_type: 'searcher' },
    },
    
    // 购买型用户（10%流量）
    buyer_users: {
      executor: 'per-vu-iterations',
      vus: 5,
      iterations: 5,
      maxDuration: '10m',
      exec: 'buyerBehavior',
      tags: { user_type: 'buyer' },
    },
    
    // 管理员用户（5%流量）
    admin_users: {
      executor: 'shared-iterations',
      vus: 3,
      iterations: 10,
      maxDuration: '10m',
      exec: 'adminBehavior',
      tags: { user_type: 'admin' },
    },
  },
  
  thresholds: {
    // 全局阈值
    http_req_duration: ['p(95)<2000'],
    http_req_failed: ['rate<0.03'],
    
    // 用户类型特定阈值
    'http_req_duration{user_type:browser}': ['p(95)<1500'],
    'http_req_duration{user_type:searcher}': ['p(95)<1000'],
    'http_req_duration{user_type:buyer}': ['p(95)<3000'],
    'http_req_duration{user_type:admin}': ['p(95)<5000'],
    
    // 业务指标阈值
    'error_rate': ['rate<0.05'],
    'transaction_duration{user_type:buyer}': ['p(95)<10000'],
    'checkout_duration': ['p(95)<15000'],
  },
  
  tags: {
    environment: 'production',
    test_type: 'ecommerce',
    application: 'online-store'
  },
};

// 测试数据
export function setup() {
  console.log('Setting up ecommerce test data...');
  
  // 模拟产品数据
  const products = [];
  const categories = ['Electronics', 'Clothing', 'Home', 'Sports', 'Books', 'Beauty'];
  
  for (let i = 1; i <= 50; i++) {
    const category = categories[Math.floor(Math.random() * categories.length)];
    products.push({
      id: i,
      name: `Product ${i}`,
      category: category,
      price: Math.round((Math.random() * 500 + 10) * 100) / 100,
      rating: Math.round((Math.random() * 5) * 10) / 10,
      inStock: Math.random() > 0.1 // 90%有库存
    });
  }
  
  // 模拟用户数据
  const users = [];
  for (let i = 1; i <= 20; i++) {
    users.push({
      id: i,
      username: `testuser${i}`,
      email: `user${i}@test.com`,
      tier: Math.random() > 0.7 ? 'premium' : 'standard'
    });
  }
  
  return {
    products: products,
    users: users,
    startTime: Date.now(),
    testConfig: {
      baseUrl: BASE_URL,
      maxProductsPerPage: 20,
      searchTimeout: 5000,
      checkoutTimeout: 30000
    }
  };
}

// 浏览型用户行为
export function browseBehavior() {
  const userType = 'browser';
  
  group('browse_homepage', function () {
    const startTime = Date.now();
    
    const response = http.get(`${BASE_URL}/get?page=home`);
    metrics.pageViews.add(1);
    
    const loadTime = Date.now() - startTime;
    metrics.pageLoadTime.add(loadTime);
    
    check(response, {
      'homepage loaded successfully': (r) => r.status === 200,
      'homepage load time reasonable': (r) => loadTime < 3000
    });
    
    console.log(`Homepage loaded in ${loadTime}ms`);
    sleep(Math.random() * 5 + 3); // 浏览3-8秒
  });
  
  group('browse_categories', function () {
    const categories = ['electronics', 'clothing', 'home', 'sports'];
    const category = categories[Math.floor(Math.random() * categories.length)];
    
    const response = http.get(`${BASE_URL}/get?category=${category}`);
    metrics.pageViews.add(1);
    
    check(response, {
      'category page loaded': (r) => r.status === 200
    });
    
    sleep(Math.random() * 8 + 5); // 浏览5-13秒
  });
  
  group('view_product_details', function () {
    const productId = Math.floor(Math.random() * 50) + 1;
    
    const startTime = Date.now();
    const response = http.get(`${BASE_URL}/get?product=${productId}`);
    
    const loadTime = Date.now() - startTime;
    metrics.productViews.add(1);
    metrics.pageLoadTime.add(loadTime);
    
    check(response, {
      'product page loaded': (r) => r.status === 200,
      'product details available': (r) => r.json().url.includes('product=')
    });
    
    console.log(`Product ${productId} viewed in ${loadTime}ms`);
    sleep(Math.random() * 10 + 5); // 浏览5-15秒
  });
  
  // 30%的浏览用户会添加到购物车
  if (Math.random() < 0.3) {
    group('add_to_cart', function () {
      const productId = Math.floor(Math.random() * 50) + 1;
      const quantity = Math.floor(Math.random() * 3) + 1;
      
      const response = http.post(`${BASE_URL}/post`, {
        action: 'add_to_cart',
        productId: productId,
        quantity: quantity
      });
      
      metrics.cartAdditions.add(1);
      
      check(response, {
        'item added to cart': (r) => r.status === 200
      });
      
      console.log(`Product ${productId} added to cart`);
      sleep(2);
    });
  }
}

// 搜索型用户行为
export function searcherBehavior() {
  const userType = 'searcher';
  
  group('search_operations', function () {
    const searchTerms = [
      'laptop', 'phone', 'shirt', 'book', 'game',
      'watch', 'shoes', 'furniture', 'cosmetics', 'sports'
    ];
    
    const searchTerm = searchTerms[Math.floor(Math.random() * searchTerms.length)];
    
    const startTime = Date.now();
    const response = http.get(`${BASE_URL}/get?q=${searchTerm}`);
    
    const searchTime = Date.now() - startTime;
    metrics.searchResponseTime.add(searchTime);
    
    check(response, {
      'search completed successfully': (r) => r.status === 200,
      'search response time acceptable': (r) => searchTime < 2000
    });
    
    console.log(`Search for "${searchTerm}" completed in ${searchTime}ms`);
    
    // 查看搜索结果
    sleep(Math.random() * 3 + 2);
    
    // 50%的搜索用户会查看产品详情
    if (Math.random() < 0.5) {
      const productId = Math.floor(Math.random() * 10) + 1; // 查看前10个结果
      
      const productResponse = http.get(`${BASE_URL}/get?product=${productId}`);
      metrics.productViews.add(1);
      
      check(productResponse, {
        'search result product viewed': (r) => r.status === 200
      });
      
      sleep(Math.random() * 5 + 3);
    }
  });
  
  // 高级搜索功能
  if (Math.random() < 0.3) {
    group('advanced_search', function () {
      const filters = {
        category: ['electronics', 'clothing'][Math.floor(Math.random() * 2)],
        priceRange: '50-200',
        rating: '4+',
        inStock: true
      };
      
      const response = http.post(`${BASE_URL}/post`, {
        action: 'advanced_search',
        filters: filters
      });
      
      check(response, {
        'advanced search completed': (r) => r.status === 200
      });
      
      sleep(3);
    });
  }
}

// 购买型用户行为
export function buyerBehavior() {
  const userType = 'buyer';
  const transactionStart = Date.now();
  
  try {
    group('complete_purchase_flow', function () {
      // 1. 用户登录
      group('user_login', function () {
        const response = http.post(`${BASE_URL}/post`, {
          action: 'login',
          username: 'testuser',
          password: 'password'
        });
        
        check(response, {
          'user login successful': (r) => r.status === 200
        });
        
        sleep(1);
      });
      
      // 2. 浏览和选择产品
      group('product_selection', function () {
        const productsToAdd = [];
        const numProducts = Math.floor(Math.random() * 3) + 1; // 1-3个产品
        
        for (let i = 0; i < numProducts; i++) {
          const productId = Math.floor(Math.random() * 50) + 1;
          const quantity = Math.floor(Math.random() * 2) + 1;
          productsToAdd.push({ productId, quantity });
        }
        
        // 添加到购物车
        productsToAdd.forEach(item => {
          const response = http.post(`${BASE_URL}/post`, {
            action: 'add_to_cart',
            productId: item.productId,
            quantity: item.quantity
          });
          
          metrics.cartAdditions.add(1);
          check(response, { 'item added to cart': (r) => r.status === 200 });
        });
        
        sleep(2);
      });
      
      // 3. 查看购物车
      group('review_cart', function () {
        const response = http.get(`${BASE_URL}/get?action=cart`);
        
        check(response, {
          'cart review successful': (r) => r.status === 200
        });
        
        sleep(2);
      });
      
      // 4. 结算流程
      group('checkout_process', function () {
        const checkoutStart = Date.now();
        
        // 选择配送地址
        const addressResponse = http.post(`${BASE_URL}/post`, {
          action: 'select_address',
          addressId: 1
        });
        
        check(addressResponse, { 'address selected': (r) => r.status === 200 });
        sleep(1);
        
        // 选择支付方式
        const paymentResponse = http.post(`${BASE_URL}/post`, {
          action: 'select_payment',
          method: 'credit_card'
        });
        
        check(paymentResponse, { 'payment method selected': (r) => r.status === 200 });
        sleep(1);
        
        // 确认订单
        const orderResponse = http.post(`${BASE_URL}/post`, {
          action: 'place_order',
          totalAmount: Math.round((Math.random() * 500 + 10) * 100) / 100
        });
        
        const checkoutTime = Date.now() - checkoutStart;
        metrics.checkoutDuration.add(checkoutTime);
        
        check(orderResponse, {
          'order placed successfully': (r) => r.status === 200,
          'checkout completed in reasonable time': (r) => checkoutTime < 15000
        });
        
        console.log(`Checkout completed in ${checkoutTime}ms`);
        
        // 记录购买成功
        metrics.purchases.add(1);
        metrics.conversionRate.add(true);
      });
      
      // 5. 订单确认
      group('order_confirmation', function () {
        const response = http.get(`${BASE_URL}/get?action=order_confirmation`);
        
        check(response, {
          'order confirmation received': (r) => r.status === 200
        });
        
        sleep(3);
      });
    });
    
    // 记录成功交易
    const transactionTime = Date.now() - transactionStart;
    metrics.successfulTransactions.add(1);
    metrics.transactionDuration.add(transactionTime);
    metrics.errorRate.add(true);
    
    console.log(`Purchase transaction completed successfully in ${transactionTime}ms`);
    
  } catch (error) {
    // 记录失败交易
    metrics.failedTransactions.add(1);
    metrics.errorRate.add(false);
    metrics.conversionRate.add(false);
    
    console.error('Purchase transaction failed:', error.message);
  }
}

// 管理员用户行为
export function adminBehavior() {
  const userType = 'admin';
  
  group('admin_dashboard', function () {
    const response = http.get(`${BASE_URL}/get?action=admin_dashboard`);
    
    check(response, {
      'admin dashboard accessible': (r) => r.status === 200
    });
    
    sleep(5);
  });
  
  group('product_management', function () {
    // 查看产品列表
    const productsResponse = http.get(`${BASE_URL}/get?action=admin_products`);
    check(productsResponse, { 'product list loaded': (r) => r.status === 200 });
    
    sleep(2);
    
    // 更新产品信息（30%概率）
    if (Math.random() < 0.3) {
      const updateResponse = http.post(`${BASE_URL}/post`, {
        action: 'update_product',
        productId: Math.floor(Math.random() * 50) + 1,
        price: Math.round((Math.random() * 100 + 10) * 100) / 100
      });
      
      check(updateResponse, { 'product updated': (r) => r.status === 200 });
    }
    
    sleep(3);
  });
  
  group('order_management', function () {
    // 查看订单列表
    const ordersResponse = http.get(`${BASE_URL}/get?action=admin_orders`);
    check(ordersResponse, { 'order list loaded': (r) => r.status === 200 });
    
    sleep(2);
    
    // 处理订单（20%概率）
    if (Math.random() < 0.2) {
      const processResponse = http.post(`${BASE_URL}/post`, {
        action: 'process_order',
        orderId: Math.floor(Math.random() * 100) + 1
      });
      
      check(processResponse, { 'order processed': (r) => r.status === 200 });
    }
    
    sleep(3);
  });
  
  group('analytics_review', function () {
    // 查看分析报告
    const analyticsResponse = http.get(`${BASE_URL}/get?action=analytics`);
    check(analyticsResponse, { 'analytics loaded': (r) => r.status === 200 });
    
    sleep(10); // 管理员会花更多时间分析数据
  });
}

// 测试结果分析
export function teardown(data) {
  const totalDuration = Date.now() - data.startTime;
  
  console.log('=== Ecommerce Performance Test Results ===');
  console.log(`Test duration: ${Math.round(totalDuration / 1000)} seconds`);
  console.log(`Products in catalog: ${data.products.length}`);
  console.log(`Test users: ${data.users.length}`);
  console.log('');
  
  console.log('=== Business Metrics ===');
  console.log('Total page views:', metrics.pageViews);
  console.log('Product views:', metrics.productViews);
  console.log('Cart additions:', metrics.cartAdditions);
  console.log('Successful purchases:', metrics.purchases);
  
  if (metrics.cartAdditions > 0) {
    const conversionRate = (metrics.purchases / metrics.cartAdditions) * 100;
    console.log(`Conversion rate: ${conversionRate.toFixed(2)}%`);
  }
  
  console.log('');
  console.log('=== Performance Metrics ===');
  console.log('Successful transactions:', metrics.successfulTransactions);
  console.log('Failed transactions:', metrics.failedTransactions);
  
  const totalTransactions = metrics.successfulTransactions + metrics.failedTransactions;
  if (totalTransactions > 0) {
    const successRate = (metrics.successfulTransactions / totalTransactions) * 100;
    console.log(`Transaction success rate: ${successRate.toFixed(2)}%`);
  }
  
  console.log('');
  console.log('=== Recommendations ===');
  
  if (metrics.failedTransactions > totalTransactions * 0.1) {
    console.log('⚠ High transaction failure rate - review checkout process');
  }
  
  if (metrics.errorRate > 0.05) {
    console.log('⚠ High error rate - investigate system stability');
  }
  
  console.log('✅ Ecommerce performance test completed successfully');
}
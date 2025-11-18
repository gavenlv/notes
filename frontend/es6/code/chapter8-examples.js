// 第8章：模块化与导入导出 - 代码示例

// ===== 8.1 模块化的必要性 =====

// 传统JavaScript的问题
// script1.js
var data = { name: "Alice", age: 30 };
function processData() {
  console.log("Processing data:", data);
}

// script2.js
var data = { name: "Bob", age: 25 }; // 覆盖了script1.js中的data变量
function processData() {
  console.log("Different processing:", data);
}

// ===== 8.2 导入导出语法 =====

// 命名导出示例
// math.js
export function add(a, b) {
  return a + b;
}

export function subtract(a, b) {
  return a - b;
}

export const PI = 3.14159;

export class Calculator {
  multiply(a, b) {
    return a * b;
  }
  
  divide(a, b) {
    if (b === 0) {
      throw new Error("Division by zero");
    }
    return a / b;
  }
}

// 先定义再导出
// utils.js
function formatDate(date) {
  return date.toISOString().split('T')[0];
}

function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

const API_URL = 'https://api.example.com';

export { formatDate, validateEmail, API_URL };

// 使用as关键字重命名导出
// user.js
function createUser(name, email) {
  return { id: Date.now(), name, email };
}

function updateUser(id, data) {
  // 更新用户逻辑
  return { id, ...data };
}

export { createUser as create, updateUser as update };

// 默认导出示例
// config.js
export default {
  apiUrl: 'https://api.example.com',
  timeout: 5000,
  retries: 3,
  headers: {
    'Content-Type': 'application/json'
  }
};

// 默认导出函数
// httpClient.js
export default class HttpClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
  }
  
  get(url) {
    return fetch(`${this.baseUrl}${url}`)
      .then(response => response.json());
  }
  
  post(url, data) {
    return fetch(`${this.baseUrl}${url}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
    .then(response => response.json());
  }
}

// 先定义再默认导出
// logger.js
class Logger {
  log(message) {
    console.log(`[${new Date().toISOString()}] ${message}`);
  }
  
  error(message) {
    console.error(`[${new Date().toISOString()}] ERROR: ${message}`);
  }
  
  warn(message) {
    console.warn(`[${new Date().toISOString()}] WARNING: ${message}`);
  }
}

export default Logger;

// 导入示例
// main.js
// 导入命名导出
import { add, subtract, PI } from './math.js';

console.log(add(5, 3)); // 8
console.log(subtract(5, 3)); // 2
console.log(PI); // 3.14159

// 使用as关键字重命名导入
import { formatDate as format, validateEmail as validate } from './utils.js';

const today = format(new Date());
const isValid = validate('user@example.com');

// 导入默认导出
import config from './config.js';
import HttpClient from './httpClient.js';

const client = new HttpClient(config.apiUrl);

// 混合导入
import defaultExport, { namedExport1, namedExport2 } from './module.js';

// 导入所有内容到命名空间
import * as math from './math.js';

console.log(math.add(5, 3)); // 8
console.log(math.subtract(5, 3)); // 2
console.log(math.PI); // 3.14159

// 仅导入模块（用于副作用）
import './polyfills.js'; // 执行polyfills.js中的代码，但不导入任何值

// 重新导出示例
// utils/index.js
export { formatDate, validateEmail } from './dateUtils.js';
export { API_URL } from './config.js';
export default from './logger.js';

// 重新导出所有内容
export * from './dateUtils.js';
export * from './stringUtils.js';

// ===== 8.3 默认导出与命名导出 =====

// 默认导出示例
// axios.js
export default class Axios {
  constructor(config) {
    this.config = config;
  }
  
  get(url) {
    // GET请求逻辑
  }
  
  post(url, data) {
    // POST请求逻辑
  }
}

// 命名导出示例
// math.js
export function add(a, b) { return a + b; }
export function subtract(a, b) { return a - b; }
export function multiply(a, b) { return a * b; }
export function divide(a, b) { return a / b; }

// 常量集合
export const API_BASE_URL = 'https://api.example.com';
export const MAX_RETRY_ATTEMPTS = 3;
export const DEFAULT_TIMEOUT = 5000;

// 混合使用示例
// http.js
export default class HttpClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
  }
  
  get(url) {
    return fetch(`${this.baseUrl}${url}`)
      .then(response => response.json());
  }
}

export function get(url, options) {
  // 辅助函数
  return fetch(url, options).then(response => response.json());
}

export function post(url, data, options) {
  // 辅助函数
  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers
    },
    body: JSON.stringify(data)
  }).then(response => response.json());
}

export const METHODS = {
  GET: 'GET',
  POST: 'POST',
  PUT: 'PUT',
  DELETE: 'DELETE'
};

// 使用混合导入
// main.js
import HttpClient, { get, post, METHODS } from './http.js';

const client = new HttpClient('https://api.example.com');
client.get('/api/data'); // 使用默认导出

// 或者使用辅助函数
get('/api/data', { method: METHODS.GET });

// ===== 8.4 动态导入 =====

// 基本语法
import('./math.js')
  .then(math => {
    console.log(math.add(5, 3)); // 8
    console.log(math.subtract(5, 3)); // 2
  })
  .catch(error => {
    console.error('Failed to load module:', error);
  });

// 使用async/await语法
async function loadMathModule() {
  try {
    const math = await import('./math.js');
    console.log(math.add(5, 3)); // 8
    console.log(math.subtract(5, 3)); // 2
  } catch (error) {
    console.error('Failed to load module:', error);
  }
}

// 条件加载
async function loadTheme(theme) {
  if (theme === 'dark') {
    const { applyDarkTheme } = await import('./themes/dark.js');
    applyDarkTheme();
  } else {
    const { applyLightTheme } = await import('./themes/light.js');
    applyLightTheme();
  }
}

// 懒加载
// 路由懒加载示例
const routes = [
  {
    path: '/home',
    component: () => import('./views/Home.js')
  },
  {
    path: '/about',
    component: () => import('./views/About.js')
  }
];

// 代码分割
// 按需加载大型库
document.getElementById('load-chart').addEventListener('click', async () => {
  const { Chart } = await import('./chart-library.js');
  const chart = new Chart(document.getElementById('chart-container'));
  // 使用图表库
});

// ===== 8.5 实际应用场景 =====

// 构建大型应用
// app.js - 应用入口
import Router from './router/Router.js';
import { UserService } from './services/UserService.js';
import { AuthService } from './services/AuthService.js';
import './styles/main.css';

// 初始化应用
const router = new Router();
const userService = new UserService();
const authService = new AuthService();

// 配置路由
router.addRoute('/login', () => import('./views/Login.js'));
router.addRoute('/dashboard', () => import('./views/Dashboard.js'));
router.addRoute('/profile', () => import('./views/Profile.js'));

// 启动应用
router.start();

// 创建可复用组件库
// components/Button.js
export default class Button {
  constructor(text, onClick) {
    this.text = text;
    this.onClick = onClick;
  }
  
  render() {
    const button = document.createElement('button');
    button.textContent = this.text;
    button.addEventListener('click', this.onClick);
    return button;
  }
}

// components/Modal.js
export default class Modal {
  constructor(title, content) {
    this.title = title;
    this.content = content;
  }
  
  show() {
    // 创建模态框元素
    const modal = document.createElement('div');
    modal.className = 'modal';
    
    const header = document.createElement('div');
    header.className = 'modal-header';
    header.textContent = this.title;
    
    const body = document.createElement('div');
    body.className = 'modal-body';
    body.textContent = this.content;
    
    modal.appendChild(header);
    modal.appendChild(body);
    
    document.body.appendChild(modal);
  }
  
  hide() {
    const modal = document.querySelector('.modal');
    if (modal) {
      document.body.removeChild(modal);
    }
  }
}

// components/index.js - 组件库入口
import Button from './Button.js';
import Modal from './Modal.js';

export { Button, Modal };
export default { Button, Modal };

// 使用组件库
// app.js
import { Button, Modal } from './components/index.js';

const button = new Button('Click me', () => {
  const modal = new Modal('Hello', 'This is a modal dialog');
  modal.show();
});

document.body.appendChild(button.render());

// 配置管理
// config/index.js
import development from './development.js';
import production from './production.js';

const environment = process.env.NODE_ENV || 'development';

export default environment === 'production' ? production : development;

// config/development.js
export default {
  apiUrl: 'http://localhost:3000/api',
  logLevel: 'debug',
  enableMockData: true
};

// config/production.js
export default {
  apiUrl: 'https://api.example.com',
  logLevel: 'error',
  enableMockData: false
};

// 使用配置
// app.js
import config from './config/index.js';

console.log(`API URL: ${config.apiUrl}`);
console.log(`Log Level: ${config.logLevel}`);

// ===== 8.6 实践练习 =====

// 练习1：创建数学工具库
// math/utils.js
export function add(a, b) {
  return a + b;
}

export function subtract(a, b) {
  return a - b;
}

export function multiply(a, b) {
  return a * b;
}

export function divide(a, b) {
  if (b === 0) {
    throw new Error('Division by zero');
  }
  return a / b;
}

export const PI = 3.14159;

export default {
  add,
  subtract,
  multiply,
  divide,
  PI
};

// math/advanced.js
import { PI } from './utils.js';

export function circleArea(radius) {
  return PI * radius * radius;
}

export function circleCircumference(radius) {
  return 2 * PI * radius;
}

export function factorial(n) {
  if (n <= 1) return 1;
  return n * factorial(n - 1);
}

// math/index.js
export * from './utils.js';
export * from './advanced.js';

// 使用数学工具库
// app.js
import math from './math/index.js';

console.log(math.add(5, 3)); // 8
console.log(math.circleArea(5)); // 78.53975
console.log(math.factorial(5)); // 120

// 或者使用命名导入
import { add, circleArea, factorial } from './math/index.js';

console.log(add(5, 3)); // 8
console.log(circleArea(5)); // 78.53975
console.log(factorial(5)); // 120

// 练习2：实现动态加载的图片库
// imageProcessors/jpeg.js
export default class JpegProcessor {
  process(imageData) {
    console.log('Processing JPEG image');
    // JPEG处理逻辑
    return imageData;
  }
}

// imageProcessors/png.js
export default class PngProcessor {
  process(imageData) {
    console.log('Processing PNG image');
    // PNG处理逻辑
    return imageData;
  }
}

// imageProcessors/gif.js
export default class GifProcessor {
  process(imageData) {
    console.log('Processing GIF image');
    // GIF处理逻辑
    return imageData;
  }
}

// imageProcessor.js
class ImageProcessor {
  async processImage(imageData, format) {
    try {
      const Processor = await import(`./imageProcessors/${format}.js`);
      const processor = new Processor.default();
      return processor.process(imageData);
    } catch (error) {
      throw new Error(`Unsupported image format: ${format}`);
    }
  }
}

export default ImageProcessor;

// 使用图片处理器
// app.js
import ImageProcessor from './imageProcessor.js';

const processor = new ImageProcessor();

// 处理JPEG图片
const jpegData = new Uint8Array([255, 216, 255, 224]); // JPEG文件头示例
processor.processImage(jpegData, 'jpeg')
  .then(processedImage => {
    console.log('JPEG processed successfully');
  })
  .catch(error => {
    console.error('Error processing JPEG:', error);
  });

// 处理PNG图片
const pngData = new Uint8Array([137, 80, 78, 71, 13, 10, 26, 10]); // PNG文件头示例
processor.processImage(pngData, 'png')
  .then(processedImage => {
    console.log('PNG processed successfully');
  })
  .catch(error => {
    console.error('Error processing PNG:', error);
  });

// 练习3：创建支持多语言的国际化库
// i18n/locales/en.js
export default {
  greeting: 'Hello',
  farewell: 'Goodbye',
  thankYou: 'Thank you',
  welcome: 'Welcome to our application'
};

// i18n/locales/zh.js
export default {
  greeting: '你好',
  farewell: '再见',
  thankYou: '谢谢',
  welcome: '欢迎使用我们的应用'
};

// i18n/i18n.js
class I18n {
  constructor(defaultLocale = 'en') {
    this.defaultLocale = defaultLocale;
    this.currentLocale = defaultLocale;
    this.messages = {};
  }
  
  async loadLocale(locale) {
    try {
      const messages = await import(`./locales/${locale}.js`);
      this.messages[locale] = messages.default;
      return true;
    } catch (error) {
      console.error(`Failed to load locale: ${locale}`, error);
      return false;
    }
  }
  
  async setLocale(locale) {
    if (!this.messages[locale]) {
      const loaded = await this.loadLocale(locale);
      if (!loaded) return false;
    }
    
    this.currentLocale = locale;
    return true;
  }
  
  t(key, locale = this.currentLocale) {
    if (!this.messages[locale]) {
      console.warn(`Locale not loaded: ${locale}, falling back to ${this.defaultLocale}`);
      locale = this.defaultLocale;
    }
    
    if (!this.messages[locale]) {
      console.warn(`Default locale not loaded: ${this.defaultLocale}`);
      return key;
    }
    
    return this.messages[locale][key] || key;
  }
}

export default I18n;

// 使用国际化库
// app.js
import I18n from './i18n/i18n.js';

const i18n = new I18n('en');

// 加载并设置语言
(async () => {
  await i18n.loadLocale('en');
  await i18n.loadLocale('zh');
  
  // 使用英文
  console.log(i18n.t('greeting')); // Hello
  console.log(i18n.t('welcome')); // Welcome to our application
  
  // 切换到中文
  await i18n.setLocale('zh');
  console.log(i18n.t('greeting')); // 你好
  console.log(i18n.t('welcome')); // 欢迎使用我们的应用
})();

// ===== 8.7 最佳实践 =====

// 模块设计原则
// utils/string.js - 只处理字符串相关功能
export function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

export function truncate(str, length) {
  return str.length > length ? str.slice(0, length) + '...' : str;
}

// utils/array.js - 只处理数组相关功能
export function unique(arr) {
  return [...new Set(arr)];
}

export function chunk(arr, size) {
  const chunks = [];
  for (let i = 0; i < arr.length; i += size) {
    chunks.push(arr.slice(i, i + size));
  }
  return chunks;
}

// 导入导出规范
// 好的导入示例
import React, { useState, useEffect } from 'react';
import { Button, Modal } from './components';
import { formatDate, validateEmail } from './utils';
import config from './config';

// 避免的导入示例
// import * as utils from './utils';
// import * as components from './components';

// 性能优化
// 按需加载示例
async function loadAdminPanel() {
  if (user.isAdmin) {
    const { AdminPanel } = await import('./admin/AdminPanel.js');
    return new AdminPanel();
  }
  return null;
}

// 预加载示例
function preloadCriticalModules() {
  // 预加载关键模块
  import('./critical/module1.js');
  import('./critical/module2.js');
}

// ===== 8.8 常见问题与解决方案 =====

// 循环依赖问题
// a.js
import { bFunction } from './b.js';

export function aFunction() {
  console.log('aFunction called');
  bFunction();
}

// b.js
import { aFunction } from './a.js';

export function bFunction() {
  console.log('bFunction called');
  aFunction();
}

// 解决方案1：提取共同部分
// common.js
export function sharedFunction() {
  console.log('Shared function called');
}

// a.js
import { sharedFunction } from './common.js';

export function aFunction() {
  console.log('aFunction called');
  sharedFunction();
}

// b.js
import { sharedFunction } from './common.js';

export function bFunction() {
  console.log('bFunction called');
  sharedFunction();
}

// 模块路径问题
// 错误的导入
// import utils from 'utils'; // 缺少文件扩展名和相对路径

// 正确的导入
import utils from './utils.js';
import helper from '../helpers/helper.js';

// 使用导入映射(在HTML中)
/*
<script type="importmap">
{
  "imports": {
    "utils": "/js/utils.js",
    "components/": "/js/components/"
  }
}
</script>
*/

// 然后可以在代码中使用
// import utils from 'utils';
// import Button from 'components/Button.js';

// 模块兼容性问题
// CommonJS模块
// commonjs-module.js
/*
module.exports = {
  add: function(a, b) { return a + b; },
  subtract: function(a, b) { return a - b; }
};
*/

// ES6模块中导入CommonJS模块
// import { add, subtract } from './commonjs-module.js'; // 可能不工作

// 解决方案：使用默认导入
// import commonjsModule from './commonjs-module.js';
// const { add, subtract } = commonjsModule;

// 动态导入与打包工具
// 动态导入
// const module = await import(`./modules/${moduleName}.js`);

// 使用Webpack魔法注释
/*
const module = await import(
  // webpackChunkName: "module-[request]"
  `./modules/${moduleName}.js`
);
*/
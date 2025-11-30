# 第11章：JavaScript实战项目

## 11.1 项目概述

本章将通过一个完整的实战项目，综合运用前面章节学到的JavaScript知识，从零开始构建一个功能丰富的单页应用(SPA)。这个项目将涵盖现代前端开发的各个方面，包括组件化设计、状态管理、路由、API交互、性能优化等。

### 11.1.1 项目目标

我们将构建一个**任务管理应用**，具有以下功能：
1. 用户认证（登录/注册）
2. 任务CRUD操作（创建、读取、更新、删除）
3. 任务分类和标签
4. 任务搜索和过滤
5. 数据可视化（任务统计图表）
6. 响应式设计
7. 离线支持和数据同步

### 11.1.2 技术栈选择

为了确保项目的实用性和教学价值，我们将使用以下技术栈：

- **核心语言**: ES2021+ JavaScript
- **构建工具**: Vite (开发体验好，构建速度快)
- **CSS框架**: 自定义CSS (重点展示原生CSS能力)
- **状态管理**: 自定义状态管理器 (展示状态管理原理)
- **路由**: 自定义路由器 (展示路由实现原理)
- **图表库**: Chart.js (轻量级图表库)
- **数据存储**: localStorage + IndexedDB (离线存储)
- **API交互**: Fetch API + 模拟API服务器

### 11.1.3 项目结构

```
task-manager/
├── index.html                 # 入口HTML文件
├── src/
│   ├── index.js               # 应用入口
│   ├── main.js                # 主应用逻辑
│   ├── styles/
│   │   ├── main.css           # 主样式文件
│   │   ├── components/        # 组件样式
│   │   └── utils/             # 工具样式
│   ├── components/            # UI组件
│   │   ├── common/            # 通用组件
│   │   ├── auth/              # 认证组件
│   │   ├── tasks/             # 任务相关组件
│   │   └── dashboard/         # 仪表板组件
│   ├── state/                 # 状态管理
│   │   ├── store.js           # 状态存储
│   │   ├── actions.js         # 状态操作
│   │   └── reducers.js        # 状态更新逻辑
│   ├── router/                # 路由
│   │   └── router.js          # 路由器
│   ├── services/              # 服务层
│   │   ├── api.js             # API服务
│   │   ├── storage.js         # 存储服务
│   │   └── auth.js            # 认证服务
│   ├── utils/                 # 工具函数
│   │   ├── helpers.js         # 通用助手函数
│   │   ├── constants.js       # 常量定义
│   │   └── validators.js      # 验证函数
│   └── pages/                 # 页面组件
│       ├── Login.js           # 登录页面
│       ├── Dashboard.js       # 仪表板页面
│       ├── TaskList.js        # 任务列表页面
│       └── Profile.js         # 个人资料页面
└── public/                    # 静态资源
    ├── icons/                 # 图标
    └── images/                # 图片
```

## 11.2 项目搭建与基础配置

### 11.2.1 初始化项目

首先，我们创建基本的项目结构并配置开发环境。

```bash
# 创建项目目录
mkdir task-manager && cd task-manager

# 初始化package.json
npm init -y

# 安装依赖
npm install --save-dev vite
npm install chart.js

# 创建项目结构
mkdir -p src/{styles/{components,utils},components/{common,auth,tasks,dashboard},state,router,services,utils,pages,public/{icons,images}}
```

### 11.2.2 配置Vite

创建`vite.config.js`文件：

```javascript
// vite.config.js
import { defineConfig } from 'vite';

export default defineConfig({
  root: '.', // 设置根目录
  server: {
    port: 3000,
    open: true
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      input: {
        main: './index.html'
      }
    }
  },
  publicDir: 'public',
  optimizeDeps: {
    include: ['chart.js']
  }
});
```

### 11.2.3 创建入口HTML

```html
<!-- index.html -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>任务管理系统</title>
  <meta name="description" content="一个功能丰富的任务管理应用" />
  <link rel="stylesheet" href="./src/styles/main.css" />
</head>
<body>
  <div id="app">
    <header class="app-header">
      <nav class="navbar">
        <div class="navbar-brand">
          <h1>任务管理器</h1>
        </div>
        <ul class="navbar-nav">
          <li><a href="#/" data-route>首页</a></li>
          <li><a href="#/tasks" data-route>任务</a></li>
          <li><a href="#/stats" data-route>统计</a></li>
          <li><a href="#/profile" data-route>个人资料</a></li>
        </ul>
        <div class="navbar-actions">
          <div id="user-info" class="user-info" style="display: none;">
            <span id="username"></span>
            <button id="logout-btn" class="btn btn-ghost">退出</button>
          </div>
          <div id="auth-buttons">
            <button id="login-btn" class="btn btn-outline">登录</button>
            <button id="register-btn" class="btn btn-primary">注册</button>
          </div>
        </div>
      </nav>
    </header>
    
    <main class="app-main">
      <div id="app-content" class="container">
        <!-- 动态内容将在这里渲染 -->
      </div>
    </main>
    
    <footer class="app-footer">
      <p>&copy; 2023 任务管理系统. 使用 JavaScript 构建的教育项目.</p>
    </footer>
  </div>
  
  <!-- 模态框容器 -->
  <div id="modal-container"></div>
  
  <!-- 通知容器 -->
  <div id="notification-container" class="notification-container"></div>
  
  <script type="module" src="./src/index.js"></script>
</body>
</html>
```

### 11.2.4 基础样式设置

```css
/* src/styles/main.css */
:root {
  --primary-color: #4a6cf7;
  --secondary-color: #6c757d;
  --success-color: #28a745;
  --danger-color: #dc3545;
  --warning-color: #ffc107;
  --info-color: #17a2b8;
  --light-color: #f8f9fa;
  --dark-color: #212529;
  
  --font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
  --font-size-base: 1rem;
  --line-height-base: 1.5;
  
  --border-radius: 0.375rem;
  --box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  --transition: all 0.2s ease-in-out;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-family);
  font-size: var(--font-size-base);
  line-height: var(--line-height-base);
  color: var(--dark-color);
  background-color: var(--light-color);
}

.app-header {
  background-color: white;
  box-shadow: var(--box-shadow);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  max-width: 1200px;
  margin: 0 auto;
}

.navbar-brand h1 {
  font-size: 1.5rem;
  color: var(--primary-color);
}

.navbar-nav {
  display: flex;
  list-style: none;
  gap: 1rem;
}

.navbar-nav a {
  text-decoration: none;
  color: var(--dark-color);
  padding: 0.5rem 1rem;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.navbar-nav a:hover,
.navbar-nav a.active {
  background-color: var(--light-color);
  color: var(--primary-color);
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.app-main {
  min-height: calc(100vh - 60px - 60px);
  padding: 2rem 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.app-footer {
  background-color: white;
  padding: 1rem;
  text-align: center;
  border-top: 1px solid #e9ecef;
}

/* 通用按钮样式 */
.btn {
  display: inline-block;
  font-weight: 400;
  text-align: center;
  white-space: nowrap;
  vertical-align: middle;
  user-select: none;
  border: 1px solid transparent;
  padding: 0.375rem 0.75rem;
  font-size: 1rem;
  line-height: 1.5;
  border-radius: var(--border-radius);
  transition: var(--transition);
  cursor: pointer;
}

.btn-primary {
  color: white;
  background-color: var(--primary-color);
  border-color: var(--primary-color);
}

.btn-primary:hover {
  background-color: #3a5bd9;
  border-color: #3a5bd9;
}

.btn-outline {
  color: var(--primary-color);
  background-color: transparent;
  background-image: none;
  border-color: var(--primary-color);
}

.btn-outline:hover {
  color: white;
  background-color: var(--primary-color);
}

.btn-ghost {
  color: var(--secondary-color);
  background-color: transparent;
  border: none;
}

.btn-ghost:hover {
  color: var(--dark-color);
}

/* 通知样式 */
.notification-container {
  position: fixed;
  top: 80px;
  right: 20px;
  z-index: 1050;
}

.notification {
  background-color: white;
  border-radius: var(--border-radius);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
  padding: 1rem;
  margin-bottom: 0.5rem;
  min-width: 300px;
  display: flex;
  align-items: center;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.notification.success {
  border-left: 4px solid var(--success-color);
}

.notification.error {
  border-left: 4px solid var(--danger-color);
}

.notification.warning {
  border-left: 4px solid var(--warning-color);
}

.notification.info {
  border-left: 4px solid var(--info-color);
}

/* 模态框样式 */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1040;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal {
  background-color: white;
  border-radius: var(--border-radius);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  padding: 1rem;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  margin: 0;
  font-size: 1.25rem;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  line-height: 1;
  color: var(--secondary-color);
  cursor: pointer;
}

.modal-body {
  padding: 1rem;
}

.modal-footer {
  padding: 1rem;
  border-top: 1px solid #e9ecef;
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .navbar {
    flex-direction: column;
    gap: 1rem;
  }
  
  .navbar-nav {
    width: 100%;
    justify-content: center;
  }
  
  .navbar-actions {
    width: 100%;
    justify-content: center;
  }
  
  .modal {
    width: 95%;
  }
}

/* 表单样式 */
.form-group {
  margin-bottom: 1rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-control {
  display: block;
  width: 100%;
  padding: 0.375rem 0.75rem;
  font-size: 1rem;
  line-height: 1.5;
  color: var(--dark-color);
  background-color: white;
  border: 1px solid #ced4da;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.form-control:focus {
  color: var(--dark-color);
  background-color: white;
  border-color: var(--primary-color);
  outline: 0;
  box-shadow: 0 0 0 0.2rem rgba(74, 108, 247, 0.25);
}

.form-text {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: var(--secondary-color);
}
```

## 11.3 路由系统实现

### 11.3.1 路由器核心实现

```javascript
// src/router/router.js
class Router {
  constructor(routes) {
    this.routes = routes;
    this.currentRoute = null;
    this.history = window.history;
    this.init();
  }
  
  init() {
    // 监听浏览器前进后退
    window.addEventListener('popstate', (event) => {
      this.handleRouteChange();
    });
    
    // 监听页面加载
    window.addEventListener('load', () => {
      this.handleRouteChange();
    });
    
    // 拦截导航链接点击
    document.addEventListener('click', (event) => {
      const link = event.target.closest('[data-route]');
      if (link) {
        event.preventDefault();
        const href = link.getAttribute('href');
        this.navigate(href);
      }
    });
    
    // 初始路由
    this.handleRouteChange();
  }
  
  navigate(path) {
    this.history.pushState({}, '', path);
    this.handleRouteChange();
  }
  
  handleRouteChange() {
    const path = window.location.pathname || '/';
    const search = window.location.search || '';
    const fullPath = path + search;
    
    // 查找匹配的路由
    const route = this.findRoute(path);
    
    if (route) {
      this.currentRoute = { ...route, params: this.extractParams(route.path, path) };
      this.render();
    } else {
      // 404处理
      this.currentRoute = { component: 'NotFound', params: {} };
      this.render();
    }
  }
  
  findRoute(path) {
    // 精确匹配
    const exactMatch = this.routes.find(route => route.path === path);
    if (exactMatch) return exactMatch;
    
    // 参数化路由匹配
    const paramMatch = this.routes.find(route => {
      const routeSegments = route.path.split('/').filter(Boolean);
      const pathSegments = path.split('/').filter(Boolean);
      
      if (routeSegments.length !== pathSegments.length) return false;
      
      return routeSegments.every((segment, index) => {
        return segment.startsWith(':') || segment === pathSegments[index];
      });
    });
    
    return paramMatch;
  }
  
  extractParams(routePath, actualPath) {
    const params = {};
    const routeSegments = routePath.split('/').filter(Boolean);
    const pathSegments = actualPath.split('/').filter(Boolean);
    
    routeSegments.forEach((segment, index) => {
      if (segment.startsWith(':')) {
        const paramName = segment.substring(1);
        params[paramName] = pathSegments[index];
      }
    });
    
    return params;
  }
  
  render() {
    const appContent = document.getElementById('app-content');
    
    // 显示加载状态
    appContent.innerHTML = '<div class="text-center p-4">加载中...</div>';
    
    // 动态加载并渲染组件
    this.loadComponent(this.currentRoute.component)
      .then(component => {
        // 更新导航活动状态
        this.updateActiveNavLinks();
        
        // 渲染组件
        if (typeof component.render === 'function') {
          appContent.innerHTML = component.render(this.currentRoute.params);
          component.onMount && component.onMount();
        } else if (typeof component === 'function') {
          appContent.innerHTML = component(this.currentRoute.params);
        } else {
          appContent.innerHTML = component;
        }
      })
      .catch(error => {
        console.error('路由渲染错误:', error);
        appContent.innerHTML = '<div class="alert alert-danger">加载页面失败</div>';
      });
  }
  
  async loadComponent(componentName) {
    // 如果组件已经加载，直接返回
    if (window.AppComponents && window.AppComponents[componentName]) {
      return window.AppComponents[componentName];
    }
    
    try {
      // 动态导入组件
      const module = await import(`../pages/${componentName}.js`);
      const component = module.default;
      
      // 缓存组件
      if (!window.AppComponents) window.AppComponents = {};
      window.AppComponents[componentName] = component;
      
      return component;
    } catch (error) {
      console.error(`加载组件 ${componentName} 失败:`, error);
      
      // 返回404组件
      return {
        render: () => '<div class="text-center p-4"><h2>页面未找到</h2><p>您访问的页面不存在</p></div>'
      };
    }
  }
  
  updateActiveNavLinks() {
    document.querySelectorAll('[data-route]').forEach(link => {
      const href = link.getAttribute('href');
      if (href === window.location.pathname) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });
  }
}

export default Router;
```

### 11.3.2 路由配置

```javascript
// src/router/routes.js
export default [
  {
    path: '/',
    component: 'Dashboard',
    title: '仪表板'
  },
  {
    path: '/login',
    component: 'Login',
    title: '登录'
  },
  {
    path: '/register',
    component: 'Register',
    title: '注册'
  },
  {
    path: '/tasks',
    component: 'TaskList',
    title: '任务列表'
  },
  {
    path: '/tasks/new',
    component: 'TaskForm',
    title: '新建任务'
  },
  {
    path: '/tasks/:id/edit',
    component: 'TaskForm',
    title: '编辑任务'
  },
  {
    path: '/tasks/:id',
    component: 'TaskDetail',
    title: '任务详情'
  },
  {
    path: '/stats',
    component: 'Stats',
    title: '统计分析'
  },
  {
    path: '/profile',
    component: 'Profile',
    title: '个人资料'
  }
];
```

## 11.4 状态管理系统

### 11.4.1 简单状态管理器

```javascript
// src/state/store.js
class Store {
  constructor(initialState, reducers) {
    this.state = initialState;
    this.reducers = reducers;
    this.listeners = [];
    
    // 状态持久化
    this.loadState();
  }
  
  getState() {
    return this.state;
  }
  
  dispatch(action) {
    // 保存prevState用于对比
    const prevState = { ...this.state };
    
    // 执行reducer更新状态
    const newState = this.reducers(this.state, action);
    
    // 检查状态是否发生变化
    const stateChanged = JSON.stringify(prevState) !== JSON.stringify(newState);
    
    if (stateChanged) {
      this.state = newState;
      
      // 保存状态到持久化存储
      this.saveState();
      
      // 通知所有监听器
      this.notifyListeners(prevState, action);
    }
    
    return this.state;
  }
  
  subscribe(listener) {
    this.listeners.push(listener);
    
    // 返回取消订阅函数
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }
  
  notifyListeners(prevState, action) {
    this.listeners.forEach(listener => {
      listener(this.state, prevState, action);
    });
  }
  
  saveState() {
    try {
      localStorage.setItem('task_manager_state', JSON.stringify(this.state));
    } catch (error) {
      console.error('保存状态失败:', error);
    }
  }
  
  loadState() {
    try {
      const savedState = localStorage.getItem('task_manager_state');
      if (savedState) {
        this.state = { ...this.state, ...JSON.parse(savedState) };
      }
    } catch (error) {
      console.error('加载状态失败:', error);
    }
  }
}

export default Store;
```

### 11.4.2 Reducers

```javascript
// src/state/reducers.js
import { ADD_TASK, UPDATE_TASK, DELETE_TASK, SET_FILTER, SET_USER, LOGOUT, SET_LOADING } from './actions.js';

const initialState = {
  user: null,
  tasks: [],
  filter: {
    status: 'all', // all, active, completed
    category: 'all',
    searchTerm: ''
  },
  loading: false,
  error: null
};

export default function appReducer(state = initialState, action) {
  switch (action.type) {
    case SET_USER:
      return {
        ...state,
        user: action.payload
      };
      
    case LOGOUT:
      return {
        ...initialState
      };
      
    case SET_LOADING:
      return {
        ...state,
        loading: action.payload
      };
      
    case ADD_TASK:
      return {
        ...state,
        tasks: [...state.tasks, action.payload]
      };
      
    case UPDATE_TASK:
      return {
        ...state,
        tasks: state.tasks.map(task => 
          task.id === action.payload.id ? action.payload : task
        )
      };
      
    case DELETE_TASK:
      return {
        ...state,
        tasks: state.tasks.filter(task => task.id !== action.payload)
      };
      
    case SET_FILTER:
      return {
        ...state,
        filter: {
          ...state.filter,
          ...action.payload
        }
      };
      
    default:
      return state;
  }
}
```

### 11.4.3 Actions

```javascript
// src/state/actions.js
export const SET_USER = 'SET_USER';
export const LOGOUT = 'LOGOUT';
export const SET_LOADING = 'SET_LOADING';
export const ADD_TASK = 'ADD_TASK';
export const UPDATE_TASK = 'UPDATE_TASK';
export const DELETE_TASK = 'DELETE_TASK';
export const SET_FILTER = 'SET_FILTER';

// 用户相关actions
export const setUser = (user) => ({
  type: SET_USER,
  payload: user
});

export const logout = () => ({
  type: LOGOUT
});

export const setLoading = (loading) => ({
  type: SET_LOADING,
  payload: loading
});

// 任务相关actions
export const addTask = (task) => ({
  type: ADD_TASK,
  payload: task
});

export const updateTask = (task) => ({
  type: UPDATE_TASK,
  payload: task
});

export const deleteTask = (taskId) => ({
  type: DELETE_TASK,
  payload: taskId
});

// 过滤相关actions
export const setFilter = (filter) => ({
  type: SET_FILTER,
  payload: filter
});

// 异步action creators
export const login = (credentials) => {
  return async (dispatch) => {
    dispatch(setLoading(true));
    
    try {
      // 这里调用API登录
      const user = await AuthService.login(credentials);
      dispatch(setUser(user));
      return user;
    } catch (error) {
      dispatch(setLoading(false));
      throw error;
    }
  };
};

export const fetchTasks = () => {
  return async (dispatch) => {
    dispatch(setLoading(true));
    
    try {
      // 这里调用API获取任务
      const tasks = await TaskService.getAll();
      
      // 批量添加任务
      tasks.forEach(task => {
        dispatch(addTask(task));
      });
      
      dispatch(setLoading(false));
      return tasks;
    } catch (error) {
      dispatch(setLoading(false));
      throw error;
    }
  };
};
```

### 11.4.4 异步Action中间件

```javascript
// src/state/middleware.js
export const thunkMiddleware = (store) => (next) => (action) => {
  // 如果action是函数，执行它并传入dispatch和getState
  if (typeof action === 'function') {
    return action(store.dispatch, store.getState);
  }
  
  // 否则继续传递action
  return next(action);
};

// 简单的logger中间件
export const loggerMiddleware = (store) => (next) => (action) => {
  console.group(`Action: ${action.type}`);
  console.log('Prev State:', store.getState());
  console.log('Action:', action);
  
  const result = next(action);
  
  console.log('Next State:', store.getState());
  console.groupEnd();
  
  return result;
};
```

## 11.5 服务层实现

### 11.5.1 API服务

```javascript
// src/services/api.js
class ApiService {
  constructor() {
    this.baseURL = 'http://localhost:3001/api';
  }
  
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };
    
    // 添加认证令牌
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    try {
      const response = await fetch(url, config);
      
      // 处理401未授权错误
      if (response.status === 401) {
        // 清除本地存储的认证信息
        localStorage.removeItem('auth_token');
        
        // 可以触发全局状态更新或重定向到登录页
        window.location.hash = '#/login';
        throw new Error('认证失败，请重新登录');
      }
      
      // 处理其他HTTP错误
      if (!response.ok) {
        const error = new Error(`HTTP Error: ${response.status} ${response.statusText}`);
        error.status = response.status;
        error.statusText = response.statusText;
        
        try {
          // 尝试获取错误详情
          const errorData = await response.json();
          error.message = errorData.message || error.message;
        } catch (e) {
          // 如果无法解析错误响应，使用默认错误信息
        }
        
        throw error;
      }
      
      // 检查响应是否有内容
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      } else {
        return await response.text();
      }
    } catch (error) {
      console.error('API请求错误:', error);
      throw error;
    }
  }
  
  async get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }
  
  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }
  
  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }
  
  async patch(endpoint, data) {
    return this.request(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  }
  
  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
}

export default new ApiService();
```

### 11.5.2 认证服务

```javascript
// src/services/auth.js
import ApiService from './api.js';

class AuthService {
  async login(credentials) {
    try {
      const response = await ApiService.post('/auth/login', credentials);
      
      // 保存令牌
      localStorage.setItem('auth_token', response.token);
      
      // 返回用户信息
      return response.user;
    } catch (error) {
      throw new Error('登录失败: ' + error.message);
    }
  }
  
  async register(userData) {
    try {
      const response = await ApiService.post('/auth/register', userData);
      
      // 保存令牌
      localStorage.setItem('auth_token', response.token);
      
      // 返回用户信息
      return response.user;
    } catch (error) {
      throw new Error('注册失败: ' + error.message);
    }
  }
  
  async logout() {
    try {
      // 调用API注销
      await ApiService.post('/auth/logout');
    } catch (error) {
      console.error('API注销失败:', error);
    } finally {
      // 无论API调用成功与否，都清除本地令牌
      localStorage.removeItem('auth_token');
    }
  }
  
  async getCurrentUser() {
    try {
      const response = await ApiService.get('/auth/me');
      return response.user;
    } catch (error) {
      throw new Error('获取用户信息失败: ' + error.message);
    }
  }
  
  async updateProfile(userData) {
    try {
      const response = await ApiService.put('/auth/profile', userData);
      return response.user;
    } catch (error) {
      throw new Error('更新用户信息失败: ' + error.message);
    }
  }
  
  isAuthenticated() {
    return !!localStorage.getItem('auth_token');
  }
  
  getToken() {
    return localStorage.getItem('auth_token');
  }
}

export default new AuthService();
```

### 11.5.3 任务服务

```javascript
// src/services/task.js
import ApiService from './api.js';

class TaskService {
  async getAll() {
    try {
      const response = await ApiService.get('/tasks');
      return response.tasks;
    } catch (error) {
      throw new Error('获取任务列表失败: ' + error.message);
    }
  }
  
  async getById(id) {
    try {
      const response = await ApiService.get(`/tasks/${id}`);
      return response.task;
    } catch (error) {
      throw new Error(`获取任务#${id}失败: ` + error.message);
    }
  }
  
  async create(taskData) {
    try {
      const response = await ApiService.post('/tasks', taskData);
      return response.task;
    } catch (error) {
      throw new Error('创建任务失败: ' + error.message);
    }
  }
  
  async update(id, taskData) {
    try {
      const response = await ApiService.put(`/tasks/${id}`, taskData);
      return response.task;
    } catch (error) {
      throw new Error(`更新任务#${id}失败: ` + error.message);
    }
  }
  
  async delete(id) {
    try {
      await ApiService.delete(`/tasks/${id}`);
      return true;
    } catch (error) {
      throw new Error(`删除任务#${id}失败: ` + error.message);
    }
  }
  
  async toggleComplete(id) {
    try {
      const response = await ApiService.patch(`/tasks/${id}/toggle-complete`);
      return response.task;
    } catch (error) {
      throw new Error(`更新任务#${id}完成状态失败: ` + error.message);
    }
  }
}

export default new TaskService();
```

### 11.5.4 存储服务

```javascript
// src/services/storage.js
class StorageService {
  constructor() {
    this.dbName = 'TaskManagerDB';
    this.dbVersion = 1;
    this.db = null;
  }
  
  async init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion);
      
      request.onerror = (event) => {
        reject('数据库打开失败');
      };
      
      request.onsuccess = (event) => {
        this.db = event.target.result;
        resolve(this.db);
      };
      
      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        
        // 创建tasks对象存储
        if (!db.objectStoreNames.contains('tasks')) {
          const tasksStore = db.createObjectStore('tasks', { keyPath: 'id' });
          tasksStore.createIndex('status', 'status', { unique: false });
          tasksStore.createIndex('category', 'category', { unique: false });
          tasksStore.createIndex('createdDate', 'createdDate', { unique: false });
        }
        
        // 创建user对象存储
        if (!db.objectStoreNames.contains('user')) {
          db.createObjectStore('user', { keyPath: 'id' });
        }
      };
    });
  }
  
  async get(storeName, id) {
    if (!this.db) await this.init();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readonly');
      const store = transaction.objectStore(storeName);
      const request = store.get(id);
      
      request.onerror = () => reject('获取数据失败');
      request.onsuccess = () => resolve(request.result);
    });
  }
  
  async getAll(storeName, indexName = null, query = null) {
    if (!this.db) await this.init();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readonly');
      const store = transaction.objectStore(storeName);
      
      let request;
      if (indexName && query) {
        const index = store.index(indexName);
        request = index.getAll(query);
      } else {
        request = store.getAll();
      }
      
      request.onerror = () => reject('获取数据失败');
      request.onsuccess = () => resolve(request.result || []);
    });
  }
  
  async put(storeName, data) {
    if (!this.db) await this.init();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.put(data);
      
      request.onerror = () => reject('保存数据失败');
      request.onsuccess = () => resolve(request.result);
    });
  }
  
  async delete(storeName, id) {
    if (!this.db) await this.init();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.delete(id);
      
      request.onerror = () => reject('删除数据失败');
      request.onsuccess = () => resolve(request.result);
    });
  }
  
  async clear(storeName) {
    if (!this.db) await this.init();
    
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.clear();
      
      request.onerror = () => reject('清空数据失败');
      request.onsuccess = () => resolve(request.result);
    });
  }
}

export default new StorageService();
```

## 11.6 通用工具函数

### 11.6.1 助手函数

```javascript
// src/utils/helpers.js
/**
 * 格式化日期
 * @param {Date|string} date - 日期对象或日期字符串
 * @param {string} format - 格式化模式，如 'YYYY-MM-DD'
 * @return {string} 格式化后的日期字符串
 */
export function formatDate(date, format = 'YYYY-MM-DD') {
  const d = new Date(date);
  
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  
  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes);
}

/**
 * 计算两个日期之间的天数差
 * @param {Date|string} date1 - 第一个日期
 * @param {Date|string} date2 - 第二个日期
 * @return {number} 天数差
 */
export function daysBetween(date1, date2) {
  const d1 = new Date(date1);
  const d2 = new Date(date2);
  
  // 设置时间为0点，确保只计算日期差
  d1.setHours(0, 0, 0, 0);
  d2.setHours(0, 0, 0, 0);
  
  const timeDiff = d2.getTime() - d1.getTime();
  return Math.ceil(timeDiff / (1000 * 3600 * 24));
}

/**
 * 生成唯一ID
 * @param {string} prefix - ID前缀
 * @return {string} 唯一ID
 */
export function generateId(prefix = '') {
  const timestamp = Date.now().toString(36);
  const randomStr = Math.random().toString(36).substring(2);
  return prefix ? `${prefix}_${timestamp}_${randomStr}` : `${timestamp}_${randomStr}`;
}

/**
 * 深克隆对象
 * @param {*} obj - 要克隆的对象
 * @return {*} 克隆后的对象
 */
export function deepClone(obj) {
  // 处理基本类型和null
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }
  
  // 处理Date对象
  if (obj instanceof Date) {
    return new Date(obj.getTime());
  }
  
  // 处理数组
  if (Array.isArray(obj)) {
    return obj.map(item => deepClone(item));
  }
  
  // 处理普通对象
  const clonedObj = {};
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      clonedObj[key] = deepClone(obj[key]);
    }
  }
  
  return clonedObj;
}

/**
 * 防抖函数
 * @param {Function} func - 要防抖的函数
 * @param {number} wait - 等待时间（毫秒）
 * @return {Function} 防抖后的函数
 */
export function debounce(func, wait) {
  let timeout;
  
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * 节流函数
 * @param {Function} func - 要节流的函数
 * @param {number} limit - 限制时间（毫秒）
 * @return {Function} 节流后的函数
 */
export function throttle(func, limit) {
  let inThrottle;
  
  return function executedFunction(...args) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => {
        inThrottle = false;
      }, limit);
    }
  };
}

/**
 * 从数组中移除指定元素
 * @param {Array} array - 源数组
 * @param {*} element - 要移除的元素
 * @return {Array} 移除指定元素后的新数组
 */
export function removeElement(array, element) {
  const index = array.indexOf(element);
  if (index > -1) {
    return [...array.slice(0, index), ...array.slice(index + 1)];
  }
  return [...array];
}

/**
 * 获取数组的随机元素
 * @param {Array} array - 源数组
 * @param {number} count - 要获取的元素数量，默认为1
 * @return {*} 随机元素或随机元素数组
 */
export function getRandomElements(array, count = 1) {
  if (count === 1) {
    return array[Math.floor(Math.random() * array.length)];
  }
  
  const shuffled = [...array].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, Math.min(count, array.length));
}

/**
 * 转换文件大小为易读格式
 * @param {number} bytes - 字节数
 * @param {number} decimals - 小数位数，默认为2
 * @return {string} 格式化后的文件大小
 */
export function formatFileSize(bytes, decimals = 2) {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * 截断文本
 * @param {string} text - 源文本
 * @param {number} length - 最大长度
 * @param {string} suffix - 后缀，默认为'...'
 * @return {string} 截断后的文本
 */
export function truncateText(text, length, suffix = '...') {
  if (text.length <= length) {
    return text;
  }
  return text.substring(0, length - suffix.length) + suffix;
}

/**
 * 高亮搜索关键词
 * @param {string} text - 源文本
 * @param {string} searchTerm - 搜索词
 * @param {string} className - 高亮样式类名，默认为'highlight'
 * @return {string} 高亮处理后的HTML
 */
export function highlightSearchTerm(text, searchTerm, className = 'highlight') {
  if (!searchTerm || searchTerm.trim() === '') {
    return text;
  }
  
  // 转义搜索词中的特殊字符
  const escapedSearchTerm = searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  
  // 创建正则表达式（全局匹配，不区分大小写）
  const regex = new RegExp(`(${escapedSearchTerm})`, 'gi');
  
  // 替换匹配的文本为带高亮的HTML
  return text.replace(regex, `<span class="${className}">$1</span>`);
}
```

### 11.6.2 常量定义

```javascript
// src/utils/constants.js
// API端点
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    PROFILE: '/auth/profile',
    CURRENT: '/auth/me'
  },
  TASKS: {
    ALL: '/tasks',
    BY_ID: (id) => `/tasks/${id}`,
    TOGGLE_COMPLETE: (id) => `/tasks/${id}/toggle-complete`
  }
};

// 任务状态
export const TASK_STATUS = {
  PENDING: 'pending',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  CANCELLED: 'cancelled'
};

// 任务优先级
export const TASK_PRIORITY = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  URGENT: 'urgent'
};

// 任务分类
export const TASK_CATEGORIES = [
  { id: 'personal', name: '个人' },
  { id: 'work', name: '工作' },
  { id: 'study', name: '学习' },
  { id: 'health', name: '健康' },
  { id: 'finance', name: '财务' },
  { id: 'other', name: '其他' }
];

// 通知类型
export const NOTIFICATION_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info'
};

// 本地存储键
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  USER_PREFERENCES: 'user_preferences',
  APP_SETTINGS: 'app_settings'
};

// 路由名称
export const ROUTE_NAMES = {
  DASHBOARD: 'Dashboard',
  LOGIN: 'Login',
  REGISTER: 'Register',
  TASK_LIST: 'TaskList',
  TASK_FORM: 'TaskForm',
  TASK_DETAIL: 'TaskDetail',
  STATS: 'Stats',
  PROFILE: 'Profile'
};

// 日期格式
export const DATE_FORMATS = {
  SHORT: 'YYYY-MM-DD',
  LONG: 'YYYY-MM-DD HH:mm',
  TIME_ONLY: 'HH:mm'
};

// 错误消息
export const ERROR_MESSAGES = {
  NETWORK_ERROR: '网络连接失败，请检查网络设置',
  AUTH_REQUIRED: '需要登录才能执行此操作',
  PERMISSION_DENIED: '没有权限执行此操作',
  RESOURCE_NOT_FOUND: '请求的资源不存在',
  VALIDATION_ERROR: '输入数据验证失败',
  UNKNOWN_ERROR: '发生未知错误，请稍后再试'
};
```

### 11.6.3 验证函数

```javascript
// src/utils/validators.js
/**
 * 验证邮箱格式
 * @param {string} email - 邮箱地址
 * @return {boolean} 是否有效
 */
export function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * 验证密码强度
 * @param {string} password - 密码
 * @return {Object} 验证结果和错误信息
 */
export function validatePassword(password) {
  const result = {
    isValid: true,
    errors: []
  };
  
  if (!password) {
    result.isValid = false;
    result.errors.push('密码不能为空');
    return result;
  }
  
  if (password.length < 8) {
    result.isValid = false;
    result.errors.push('密码长度至少为8位');
  }
  
  if (!/[A-Z]/.test(password)) {
    result.isValid = false;
    result.errors.push('密码必须包含至少一个大写字母');
  }
  
  if (!/[a-z]/.test(password)) {
    result.isValid = false;
    result.errors.push('密码必须包含至少一个小写字母');
  }
  
  if (!/[0-9]/.test(password)) {
    result.isValid = false;
    result.errors.push('密码必须包含至少一个数字');
  }
  
  return result;
}

/**
 * 验证任务数据
 * @param {Object} taskData - 任务数据
 * @return {Object} 验证结果和错误信息
 */
export function validateTaskData(taskData) {
  const result = {
    isValid: true,
    errors: []
  };
  
  if (!taskData.title || taskData.title.trim() === '') {
    result.isValid = false;
    result.errors.push('任务标题不能为空');
  }
  
  if (taskData.title && taskData.title.length > 100) {
    result.isValid = false;
    result.errors.push('任务标题不能超过100个字符');
  }
  
  if (taskData.description && taskData.description.length > 500) {
    result.isValid = false;
    result.errors.push('任务描述不能超过500个字符');
  }
  
  if (taskData.dueDate && isNaN(Date.parse(taskData.dueDate))) {
    result.isValid = false;
    result.errors.push('截止日期格式不正确');
  }
  
  return result;
}

/**
 * 验证用户资料数据
 * @param {Object} userData - 用户数据
 * @return {Object} 验证结果和错误信息
 */
export function validateUserData(userData) {
  const result = {
    isValid: true,
    errors: []
  };
  
  if (!userData.name || userData.name.trim() === '') {
    result.isValid = false;
    result.errors.push('姓名不能为空');
  }
  
  if (userData.name && userData.name.length > 50) {
    result.isValid = false;
    result.errors.push('姓名不能超过50个字符');
  }
  
  if (userData.email && !isValidEmail(userData.email)) {
    result.isValid = false;
    result.errors.push('邮箱格式不正确');
  }
  
  if (userData.phone && !/^1[3-9]\d{9}$/.test(userData.phone)) {
    result.isValid = false;
    result.errors.push('手机号码格式不正确');
  }
  
  return result;
}

/**
 * 验证搜索查询
 * @param {string} query - 搜索查询
 * @return {Object} 验证结果
 */
export function validateSearchQuery(query) {
  const result = {
    isValid: true,
    errors: []
  };
  
  if (query && query.length > 100) {
    result.isValid = false;
    result.errors.push('搜索查询不能超过100个字符');
  }
  
  return result;
}
```

## 11.7 页面组件实现

### 11.7.1 仪表板组件

```javascript
// src/pages/Dashboard.js
import { formatDate } from '../utils/helpers.js';
import { TASK_STATUS, TASK_CATEGORIES } from '../utils/constants.js';

export default {
  render(params) {
    return `
      <div class="dashboard">
        <div class="dashboard-header">
          <h2>任务仪表板</h2>
          <div class="dashboard-actions">
            <button id="new-task-btn" class="btn btn-primary">
              <i class="icon-plus"></i> 新建任务
            </button>
          </div>
        </div>
        
        <div class="dashboard-stats">
          <div class="stat-card">
            <div class="stat-value" id="total-tasks">0</div>
            <div class="stat-label">总任务数</div>
          </div>
          <div class="stat-card">
            <div class="stat-value" id="completed-tasks">0</div>
            <div class="stat-label">已完成</div>
          </div>
          <div class="stat-card">
            <div class="stat-value" id="pending-tasks">0</div>
            <div class="stat-label">进行中</div>
          </div>
          <div class="stat-card">
            <div class="stat-value" id="overdue-tasks">0</div>
            <div class="stat-label">已逾期</div>
          </div>
        </div>
        
        <div class="dashboard-content">
          <div class="dashboard-left">
            <div class="chart-container">
              <h3>任务完成趋势</h3>
              <canvas id="completion-chart"></canvas>
            </div>
            
            <div class="chart-container">
              <h3>任务分类分布</h3>
              <canvas id="category-chart"></canvas>
            </div>
          </div>
          
          <div class="dashboard-right">
            <div class="recent-tasks">
              <h3>最近任务</h3>
              <div id="recent-tasks-list" class="task-list">
                <div class="text-center p-4">加载中...</div>
              </div>
            </div>
            
            <div class="upcoming-tasks">
              <h3>即将到期</h3>
              <div id="upcoming-tasks-list" class="task-list">
                <div class="text-center p-4">加载中...</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  },
  
  onMount() {
    this.loadTasksData();
    this.setupEventListeners();
    this.renderCharts();
  },
  
  loadTasksData() {
    // 从全局状态获取任务数据
    const state = window.store.getState();
    const tasks = state.tasks || [];
    
    // 更新统计数据
    this.updateStats(tasks);
    
    // 渲染任务列表
    this.renderRecentTasks(tasks);
    this.renderUpcomingTasks(tasks);
  },
  
  updateStats(tasks) {
    const totalTasks = tasks.length;
    const completedTasks = tasks.filter(task => task.status === TASK_STATUS.COMPLETED).length;
    const pendingTasks = tasks.filter(task => 
      task.status === TASK_STATUS.PENDING || task.status === TASK_STATUS.IN_PROGRESS
    ).length;
    const overdueTasks = tasks.filter(task => {
      const dueDate = new Date(task.dueDate);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      return task.status !== TASK_STATUS.COMPLETED && dueDate < today;
    }).length;
    
    document.getElementById('total-tasks').textContent = totalTasks;
    document.getElementById('completed-tasks').textContent = completedTasks;
    document.getElementById('pending-tasks').textContent = pendingTasks;
    document.getElementById('overdue-tasks').textContent = overdueTasks;
  },
  
  renderRecentTasks(tasks) {
    const recentTasks = [...tasks]
      .sort((a, b) => new Date(b.createdDate) - new Date(a.createdDate))
      .slice(0, 5);
    
    const container = document.getElementById('recent-tasks-list');
    
    if (recentTasks.length === 0) {
      container.innerHTML = '<div class="text-center p-4">暂无任务</div>';
      return;
    }
    
    container.innerHTML = recentTasks.map(task => `
      <div class="task-item ${task.status === TASK_STATUS.COMPLETED ? 'completed' : ''}">
        <div class="task-info">
          <h4>${task.title}</h4>
          <p>${task.description ? task.description.substring(0, 50) + '...' : ''}</p>
          <div class="task-meta">
            <span class="task-category">${this.getCategoryName(task.category)}</span>
            <span class="task-date">创建于 ${formatDate(task.createdDate)}</span>
          </div>
        </div>
        <div class="task-actions">
          <a href="#/tasks/${task.id}" class="btn btn-sm btn-outline">查看</a>
        </div>
      </div>
    `).join('');
  },
  
  renderUpcomingTasks(tasks) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const upcomingTasks = tasks
      .filter(task => {
        const dueDate = new Date(task.dueDate);
        return task.status !== TASK_STATUS.COMPLETED && 
               dueDate >= today &&
               Math.floor((dueDate - today) / (1000 * 60 * 60 * 24)) <= 7;
      })
      .sort((a, b) => new Date(a.dueDate) - new Date(b.dueDate))
      .slice(0, 5);
    
    const container = document.getElementById('upcoming-tasks-list');
    
    if (upcomingTasks.length === 0) {
      container.innerHTML = '<div class="text-center p-4">暂无即将到期的任务</div>';
      return;
    }
    
    container.innerHTML = upcomingTasks.map(task => {
      const dueDate = new Date(task.dueDate);
      const today = new Date();
      const daysUntilDue = Math.ceil((dueDate - today) / (1000 * 60 * 60 * 24));
      const isOverdue = daysUntilDue < 0;
      
      return `
        <div class="task-item ${task.status === TASK_STATUS.COMPLETED ? 'completed' : ''} ${isOverdue ? 'overdue' : ''}">
          <div class="task-info">
            <h4>${task.title}</h4>
            <div class="task-meta">
              <span class="task-due-date">
                ${isOverdue ? '逾期 ' : '剩余 '}${Math.abs(daysUntilDue)} 天
              </span>
              <span class="task-date">${formatDate(task.dueDate)}</span>
            </div>
          </div>
          <div class="task-actions">
            <a href="#/tasks/${task.id}" class="btn btn-sm btn-outline">查看</a>
          </div>
        </div>
      `;
    }).join('');
  },
  
  renderCharts() {
    this.renderCompletionChart();
    this.renderCategoryChart();
  },
  
  renderCompletionChart() {
    const state = window.store.getState();
    const tasks = state.tasks || [];
    
    // 按日期统计完成的任务数量
    const completedByDate = {};
    tasks.forEach(task => {
      if (task.status === TASK_STATUS.COMPLETED) {
        const date = formatDate(task.updatedDate || task.dueDate);
        completedByDate[date] = (completedByDate[date] || 0) + 1;
      }
    });
    
    // 获取最近7天的日期
    const dates = [];
    const counts = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const dateStr = formatDate(date);
      dates.push(dateStr);
      counts.push(completedByDate[dateStr] || 0);
    }
    
    // 创建图表
    const ctx = document.getElementById('completion-chart').getContext('2d');
    
    // 如果已经存在图表，先销毁它
    if (window.completionChart) {
      window.completionChart.destroy();
    }
    
    window.completionChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: dates,
        datasets: [{
          label: '完成任务数',
          data: counts,
          borderColor: '#4a6cf7',
          backgroundColor: 'rgba(74, 108, 247, 0.1)',
          tension: 0.4,
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 1
            }
          }
        },
        plugins: {
          legend: {
            display: false
          }
        }
      }
    });
  },
  
  renderCategoryChart() {
    const state = window.store.getState();
    const tasks = state.tasks || [];
    
    // 按分类统计任务数量
    const categoryCount = {};
    tasks.forEach(task => {
      const category = task.category || 'other';
      categoryCount[category] = (categoryCount[category] || 0) + 1;
    });
    
    // 准备图表数据
    const labels = [];
    const data = [];
    const backgroundColors = [];
    
    TASK_CATEGORIES.forEach(category => {
      if (categoryCount[category.id]) {
        labels.push(category.name);
        data.push(categoryCount[category.id]);
        backgroundColors.push(this.getRandomColor());
      }
    });
    
    // 创建图表
    const ctx = document.getElementById('category-chart').getContext('2d');
    
    // 如果已经存在图表，先销毁它
    if (window.categoryChart) {
      window.categoryChart.destroy();
    }
    
    window.categoryChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: data,
          backgroundColor: backgroundColors,
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom'
          }
        }
      }
    });
  },
  
  setupEventListeners() {
    // 新建任务按钮
    document.getElementById('new-task-btn').addEventListener('click', () => {
      window.location.hash = '#/tasks/new';
    });
    
    // 监听状态变化
    window.store.subscribe(() => {
      this.loadTasksData();
      this.renderCharts();
    });
  },
  
  getCategoryName(categoryId) {
    const category = TASK_CATEGORIES.find(cat => cat.id === categoryId);
    return category ? category.name : '未分类';
  },
  
  getRandomColor() {
    const colors = [
      '#4a6cf7', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6',
      '#3498db', '#1abc9c', '#34495e', '#f1c40f', '#e67e22'
    ];
    return colors[Math.floor(Math.random() * colors.length)];
  }
};
```

### 11.7.2 任务列表组件

```javascript
// src/pages/TaskList.js
import { formatDate, highlightSearchTerm } from '../utils/helpers.js';
import { TASK_STATUS, TASK_CATEGORIES } from '../utils/constants.js';
import NotificationService from '../services/notification.js';

export default {
  render(params) {
    return `
      <div class="task-list-page">
        <div class="page-header">
          <h2>任务列表</h2>
          <div class="page-actions">
            <button id="filter-btn" class="btn btn-outline">
              <i class="icon-filter"></i> 筛选
            </button>
            <button id="new-task-btn" class="btn btn-primary">
              <i class="icon-plus"></i> 新建任务
            </button>
          </div>
        </div>
        
        <div class="search-filter-container">
          <div class="search-container">
            <input 
              type="text" 
              id="search-input" 
              class="form-control" 
              placeholder="搜索任务..."
            >
            <button id="search-btn" class="btn btn-primary">搜索</button>
          </div>
          
          <div class="filter-container" id="filter-container" style="display: none;">
            <div class="filter-row">
              <div class="filter-group">
                <label for="status-filter" class="form-label">状态</label>
                <select id="status-filter" class="form-control">
                  <option value="all">全部</option>
                  <option value="${TASK_STATUS.PENDING}">待处理</option>
                  <option value="${TASK_STATUS.IN_PROGRESS}">进行中</option>
                  <option value="${TASK_STATUS.COMPLETED}">已完成</option>
                  <option value="${TASK_STATUS.CANCELLED}">已取消</option>
                </select>
              </div>
              
              <div class="filter-group">
                <label for="category-filter" class="form-label">分类</label>
                <select id="category-filter" class="form-control">
                  <option value="all">全部分类</option>
                  ${TASK_CATEGORIES.map(cat => `
                    <option value="${cat.id}">${cat.name}</option>
                  `).join('')}
                </select>
              </div>
              
              <div class="filter-group">
                <label for="priority-filter" class="form-label">优先级</label>
                <select id="priority-filter" class="form-control">
                  <option value="all">全部优先级</option>
                  <option value="low">低</option>
                  <option value="medium">中</option>
                  <option value="high">高</option>
                  <option value="urgent">紧急</option>
                </select>
              </div>
            </div>
            
            <div class="filter-actions">
              <button id="apply-filter-btn" class="btn btn-primary">应用筛选</button>
              <button id="reset-filter-btn" class="btn btn-outline">重置</button>
            </div>
          </div>
        </div>
        
        <div class="task-list-container">
          <div class="list-view-controls">
            <div class="view-toggles">
              <button id="grid-view-btn" class="btn btn-sm btn-outline active">
                <i class="icon-grid"></i>
              </button>
              <button id="list-view-btn" class="btn btn-sm btn-outline">
                <i class="icon-list"></i>
              </button>
            </div>
            
            <div class="sort-controls">
              <select id="sort-select" class="form-control">
                <option value="createdDate-desc">创建时间（最新）</option>
                <option value="createdDate-asc">创建时间（最早）</option>
                <option value="dueDate-asc">截止日期（最近）</option>
                <option value="dueDate-desc">截止日期（最远）</option>
                <option value="priority-desc">优先级（高到低）</option>
                <option value="priority-asc">优先级（低到高）</option>
                <option value="title-asc">标题（A-Z）</option>
                <option value="title-desc">标题（Z-A）</option>
              </select>
            </div>
          </div>
          
          <div id="tasks-list" class="tasks-list list-view">
            <div class="text-center p-4">加载中...</div>
          </div>
        </div>
      </div>
    `;
  },
  
  onMount() {
    this.setupEventListeners();
    this.loadTasks();
    
    // 监听状态变化
    this.unsubscribe = window.store.subscribe(() => {
      this.loadTasks();
    });
  },
  
  onUnmount() {
    if (this.unsubscribe) {
      this.unsubscribe();
    }
  },
  
  setupEventListeners() {
    // 搜索功能
    document.getElementById('search-btn').addEventListener('click', () => {
      this.handleSearch();
    });
    
    document.getElementById('search-input').addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.handleSearch();
      }
    });
    
    // 筛选功能
    document.getElementById('filter-btn').addEventListener('click', () => {
      const filterContainer = document.getElementById('filter-container');
      filterContainer.style.display = filterContainer.style.display === 'none' ? 'block' : 'none';
    });
    
    document.getElementById('apply-filter-btn').addEventListener('click', () => {
      this.applyFilters();
    });
    
    document.getElementById('reset-filter-btn').addEventListener('click', () => {
      this.resetFilters();
    });
    
    // 新建任务
    document.getElementById('new-task-btn').addEventListener('click', () => {
      window.location.hash = '#/tasks/new';
    });
    
    // 视图切换
    document.getElementById('grid-view-btn').addEventListener('click', () => {
      this.switchView('grid');
    });
    
    document.getElementById('list-view-btn').addEventListener('click', () => {
      this.switchView('list');
    });
    
    // 排序
    document.getElementById('sort-select').addEventListener('change', () => {
      this.loadTasks();
    });
  },
  
  handleSearch() {
    const searchTerm = document.getElementById('search-input').value.trim();
    
    if (searchTerm) {
      this.currentSearchTerm = searchTerm;
    } else {
      this.currentSearchTerm = '';
    }
    
    this.loadTasks();
  },
  
  applyFilters() {
    this.currentFilters = {
      status: document.getElementById('status-filter').value,
      category: document.getElementById('category-filter').value,
      priority: document.getElementById('priority-filter').value
    };
    
    this.loadTasks();
    
    // 隐藏筛选面板
    document.getElementById('filter-container').style.display = 'none';
  },
  
  resetFilters() {
    // 重置筛选条件
    document.getElementById('status-filter').value = 'all';
    document.getElementById('category-filter').value = 'all';
    document.getElementById('priority-filter').value = 'all';
    
    this.currentFilters = {
      status: 'all',
      category: 'all',
      priority: 'all'
    };
    
    this.loadTasks();
    
    // 隐藏筛选面板
    document.getElementById('filter-container').style.display = 'none';
  },
  
  switchView(view) {
    const listView = document.getElementById('tasks-list');
    const gridBtn = document.getElementById('grid-view-btn');
    const listBtn = document.getElementById('list-view-btn');
    
    if (view === 'grid') {
      listView.className = 'tasks-list grid-view';
      gridBtn.classList.add('active');
      listBtn.classList.remove('active');
    } else {
      listView.className = 'tasks-list list-view';
      listBtn.classList.add('active');
      gridBtn.classList.remove('active');
    }
  },
  
  loadTasks() {
    const state = window.store.getState();
    let tasks = [...(state.tasks || [])];
    
    // 应用搜索
    if (this.currentSearchTerm) {
      tasks = tasks.filter(task => 
        task.title.toLowerCase().includes(this.currentSearchTerm.toLowerCase()) ||
        (task.description && task.description.toLowerCase().includes(this.currentSearchTerm.toLowerCase()))
      );
    }
    
    // 应用筛选
    if (this.currentFilters) {
      if (this.currentFilters.status !== 'all') {
        tasks = tasks.filter(task => task.status === this.currentFilters.status);
      }
      
      if (this.currentFilters.category !== 'all') {
        tasks = tasks.filter(task => task.category === this.currentFilters.category);
      }
      
      if (this.currentFilters.priority !== 'all') {
        tasks = tasks.filter(task => task.priority === this.currentFilters.priority);
      }
    }
    
    // 应用排序
    const sortValue = document.getElementById('sort-select').value;
    const [sortField, sortOrder] = sortValue.split('-');
    
    tasks.sort((a, b) => {
      let aValue = a[sortField];
      let bValue = b[sortField];
      
      // 处理日期字段
      if (sortField.includes('Date')) {
        aValue = new Date(aValue || 0);
        bValue = new Date(bValue || 0);
      }
      
      // 处理优先级
      if (sortField === 'priority') {
        const priorityOrder = { low: 1, medium: 2, high: 3, urgent: 4 };
        aValue = priorityOrder[aValue] || 0;
        bValue = priorityOrder[bValue] || 0;
      }
      
      // 比较值
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : aValue < bValue ? -1 : 0;
      } else {
        return aValue < bValue ? 1 : aValue > bValue ? -1 : 0;
      }
    });
    
    this.renderTasks(tasks);
  },
  
  renderTasks(tasks) {
    const container = document.getElementById('tasks-list');
    
    if (tasks.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">
            <i class="icon-task"></i>
          </div>
          <h3>暂无任务</h3>
          <p>您还没有创建任何任务</p>
          <button id="empty-new-task-btn" class="btn btn-primary">创建第一个任务</button>
        </div>
      `;
      
      // 绑定空状态按钮事件
      document.getElementById('empty-new-task-btn').addEventListener('click', () => {
        window.location.hash = '#/tasks/new';
      });
      
      return;
    }
    
    container.innerHTML = tasks.map(task => this.renderTaskItem(task)).join('');
    
    // 绑定任务项事件
    this.bindTaskItemEvents();
  },
  
  renderTaskItem(task) {
    const statusClass = this.getStatusClass(task.status);
    const priorityClass = this.getPriorityClass(task.priority);
    const categoryName = this.getCategoryName(task.category);
    const dueDate = task.dueDate ? new Date(task.dueDate) : null;
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const isOverdue = dueDate && dueDate < today && task.status !== TASK_STATUS.COMPLETED;
    const isCompleted = task.status === TASK_STATUS.COMPLETED;
    
    const title = this.currentSearchTerm ? 
      highlightSearchTerm(task.title, this.currentSearchTerm) : 
      task.title;
      
    const description = task.description ? 
      (this.currentSearchTerm ? 
        highlightSearchTerm(task.description.substring(0, 100), this.currentSearchTerm) : 
        task.description.substring(0, 100)) : '';
    
    return `
      <div class="task-item ${statusClass} ${priorityClass} ${isOverdue ? 'overdue' : ''}" data-task-id="${task.id}">
        <div class="task-status">
          <input 
            type="checkbox" 
            class="task-checkbox" 
            data-task-id="${task.id}"
            ${isCompleted ? 'checked' : ''}
          >
        </div>
        
        <div class="task-content">
          <h3 class="task-title">${title}</h3>
          ${description ? `<p class="task-description">${description}${task.description.length > 100 ? '...' : ''}</p>` : ''}
          
          <div class="task-meta">
            <span class="task-status-badge status-${task.status}">${this.getStatusName(task.status)}</span>
            <span class="task-category">${categoryName}</span>
            ${dueDate ? `<span class="task-due-date ${isOverdue ? 'overdue' : ''}">${formatDate(dueDate)}</span>` : ''}
            <span class="task-priority priority-${task.priority}">${this.getPriorityName(task.priority)}</span>
          </div>
        </div>
        
        <div class="task-actions">
          <button class="btn btn-sm btn-outline edit-task-btn" data-task-id="${task.id}">
            <i class="icon-edit"></i>
          </button>
          <button class="btn btn-sm btn-danger delete-task-btn" data-task-id="${task.id}">
            <i class="icon-delete"></i>
          </button>
        </div>
      </div>
    `;
  },
  
  bindTaskItemEvents() {
    // 任务复选框
    document.querySelectorAll('.task-checkbox').forEach(checkbox => {
      checkbox.addEventListener('change', (e) => {
        const taskId = e.target.dataset.taskId;
        this.toggleTaskComplete(taskId, e.target.checked);
      });
    });
    
    // 编辑按钮
    document.querySelectorAll('.edit-task-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const taskId = e.currentTarget.dataset.taskId;
        window.location.hash = `#/tasks/${taskId}/edit`;
      });
    });
    
    // 删除按钮
    document.querySelectorAll('.delete-task-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const taskId = e.currentTarget.dataset.taskId;
        this.deleteTask(taskId);
      });
    });
    
    // 任务项点击（查看详情）
    document.querySelectorAll('.task-item').forEach(item => {
      // 排除按钮和复选框
      item.addEventListener('click', (e) => {
        if (e.target.closest('.task-actions') || e.target.classList.contains('task-checkbox')) {
          return;
        }
        
        const taskId = item.dataset.taskId;
        window.location.hash = `#/tasks/${taskId}`;
      });
    });
  },
  
  toggleTaskComplete(taskId, isComplete) {
    // 获取当前任务
    const state = window.store.getState();
    const task = state.tasks.find(t => t.id === taskId);
    
    if (!task) {
      NotificationService.show('任务未找到', 'error');
      return;
    }
    
    // 更新任务状态
    const updatedTask = {
      ...task,
      status: isComplete ? TASK_STATUS.COMPLETED : TASK_STATUS.IN_PROGRESS,
      updatedDate: new Date().toISOString()
    };
    
    // 分发更新任务action
    window.store.dispatch({
      type: 'UPDATE_TASK',
      payload: updatedTask
    });
    
    // 显示通知
    const message = isComplete ? '任务已标记为完成' : '任务已标记为进行中';
    NotificationService.show(message, 'success');
    
    // 如果有API服务，这里可以调用API更新
    try {
      TaskService.update(taskId, updatedTask);
    } catch (error) {
      console.error('更新任务失败:', error);
      // 可以考虑回滚状态或显示错误
    }
  },
  
  deleteTask(taskId) {
    if (confirm('确定要删除这个任务吗？此操作不可撤销。')) {
      // 分发删除任务action
      window.store.dispatch({
        type: 'DELETE_TASK',
        payload: taskId
      });
      
      // 显示通知
      NotificationService.show('任务已删除', 'success');
      
      // 如果有API服务，这里可以调用API删除
      try {
        TaskService.delete(taskId);
      } catch (error) {
        console.error('删除任务失败:', error);
        // 可以考虑回滚状态或显示错误
      }
    }
  },
  
  getStatusClass(status) {
    return `status-${status}`;
  },
  
  getPriorityClass(priority) {
    return `priority-${priority}`;
  },
  
  getStatusName(status) {
    const statusNames = {
      [TASK_STATUS.PENDING]: '待处理',
      [TASK_STATUS.IN_PROGRESS]: '进行中',
      [TASK_STATUS.COMPLETED]: '已完成',
      [TASK_STATUS.CANCELLED]: '已取消'
    };
    
    return statusNames[status] || status;
  },
  
  getPriorityName(priority) {
    const priorityNames = {
      low: '低',
      medium: '中',
      high: '高',
      urgent: '紧急'
    };
    
    return priorityNames[priority] || priority;
  },
  
  getCategoryName(categoryId) {
    const category = TASK_CATEGORIES.find(cat => cat.id === categoryId);
    return category ? category.name : '未分类';
  }
};
```

## 11.8 应用入口与初始化

### 11.8.1 应用初始化

```javascript
// src/index.js
import { Store } from './state/store.js';
import appReducer from './state/reducers.js';
import { thunkMiddleware, loggerMiddleware } from './state/middleware.js';
import Router from './router/router.js';
import routes from './router/routes.js';
import NotificationService from './services/notification.js';
import AuthService from './services/auth.js';

// 初始化状态管理
const store = new Store(
  { user: null, tasks: [], loading: false, filter: {} },
  appReducer
);

// 添加中间件（简化版中间件实现）
const originalDispatch = store.dispatch;
store.dispatch = (action) => {
  // 应用thunk中间件
  if (typeof action === 'function') {
    return action(store.dispatch, store.getState);
  }
  
  // 应用logger中间件
  console.group(`Action: ${action.type}`);
  console.log('Prev State:', store.getState());
  console.log('Action:', action);
  
  const result = originalDispatch(action);
  
  console.log('Next State:', store.getState());
  console.groupEnd();
  
  return result;
};

// 将store暴露到全局，以便组件访问
window.store = store;

// 初始化路由
const router = new Router(routes);

// 检查用户认证状态
async function checkAuthStatus() {
  try {
    if (AuthService.isAuthenticated()) {
      const user = await AuthService.getCurrentUser();
      store.dispatch({
        type: 'SET_USER',
        payload: user
      });
      
      // 更新UI显示用户信息
      updateAuthUI(true);
    } else {
      updateAuthUI(false);
    }
  } catch (error) {
    console.error('检查认证状态失败:', error);
    updateAuthUI(false);
  }
}

// 更新认证UI
function updateAuthUI(isAuthenticated) {
  const authButtons = document.getElementById('auth-buttons');
  const userInfo = document.getElementById('user-info');
  const username = document.getElementById('username');
  
  if (isAuthenticated) {
    const state = store.getState();
    const user = state.user;
    
    authButtons.style.display = 'none';
    userInfo.style.display = 'flex';
    username.textContent = user.name || '用户';
  } else {
    authButtons.style.display = 'flex';
    userInfo.style.display = 'none';
  }
}

// 设置全局事件监听器
function setupGlobalEventListeners() {
  // 退出登录按钮
  document.getElementById('logout-btn').addEventListener('click', async () => {
    try {
      await AuthService.logout();
      store.dispatch({ type: 'LOGOUT' });
      updateAuthUI(false);
      NotificationService.show('已成功退出登录', 'success');
      
      // 如果不在登录页面，重定向到登录页
      if (!window.location.hash.includes('/login')) {
        router.navigate('/login');
      }
    } catch (error) {
      console.error('退出登录失败:', error);
      NotificationService.show('退出登录失败', 'error');
    }
  });
  
  // 登录按钮
  document.getElementById('login-btn').addEventListener('click', () => {
    router.navigate('/login');
  });
  
  // 注册按钮
  document.getElementById('register-btn').addEventListener('click', () => {
    router.navigate('/register');
  });
  
  // 监听状态变化更新UI
  store.subscribe(() => {
    const state = store.getState();
    updateAuthUI(!!state.user);
  });
}

// 初始化应用
async function initializeApp() {
  // 设置全局事件监听器
  setupGlobalEventListeners();
  
  // 检查认证状态
  await checkAuthStatus();
  
  // 如果用户已认证，加载任务数据
  if (store.getState().user) {
    try {
      // 这里可以加载任务数据
      // await store.dispatch(fetchTasks());
    } catch (error) {
      console.error('加载任务数据失败:', error);
      NotificationService.show('加载任务数据失败', 'error');
    }
  }
}

// 当DOM加载完成后初始化应用
document.addEventListener('DOMContentLoaded', initializeApp);
```

### 11.8.2 添加样式补充

```css
/* src/styles/components/task-list.css */
.task-list-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.page-header h2 {
  margin: 0;
  color: var(--dark-color);
}

.page-actions {
  display: flex;
  gap: 0.5rem;
}

.search-filter-container {
  margin-bottom: 1.5rem;
  background-color: white;
  border-radius: var(--border-radius);
  padding: 1rem;
  box-shadow: var(--box-shadow);
}

.search-container {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.search-container input {
  flex: 1;
}

.filter-container {
  border-top: 1px solid #e9ecef;
  padding-top: 1rem;
}

.filter-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.filter-group {
  flex: 1;
  min-width: 150px;
}

.filter-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.task-list-container {
  background-color: white;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  overflow: hidden;
}

.list-view-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e9ecef;
}

.view-toggles {
  display: flex;
  gap: 0.25rem;
}

.sort-controls {
  width: 250px;
}

.tasks-list {
  padding: 1rem;
}

/* 列表视图样式 */
.tasks-list.list-view {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.tasks-list.list-view .task-item {
  display: flex;
  align-items: flex-start;
  padding: 1rem;
  border: 1px solid #e9ecef;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.tasks-list.list-view .task-item:hover {
  border-color: var(--primary-color);
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.tasks-list.list-view .task-item.completed {
  opacity: 0.7;
  background-color: #f8f9fa;
}

.tasks-list.list-view .task-item.overdue {
  border-color: var(--danger-color);
}

.tasks-list.list-view .task-status {
  margin-right: 1rem;
  padding-top: 0.25rem;
}

.task-checkbox {
  width: 1.25rem;
  height: 1.25rem;
  cursor: pointer;
}

.tasks-list.list-view .task-content {
  flex: 1;
}

.tasks-list.list-view .task-title {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
  cursor: pointer;
}

.tasks-list.list-view .task-description {
  margin: 0 0 0.75rem;
  color: var(--secondary-color);
  line-height: 1.4;
}

.tasks-list.list-view .task-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  font-size: 0.85rem;
}

.task-status-badge,
.task-category,
.task-due-date,
.task-priority {
  padding: 0.2rem 0.5rem;
  border-radius: var(--border-radius);
  font-size: 0.75rem;
  font-weight: 500;
}

.task-status-badge {
  color: white;
}

.task-status-badge.status-pending {
  background-color: var(--info-color);
}

.task-status-badge.status-in_progress {
  background-color: var(--warning-color);
}

.task-status-badge.status-completed {
  background-color: var(--success-color);
}

.task-status-badge.status-cancelled {
  background-color: var(--secondary-color);
}

.task-category {
  background-color: #e9ecef;
  color: var(--secondary-color);
}

.task-due-date {
  background-color: #e3f2fd;
  color: var(--primary-color);
}

.task-due-date.overdue {
  background-color: #ffebee;
  color: var(--danger-color);
}

.task-priority {
  color: white;
}

.task-priority.priority-low {
  background-color: var(--info-color);
}

.task-priority.priority-medium {
  background-color: var(--warning-color);
}

.task-priority.priority-high {
  background-color: var(--danger-color);
}

.task-priority.priority-urgent {
  background-color: #721c24;
  background-color: #8b0000;
}

.tasks-list.list-view .task-actions {
  display: flex;
  gap: 0.25rem;
}

/* 网格视图样式 */
.tasks-list.grid-view {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.tasks-list.grid-view .task-item {
  display: flex;
  flex-direction: column;
  padding: 1rem;
  border: 1px solid #e9ecef;
  border-radius: var(--border-radius);
  height: 100%;
  transition: var(--transition);
}

.tasks-list.grid-view .task-item:hover {
  border-color: var(--primary-color);
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.tasks-list.grid-view .task-status {
  margin-bottom: 0.75rem;
  align-self: flex-start;
}

.tasks-list.grid-view .task-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.tasks-list.grid-view .task-title {
  margin: 0 0 0.5rem;
  font-size: 1rem;
  cursor: pointer;
}

.tasks-list.grid-view .task-description {
  margin: 0 0 1rem;
  color: var(--secondary-color);
  line-height: 1.4;
  flex: 1;
}

.tasks-list.grid-view .task-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  margin-bottom: 1rem;
}

.tasks-list.grid-view .task-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.25rem;
}

/* 空状态样式 */
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--secondary-color);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state h3 {
  margin: 0 0 0.5rem;
  color: var(--dark-color);
}

.empty-state p {
  margin: 0 0 1.5rem;
}
```

## 11.9 项目部署与优化

### 11.9.1 构建优化配置

```javascript
// vite.config.js (优化版)
import { defineConfig } from 'vite';

export default defineConfig({
  root: '.',
  server: {
    port: 3000,
    open: true
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    
    // 代码分割配置
    rollupOptions: {
      output: {
        manualChunks: {
          // 将 Chart.js 分离到单独的 chunk
          chart: ['chart.js'],
          
          // 将工具函数分离到单独的 chunk
          utils: ['./src/utils/helpers.js', './src/utils/validators.js']
        }
      }
    },
    
    // 资源内联阈值
    assetsInlineLimit: 4096,
    
    // 压缩选项
    minify: 'terser',
    terserOptions: {
      compress: {
        // 移除 console
        drop_console: true,
        // 移除 debugger
        drop_debugger: true,
        // 移除注释
        comments: false
      }
    }
  },
  
  publicDir: 'public',
  
  optimizeDeps: {
    include: ['chart.js']
  }
});
```

### 11.9.2 生产环境检查清单

1. **代码质量检查**
   - 移除所有调试代码和console语句
   - 检查是否有未使用的代码
   - 确保没有硬编码的API密钥或敏感信息

2. **性能优化**
   - 启用代码压缩和混淆
   - 实现适当的缓存策略
   - 优化图片和静态资源
   - 使用CDN加载第三方库

3. **安全检查**
   - 验证所有用户输入
   - 实施适当的CORS策略
   - 使用HTTPS
   - 检查XSS和CSRF防护

4. **兼容性测试**
   - 在主流浏览器中测试应用
   - 检查响应式设计在不同设备上的表现
   - 测试关键功能在低性能设备上的表现

### 11.9.3 部署脚本

```json
// package.json 部署脚本
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "deploy:staging": "npm run build && rsync -avz --delete dist/ user@staging-server:/var/www/task-manager-staging/",
    "deploy:production": "npm run build && rsync -avz --delete dist/ user@production-server:/var/www/task-manager/",
    "lint": "eslint src/ --ext .js",
    "lint:fix": "eslint src/ --ext .js --fix",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  }
}
```

## 11.10 总结与展望

### 11.10.1 项目总结

通过这个任务管理应用，我们综合运用了JavaScript的各种高级特性：

1. **ES6+特性**：类、箭头函数、解构赋值、Promise、async/await等
2. **模块化设计**：使用ES模块组织代码，实现清晰的代码结构
3. **状态管理**：实现了简单的Redux-like状态管理系统
4. **路由系统**：构建了自定义的前端路由器
5. **组件化架构**：采用面向对象的方法构建可复用的页面组件
6. **性能优化**：代码分割、懒加载、缓存策略等
7. **异步编程**：使用Promise和async/await处理异步操作
8. **DOM操作**：高效地操作DOM，更新用户界面
9. **事件处理**：实现复杂的事件委托和事件监听
10. **数据处理**：过滤、排序、搜索等数据处理操作

### 11.10.2 技术亮点

1. **纯JavaScript实现**：没有使用任何前端框架，展示了原生JavaScript的强大能力
2. **模块化架构**：清晰的目录结构和模块划分，易于维护和扩展
3. **响应式设计**：适配不同屏幕尺寸的响应式布局
4. **离线支持**：使用IndexedDB提供离线数据存储
5. **渐进式增强**：核心功能在任何环境下都能正常工作
6. **代码分割**：实现按需加载，减少初始加载时间
7. **状态持久化**：使用localStorage保存用户数据和状态

### 11.10.3 可能的扩展方向

1. **功能扩展**
   - 任务分享和协作
   - 文件附件支持
   - 任务提醒和通知
   - 多语言支持
   - 深色模式

2. **技术改进**
   - 使用Web Workers处理复杂数据计算
   - 实现更高级的缓存策略
   - 添加单元测试和集成测试
   - 使用TypeScript增强类型安全
   - 引入PWA特性

3. **架构优化**
   - 微前端架构
   - 服务端渲染(SSR)
   - 更细粒度的状态管理
   - 引入设计模式简化复杂度

4. **性能提升**
   - 虚拟滚动处理大量数据
   - 图片懒加载和压缩
   - 更智能的预加载策略
   - WebAssembly加速计算密集型任务

通过这个项目，我们不仅展示了JavaScript的强大能力，还演示了如何构建一个现代、高性能、可维护的单页应用。这个项目可以作为进一步学习和开发更复杂应用的基础。
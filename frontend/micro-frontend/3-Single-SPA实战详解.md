# 第三章：Single-SPA 实战详解

## 3.1 Single-SPA 简介

### 3.1.1 什么是 Single-SPA

Single-SPA 是一个开源的微前端框架，它允许你在同一个页面上使用多种前端框架（如 React、Vue、Angular 等）构建应用，而不需要刷新页面。它是微前端领域的先驱之一，为微前端架构提供了成熟稳定的解决方案。

### 3.1.2 Single-SPA 的核心概念

Single-SPA 的核心概念包括：

1. **应用（Application）**：独立的前端应用，可以是 React、Vue、Angular 等任何框架构建的应用
2. **生命周期函数**：每个应用都必须实现的一组函数，包括 bootstrap、mount、unmount
3. **路由匹配**：决定何时激活哪个应用的规则
4. **注册应用**：将应用注册到 Single-SPA 中的过程

## 3.2 Single-SPA 核心原理

### 3.2.1 工作机制

Single-SPA 的工作机制可以概括为以下几个步骤：

1. **应用注册**：将所有微应用注册到 Single-SPA 中，指定每个应用的激活条件
2. **路由监听**：监听浏览器的 URL 变化
3. **应用匹配**：根据当前 URL 匹配应该激活的应用
4. **生命周期管理**：调用应用的生命周期函数来加载、挂载或卸载应用
5. **状态协调**：确保同一时间只有一个应用处于激活状态（除非配置了并行激活）

### 3.2.2 生命周期函数

每个注册到 Single-SPA 的应用都必须实现三个生命周期函数：

1. **bootstrap**：应用初始化时调用，只会调用一次
2. **mount**：应用挂载到页面时调用
3. **unmount**：应用从页面卸载时调用

```javascript
// 应用生命周期函数示例
const lifecycles = {
  async bootstrap(props) {
    // 初始化应用
    console.log('应用正在初始化', props);
  },
  
  async mount(props) {
    // 挂载应用到页面
    console.log('应用正在挂载', props);
    // 渲染应用内容
  },
  
  async unmount(props) {
    // 从页面卸载应用
    console.log('应用正在卸载', props);
    // 清理应用资源
  }
};
```

## 3.3 Single-SPA 环境搭建

### 3.3.1 创建主应用

首先，我们需要创建一个主应用来协调所有的微应用。

1. 创建项目目录：
```bash
mkdir single-spa-demo
cd single-spa-demo
npm init -y
```

2. 安装依赖：
```bash
npm install single-spa
```

3. 创建主应用入口文件 `index.html`：
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Single-SPA Demo</title>
</head>
<body>
  <div id="nav-container"></div>
  <div id="app-container"></div>
  
  <script src="./main.js"></script>
</body>
</html>
```

4. 创建主应用 JavaScript 文件 `main.js`：
```javascript
import { registerApplication, start } from 'single-spa';

// 注册应用
registerApplication({
  name: 'react-app',
  app: () => import('./react-app/react.app.js'),
  activeWhen: ['/react']
});

registerApplication({
  name: 'vue-app',
  app: () => import('./vue-app/vue.app.js'),
  activeWhen: ['/vue']
});

// 启动 single-spa
start();
```

### 3.3.2 创建 React 微应用

1. 创建 React 应用目录：
```bash
mkdir react-app
```

2. 安装 React 依赖：
```bash
npm install react react-dom single-spa-react
```

3. 创建 React 应用入口文件 `react-app/react.app.js`：
```javascript
import React from 'react';
import ReactDOM from 'react-dom';
import singleSpaReact from 'single-spa-react';
import App from './App';

const lifecycles = singleSpaReact({
  React,
  ReactDOM,
  rootComponent: App,
  domElementGetter: () => document.getElementById('app-container')
});

export const { bootstrap, mount, unmount } = lifecycles;
```

4. 创建 React 组件 `react-app/App.js`：
```javascript
import React from 'react';

const App = () => {
  return (
    <div>
      <h1>React 微应用</h1>
      <p>这是一个使用 React 构建的微应用</p>
    </div>
  );
};

export default App;
```

### 3.3.3 创建 Vue 微应用

1. 创建 Vue 应用目录：
```bash
mkdir vue-app
```

2. 安装 Vue 依赖：
```bash
npm install vue@next single-spa-vue
```

3. 创建 Vue 应用入口文件 `vue-app/vue.app.js`：
```javascript
import { createApp } from 'vue';
import singleSpaVue from 'single-spa-vue';
import App from './App.vue';

const lifecycles = singleSpaVue({
  createApp,
  appOptions: {
    el: '#app-container',
    render() {
      return h(App);
    }
  }
});

export const { bootstrap, mount, unmount } = lifecycles;
```

4. 创建 Vue 组件 `vue-app/App.vue`：
```vue
<template>
  <div>
    <h1>Vue 微应用</h1>
    <p>这是一个使用 Vue 构建的微应用</p>
  </div>
</template>

<script>
export default {
  name: 'App'
};
</script>
```

## 3.4 Single-SPA 高级特性

### 3.4.1 应用间通信

在微前端架构中，应用间通信是一个重要的话题。Single-SPA 提供了几种应用间通信的方式：

1. **自定义事件**：
```javascript
// 发送事件
window.dispatchEvent(new CustomEvent('app-message', {
  detail: { message: 'Hello from React app' }
}));

// 监听事件
window.addEventListener('app-message', (event) => {
  console.log('收到消息:', event.detail.message);
});
```

2. **全局状态管理**：
```javascript
// 创建全局状态存储
window.globalState = {
  userInfo: null,
  theme: 'light'
};

// 在应用中访问和修改全局状态
console.log(window.globalState.theme);
window.globalState.userInfo = { name: 'John' };
```

### 3.4.2 路由配置

Single-SPA 提供了灵活的路由配置选项：

```javascript
// 简单路径匹配
activeWhen: '/dashboard'

// 函数匹配
activeWhen: (location) => location.pathname.startsWith('/admin')

// 多路径匹配
activeWhen: ['/users', '/profile']

// 复杂匹配
activeWhen: (location) => {
  return location.pathname === '/dashboard' || 
         location.pathname.startsWith('/reports/');
}
```

### 3.4.3 应用加载策略

Single-SPA 支持不同的应用加载策略：

1. **立即加载**：
```javascript
registerApplication({
  name: 'app1',
  app: () => import('./app1/app1.js'),
  activeWhen: ['/app1']
});
```

2. **懒加载**：
```javascript
registerApplication({
  name: 'app2',
  app: () => import('./app2/app2.js'),
  activeWhen: ['/app2'],
  customProps: {
    loadingTimeout: 3000
  }
});
```

## 3.5 Single-SPA 最佳实践

### 3.5.1 项目结构组织

推荐的项目结构：
```
single-spa-root/
├── src/
│   ├── apps/
│   │   ├── react-app/
│   │   ├── vue-app/
│   │   └── angular-app/
│   ├── root-config.js
│   └── index.html
├── package.json
└── webpack.config.js
```

### 3.5.2 错误处理

在 Single-SPA 中正确处理错误非常重要：

```javascript
// 在生命周期函数中处理错误
const lifecycles = singleSpaReact({
  React,
  ReactDOM,
  rootComponent: App,
  errorBoundary(err, info, props) {
    // 自定义错误边界
    return <div>应用加载出错: {err.message}</div>;
  }
});
```

### 3.5.3 性能优化

1. **代码分割**：
```javascript
// 使用动态导入实现代码分割
registerApplication({
  name: 'large-app',
  app: () => import(/* webpackChunkName: "large-app" */ './large-app/app.js'),
  activeWhen: ['/large-app']
});
```

2. **预加载**：
```javascript
// 预加载即将使用的应用
import { preloadApplications } from 'single-spa';

preloadApplications(['/dashboard']);
```

## 3.6 Single-SPA 与其他方案对比

### 3.6.1 与 qiankun 的对比

| 特性 | Single-SPA | qiankun |
|------|------------|---------|
| 成熟度 | 高 | 高 |
| 学习曲线 | 较陡峭 | 相对平缓 |
| 配置复杂度 | 较高 | 较低 |
| 社区支持 | 广泛 | 国内较强 |
| 沙箱隔离 | 需手动实现 | 内置支持 |

### 3.6.2 与 Module Federation 的对比

| 特性 | Single-SPA | Module Federation |
|------|------------|-------------------|
| 实现方式 | 运行时 | 构建时+运行时 |
| 技术栈 | 任意 | Webpack 5+ |
| 部署方式 | 独立部署 | 可独立可联合 |
| 共享依赖 | 需配置 | 自动共享 |

## 3.7 本章小结

本章详细介绍了 Single-SPA 微前端框架的使用方法，包括其核心概念、环境搭建、高级特性和最佳实践。我们通过实际代码示例演示了如何创建主应用和微应用，并展示了应用间通信、路由配置等高级功能。

Single-SPA 作为微前端领域的先驱，具有成熟稳定的特点，但也存在配置复杂、学习曲线较陡峭的问题。在实际项目中，需要根据团队技术栈和项目需求来选择是否使用 Single-SPA。

在下一章中，我们将学习另一种流行的微前端方案——Module Federation，了解它是如何通过 Webpack 5 的新特性来实现微前端架构的。

## 3.8 思考题

1. Single-SPA 的生命周期函数是如何工作的？
2. 如何在 Single-SPA 中实现应用间通信？
3. Single-SPA 与 qiankun 各自适用于什么场景？

## 3.8 示例代码

本章的完整示例代码已经保存在 `frontend/micro-frontend/code/chapter3/single-spa-demo` 目录中。

### 3.8.1 代码结构

```
single-spa-demo/
├── src/
│   ├── apps/
│   │   ├── react-app/
│   │   │   ├── App.js
│   │   │   └── react.app.js
│   │   └── vue-app/
│   │       ├── App.vue
│   │       └── vue.app.js
│   ├── main.js          # 主应用入口
│   └── index.html       # 主页面
├── package.json
└── webpack.config.js
```

### 3.8.2 运行示例

1. 进入示例代码目录：
```bash
cd frontend/micro-frontend/code/chapter3/single-spa-demo
```

2. 安装依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm start
```

4. 在浏览器中打开 http://localhost:9001

### 3.8.3 示例功能说明

- 主应用负责路由协调和应用注册
- React 微应用展示了计数器功能和应用间通信
- Vue 微应用同样展示了计数器功能和应用间通信
- 两个微应用可以通过自定义事件进行通信

### 3.8.4 路由说明

- `#/react` - 显示 React 微应用
- `#/vue` - 显示 Vue 微应用

### 3.8.5 应用间通信

本示例通过 Custom Events 实现应用间通信：
- React 应用可以向 Vue 应用发送消息
- Vue 应用可以向 React 应用发送消息

## 3.9 参考资料

1. Single-SPA 官方文档：https://single-spa.js.org/
2. single-spa-react：https://github.com/single-spa/single-spa-react
3. single-spa-vue：https://github.com/single-spa/single-spa-vue
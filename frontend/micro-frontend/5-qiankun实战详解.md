# 第五章 qiankun 实战详解

## 5.1 qiankun 简介

qiankun 是一个基于 single-spa 的微前端实现库，它可以帮助你将多个独立的前端应用聚合到一个主应用中，同时保持各个应用的独立开发和部署能力。qiankun 由蚂蚁金服开源，具有以下特点：

1. **简单易用**：接入方式简单，只需几行代码即可完成主应用和子应用的集成。
2. **技术栈无关**：支持任意技术栈的子应用，包括 React、Vue、Angular 等。
3. **样式隔离**：提供 CSS 样式隔离机制，避免子应用之间的样式冲突。
4. **JS 沙箱**：通过 JavaScript 沙箱机制，确保子应用之间的全局变量和事件监听器不会相互影响。
5. **资源预加载**：支持子应用资源的预加载，提升用户体验。
6. **生命周期管理**：提供完整的子应用生命周期管理，包括加载、挂载、卸载等。

## 5.2 qiankun 核心原理

### 5.2.1 应用注册与加载

qiankun 通过 `registerMicroApps` 方法注册子应用，并在路由匹配时动态加载子应用的资源。加载过程包括：

1. **HTML 获取**：通过 fetch 获取子应用的 HTML 内容
2. **资源解析**：解析 HTML 中的 script 和 link 标签
3. **脚本执行**：在沙箱环境中执行子应用的 JavaScript 代码
4. **样式处理**：将子应用的 CSS 样式进行隔离处理

### 5.2.2 JS 沙箱机制

qiankun 通过 Proxy 代理和快照两种方式实现 JavaScript 沙箱：

1. **快照沙箱**：适用于不支持 Proxy 的低版本浏览器，通过记录全局对象的快照来实现隔离
2. **代理沙箱**：适用于支持 Proxy 的现代浏览器，通过 Proxy 代理全局对象来实现隔离

### 5.2.3 样式隔离

qiankun 提供了两种样式隔离方案：

1. **CSS 前缀**：为子应用的 CSS 选择器添加特定前缀
2. **Shadow DOM**：使用浏览器原生的 Shadow DOM 特性实现样式隔离

## 5.3 环境搭建

### 5.3.1 创建主应用

1. 初始化项目：
```bash
mkdir qiankun-host && cd qiankun-host
npm init -y
```

2. 安装依赖：
```bash
npm install qiankun
```

3. 创建主应用入口文件：
```javascript
// src/index.js
import { registerMicroApps, start } from 'qiankun';

registerMicroApps([
  {
    name: 'react-app',
    entry: '//localhost:3001',
    container: '#container',
    activeRule: '/react',
  },
  {
    name: 'vue-app',
    entry: '//localhost:3002',
    container: '#container',
    activeRule: '/vue',
  },
]);

start();
```

### 5.3.2 创建 React 子应用

1. 初始化项目：
```bash
mkdir qiankun-react-app && cd qiankun-react-app
npm init -y
```

2. 安装依赖：
```bash
npm install react react-dom
npm install -D @babel/core @babel/preset-react webpack webpack-cli webpack-dev-server html-webpack-plugin
```

3. 配置 webpack：
```javascript
// webpack.config.js
module.exports = {
  entry: './src/index.js',
  output: {
    filename: 'bundle.js',
    library: 'reactApp',
    libraryTarget: 'umd',
    publicPath: '//localhost:3001/',
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        use: 'babel-loader',
        exclude: /node_modules/,
      },
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './public/index.html',
    }),
  ],
  devServer: {
    port: 3001,
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
  },
};
```

4. 创建入口文件：
```javascript
// src/index.js
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';

function render(props) {
  const { container } = props;
  ReactDOM.render(<App />, container ? container.querySelector('#root') : document.querySelector('#root'));
}

if (!window.__POWERED_BY_QIANKUN__) {
  render({});
}

export async function bootstrap() {
  console.log('React app bootstraped');
}

export async function mount(props) {
  console.log('React app mounted');
  render(props);
}

export async function unmount(props) {
  const { container } = props;
  ReactDOM.unmountComponentAtNode(container ? container.querySelector('#root') : document.querySelector('#root'));
}
```

### 5.3.3 创建 Vue 子应用

1. 初始化项目：
```bash
mkdir qiankun-vue-app && cd qiankun-vue-app
npm init -y
```

2. 安装依赖：
```bash
npm install vue
npm install -D webpack webpack-cli webpack-dev-server vue-loader vue-template-compiler html-webpack-plugin
```

3. 配置 webpack：
```javascript
// webpack.config.js
const { VueLoaderPlugin } = require('vue-loader');

module.exports = {
  entry: './src/main.js',
  output: {
    filename: 'bundle.js',
    library: 'vueApp',
    libraryTarget: 'umd',
    publicPath: '//localhost:3002/',
  },
  module: {
    rules: [
      {
        test: /\.vue$/,
        use: 'vue-loader',
      },
    ],
  },
  plugins: [
    new VueLoaderPlugin(),
    new HtmlWebpackPlugin({
      template: './public/index.html',
    }),
  ],
  devServer: {
    port: 3002,
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
  },
};
```

4. 创建入口文件：
```javascript
// src/main.js
import Vue from 'vue';
import App from './App.vue';

let instance = null;

function render(props = {}) {
  const { container } = props;
  instance = new Vue({
    render: h => h(App),
  }).$mount(container ? container.querySelector('#app') : '#app');
}

if (!window.__POWERED_BY_QIANKUN__) {
  render();
}

export async function bootstrap() {
  console.log('Vue app bootstraped');
}

export async function mount(props) {
  console.log('Vue app mounted');
  render(props);
}

export async function unmount() {
  instance.$destroy();
  instance.$el.innerHTML = '';
  instance = null;
}
```

## 5.4 高级特性

### 5.4.1 应用间通信

qiankun 提供了全局状态管理机制，用于实现应用间的通信：

```javascript
// 主应用
import { initGlobalState } from 'qiankun';

const actions = initGlobalState({ user: 'admin' });

actions.onGlobalStateChange((state, prev) => {
  // state: 变更后的状态
  // prev: 变更前的状态
  console.log(state, prev);
});

actions.setGlobalState({ user: 'qiankun' });
```

```javascript
// 子应用
export function mount(props) {
  // 获取主应用传递的 props
  const { onGlobalStateChange, setGlobalState } = props;
  
  // 监听状态变化
  onGlobalStateChange((state, prev) => {
    console.log(state, prev);
  });
  
  // 更新状态
  setGlobalState({ user: 'sub-app' });
}
```

### 5.4.2 资源预加载

qiankun 支持子应用资源的预加载，可以通过配置开启：

```javascript
import { registerMicroApps, start } from 'qiankun';

registerMicroApps([
  {
    name: 'react-app',
    entry: '//localhost:3001',
    container: '#container',
    activeRule: '/react',
  },
]);

// 开启预加载
start({
  prefetch: true, // 开启预加载
});
```

### 5.4.3 路由管理

在 qiankun 中，路由管理需要主应用和子应用协同工作：

1. 主应用负责子应用间的路由切换
2. 子应用负责自身的路由管理

```javascript
// 主应用路由配置
import { registerMicroApps, start } from 'qiankun';

registerMicroApps([
  {
    name: 'react-app',
    entry: '//localhost:3001',
    container: '#container',
    activeRule: '/react',
  },
  {
    name: 'vue-app',
    entry: '//localhost:3002',
    container: '#container',
    activeRule: '/vue',
  },
]);

start();
```

## 5.5 最佳实践

### 5.5.1 项目结构规划

建议采用以下项目结构：

```
micro-frontend/
├── main-app/          # 主应用
│   ├── src/
│   ├── package.json
│   └── webpack.config.js
├── react-sub-app/     # React 子应用
│   ├── src/
│   ├── package.json
│   └── webpack.config.js
└── vue-sub-app/       # Vue 子应用
    ├── src/
    ├── package.json
    └── webpack.config.js
```

### 5.5.2 公共依赖管理

为了避免重复加载公共依赖，可以采用以下策略：

1. 在主应用中引入公共依赖
2. 通过 webpack externals 配置将公共依赖外置

```javascript
// webpack.config.js
module.exports = {
  // ...
  externals: {
    react: 'React',
    'react-dom': 'ReactDOM',
  },
};
```

### 5.5.3 样式隔离策略

为避免样式冲突，建议：

1. 为子应用的 CSS 选择器添加命名空间
2. 使用 CSS Modules 或 CSS-in-JS 方案
3. 在必要时启用 Shadow DOM 隔离

### 5.5.4 错误处理与监控

1. 为子应用添加错误边界
2. 实现全局错误捕获机制
3. 集成前端监控系统

## 5.6 与其他微前端方案对比

### 5.6.1 qiankun 与 Module Federation

| 特性 | qiankun | Module Federation |
|------|---------|-------------------|
| 技术栈兼容性 | 任意技术栈 | 主要针对 Webpack 5 |
| 样式隔离 | 提供多种方案 | 需手动处理 |
| JS 沙箱 | 内置支持 | 需手动处理 |
| 学习成本 | 较低 | 中等 |
| 社区支持 | 良好 | 良好 |

### 5.6.2 qiankun 与 Single-SPA

| 特性 | qiankun | Single-SPA |
|------|---------|------------|
| 易用性 | 简单易用 | 需要更多配置 |
| 样式隔离 | 内置支持 | 需手动处理 |
| JS 沙箱 | 内置支持 | 需手动处理 |
| 资源预加载 | 内置支持 | 需手动实现 |

## 5.6 示例代码

### 5.6.1 项目结构

```
chapter5/
├── qiankun-main/          # 主应用
│   ├── public/
│   │   └── index.html     # 主应用HTML模板
│   ├── src/
│   │   └── index.js       # 主应用入口文件
│   ├── package.json       # 主应用依赖
│   └── webpack.config.js  # 主应用Webpack配置
├── qiankun-react/         # React子应用
│   ├── public/
│   │   └── index.html     # React子应用HTML模板
│   ├── src/
│   │   ├── App.js         # React应用组件
│   │   └── index.js       # React子应用入口文件
│   ├── package.json       # React子应用依赖
│   └── webpack.config.js  # React子应用Webpack配置
└── qiankun-vue/           # Vue子应用
    ├── public/
    │   └── index.html     # Vue子应用HTML模板
    ├── src/
    │   ├── App.vue        # Vue应用组件
    │   └── index.js       # Vue子应用入口文件
    ├── package.json       # Vue子应用依赖
    └── webpack.config.js  # Vue子应用Webpack配置
```

### 5.6.2 主应用代码

#### 主应用入口文件 (qiankun-main/src/index.js)

```javascript
import { registerMicroApps, start } from 'qiankun';

// 注册子应用
registerMicroApps([
  {
    name: 'react-app',
    entry: '//localhost:3002',
    container: '#react-app',
    activeRule: '/react',
  },
  {
    name: 'vue-app',
    entry: '//localhost:3003',
    container: '#vue-app',
    activeRule: '/vue',
  },
]);

// 启动 qiankun
start();
```

### 5.6.3 React子应用代码

#### React子应用入口文件 (qiankun-react/src/index.js)

```javascript
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// 为了让主应用能够正确识别子应用，需要添加一些生命周期函数
export async function bootstrap() {
  console.log('React app bootstraped');
}

export async function mount(props) {
  console.log('React app mounted');
  const root = ReactDOM.createRoot(document.getElementById('root'));
  root.render(<App />);
}

export async function unmount(props) {
  console.log('React app unmounted');
  const root = ReactDOM.createRoot(document.getElementById('root'));
  root.unmount();
}
```

### 5.6.4 Vue子应用代码

#### Vue子应用入口文件 (qiankun-vue/src/index.js)

```javascript
import { createApp } from 'vue';
import App from './App';

let instance = null;

// 为了让主应用能够正确识别子应用，需要添加一些生命周期函数
export async function bootstrap() {
  console.log('Vue app bootstraped');
}

export async function mount(props) {
  console.log('Vue app mounted');
  instance = createApp(App);
  instance.mount('#root');
}

export async function unmount(props) {
  console.log('Vue app unmounted');
  instance.unmount();
  instance = null;
}
```

### 5.6.5 运行示例

1. 安装依赖：
   ```bash
   # 在主应用目录
   cd qiankun-main
   npm install
   
   # 在React子应用目录
   cd qiankun-react
   npm install
   
   # 在Vue子应用目录
   cd qiankun-vue
   npm install
   ```

2. 启动应用：
   ```bash
   # 启动主应用
   cd qiankun-main
   npm start
   
   # 启动React子应用
   cd qiankun-react
   npm start
   
   # 启动Vue子应用
   cd qiankun-vue
   npm start
   ```

3. 访问应用：
   - 主应用：http://localhost:3001
   - React子应用：http://localhost:3002
   - Vue子应用：http://localhost:3003

## 5.7 总结

qiankun 作为一个成熟且易用的微前端解决方案，具有以下优势：

1. **易于集成**：只需少量代码即可完成主应用和子应用的集成
2. **技术栈无关**：支持任意技术栈的子应用
3. **内置隔离机制**：提供 JS 沙箱和样式隔离机制
4. **丰富的特性**：支持资源预加载、应用间通信等高级特性

在选择微前端方案时，如果项目对技术栈兼容性要求较高，且希望快速集成，qiankun 是一个非常好的选择。

qiankun作为一款优秀的微前端解决方案，通过基于single-spa的封装，提供了更加友好的API和更丰富的功能。它解决了微前端开发中的诸多痛点，如应用隔离、样式隔离、JS沙箱等，使得微前端的实施变得更加简单和高效。

在实际项目中，qiankun已经得到了广泛的应用，许多大型企业级应用都采用了qiankun作为微前端解决方案。通过合理地使用qiankun，我们可以构建出更加灵活、可维护和可扩展的前端应用架构。

## 5.8 参考资料

1. qiankun 官方文档：https://qiankun.umijs.org/
2. qiankun GitHub 仓库：https://github.com/umijs/qiankun
3. single-spa 官方文档：https://single-spa.js.org/
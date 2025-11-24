# 第四章：Module Federation 实战详解

## 4.1 Module Federation 简介

### 4.1.1 什么是 Module Federation

Module Federation 是 Webpack 5 引入的一项革命性功能，它允许在运行时动态地从另一个独立构建的应用程序中加载代码模块。这项技术为微前端架构提供了一种全新的实现方式，使得不同的团队可以独立开发、构建和部署自己的应用模块，同时又能在运行时无缝集成。

### 4.1.2 Module Federation 的核心概念

Module Federation 的核心概念包括：

1. **Host（宿主）**：消费其他远程模块的应用
2. **Remote（远程）**：提供模块给其他应用使用的应用
3. **Shared（共享）**：在多个应用之间共享的依赖
4. **Federated Module（联邦模块）**：通过 Module Federation 共享的模块

## 4.2 Module Federation 核心原理

### 4.2.1 工作机制

Module Federation 的工作机制可以概括为以下几个步骤：

1. **构建时配置**：在 Webpack 配置中声明哪些模块要暴露出去，哪些模块要从远程加载
2. **运行时加载**：当应用启动时，Module Federation 会自动从远程应用加载所需的模块
3. **依赖共享**：通过共享机制避免重复加载相同的依赖包
4. **动态集成**：在运行时将远程模块集成到本地应用中

### 4.2.2 配置项详解

Module Federation 的主要配置项包括：

1. **name**：当前应用的名称，用于标识应用
2. **filename**：暴露的远程入口文件名
3. **exposes**：暴露给其他应用的模块
4. **remotes**：从其他应用加载的远程模块
5. **shared**：共享的依赖库

```javascript
// Webpack 配置中的 ModuleFederationPlugin 示例
const { ModuleFederationPlugin } = require('webpack').container;

new ModuleFederationPlugin({
  name: 'app1',
  filename: 'remoteEntry.js',
  exposes: {
    './Button': './src/Button',
    './Header': './src/Header'
  },
  remotes: {
    app2: 'app2@http://localhost:3002/remoteEntry.js'
  },
  shared: {
    react: { singleton: true },
    'react-dom': { singleton: true }
  }
})
```

## 4.3 Module Federation 环境搭建

### 4.3.1 创建 Host 应用

首先，我们需要创建一个 Host 应用来消费远程模块。

1. 创建项目目录：
```bash
mkdir mf-host
cd mf-host
npm init -y
```

2. 安装依赖：
```bash
npm install webpack webpack-cli webpack-dev-server html-webpack-plugin
```

3. 创建 Webpack 配置文件 `webpack.config.js`：
```javascript
const HtmlWebpackPlugin = require('html-webpack-plugin');
const { ModuleFederationPlugin } = require('webpack').container;
const path = require('path');

module.exports = {
  entry: './src/index.js',
  mode: 'development',
  devServer: {
    port: 3001,
    hot: true,
  },
  output: {
    publicPath: 'auto',
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        loader: 'babel-loader',
        exclude: /node_modules/,
        options: {
          presets: ['@babel/preset-react'],
        },
      },
    ],
  },
  plugins: [
    new ModuleFederationPlugin({
      name: 'host',
      filename: 'remoteEntry.js',
      remotes: {
        remote: 'remote@http://localhost:3002/remoteEntry.js',
      },
      shared: { react: { singleton: true }, 'react-dom': { singleton: true } },
    }),
    new HtmlWebpackPlugin({
      template: './public/index.html',
    }),
  ],
};
```

4. 创建公共目录和文件：
```bash
mkdir -p src public
```

5. 创建主页面模板 `public/index.html`：
```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>Module Federation Host</title>
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>
```

6. 创建入口文件 `src/index.js`：
```javascript
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';

ReactDOM.render(<App />, document.getElementById('root'));
```

7. 创建主应用组件 `src/App.js`：
```javascript
import React from 'react';

const RemoteButton = React.lazy(() => import('remote/Button'));

const App = () => {
  return (
    <div>
      <h1>Host Application</h1>
      <p>This is the host application consuming a remote component.</p>
      <React.Suspense fallback="Loading Button...">
        <RemoteButton />
      </React.Suspense>
    </div>
  );
};

export default App;
```

### 4.3.2 创建 Remote 应用

接下来，我们创建一个 Remote 应用来提供模块。

1. 创建项目目录：
```bash
mkdir mf-remote
cd mf-remote
npm init -y
```

2. 安装依赖：
```bash
npm install webpack webpack-cli webpack-dev-server html-webpack-plugin
```

3. 创建 Webpack 配置文件 `webpack.config.js`：
```javascript
const HtmlWebpackPlugin = require('html-webpack-plugin');
const { ModuleFederationPlugin } = require('webpack').container;
const path = require('path');

module.exports = {
  entry: './src/index.js',
  mode: 'development',
  devServer: {
    port: 3002,
    hot: true,
  },
  output: {
    publicPath: 'auto',
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        loader: 'babel-loader',
        exclude: /node_modules/,
        options: {
          presets: ['@babel/preset-react'],
        },
      },
    ],
  },
  plugins: [
    new ModuleFederationPlugin({
      name: 'remote',
      filename: 'remoteEntry.js',
      exposes: {
        './Button': './src/Button',
      },
      shared: { react: { singleton: true }, 'react-dom': { singleton: true } },
    }),
    new HtmlWebpackPlugin({
      template: './public/index.html',
    }),
  ],
};
```

4. 创建公共目录和文件：
```bash
mkdir -p src public
```

5. 创建主页面模板 `public/index.html`：
```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>Module Federation Remote</title>
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>
```

6. 创建入口文件 `src/index.js`：
```javascript
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';

ReactDOM.render(<App />, document.getElementById('root'));
```

7. 创建主应用组件 `src/App.js`：
```javascript
import React from 'react';
import Button from './Button';

const App = () => {
  return (
    <div>
      <h1>Remote Application</h1>
      <p>This is the remote application exposing a component.</p>
      <Button />
    </div>
  );
};

export default App;
```

8. 创建要暴露的组件 `src/Button.js`：
```javascript
import React from 'react';

const Button = () => {
  const handleClick = () => {
    alert('Button clicked from remote application!');
  };

  return (
    <button onClick={handleClick} style={{ padding: '10px 20px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
      Remote Button
    </button>
  );
};

export default Button;
```

## 4.4 Module Federation 高级特性

### 4.4.1 动态远程加载

Module Federation 支持动态加载远程模块：

```javascript
// 动态加载远程模块
const loadComponent = async (scope, module) => {
  // 初始化共享作用域
  await __webpack_init_sharing__('default');
  
  // 加载远程容器
  const container = window[scope];
  await container.init(__webpack_share_scopes__.default);
  
  // 获取模块工厂
  const factory = await container.get(module);
  
  // 创建模块
  return factory();
};

// 使用示例
const RemoteComponent = React.lazy(() => loadComponent('remote', './Component'));
```

### 4.4.2 版本兼容性

Module Federation 提供了版本兼容性检查机制：

```javascript
// 在 shared 配置中指定版本要求
shared: {
  react: { 
    singleton: true, 
    requiredVersion: '^17.0.0' 
  },
  'react-dom': { 
    singleton: true, 
    requiredVersion: '^17.0.0' 
  }
}
```

### 4.4.3 模块预加载

为了提升用户体验，我们可以预加载远程模块：

```javascript
// 预加载远程模块
const prefetchRemote = async () => {
  await import('remote/Button');
};

// 在应用启动时预加载
prefetchRemote();
```

## 4.5 Module Federation 最佳实践

### 4.5.1 项目结构组织

推荐的项目结构：
```
micro-frontend-project/
├── packages/
│   ├── host/
│   │   ├── src/
│   │   ├── webpack.config.js
│   │   └── package.json
│   ├── remote1/
│   │   ├── src/
│   │   ├── webpack.config.js
│   │   └── package.json
│   └── remote2/
│       ├── src/
│       ├── webpack.config.js
│       └── package.json
├── package.json
└── lerna.json
```

### 4.5.2 依赖管理策略

1. **共享依赖**：
```javascript
shared: {
  // 对于 React 等核心库，使用 singleton 确保单一实例
  react: { singleton: true, requiredVersion: '^17.0.0' },
  'react-dom': { singleton: true, requiredVersion: '^17.0.0' },
  
  // 对于工具库，可以选择性共享
  lodash: { singleton: true, requiredVersion: '^4.17.21' },
  
  // 对于业务组件库，可以不共享
  // 'my-component-library': {}
}
```

2. **版本冲突解决**：
```javascript
// 当遇到版本冲突时，可以强制使用特定版本
shared: {
  react: { 
    singleton: true, 
    requiredVersion: '^17.0.0',
    eager: true // 立即加载，避免异步问题
  }
}
```

### 4.5.3 错误处理

在 Module Federation 中正确处理错误非常重要：

```javascript
// 包装远程组件以处理加载错误
const RemoteComponentWrapper = ({ scope, module }) => {
  const [error, setError] = useState(null);
  
  const Component = React.useMemo(() => React.lazy(async () => {
    try {
      return await loadComponent(scope, module);
    } catch (err) {
      setError(err);
      return { default: () => <div>Error loading component</div> };
    }
  }), [scope, module]);

  if (error) {
    return <div>Failed to load remote component: {error.message}</div>;
  }

  return (
    <React.Suspense fallback="Loading...">
      <Component />
    </React.Suspense>
  );
};
```

## 4.6 Module Federation 与其他方案对比

### 4.6.1 与 Single-SPA 的对比

| 特性 | Module Federation | Single-SPA |
|------|-------------------|------------|
| 实现方式 | 构建时+运行时 | 运行时 |
| 技术栈 | Webpack 5+ | 任意 |
| 部署方式 | 可独立可联合 | 独立部署 |
| 共享依赖 | 自动共享 | 需配置 |
| 学习成本 | 中等 | 较高 |

### 4.6.2 与 qiankun 的对比

| 特性 | Module Federation | qiankun |
|------|-------------------|---------|
| 沙箱隔离 | 需手动实现 | 内置支持 |
| 样式隔离 | 需手动实现 | 内置支持 |
| JS 隔离 | 需手动实现 | 内置支持 |
| 配置复杂度 | 中等 | 较低 |
| 性能 | 较好 | 中等 |

## 4.7 本章小结

本章详细介绍了 Module Federation 的使用方法，包括其核心概念、环境搭建、高级特性和最佳实践。我们通过实际代码示例演示了如何创建 Host 应用和 Remote 应用，并展示了动态加载、版本兼容性等高级功能。

Module Federation 作为 Webpack 5 的新特性，为微前端架构提供了一种原生的解决方案。它通过构建时配置和运行时加载的方式，实现了模块的动态集成，具有良好的性能表现。但同时也需要注意依赖管理和版本兼容性等问题。

在下一章中，我们将学习另一种流行的微前端方案——qiankun，了解它是如何通过沙箱隔离等技术来实现更完善的微前端架构的。

## 4.8 思考题

1. Module Federation 的工作原理是什么？
2. 如何处理 Module Federation 中的依赖版本冲突？
3. Module Federation 与 Single-SPA 各自适用于什么场景？

## 4.8 示例代码

本章的完整示例代码已经保存在 `frontend/micro-frontend/code/chapter4` 目录中。

### 4.8.1 代码结构

```
chapter4/
├── mf-host/          # Host 应用
│   ├── src/
│   │   ├── App.js
│   │   ├── bootstrap.js
│   │   └── index.js
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   └── webpack.config.js
└── mf-remote/        # Remote 应用
    ├── src/
    │   ├── App.js
    │   ├── Button.js
    │   ├── Header.js
    │   ├── bootstrap.js
    │   └── index.js
    ├── public/
    │   └── index.html
    ├── package.json
    └── webpack.config.js
```

### 4.8.2 运行示例

1. 打开两个终端窗口

2. 在第一个终端中启动 Remote 应用：
```bash
cd frontend/micro-frontend/code/chapter4/mf-remote
npm install
npm start
```

3. 在第二个终端中启动 Host 应用：
```bash
cd frontend/micro-frontend/code/chapter4/mf-host
npm install
npm start
```

4. 在浏览器中打开以下地址：
   - Remote 应用: http://localhost:3002
   - Host 应用: http://localhost:3001

### 4.8.3 常见问题及解决方案

#### 共享模块的急切消费问题

在使用 Module Federation 时，可能会遇到 "Shared module is not available for eager consumption" 错误。这是因为共享模块在应用启动时被急切地消费，但此时模块还未准备好。

**解决方案：**

1. 创建一个 bootstrap.js 文件：
```javascript
// src/bootstrap.js
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';

ReactDOM.render(<App />, document.getElementById('root'));
```

2. 修改入口文件 index.js：
```javascript
// src/index.js
import('./bootstrap');
```

这种方法通过异步导入来延迟 React 和 ReactDOM 的消费，确保在共享模块准备好后再使用它们。

### 4.8.3 示例功能说明

- Remote 应用暴露了 Button 和 Header 两个组件
- Host 应用消费了 Remote 应用暴露的组件
- 两个应用共享 React 和 ReactDOM 依赖
- 使用 React.lazy 实现组件的动态加载

### 4.8.4 Module Federation 配置说明

#### Remote 应用配置
```javascript
new ModuleFederationPlugin({
  name: 'remote',
  filename: 'remoteEntry.js',
  exposes: {
    './Button': './src/Button',
    './Header': './src/Header',
  },
  shared: { 
    react: { singleton: true, requiredVersion: '^17.0.2' }, 
    'react-dom': { singleton: true, requiredVersion: '^17.0.2' } 
  },
})
```

#### Host 应用配置
```javascript
new ModuleFederationPlugin({
  name: 'host',
  filename: 'remoteEntry.js',
  remotes: {
    remote: 'remote@http://localhost:3002/remoteEntry.js',
  },
  shared: { 
    react: { singleton: true, requiredVersion: '^17.0.2' }, 
    'react-dom': { singleton: true, requiredVersion: '^17.0.2' } 
  },
})
```

## 4.9 参考资料

1. Webpack Module Federation 官方文档：https://webpack.js.org/concepts/module-federation/
2. Module Federation GitHub 仓库：https://github.com/module-federation/module-federation-examples
3. Webpack 官方文档：https://webpack.js.org/
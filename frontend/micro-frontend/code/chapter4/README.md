# Module Federation 微前端示例

这是一个使用 Webpack 5 Module Federation 构建的微前端示例项目，包含一个 Host 应用和一个 Remote 应用。

## 项目结构

```
chapter4/
├── mf-host/          # Host 应用
│   ├── src/
│   │   ├── App.js
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
    │   └── index.js
    ├── public/
    │   └── index.html
    ├── package.json
    └── webpack.config.js
```

## 如何运行

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

## 功能说明

- Remote 应用暴露了 Button 和 Header 两个组件
- Host 应用消费了 Remote 应用暴露的组件
- 两个应用共享 React 和 ReactDOM 依赖
- 使用 React.lazy 实现组件的动态加载

## Module Federation 配置说明

### Remote 应用配置
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

### Host 应用配置
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
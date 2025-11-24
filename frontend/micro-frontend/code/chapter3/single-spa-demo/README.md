# Single-SPA 微前端示例

这是一个使用 Single-SPA 构建的微前端示例项目，包含一个主应用和两个微应用（React 和 Vue）。

## 项目结构

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

## 如何运行

1. 安装依赖：
```bash
npm install
```

2. 启动开发服务器：
```bash
npm start
```

3. 在浏览器中打开 http://localhost:9001

## 功能说明

- 主应用负责路由协调和应用注册
- React 微应用展示了计数器功能和应用间通信
- Vue 微应用同样展示了计数器功能和应用间通信
- 两个微应用可以通过自定义事件进行通信

## 路由说明

- `#/react` - 显示 React 微应用
- `#/vue` - 显示 Vue 微应用

## 应用间通信

本示例通过 Custom Events 实现应用间通信：
- React 应用可以向 Vue 应用发送消息
- Vue 应用可以向 React 应用发送消息
# 第5章：Vite与框架集成（React/Vue）

在本章节中，我们将深入探讨Vite如何与现代JavaScript框架（特别是React和Vue）无缝集成，以及如何利用这种集成来构建高效的开发工作流程和生产应用。

## 5.1 框架集成概述

Vite 对主流框架提供了出色的原生支持，这得益于其精心设计的框架插件生态系统。本章将重点介绍：

- Vite与React的集成与配置
- Vite与Vue的集成与配置
- 框架特定的优化策略
- 跨框架组件开发
- 集成过程中的常见问题与解决方案

## 5.2 Vite与React集成

### 5.2.1 创建React项目

Vite提供了官方的React模板，可以快速创建一个基于React的Vite项目：

```bash
# 使用npm创建React项目
npm create vite@latest my-react-app -- --template react

# 使用yarn创建React项目
yarn create vite my-react-app --template react

# 使用pnpm创建React项目
pnpm create vite my-react-app --template react
```

对于TypeScript项目，可以使用react-ts模板：

```bash
npm create vite@latest my-react-app -- --template react-ts
```

### 5.2.2 React项目结构解析

创建的React项目结构如下：

```
my-react-app/
├── node_modules/
├── public/
│   └── vite.svg
├── src/
│   ├── assets/
│   │   └── react.svg
│   ├── App.css
│   ├── App.jsx
│   ├── index.css
│   └── main.jsx
├── .gitignore
├── index.html
├── package.json
├── README.md
└── vite.config.js
```

### 5.2.3 React特定配置

Vite为React项目提供了`@vitejs/plugin-react`插件，该插件包含了一系列针对React的优化。默认情况下，它已经被添加到项目的依赖中并在vite.config.js中配置。

下面是一个典型的React项目vite.config.js配置：

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // 其他配置...
})
```

### 5.2.4 React插件高级配置

`@vitejs/plugin-react`插件提供了一些高级配置选项：

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [
    react({
      // 启用Fast Refresh
      fastRefresh: true,
      // 配置Babel
      babel: {
        // 配置Babel插件
        plugins: ['my-babel-plugin'],
        // 忽略某些文件的Babel转换
        exclude: 'node_modules/**'
      },
      // 控制文件过滤规则
      include: '**/*.{jsx,tsx}'
    })
  ]
})
```

### 5.2.5 React组件库集成

Vite与常见的React组件库（如Ant Design、Material-UI等）配合使用非常简单。以Ant Design为例：

```bash
# 安装Ant Design
npm install antd
```

然后在src/main.jsx中引入样式：

```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import 'antd/dist/reset.css' // Ant Design的样式
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

## 5.3 Vite与Vue集成

### 5.3.1 创建Vue项目

Vite提供了官方的Vue模板，可以快速创建一个基于Vue的Vite项目：

```bash
# 创建Vue项目
npm create vite@latest my-vue-app -- --template vue

# 创建Vue+TypeScript项目
npm create vite@latest my-vue-app -- --template vue-ts
```

### 5.3.2 Vue项目结构解析

创建的Vue项目结构如下：

```
my-vue-app/
├── node_modules/
├── public/
│   └── vite.svg
├── src/
│   ├── assets/
│   │   └── vue.svg
│   ├── components/
│   │   └── HelloWorld.vue
│   ├── App.vue
│   └── main.js
├── .gitignore
├── index.html
├── package.json
├── README.md
└── vite.config.js
```

### 5.3.3 Vue特定配置

Vite为Vue提供了`@vitejs/plugin-vue`插件（Vue 3）和`@vitejs/plugin-vue2`插件（Vue 2）。

Vue 3项目的vite.config.js配置：

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
})
```

Vue 2项目的vite.config.js配置：

```javascript
import { defineConfig } from 'vite'
import vue2 from '@vitejs/plugin-vue2'

export default defineConfig({
  plugins: [vue2()],
})
```

### 5.3.4 Vue插件高级配置

`@vitejs/plugin-vue`插件提供了一些高级配置选项：

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [
    vue({
      // 启用Vue SFC中script的内联类型检查
      script: {
        defineModel: true, // 启用defineModel宏
        propsDestructure: true // 启用props解构
      },
      // 配置模板编译选项
      template: {
        // 启用Vue模板的响应式编译器
        compilerOptions: {
          isCustomElement: (tag) => tag.startsWith('my-custom-')
        }
      }
    })
  ]
})
```

### 5.3.5 Vue组件库集成

以Element Plus为例，集成Vue 3的组件库：

```bash
# 安装Element Plus
npm install element-plus
```

然后在src/main.js中引入：

```javascript
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'

const app = createApp(App)

app.use(ElementPlus)
app.mount('#app')
```

## 5.4 框架集成优化策略

### 5.4.1 Tree-shaking优化

Vite对两种框架都提供了优秀的Tree-shaking支持，特别是结合组件库使用时：

1. **按需引入组件**：

```jsx
// React - 按需引入Ant Design组件
import { Button, Card } from 'antd';

// Vue - 按需引入Element Plus组件
import { ElButton, ElCard } from 'element-plus';
import 'element-plus/es/components/button/style/css';
import 'element-plus/es/components/card/style/css';
```

2. **使用自动导入插件**：

对于Vue，可以使用`unplugin-vue-components`插件自动导入组件：

```bash
npm install -D unplugin-vue-components unplugin-auto-import
```

配置vite.config.js：

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
    }),
    Components({
      resolvers: [ElementPlusResolver()],
    }),
  ],
})
```

### 5.4.2 开发体验优化

1. **React Fast Refresh**：

Vite的React插件内置了React Fast Refresh，提供了比传统热重载更好的开发体验。

2. **Vue HMR**：

Vue在Vite中的HMR支持更为强大，包括组件状态保留、CSS热更新等。

### 5.4.3 类型支持优化

对于TypeScript项目：

1. **React项目**：确保配置了正确的TypeScript类型定义

```bash
npm install -D @types/react @types/react-dom
```

2. **Vue项目**：使用`vue-tsc`进行类型检查

```bash
npm install -D vue-tsc typescript
```

## 5.5 跨框架组件开发

Vite允许我们创建可以在React和Vue之间共享的组件。有几种方法可以实现这一点：

### 5.5.1 使用Web Components

Web Components是浏览器原生支持的组件模型，可以被任何框架使用：

```javascript
// 定义一个简单的Web Component
class MyComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.shadowRoot.innerHTML = `
      <style>
        p { color: blue; }
      </style>
      <p>Hello from Web Component!</p>
    `;
  }
}

customElements.define('my-component', MyComponent);
```

### 5.5.2 使用无渲染组件库

如Headless UI或Radix UI，可以与任一框架集成。

### 5.5.3 使用框架适配器

为同一组件逻辑创建不同的框架特定适配器：

```javascript
// core-logic.js - 框架无关的核心逻辑
export function calculateSomething(a, b) {
  return a + b;
}

// ReactComponent.jsx - React适配器
import React from 'react';
import { calculateSomething } from './core-logic';

export function ReactComponent({ a, b }) {
  const result = calculateSomething(a, b);
  return <div>Result: {result}</div>;
}

// VueComponent.vue - Vue适配器
<template>
  <div>Result: {{ result }}</div>
</template>

<script>
import { calculateSomething } from './core-logic';

export default {
  props: ['a', 'b'],
  computed: {
    result() {
      return calculateSomething(this.a, this.b);
    }
  }
}
</script>
```

## 5.6 常见问题与解决方案

### 5.6.1 React常见问题

1. **React Hooks错误**

**问题**：使用React Hooks时出现"Invalid hook call"错误。

**解决方案**：确保没有重复安装React，检查package.json并使用`npm dedupe`。

2. **JSX转换问题**

**问题**：JSX语法未正确转换。

**解决方案**：确保正确配置了`@vitejs/plugin-react`，并检查文件扩展名是否为.jsx或.tsx。

### 5.6.2 Vue常见问题

1. **模板编译错误**

**问题**：Vue模板编译时出错。

**解决方案**：检查模板语法，并确保在vite.config.js中正确配置了`@vitejs/plugin-vue`。

2. **单文件组件样式问题**

**问题**：SFC中的样式不生效。

**解决方案**：检查scoped样式是否正确应用，或是否有CSS命名冲突。

## 5.7 实验：创建框架集成项目

### 5.7.1 实验1：React + Ant Design集成

**目标**：创建一个使用Ant Design组件库的React项目。

**步骤**：

1. 创建项目：
```bash
npm create vite@latest react-antd-app -- --template react
cd react-antd-app
npm install
```

2. 安装Ant Design：
```bash
npm install antd
```

3. 修改src/main.jsx：
```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import 'antd/dist/reset.css'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

4. 修改App.jsx，使用Ant Design组件：
```jsx
import { Button, Card, Space } from 'antd'
import { DownloadOutlined, UploadOutlined } from '@ant-design/icons'
import './App.css'

function App() {
  return (
    <div className="App">
      <Card title="Ant Design + Vite Demo" style={{ width: 300 }}>
        <Space direction="vertical">
          <Button type="primary" icon={<DownloadOutlined />}>下载</Button>
          <Button icon={<UploadOutlined />}>上传</Button>
        </Space>
      </Card>
    </div>
  )
}

export default App
```

5. 运行项目：
```bash
npm run dev
```

### 5.7.2 实验2：Vue + Element Plus集成

**目标**：创建一个使用Element Plus组件库的Vue项目。

**步骤**：

1. 创建项目：
```bash
npm create vite@latest vue-element-app -- --template vue
cd vue-element-app
npm install
```

2. 安装Element Plus和自动导入插件：
```bash
npm install element-plus
npm install -D unplugin-vue-components unplugin-auto-import
```

3. 修改vite.config.js：
```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
    }),
    Components({
      resolvers: [ElementPlusResolver()],
    }),
  ],
})
```

4. 修改App.vue：
```vue
<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-header">
          <span>Element Plus + Vite Demo</span>
        </div>
      </template>
      <el-button type="primary" icon="Download" circle></el-button>
      <el-button type="success" icon="Upload" circle></el-button>
    </el-card>
  </div>
</template>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
```

5. 运行项目：
```bash
npm run dev
```

## 5.8 最佳实践总结

1. **选择合适的框架模板**：使用官方提供的框架模板来确保最佳的初始配置。

2. **使用框架特定插件**：确保正确配置了React或Vue的官方Vite插件。

3. **按需加载组件库**：特别是对于大型组件库，使用按需导入可以减小包体积。

4. **使用自动导入工具**：考虑使用`unplugin-auto-import`和`unplugin-vue-components`等工具来简化开发。

5. **配置路径别名**：

```javascript
// vite.config.js
import { defineConfig } from 'vite'
import path from 'path'

export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

6. **优化开发服务器配置**：

```javascript
// vite.config.js
import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    port: 3000,
    open: true,
    // 配置API代理
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
```

7. **使用TypeScript**：对于任何规模的项目，考虑使用TypeScript以获得更好的类型安全性和开发体验。

8. **添加ESLint和Prettier**：确保代码质量和一致性。

通过本章的学习，你应该能够熟练地将Vite与React或Vue集成，并使用各种优化策略来构建高效的应用程序。在下一章中，我们将探讨Vite项目的生产环境部署和CI/CD配置。
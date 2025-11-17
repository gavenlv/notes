# Vue.js生态系统与其他工具集成示例项目

本项目展示了Vue.js生态系统与其他工具的集成方式，包括开发工具、构建工具、测试工具等。

## 项目结构

```
code/
├── .env                      # 环境配置文件
├── .env.development          # 开发环境配置
├── .env.production           # 生产环境配置
├── .eslintrc.cjs             # ESLint配置
├── .prettierrc.json          # Prettier配置
├── package.json              # 项目依赖和脚本配置
├── tsconfig.json             # TypeScript配置
├── tsconfig.node.json        # Node.js TypeScript配置
├── vite.config.js            # Vite构建配置
├── vitest.config.js          # Vitest测试配置
├── playwright.config.js      # Playwright E2E测试配置
├── index.html                # 入口HTML文件
├── src/
│   ├── main.js               # 应用入口文件
│   ├── App.vue               # 根组件
│   ├── assets/               # 静态资源
│   │   └── styles/
│   │       └── global.css    # 全局样式
│   ├── components/           # 可复用组件
│   │   ├── UserProfile.vue   # 用户资料组件
│   │   ├── MobileCard.vue    # 移动端卡片组件
│   │   ├── DataTable.vue     # 数据表格组件
│   │   └── ChartViewer.vue   # 图表展示组件
│   ├── composables/          # Composition API组合函数
│   │   ├── useApi.ts         # API请求组合函数
│   │   └── useDebug.ts       # 调试组合函数
│   ├── pages/                # 页面组件
│   │   ├── Home.vue          # 首页
│   │   └── About.vue         # 关于页面
│   ├── router/               # 路由配置
│   │   └── index.js          # 路由定义
│   ├── types/                # TypeScript类型定义
│   │   └── index.ts          # 类型定义文件
│   └── utils/                # 工具函数
│       └── apiClient.ts      # API客户端
├── tests/                    # 测试文件
│   ├── unit/                 # 单元测试
│   │   ├── setup.js          # 测试环境设置
│   │   └── components/
│   │       └── UserProfile.test.js  # 用户资料组件测试
│   └── e2e/                  # 端到端测试
│       └── home.spec.js      # 首页E2E测试
└── docs/                     # 文档
    └── examples.md           # 代码示例说明
```

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式运行

```bash
npm run dev
```

这将启动开发服务器，默认在 `http://localhost:3000` 访问。

### 构建生产版本

```bash
npm run build
```

构建后的文件将输出到 `dist` 目录。

### 预览生产构建

```bash
npm run preview
```

### 运行单元测试

```bash
npm run test:unit
```

### 运行端到端测试

```bash
npm run test:e2e
```

### 代码检查

```bash
npm run lint
```

## 技术栈

- **Vue 3**: 渐进式JavaScript框架
- **Vite**: 新一代前端构建工具
- **Vue Router**: 官方路由管理器
- **Pinia**: 轻量级状态管理库
- **TypeScript**: JavaScript的超集，提供静态类型检查
- **Element Plus**: Vue 3的桌面端组件库
- **Vant**: 移动端Vue组件库
- **ECharts**: 强大的图表库
- **Axios**: 基于Promise的HTTP客户端
- **Vitest**: Vite原生单元测试框架
- **Playwright**: 现代化端到端测试工具

## 功能特性

1. **Vue DevTools集成**: 展示如何使用Vue DevTools进行调试
2. **服务端渲染概念**: 演示SSR和Nuxt.js的基本概念
3. **移动端开发**: 集成Vant组件库，展示移动端组件开发
4. **TypeScript支持**: 完整的TypeScript类型定义和使用
5. **构建工具配置**: Vite配置优化示例
6. **测试体系**: 包含单元测试和端到端测试示例
7. **第三方库集成**: Element Plus、ECharts等库的集成使用

## 项目亮点

- **现代化开发体验**: 使用Vite提供快速的开发服务器和热更新
- **类型安全**: 通过TypeScript提供完整的类型检查和智能提示
- **组件化架构**: 清晰的组件结构和职责分离
- **响应式设计**: 支持桌面端和移动端的响应式布局
- **完整的测试覆盖**: 包含单元测试和端到端测试示例
- **性能优化**: 合理的代码分割和资源优化策略

## 学习资源

- [Vue.js官方文档](https://vuejs.org/)
- [Vite官方文档](https://vitejs.dev/)
- [Vue DevTools](https://devtools.vuejs.org/)
- [Nuxt.js](https://nuxtjs.org/)
- [Element Plus](https://element-plus.org/)
- [Vant](https://vant-contrib.gitee.io/vant/)
- [TypeScript](https://www.typescriptlang.org/)
- [Vitest](https://vitest.dev/)
- [Playwright](https://playwright.dev/)

## 许可证

本项目采用MIT许可证。
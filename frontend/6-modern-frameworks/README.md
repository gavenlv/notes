# 现代 JavaScript 框架学习指南

## 📋 目录
- [React 框架基础](#react-框架基础)
- [Vue.js 框架基础](#vuejs-框架基础)
- [Angular 框架基础](#angular-框架基础)
- [框架比较与选择](#框架比较与选择)
- [状态管理](#状态管理)
- [路由管理](#路由管理)
- [组件设计模式](#组件设计模式)
- [性能优化](#性能优化)
- [学习资源](#学习资源)

## React 框架基础

### 核心概念
- **虚拟 DOM (Virtual DOM)**：React 的高效渲染机制
- **组件化开发**：函数组件与类组件
- **JSX 语法**：JavaScript 与 HTML 的融合语法
- **单向数据流**：数据流向清晰，易于追踪

### Hooks 系统
- **useState**：状态管理的基础 Hook
- **useEffect**：副作用管理
- **useContext**：上下文共享
- **自定义 Hooks**：逻辑复用

### 生命周期
- **类组件生命周期**：挂载、更新、卸载
- **函数组件生命周期**：使用 Hooks 管理

### [React 详细示例](/notes/frontend/6-modern-frameworks/code/react-basics.html)

## Vue.js 框架基础

### 核心概念
- **响应式系统**：双向数据绑定
- **模板语法**：声明式渲染
- **组件系统**：单文件组件 (SFC)
- **Vue 实例**：应用的根实例

### Composition API vs Options API
- **Options API**：传统的对象式 API
- **Composition API**：基于函数的逻辑复用
- **setup 函数**：组合式 API 的入口

### 生命周期
- **选项式 API 生命周期**：beforeCreate, created, beforeMount 等
- **组合式 API 生命周期**：onMounted, onUpdated, onUnmounted 等

### [Vue.js 详细示例](/notes/frontend/6-modern-frameworks/code/vue-basics.html)

## Angular 框架基础

### 核心概念
- **模块系统**：NgModule
- **组件系统**：基于 TypeScript 的组件
- **服务与依赖注入**：DI 系统
- **模板与指令**：结构化与属性指令

### 装饰器
- **@Component**：组件装饰器
- **@NgModule**：模块装饰器
- **@Injectable**：服务装饰器

### 生命周期
- **组件生命周期钩子**：ngOnInit, ngOnChanges, ngOnDestroy 等
- **变更检测**：Angular 的变更检测策略

### [Angular 详细示例](/notes/frontend/6-modern-frameworks/code/angular-basics.html)

## 框架比较与选择

### 技术特点对比

| 特性 | React | Vue.js | Angular |
|------|-------|--------|---------|
| 渲染方式 | 虚拟 DOM | 虚拟 DOM | 虚拟 DOM |
| 语言 | JavaScript/TypeScript | JavaScript/TypeScript | TypeScript |
| 模板系统 | JSX | 单文件组件 | 模板语法 |
| 学习曲线 | 中等 | 低 | 高 |
| 社区活跃度 | 高 | 高 | 中高 |
| 企业采用率 | 高 | 高 | 中高 |
| 性能 | 优秀 | 优秀 | 良好 |

### 选择建议
- **React**：适合需要高度定制化、重视性能的大型应用
- **Vue.js**：适合快速开发、学习成本低的项目
- **Angular**：适合大型企业级应用，需要完整框架支持

### [框架比较详细示例](/notes/frontend/6-modern-frameworks/code/framework-comparison.html)

## 状态管理

### React 状态管理
- **Redux**：集中式状态管理
- **Context API + useReducer**：轻量级状态管理
- **Zustand**：现代化的状态管理库

### Vue.js 状态管理
- **Vuex**：Vue 官方状态管理
- **Pinia**：Vue 3 推荐的状态管理
- **Provide/Inject**：组件树中的状态共享

### Angular 状态管理
- **NgRx**：基于 Redux 的状态管理
- **服务 + Subject**：RxJS 状态管理

### [状态管理详细示例](/notes/frontend/6-modern-frameworks/code/state-management.html)

## 路由管理

### React Router
- **版本演进**：v4, v5, v6
- **路由配置**：声明式路由
- **路由守卫**：权限控制
- **嵌套路由**：复杂布局管理

### Vue Router
- **路由配置**：动态路由
- **导航守卫**：前置、后置守卫
- **路由过渡**：页面切换动画

### Angular Router
- **路由配置**：模块化路由
- **CanActivate 守卫**：访问控制
- **Resolve 守卫**：数据预加载

### [路由管理详细示例](/notes/frontend/6-modern-frameworks/code/routing.html)

## 组件设计模式

### 容器组件 vs 展示组件
- **容器组件**：处理逻辑和状态
- **展示组件**：专注于 UI 渲染

### HOC (高阶组件)
- **模式实现**：函数返回组件
- **应用场景**：逻辑复用、权限控制

### Render Props
- **模式实现**：通过 props 传递渲染函数
- **灵活性**：比 HOC 更灵活的逻辑复用

### [组件设计模式详细示例](/notes/frontend/6-modern-frameworks/code/component-patterns.html)

## 性能优化

### React 性能优化
- **React.memo**：组件记忆化
- **useMemo/useCallback**：避免不必要的重新渲染
- **代码分割**：动态 import()
- **虚拟列表**：长列表优化

### Vue.js 性能优化
- **keep-alive**：组件缓存
- **v-memo**：模板记忆化
- **异步组件**：按需加载

### Angular 性能优化
- **OnPush 变更检测**：减少检测次数
- **NgFor 优化**：trackBy 函数
- **懒加载模块**：减小初始加载体积

### [性能优化详细示例](/notes/frontend/6-modern-frameworks/code/performance-optimization.html)

## 学习资源

### 推荐官方文档
- [React 官方文档](https://reactjs.org/)
- [Vue.js 官方文档](https://vuejs.org/)
- [Angular 官方文档](https://angular.io/)

### 推荐书籍
- 《深入 React 技术栈》- 陈屹
- 《Vue.js 设计与实现》- 霍春阳
- 《Angular 权威指南》- 熊节

### 在线教程
- [React.dev](https://react.dev/)
- [Vue Mastery](https://www.vuemastery.com/)
- [Angular University](https://angular-university.io/)

### 实战项目
- 构建个人博客系统
- 开发电商平台
- 创建实时协作工具
- 实现数据可视化仪表盘

## 💡 学习建议

1. **理解核心概念**：先掌握框架的核心设计理念和思想
2. **对比学习**：理解不同框架的异同点，选择适合项目的框架
3. **实践为主**：通过实际项目巩固所学知识
4. **关注生态**：学习框架周边工具和最佳实践
5. **持续更新**：关注框架的版本更新和新特性

## 🎯 学习目标

完成本阶段学习后，你将能够：

- 熟练掌握至少一种主流 JavaScript 框架
- 理解现代前端框架的设计思想和工作原理
- 设计并开发可维护、可扩展的前端应用
- 应用合适的状态管理和路由策略
- 进行框架性能优化
- 具备团队协作开发复杂前端应用的能力

---

*框架是工具，理解原理才是核心。选择适合自己项目的框架，构建卓越的用户体验！* 🚀
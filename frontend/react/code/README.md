# React从零到专家 - 实践代码示例

## 📋 项目简介

这个项目包含了《React从零到专家》教程的所有实践代码示例。每个章节都有独立的代码模块，可以直接运行和测试。

## 🛠️ 安装和运行

### 前置要求

- Node.js 16.x 或更高版本
- npm 或 yarn

### 安装依赖

```bash
# 安装依赖
npm install

# 或者使用yarn
yarn
```

### 启动开发服务器

```bash
# 启动开发服务器
npm start

# 或者使用yarn
yarn start
```

应用将在浏览器中打开 http://localhost:3000

## 📁 项目结构

```
code/
├── public/               # 静态资源
│   └── index.html       # HTML模板
├── src/                 # 源代码
│   ├── chapters/        # 各章节代码
│   │   ├── chapter1/   # 第一章示例
│   │   │   ├── examples/   # 各种示例
│   │   │   └── styles.css # 样式文件
│   │   ├── chapter2/   # 第二章示例
│   │   ├── chapter3/   # 第三章示例
│   │   └── chapter4/   # 第四章示例
│   ├── App.js          # 主应用组件
│   ├── index.js        # 应用入口
│   └── index.css      # 全局样式
└── package.json        # 项目配置
```

## 🎯 各章节内容

### 第一章：React基础入门

本章节包含以下示例：

1. **JSX语法示例**：展示JSX的基本语法、变量插入、条件渲染、列表渲染等
2. **组件使用示例**：展示函数组件、状态组件、组件组合等概念
3. **Props传递示例**：展示Props的基本用法、children prop、回调函数等
4. **第一个React应用**：完整的用户卡片展示应用

### 第二章：React核心概念

*即将推出*

### 第三章：React组件设计

*即将推出*

### 第四章：React状态管理

*即将推出*

## 💡 学习建议

1. **按顺序学习**：建议按照章节顺序学习，每个章节都建立在前一章的基础上
2. **动手实践**：不要只看代码，要亲自运行、修改和扩展
3. **理解原理**：不仅要知道如何写代码，还要理解为什么这样写
4. **查阅文档**：遇到问题时，及时查阅[React官方文档](https://react.dev/)
5. **练习扩展**：尝试修改示例代码，添加新功能

## 🔧 修改和扩展

如果你想修改或扩展示例代码：

1. 找到对应章节的示例文件
2. 修改代码并保存
3. 浏览器会自动刷新显示修改结果
4. 如果有编译错误，查看控制台的错误信息

## 🐛 常见问题

### Q: 修改代码后页面没有更新？

A: 检查控制台是否有编译错误，或者尝试刷新浏览器页面。

### Q: 运行 `npm start` 时出现端口占用错误？

A: 可以使用以下命令指定不同的端口：
```bash
PORT=3001 npm start
```

### Q: 我想使用yarn而不是npm？

A: 完全可以！只需要将 `npm install` 替换为 `yarn`，将 `npm start` 替换为 `yarn start`。

## 📚 相关资源

- [React官方文档](https://react.dev/)
- [React教程](https://react.dev/learn)
- [JavaScript基础教程](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript)

---

**享受你的React学习之旅！** 🚀
# 第一章：React基础入门

## 1.1 React简介

### 什么是React？

React是由Facebook（现Meta）开发的一个用于构建用户界面的JavaScript库。它采用组件化的开发方式，让开发者可以构建大型应用而不必担心代码的复杂性。

### React的核心特性

- **声明式渲染**：使用JSX语法描述UI，React会自动管理DOM更新
- **组件化**：将UI拆分为独立可复用的组件
- **单向数据流**：数据从父组件流向子组件，便于追踪和调试
- **虚拟DOM**：通过虚拟DOM减少对实际DOM的操作，提高性能

### React的优势

- **高效性**：虚拟DOM和Diff算法使React应用性能出色
- **灵活性**：可以与各种技术栈结合使用
- **可维护性**：组件化和单向数据流使代码更易维护
- **大型社区支持**：丰富的第三方库和工具

## 1.2 开发环境搭建

### 安装Node.js和npm

React开发需要Node.js环境，建议安装最新的LTS版本。

**Windows安装：**

1. 访问[Node.js官网](https://nodejs.org/)
2. 下载Windows安装包
3. 运行安装程序，按照提示完成安装

**验证安装：**

```bash
node -v
npm -v
```

### 创建React项目

我们将使用Vite来创建React项目，它是一个现代化的前端构建工具，提供更快的开发体验。

```bash
# 使用npm创建Vite React项目
npm create vite@latest my-react-app -- --template react

# 进入项目目录
cd my-react-app

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 编辑器配置

推荐使用VSCode并安装以下扩展：

- **ESLint**：代码检查
- **Prettier**：代码格式化
- **React Developer Tools**：React开发工具

## 1.3 JSX语法基础

### 什么是JSX？

JSX是JavaScript的语法扩展，允许你在JavaScript中编写类似HTML的代码。它看起来像模板语言，但具有JavaScript的全部功能。

### 基本语法

```jsx
const element = <h1>Hello, world!</h1>;
```

### JSX中使用JavaScript表达式

```jsx
const name = 'React';
const element = <h1>Hello, {name}!</h1>;
```

### JSX属性

```jsx
const element = <div className="container" style={{ color: 'red' }}>Hello World</div>;
```

### JSX嵌套

```jsx
const element = (
  <div>
    <h1>Hello</h1>
    <p>React is amazing!</p>
  </div>
);
```

### JSX与JavaScript函数

```jsx
function getGreeting(user) {
  if (user) {
    return <h1>Hello, {user}!</h1>;
  }
  return <h1>Hello, Stranger.</h1>;
}
```

## 1.4 第一个React应用

### 项目结构解析

一个典型的React项目结构如下：

```
my-react-app/
├── public/
│   └── index.html
├── src/
│   ├── assets/
│   ├── components/
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── package.json
└── vite.config.js
```

### 创建第一个组件

```jsx
// App.jsx
import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div>
        <a href="https://vitejs.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.jsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  )
}

export default App
```

### 渲染到DOM

```jsx
// main.jsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

## 1.5 组件的概念与使用

### 什么是组件？

组件是React应用的构建块，一个组件就是一个可以独立复用的UI单元。

### 函数组件

```jsx
function Welcome(props) {
  return <h1>Hello, {props.name}</h1>;
}
```

### 组件的复用

```jsx
function App() {
  return (
    <div>
      <Welcome name="Alice" />
      <Welcome name="Bob" />
      <Welcome name="Charlie" />
    </div>
  );
}
```

### 组件的组合

```jsx
function Greeting() {
  return (
    <div>
      <Welcome name="Alice" />
      <Message text="Welcome to React!" />
    </div>
  );
}

function Message(props) {
  return <p>{props.text}</p>;
}
```

## 1.6 Props的使用

### 什么是Props？

Props是组件之间传递数据的方式，从父组件传递给子组件。

### Props的基本使用

```jsx
function UserProfile(props) {
  return (
    <div>
      <h2>{props.name}</h2>
      <p>Age: {props.age}</p>
      <p>Email: {props.email}</p>
    </div>
  );
}

function App() {
  return (
    <UserProfile 
      name="John Doe" 
      age={30} 
      email="john@example.com" 
    />
  );
}
```

### Props的只读性

**重要原则**：组件永远不能修改自己的props。Props是只读的。

```jsx
// 错误！props不能被修改
function Counter(props) {
  props.count = props.count + 1; // 错误！
  return <h1>Count: {props.count}</h1>;
}
```

### Props的默认值

```jsx
function Greeting({ name = 'Guest' }) {
  return <h1>Hello, {name}!</h1>;
}
```

## 1.7 练习与实践

### 练习1：创建一个问候组件

创建一个可复用的问候组件，接收用户的名字，并显示个性化的问候语。

### 练习2：创建一个产品列表

创建一个产品列表组件，接收产品数组作为props，并渲染每个产品的名称、价格和描述。

### 练习3：嵌套组件练习

创建一个页面布局组件，包含头部、内容区域和页脚，然后在内容区域中嵌入其他组件。

## 1.8 本章小结

本章我们学习了React的基础知识，包括：

- React的核心概念和优势
- 如何搭建React开发环境
- JSX语法基础
- 创建和使用React组件
- Props的传递和使用

这些基础知识是React开发的基石，掌握好它们将为后续更深入的学习打下坚实的基础。在接下来的章节中，我们将学习React的核心概念，如状态管理、生命周期等。

## 代码示例

本章的代码示例可以在[code目录](./code/)中找到。每个示例都包含完整的代码和运行说明。

# 第二章：React核心概念

## 2.1 React状态管理（State）

### 什么是状态？

状态（State）是React组件中用于存储和管理组件内部数据的对象。当状态发生变化时，组件会重新渲染以反映最新的数据。

### 使用useState Hook

在React 16.8引入Hooks后，函数组件可以使用`useState` Hook来管理状态。

```jsx
import { useState } from 'react';

function Counter() {
  // 声明一个state变量count，初始值为0
  // setCount是更新count的函数
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={() => setCount(count + 1)}>
        Click me
      </button>
    </div>
  );
}
```

### useState的工作原理

- `useState`接收一个初始值作为参数
- 返回一个数组，第一个元素是当前状态值，第二个元素是更新状态的函数
- 调用更新函数时，React会重新渲染组件
- 状态更新是异步的，不要依赖立即获取更新后的状态

### 状态更新的最佳实践

```jsx
// 直接设置新值
setCount(5);

// 基于当前状态计算新值（推荐）
setCount(prevCount => prevCount + 1);

// 对象状态更新
setUser(prevUser => ({
  ...prevUser,
  name: 'New Name'
}));
```

## 2.2 React Hooks详解

### 什么是Hooks？

Hooks是React 16.8引入的新特性，允许你在不编写class的情况下使用state以及其他React特性。

### useState Hook

用于在函数组件中添加状态，前面已经介绍过。

### useEffect Hook

用于处理副作用（如数据获取、订阅或手动更改DOM）。

```jsx
import { useState, useEffect } from 'react';

function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 副作用函数
    async function fetchUser() {
      setLoading(true);
      try {
        const response = await fetch(`/api/users/${userId}`);
        const data = await response.json();
        setUser(data);
      } catch (error) {
        console.error('Failed to fetch user:', error);
      } finally {
        setLoading(false);
      }
    }

    // 执行副作用
    fetchUser();

    // 清理函数
    return () => {
      // 清理逻辑，如取消请求、清除定时器等
    };
  }, [userId]); // 依赖数组，当userId变化时重新执行

  if (loading) return <div>Loading...</div>;
  if (!user) return <div>User not found</div>;

  return (
    <div>
      <h2>{user.name}</h2>
      <p>{user.email}</p>
    </div>
  );
}
```

### useContext Hook

用于访问React上下文。

```jsx
import { useContext } from 'react';
import { ThemeContext } from './ThemeContext';

function ThemedButton() {
  const theme = useContext(ThemeContext);
  
  return (
    <button style={{ 
      backgroundColor: theme.background, 
      color: theme.foreground 
    }}>
      Themed Button
    </button>
  );
}
```

### useReducer Hook

用于复杂状态逻辑的管理，类似于Redux的简化版本。

```jsx
import { useReducer } from 'react';

// 定义reducer函数
function counterReducer(state, action) {
  switch (action.type) {
    case 'increment':
      return { count: state.count + 1 };
    case 'decrement':
      return { count: state.count - 1 };
    case 'reset':
      return { count: 0 };
    default:
      throw new Error(`Unsupported action type: ${action.type}`);
  }
}

function Counter() {
  // 初始化状态为{ count: 0 }
  const [state, dispatch] = useReducer(counterReducer, { count: 0 });

  return (
    <div>
      <p>Count: {state.count}</p>
      <button onClick={() => dispatch({ type: 'increment' })}>+</button>
      <button onClick={() => dispatch({ type: 'decrement' })}>-</button>
      <button onClick={() => dispatch({ type: 'reset' })}>Reset</button>
    </div>
  );
}
```

## 2.3 事件处理

### 事件处理的基本语法

```jsx
function Button() {
  function handleClick() {
    console.log('Button clicked!');
  }

  return <button onClick={handleClick}>Click me</button>;
}
```

### 向事件处理函数传递参数

```jsx
function TodoList({ todos, onDeleteTodo }) {
  return (
    <ul>
      {todos.map(todo => (
        <li key={todo.id}>
          {todo.text}
          <button onClick={() => onDeleteTodo(todo.id)}>Delete</button>
        </li>
      ))}
    </ul>
  );
}
```

### 事件对象

```jsx
function Form() {
  function handleSubmit(e) {
    e.preventDefault(); // 阻止默认提交行为
    console.log('Form submitted');
  }

  return (
    <form onSubmit={handleSubmit}>
      <button type="submit">Submit</button>
    </form>
  );
}
```

## 2.4 条件渲染

### if-else条件渲染

```jsx
function Greeting({ isLoggedIn, user }) {
  if (isLoggedIn) {
    return <h1>Welcome back, {user.name}!</h1>;
  }
  return <h1>Please sign up.</h1>;
}
```

### 逻辑与运算符 &&

```jsx
function Notification({ message }) {
  return (
    <div>
      {message && <p className="notification">{message}</p>}
    </div>
  );
}
```

### 条件运算符

```jsx
function UserStatus({ isActive }) {
  return (
    <span>
      User is {isActive ? 'active' : 'inactive'}
    </span>
  );
}
```

## 2.5 列表与键

### 渲染列表

```jsx
function TodoList({ todos }) {
  return (
    <ul>
      {todos.map(todo => (
        <li key={todo.id}>
          {todo.text}
        </li>
      ))}
    </ul>
  );
}
```

### 键的重要性

键帮助React识别哪些项已更改、添加或删除。

- 键应该是唯一的
- 理想情况下，使用稳定的、唯一的标识符
- 避免使用数组索引作为键（特别是当数组可能重新排序时）

```jsx
// 推荐
{todos.map(todo => (
  <li key={todo.id}>{todo.text}</li>
))}

// 避免（除非数据静态且不会重新排序）
{todos.map((todo, index) => (
  <li key={index}>{todo.text}</li>
))}
```

## 2.6 表单处理

### 受控组件

在React中，通常使用受控组件来处理表单，即表单元素的值由React状态控制。

```jsx
import { useState } from 'react';

function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  function handleSubmit(e) {
    e.preventDefault();
    console.log('Email:', email);
    console.log('Password:', password);
    // 这里可以添加登录逻辑
  }

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="email">Email:</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          required
        />
      </div>
      <div>
        <label htmlFor="password">Password:</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
        />
      </div>
      <button type="submit">Login</button>
    </form>
  );
}
```

### 表单状态优化

对于复杂表单，可以将所有表单状态合并到一个对象中。

```jsx
import { useState } from 'react';

function ContactForm() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: ''
  });

  function handleChange(e) {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    console.log('Form data:', formData);
    // 提交逻辑
  }

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="name">Name:</label>
        <input
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          required
        />
      </div>
      <div>
        <label htmlFor="email">Email:</label>
        <input
          id="email"
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          required
        />
      </div>
      <div>
        <label htmlFor="message">Message:</label>
        <textarea
          id="message"
          name="message"
          value={formData.message}
          onChange={handleChange}
          required
        />
      </div>
      <button type="submit">Submit</button>
    </form>
  );
}
```

## 2.7 副作用处理

### 使用useEffect处理副作用

副作用是指在渲染过程之外执行的操作，如数据获取、订阅、手动DOM操作等。

```jsx
import { useState, useEffect } from 'react';

function DataFetching({ url }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    async function fetchData() {
      setLoading(true);
      try {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch data');
        const result = await response.json();
        if (isMounted) {
          setData(result);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    fetchData();

    // 清理函数
    return () => {
      isMounted = false;
    };
  }, [url]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!data) return <div>No data</div>;

  return <div>Data: {JSON.stringify(data)}</div>;
}
```

### 依赖数组的重要性

useEffect的第二个参数是依赖数组，控制effect何时重新运行。

- 空数组`[]`：只在组件挂载时运行一次
- 包含变量的数组：当数组中的任何变量发生变化时运行
- 不提供第二个参数：每次渲染后都运行

## 2.8 自定义Hooks

### 什么是自定义Hook？

自定义Hook是一个函数，其名称以"use"开头，可以调用其他Hook。

### 创建自定义Hook

```jsx
import { useState, useEffect } from 'react';

// 自定义Hook用于数据获取
function useFetch(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    async function fetchData() {
      setLoading(true);
      try {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch data');
        const result = await response.json();
        if (isMounted) {
          setData(result);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    fetchData();

    return () => {
      isMounted = false;
    };
  }, [url]);

  return { data, loading, error };
}

// 使用自定义Hook
function DataDisplay({ url }) {
  const { data, loading, error } = useFetch(url);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!data) return <div>No data</div>;

  return <div>Data: {JSON.stringify(data)}</div>;
}
```

## 2.9 练习与实践

### 练习1：创建一个表单组件

创建一个完整的表单组件，包括：
- 用户名、邮箱、密码字段
- 表单验证
- 提交处理
- 错误显示

### 练习2：使用自定义Hook

创建一个自定义Hook用于管理表单状态和验证。

### 练习3：列表管理应用

创建一个任务管理应用，包括：
- 添加任务
- 标记任务完成
- 删除任务
- 过滤任务（全部、完成、未完成）

## 2.10 本章小结

本章我们深入学习了React的核心概念，包括：

- 状态管理（useState）
- 副作用处理（useEffect）
- 其他常用Hook（useContext, useReducer）
- 事件处理
- 条件渲染
- 列表与键
- 表单处理
- 自定义Hook的创建和使用

这些核心概念是React开发的基础，掌握好它们将使你能够构建更复杂、更健壮的React应用。在接下来的章节中，我们将学习React组件设计的最佳实践。

## 代码示例

本章的代码示例可以在[code目录](./code/)中找到。每个示例都包含完整的代码和运行说明。

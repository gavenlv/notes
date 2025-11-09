# React 进阶概念

本章将深入探讨React的高级概念，帮助你构建更复杂、更高效的React应用。这些进阶知识对于成为专业的React开发者至关重要。

## 目录

1. [React 性能优化](#react-性能优化)
2. [React 状态管理](#react-状态管理)
3. [React Router](#react-router)
4. [React 测试](#react-测试)
5. [React 与 TypeScript](#react-与-typescript)
6. [React 与 Redux](#react-与-redux)
7. [React 与 Context API](#react-与-context-api)
8. [React 与 Hooks 进阶](#react-与-hooks-进阶)
9. [React 与样式解决方案](#react-与样式解决方案)
10. [React 与服务端渲染](#react-与服务端渲染)

## React 性能优化

### React.memo

`React.memo` 是一个高阶组件，用于优化函数组件的渲染性能。它会记忆组件的渲染结果，并在下一次渲染时，如果组件的 props 没有变化，则直接返回记忆的结果，避免不必要的重新渲染。

```jsx
import React, { memo, useState } from 'react';

// 使用 memo 包装组件
const MemoizedComponent = memo(({ value }) => {
  console.log('渲染 MemoizedComponent');
  return <div>值: {value}</div>;
});

function App() {
  const [count, setCount] = useState(0);
  const [name, setName] = useState('React');

  return (
    <div>
      <button onClick={() => setCount(count + 1)}>增加计数</button>
      <button onClick={() => setName('React Advanced')}>修改名称</button>
      <div>计数: {count}</div>
      {/* 只有当 name 变化时，MemoizedComponent 才会重新渲染 */}
      <MemoizedComponent value={name} />
    </div>
  );
}
```

### useMemo 和 useCallback

`useMemo` 和 `useCallback` 是 React Hooks，用于优化渲染性能：

- `useMemo`: 用于缓存计算结果，避免在每次渲染时重复计算
- `useCallback`: 用于缓存函数引用，避免在每次渲染时创建新的函数实例

```jsx
import React, { useState, useMemo, useCallback } from 'react';

function App() {
  const [count, setCount] = useState(0);
  const [todos, setTodos] = useState([]);

  // 使用 useMemo 缓存计算结果
  const expensiveValue = useMemo(() => {
    console.log('计算 expensiveValue');
    // 模拟耗时计算
    let result = 0;
    for (let i = 0; i < 1000000; i++) {
      result += i;
    }
    return result + count;
  }, [count]); // 只有当 count 变化时，才会重新计算

  // 使用 useCallback 缓存函数引用
  const addTodo = useCallback(() => {
    setTodos(prevTodos => [...prevTodos, `Todo ${prevTodos.length + 1}`]);
  }, []); // 空依赖数组表示函数只创建一次

  return (
    <div>
      <button onClick={() => setCount(count + 1)}>增加计数</button>
      <button onClick={addTodo}>添加待办</button>
      <div>计数: {count}</div>
      <div>计算结果: {expensiveValue}</div>
      <div>待办数量: {todos.length}</div>
    </div>
  );
}
```

### 虚拟列表

对于大量数据的渲染，使用虚拟列表可以显著提高性能。虚拟列表只渲染可视区域内的项目，而不是所有数据。

```jsx
import React, { useState, useRef, useEffect, useMemo } from 'react';

function VirtualList({ items, itemHeight, containerHeight }) {
  const [scrollTop, setScrollTop] = useState(0);
  const containerRef = useRef(null);
  
  // 计算可见项目的索引范围
  const visibleRange = useMemo(() => {
    const startIndex = Math.floor(scrollTop / itemHeight);
    const visibleCount = Math.ceil(containerHeight / itemHeight);
    const endIndex = Math.min(startIndex + visibleCount + 1, items.length); // +1 为了有一些缓冲
    
    return { startIndex, endIndex };
  }, [scrollTop, itemHeight, containerHeight, items.length]);
  
  // 获取可见项目
  const visibleItems = useMemo(() => {
    return items.slice(visibleRange.startIndex, visibleRange.endIndex);
  }, [items, visibleRange.startIndex, visibleRange.endIndex]);
  
  // 计算偏移量
  const offsetY = visibleRange.startIndex * itemHeight;
  
  const handleScroll = () => {
    if (containerRef.current) {
      setScrollTop(containerRef.current.scrollTop);
    }
  };

  return (
    <div
      ref={containerRef}
      style={{ height: containerHeight, overflowY: 'auto' }}
      onScroll={handleScroll}
    >
      <div style={{ height: items.length * itemHeight, position: 'relative' }}>
        <div style={{ transform: `translateY(${offsetY}px)` }}>
          {visibleItems.map((item, index) => {
            const actualIndex = visibleRange.startIndex + index;
            return (
              <div
                key={actualIndex}
                style={{
                  height: itemHeight,
                  borderBottom: '1px solid #eee',
                  padding: '10px',
                  boxSizing: 'border-box'
                }}
              >
                {item}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// 使用示例
function App() {
  // 创建10000个项目
  const items = Array.from({ length: 10000 }, (_, i) => `项目 ${i + 1}`);
  
  return (
    <div>
      <h1>虚拟列表示例</h1>
      <VirtualList 
        items={items} 
        itemHeight={50} 
        containerHeight={400} 
      />
    </div>
  );
}
```

### 代码分割

代码分割允许我们将代码拆分成小块，然后在需要时动态加载。这可以减小初始加载的包大小，提高应用的加载速度。

```jsx
import React, { useState, Suspense, lazy } from 'react';

// 动态导入组件
const LazyComponent = lazy(() => import('./LazyComponent'));

function App() {
  const [showLazy, setShowLazy] = useState(false);

  return (
    <div>
      <h1>代码分割示例</h1>
      <button onClick={() => setShowLazy(true)}>加载懒加载组件</button>
      
      {showLazy && (
        <Suspense fallback={<div>加载中...</div>}>
          <LazyComponent />
        </Suspense>
      )}
    </div>
  );
}
```

## React 状态管理

### 使用 Context API 进行状态管理

React 的 Context API 提供了一种在组件树中共享数据的方式，无需通过 props 逐层传递。

```jsx
import React, { createContext, useContext, useState, useReducer } from 'react';

// 创建 Context
const AppContext = createContext();

// 创建 Provider 组件
export function AppProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isDarkMode, setIsDarkMode] = useState(false);
  
  const value = {
    user,
    setUser,
    isDarkMode,
    setIsDarkMode
  };
  
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

// 创建自定义 Hook 便于使用 Context
export function useAppContext() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
}

// 使用示例
function Navbar() {
  const { user, isDarkMode, setIsDarkMode } = useAppContext();
  
  return (
    <nav className={isDarkMode ? 'dark' : 'light'}>
      <span>{user ? `欢迎, ${user.name}` : '请登录'}</span>
      <button onClick={() => setIsDarkMode(!isDarkMode)}>
        {isDarkMode ? '切换到亮色模式' : '切换到暗色模式'}
      </button>
    </nav>
  );
}

function App() {
  return (
    <AppProvider>
      <Navbar />
      {/* 其他组件 */}
    </AppProvider>
  );
}
```

### 使用 useReducer 进行复杂状态管理

对于复杂的状态逻辑，`useReducer` Hook 是一个很好的选择。它类似于 Redux 的模式，但只在组件内部使用。

```jsx
import React, { useReducer } from 'react';

// 定义 reducer 函数
function todoReducer(state, action) {
  switch (action.type) {
    case 'ADD_TODO':
      return [...state, {
        id: Date.now(),
        text: action.payload,
        completed: false
      }];
    case 'TOGGLE_TODO':
      return state.map(todo => 
        todo.id === action.payload 
          ? { ...todo, completed: !todo.completed }
          : todo
      );
    case 'DELETE_TODO':
      return state.filter(todo => todo.id !== action.payload);
    default:
      return state;
  }
}

function TodoApp() {
  const [todos, dispatch] = useReducer(todoReducer, []);
  const [inputText, setInputText] = React.useState('');
  
  const handleAddTodo = () => {
    if (inputText.trim()) {
      dispatch({ type: 'ADD_TODO', payload: inputText });
      setInputText('');
    }
  };
  
  return (
    <div>
      <h1>待办事项</h1>
      <input
        type="text"
        value={inputText}
        onChange={(e) => setInputText(e.target.value)}
        placeholder="添加新待办..."
      />
      <button onClick={handleAddTodo}>添加</button>
      
      <ul>
        {todos.map(todo => (
          <li key={todo.id}>
            <span 
              style={{ 
                textDecoration: todo.completed ? 'line-through' : 'none' 
              }}
              onClick={() => dispatch({ type: 'TOGGLE_TODO', payload: todo.id })}
            >
              {todo.text}
            </span>
            <button 
              onClick={() => dispatch({ type: 'DELETE_TODO', payload: todo.id })}
            >
              删除
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

## React Router

React Router 是 React 应用中处理路由的标准库。它允许你根据 URL 显示不同的组件。

### 基本路由设置

```jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';

function Home() {
  return <h1>首页</h1>;
}

function About() {
  return <h1>关于我们</h1>;
}

function Contact() {
  return <h1>联系我们</h1>;
}

function App() {
  return (
    <Router>
      <nav>
        <ul>
          <li><Link to="/">首页</Link></li>
          <li><Link to="/about">关于我们</Link></li>
          <li><Link to="/contact">联系我们</Link></li>
        </ul>
      </nav>
      
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />
      </Routes>
    </Router>
  );
}
```

### 动态路由

动态路由允许我们在路由路径中使用参数。

```jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useParams } from 'react-router-dom';

// 产品列表
function Products() {
  const products = [
    { id: 1, name: '产品 1' },
    { id: 2, name: '产品 2' },
    { id: 3, name: '产品 3' }
  ];
  
  return (
    <div>
      <h1>产品列表</h1>
      <ul>
        {products.map(product => (
          <li key={product.id}>
            <Link to={`/products/${product.id}`}>{product.name}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

// 产品详情
function ProductDetail() {
  // 使用 useParams 获取路由参数
  const { id } = useParams();
  
  // 模拟从 API 获取产品数据
  const product = {
    id,
    name: `产品 ${id}`,
    description: `这是产品 ${id} 的详细描述`
  };
  
  return (
    <div>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      <Link to="/products">返回产品列表</Link>
    </div>
  );
}

function App() {
  return (
    <Router>
      <nav>
        <ul>
          <li><Link to="/">首页</Link></li>
          <li><Link to="/products">产品</Link></li>
        </ul>
      </nav>
      
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/products" element={<Products />} />
        <Route path="/products/:id" element={<ProductDetail />} />
      </Routes>
    </Router>
  );
}
```

### 嵌套路由

嵌套路由允许我们在一个路由中嵌套另一个路由。

```jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Outlet } from 'react-router-dom';

function Dashboard() {
  return (
    <div>
      <h1>仪表盘</h1>
      <nav>
        <ul>
          <li><Link to="/dashboard/profile">个人资料</Link></li>
          <li><Link to="/dashboard/settings">设置</Link></li>
        </ul>
      </nav>
      {/* Outlet 组件用于渲染匹配的子路由 */}
      <Outlet />
    </div>
  );
}

function Profile() {
  return <h2>个人资料</h2>;
}

function Settings() {
  return <h2>设置</h2>;
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />}>
          <Route path="profile" element={<Profile />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </Router>
  );
}
```

## React 测试

### 使用 Jest 和 React Testing Library 进行测试

Jest 是一个 JavaScript 测试框架，而 React Testing Library 是一个用于测试 React 组件的库。

#### 安装依赖

```bash
npm install --save-dev jest @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

#### 基本组件测试

```jsx
// Counter.jsx
import React, { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);
  
  return (
    <div>
      <p>计数: {count}</p>
      <button onClick={() => setCount(count + 1)}>增加</button>
      <button onClick={() => setCount(count - 1)}>减少</button>
    </div>
  );
}

export default Counter;

// Counter.test.jsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Counter from './Counter';

test('初始计数为 0', () => {
  render(<Counter />);
  // 检查初始计数是否为 0
  expect(screen.getByText('计数: 0')).toBeInTheDocument();
});

test('点击增加按钮计数增加', () => {
  render(<Counter />);
  // 点击增加按钮
  fireEvent.click(screen.getByText('增加'));
  // 检查计数是否变为 1
  expect(screen.getByText('计数: 1')).toBeInTheDocument();
});

test('点击减少按钮计数减少', () => {
  render(<Counter />);
  // 先点击增加按钮
  fireEvent.click(screen.getByText('增加'));
  // 然后点击减少按钮
  fireEvent.click(screen.getByText('减少'));
  // 检查计数是否变为 0
  expect(screen.getByText('计数: 0')).toBeInTheDocument();
});
```

#### 模拟 API 调用的测试

```jsx
// UserList.jsx
import React, { useEffect, useState } from 'react';

function UserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await fetch('https://jsonplaceholder.typicode.com/users');
        if (!response.ok) {
          throw new Error('Failed to fetch users');
        }
        const data = await response.json();
        setUsers(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchUsers();
  }, []);
  
  if (loading) {
    return <div>加载中...</div>;
  }
  
  if (error) {
    return <div>错误: {error}</div>;
  }
  
  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}

export default UserList;

// UserList.test.jsx
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import UserList from './UserList';

// 模拟 fetch 函数
global.fetch = jest.fn();

describe('UserList 组件', () => {
  afterEach(() => {
    jest.resetAllMocks();
  });
  
  test('加载状态显示加载中', async () => {
    // 模拟 fetch 延迟响应
    fetch.mockImplementation(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve([])
      })
    );
    
    // 使用 hydrate 而不是 render 来捕获初始加载状态
    const { unmount } = render(<UserList />);
    
    // 检查是否显示加载中
    expect(screen.getByText('加载中...')).toBeInTheDocument();
    
    unmount();
  });
  
  test('成功获取数据后显示用户列表', async () => {
    // 模拟成功响应
    const mockUsers = [
      { id: 1, name: 'John Doe' },
      { id: 2, name: 'Jane Doe' }
    ];
    
    fetch.mockImplementation(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockUsers)
      })
    );
    
    render(<UserList />);
    
    // 等待数据加载完成并检查用户列表
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Doe')).toBeInTheDocument();
    });
  });
  
  test('获取数据失败时显示错误信息', async () => {
    // 模拟失败响应
    fetch.mockImplementation(() => 
      Promise.reject(new Error('Failed to fetch users'))
    );
    
    render(<UserList />);
    
    // 等待错误信息显示
    await waitFor(() => {
      expect(screen.getByText(/错误/)).toBeInTheDocument();
    });
  });
});
```

## React 与 TypeScript

TypeScript 为 JavaScript 添加了静态类型，这可以帮助我们在开发过程中捕获错误。

### 组件类型定义

```tsx
import React, { useState, FC } from 'react';

// 定义组件的 Props 类型
interface GreetingProps {
  name: string;
  age?: number; // 可选属性
  onGreet: (message: string) => void;
}

// 使用 FC (FunctionComponent) 类型和泛型定义组件
const Greeting: FC<GreetingProps> = ({ name, age, onGreet }) => {
  const [greeting, setGreeting] = useState<string>('');
  
  const handleClick = () => {
    const message = age ? `Hello, ${name}! You are ${age} years old.` : `Hello, ${name}!`;
    setGreeting(message);
    onGreet(message);
  };
  
  return (
    <div>
      <button onClick={handleClick}>打招呼</button>
      {greeting && <p>{greeting}</p>}
    </div>
  );
};

export default Greeting;
```

### useState 和 useReducer 的类型定义

```tsx
import React, { useState, useReducer } from 'react';

// 定义待办事项的类型
interface Todo {
  id: number;
  text: string;
  completed: boolean;
}

// 定义 action 类型
type TodoAction =
  | { type: 'ADD_TODO'; payload: string }
  | { type: 'TOGGLE_TODO'; payload: number }
  | { type: 'DELETE_TODO'; payload: number };

function TodoApp() {
  // 为 useState 提供类型参数
  const [inputText, setInputText] = useState<string>('');
  
  // 为 useReducer 提供状态和 action 的类型
  const [todos, dispatch] = useReducer<TodoAction, Todo[]>(
    (state, action) => {
      switch (action.type) {
        case 'ADD_TODO':
          return [
            ...state,
            {
              id: Date.now(),
              text: action.payload,
              completed: false
            }
          ];
        case 'TOGGLE_TODO':
          return state.map(todo =>
            todo.id === action.payload
              ? { ...todo, completed: !todo.completed }
              : todo
          );
        case 'DELETE_TODO':
          return state.filter(todo => todo.id !== action.payload);
        default:
          return state;
      }
    },
    []
  );
  
  return (
    <div>
      <input
        type="text"
        value={inputText}
        onChange={(e) => setInputText(e.target.value)}
        placeholder="添加新待办..."
      />
      <button
        onClick={() => {
          if (inputText.trim()) {
            dispatch({ type: 'ADD_TODO', payload: inputText });
            setInputText('');
          }
        }}
      >
        添加
      </button>
      
      <ul>
        {todos.map(todo => (
          <li key={todo.id}>
            <span
              style={{
                textDecoration: todo.completed ? 'line-through' : 'none'
              }}
              onClick={() => dispatch({ type: 'TOGGLE_TODO', payload: todo.id })}
            >
              {todo.text}
            </span>
            <button
              onClick={() => dispatch({ type: 'DELETE_TODO', payload: todo.id })}
            >
              删除
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default TodoApp;
```

## React 与 Redux

Redux 是一个用于管理应用状态的库，它通常与 React 一起使用。

### Redux 基本设置

```jsx
// store.js
import { configureStore, createSlice } from '@reduxjs/toolkit';

// 创建待办事项的 slice
const todosSlice = createSlice({
  name: 'todos',
  initialState: [],
  reducers: {
    addTodo: (state, action) => {
      state.push({
        id: Date.now(),
        text: action.payload,
        completed: false
      });
    },
    toggleTodo: (state, action) => {
      const todo = state.find(todo => todo.id === action.payload);
      if (todo) {
        todo.completed = !todo.completed;
      }
    },
    deleteTodo: (state, action) => {
      return state.filter(todo => todo.id !== action.payload);
    }
  }
});

// 导出 actions
export const { addTodo, toggleTodo, deleteTodo } = todosSlice.actions;

// 配置 store
const store = configureStore({
  reducer: {
    todos: todosSlice.reducer
  }
});

export default store;

// App.jsx
import React, { useState } from 'react';
import { Provider, useSelector, useDispatch } from 'react-redux';
import store, { addTodo, toggleTodo, deleteTodo } from './store';

// 待办事项列表组件
function TodoList() {
  // 使用 useSelector 获取状态
  const todos = useSelector((state) => state.todos);
  const dispatch = useDispatch();
  
  return (
    <ul>
      {todos.map(todo => (
        <li key={todo.id}>
          <span
            style={{
              textDecoration: todo.completed ? 'line-through' : 'none'
            }}
            onClick={() => dispatch(toggleTodo(todo.id))}
          >
            {todo.text}
          </span>
          <button onClick={() => dispatch(deleteTodo(todo.id))}>删除</button>
        </li>
      ))}
    </ul>
  );
}

// 添加待办组件
function AddTodo() {
  const [text, setText] = useState('');
  const dispatch = useDispatch();
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (text.trim()) {
      dispatch(addTodo(text));
      setText('');
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="添加新待办..."
      />
      <button type="submit">添加</button>
    </form>
  );
}

// 主应用组件
function App() {
  return (
    <Provider store={store}>
      <h1>待办事项</h1>
      <AddTodo />
      <TodoList />
    </Provider>
  );
}

export default App;
```

## React 与 Context API

Context API 是 React 内置的状态管理解决方案，它提供了一种在组件树中共享数据的方式。

### 高级 Context 使用

```jsx
import React, { createContext, useContext, useReducer, useEffect } from 'react';

// 定义状态类型
interface State {
  user: {
    id: string;
    name: string;
    email: string;
  } | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// 定义 action 类型
type Action =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: State['user'] }
  | { type: 'LOGIN_FAILURE'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'UPDATE_USER'; payload: Partial<State['user']> };

// 创建 Context
const AuthContext = createContext<{
  state: State;
  dispatch: React.Dispatch<Action>;
} | null>(null);

// 初始状态
const initialState: State = {
  user: null,
  isAuthenticated: false,
  isLoading: true
};

// Reducer 函数
function authReducer(state: State, action: Action): State {
  switch (action.type) {
    case 'LOGIN_START':
      return { ...state, isLoading: true };
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        isAuthenticated: true,
        user: action.payload,
        isLoading: false
      };
    case 'LOGIN_FAILURE':
      return {
        ...state,
        isAuthenticated: false,
        user: null,
        isLoading: false
      };
    case 'LOGOUT':
      return {
        ...state,
        isAuthenticated: false,
        user: null
      };
    case 'UPDATE_USER':
      return {
        ...state,
        user: state.user ? { ...state.user, ...action.payload } : null
      };
    default:
      return state;
  }
}

// 创建 Provider 组件
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, initialState);
  
  // 模拟从 localStorage 加载用户数据
  useEffect(() => {
    const loadUser = () => {
      try {
        const userData = localStorage.getItem('user');
        if (userData) {
          dispatch({ type: 'LOGIN_SUCCESS', payload: JSON.parse(userData) });
        } else {
          dispatch({ type: 'LOGIN_FAILURE', payload: 'No user data' });
        }
      } catch (error) {
        dispatch({ type: 'LOGIN_FAILURE', payload: 'Failed to load user' });
      }
    };
    
    loadUser();
  }, []);
  
  // 当用户状态变化时，保存到 localStorage
  useEffect(() => {
    if (state.user) {
      localStorage.setItem('user', JSON.stringify(state.user));
    } else {
      localStorage.removeItem('user');
    }
  }, [state.user]);
  
  // 提供认证相关的方法
  const authMethods = {
    login: async (email: string, password: string) => {
      dispatch({ type: 'LOGIN_START' });
      try {
        // 模拟 API 调用
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // 模拟成功登录
        const user = {
          id: '1',
          name: 'John Doe',
          email
        };
        
        dispatch({ type: 'LOGIN_SUCCESS', payload: user });
        return { success: true };
      } catch (error) {
        dispatch({ type: 'LOGIN_FAILURE', payload: 'Invalid credentials' });
        return { success: false, error: 'Invalid credentials' };
      }
    },
    logout: () => {
      dispatch({ type: 'LOGOUT' });
    },
    updateUser: (userData: Partial<State['user']>) => {
      dispatch({ type: 'UPDATE_USER', payload: userData });
    }
  };
  
  const value = {
    state,
    dispatch,
    ...authMethods
  };
  
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// 创建自定义 Hook
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// 示例使用
function LoginPage() {
  const { login, state } = useAuth();
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [error, setError] = React.useState('');
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    const result = await login(email, password);
    if (!result.success) {
      setError(result.error || '登录失败');
    }
  };
  
  if (state.isLoading) {
    return <div>加载中...</div>;
  }
  
  return (
    <form onSubmit={handleSubmit}>
      <h2>登录</h2>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      <div>
        <label>邮箱</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>
      <div>
        <label>密码</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>
      <button type="submit" disabled={state.isLoading}>
        {state.isLoading ? '登录中...' : '登录'}
      </button>
    </form>
  );
}

function ProfilePage() {
  const { state, updateUser, logout } = useAuth();
  const [name, setName] = React.useState(state.user?.name || '');
  
  const handleUpdate = () => {
    updateUser({ name });
  };
  
  if (!state.isAuthenticated) {
    return <div>请先登录</div>;
  }
  
  return (
    <div>
      <h2>个人资料</h2>
      <div>
        <label>姓名</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </div>
      <div>
        <label>邮箱</label>
        <input type="email" value={state.user?.email || ''} disabled />
      </div>
      <button onClick={handleUpdate}>更新</button>
      <button onClick={logout}>退出登录</button>
    </div>
  );
}
```

## React 与 Hooks 进阶

### 自定义 Hook 的高级使用

#### useLocalStorage Hook

```jsx
import { useState, useEffect } from 'react';

function useLocalStorage<T>(key: string, initialValue: T): [T, (value: T | ((val: T) => T)) => void, boolean] {
  const [storedValue, setStoredValue] = useState<T>(initialValue);
  const [loading, setLoading] = useState(true);
  
  // 从 localStorage 加载数据
  useEffect(() => {
    try {
      const item = window.localStorage.getItem(key);
      if (item) {
        setStoredValue(JSON.parse(item));
      }
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
    } finally {
      setLoading(false);
    }
  }, [key]);
  
  // 更新 localStorage 和状态
  const setValue = (value: T | ((val: T) => T)) => {
    try {
      // 允许 value 是一个函数
      const valueToStore =
        value instanceof Function ? value(storedValue) : value;
      
      // 保存到状态
      setStoredValue(valueToStore);
      
      // 保存到 localStorage
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  };
  
  return [storedValue, setValue, loading];
}

// 使用示例
function TodoApp() {
  const [todos, setTodos, loading] = useLocalStorage('todos', []);
  const [inputText, setInputText] = useState('');
  
  const addTodo = () => {
    if (inputText.trim()) {
      setTodos([...todos, {
        id: Date.now(),
        text: inputText,
        completed: false
      }]);
      setInputText('');
    }
  };
  
  const toggleTodo = (id: number) => {
    setTodos(todos.map(todo => 
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ));
  };
  
  if (loading) {
    return <div>加载中...</div>;
  }
  
  return (
    <div>
      <input
        type="text"
        value={inputText}
        onChange={(e) => setInputText(e.target.value)}
        placeholder="添加新待办..."
      />
      <button onClick={addTodo}>添加</button>
      <ul>
        {todos.map(todo => (
          <li key={todo.id}>
            <span
              style={{
                textDecoration: todo.completed ? 'line-through' : 'none'
              }}
              onClick={() => toggleTodo(todo.id)}
            >
              {todo.text}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

#### useDebounce Hook

```jsx
import { useState, useEffect } from 'react';

function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);
  
  useEffect(() => {
    // 设置一个定时器
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);
    
    // 清除定时器
    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]); // 只有当 value 或 delay 变化时才重新执行
  
  return debouncedValue;
}

// 使用示例
function Search() {
  const [searchTerm, setSearchTerm] = useState('');
  // 搜索词在停止输入 500ms 后才会更新
  const debouncedSearchTerm = useDebounce(searchTerm, 500);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    const fetchResults = async () => {
      if (!debouncedSearchTerm.trim()) {
        setResults([]);
        return;
      }
      
      setLoading(true);
      try {
        // 模拟 API 调用
        const response = await fetch(
          `https://jsonplaceholder.typicode.com/posts?q=${debouncedSearchTerm}`
        );
        const data = await response.json();
        setResults(data);
      } catch (error) {
        console.error('Error fetching search results:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchResults();
  }, [debouncedSearchTerm]); // 只依赖 debouncedSearchTerm
  
  return (
    <div>
      <input
        type="text"
        placeholder="搜索..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />
      {loading && <p>搜索中...</p>}
      <ul>
        {results.map((result) => (
          <li key={result.id}>{result.title}</li>
        ))}
      </ul>
    </div>
  );
}
```

#### useThrottle Hook

```jsx
import { useRef, useEffect } from 'react';

function useThrottle<T>(callback: (value: T) => void, delay: number): (value: T) => void {
  const lastRan = useRef<number>(0);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  return (value: T) => {
    const now = Date.now();
    const timeSinceLastRun = now - lastRan.current;
    
    // 清除之前的定时器
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    
    // 如果距离上次运行的时间大于延迟，则立即执行
    if (timeSinceLastRun >= delay) {
      lastRan.current = now;
      callback(value);
    } else {
      // 否则，设置定时器，在剩余时间后执行
      timeoutRef.current = setTimeout(() => {
        lastRan.current = Date.now();
        callback(value);
      }, delay - timeSinceLastRun);
    }
  };
}

// 使用示例
function ScrollTracker() {
  const [scrollPosition, setScrollPosition] = React.useState(0);
  
  // 创建一个节流函数，每 200ms 最多执行一次
  const throttledScroll = useThrottle((position: number) => {
    setScrollPosition(position);
  }, 200);
  
  React.useEffect(() => {
    const handleScroll = () => {
      throttledScroll(window.scrollY);
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [throttledScroll]);
  
  return (
    <div>
      <div style={{ position: 'fixed', top: 0, right: 0, background: 'white', padding: '10px' }}>
        滚动位置: {scrollPosition}px
      </div>
      {/* 长内容，用于测试滚动 */}
      <div style={{ height: '200vh', padding: '20px' }}>
        <h1>滚动测试</h1>
        <p>向下滚动页面查看滚动位置</p>
      </div>
    </div>
  );
}
```

## React 与样式解决方案

### CSS Modules

CSS Modules 允许我们为组件编写局部作用域的 CSS。

```jsx
// Button.module.css
.button {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.2s;
}

.primary {
  background-color: #4299e1;
  color: white;
}

.primary:hover {
  background-color: #3182ce;
}

.secondary {
  background-color: #e2e8f0;
  color: #2d3748;
}

.secondary:hover {
  background-color: #cbd5e0;
}

// Button.jsx
import React from 'react';
import styles from './Button.module.css';

interface ButtonProps {
  variant?: 'primary' | 'secondary';
  children: React.ReactNode;
  onClick?: () => void;
}

function Button({ variant = 'primary', children, onClick }: ButtonProps) {
  return (
    <button
      className={`${styles.button} ${styles[variant]}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
}

export default Button;
```

### styled-components

styled-components 是一个流行的 CSS-in-JS 库，它允许我们使用 JavaScript 编写 CSS。

```jsx
import React from 'react';
import styled, { css } from 'styled-components';

// 定义一个基础按钮组件
const ButtonBase = styled.button`
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  &:active {
    transform: translateY(0);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

// 定义主要按钮变体
const PrimaryButton = styled(ButtonBase)`
  background-color: #4299e1;
  color: white;
  
  &:hover:not(:disabled) {
    background-color: #3182ce;
  }
`;

// 定义次要按钮变体
const SecondaryButton = styled(ButtonBase)`
  background-color: #e2e8f0;
  color: #2d3748;
  
  &:hover:not(:disabled) {
    background-color: #cbd5e0;
  }
`;

// 定义危险按钮变体
const DangerButton = styled(ButtonBase)`
  background-color: #e53e3e;
  color: white;
  
  &:hover:not(:disabled) {
    background-color: #c53030;
  }
`;

// 定义按钮大小变体
const ButtonSize = css`
  ${props => props.size === 'small' && css`
    padding: 6px 12px;
    font-size: 14px;
  `}
  
  ${props => props.size === 'large' && css`
    padding: 12px 24px;
    font-size: 18px;
  `}
`;

// 最终的 Button 组件
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
}

function Button({ variant = 'primary', size = 'medium', disabled = false, children, onClick }: ButtonProps) {
  // 根据变体选择对应的按钮组件
  let ButtonComponent;
  switch (variant) {
    case 'secondary':
      ButtonComponent = SecondaryButton;
      break;
    case 'danger':
      ButtonComponent = DangerButton;
      break;
    default:
      ButtonComponent = PrimaryButton;
  }
  
  return (
    <ButtonComponent 
      size={size}
      disabled={disabled}
      onClick={onClick}
      css={ButtonSize}
    >
      {children}
    </ButtonComponent>
  );
}

export default Button;
```

### Tailwind CSS

Tailwind CSS 是一个实用优先的 CSS 框架，它提供了大量的工具类。

```jsx
import React from 'react';

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'success' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  fullWidth?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
}

function Button({
  variant = 'primary',
  size = 'md',
  disabled = false,
  fullWidth = false,
  children,
  onClick
}: ButtonProps) {
  // 变体样式
  const variantStyles = {
    primary: 'bg-blue-500 text-white hover:bg-blue-600',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300',
    success: 'bg-green-500 text-white hover:bg-green-600',
    danger: 'bg-red-500 text-white hover:bg-red-600'
  };
  
  // 大小样式
  const sizeStyles = {
    sm: 'px-3 py-1 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg'
  };
  
  // 通用样式
  const baseStyles = 'font-medium rounded-md transition duration-200 focus:outline-none focus:ring-2 focus:ring-opacity-50';
  
  // 禁用样式
  const disabledStyles = disabled ? 'opacity-50 cursor-not-allowed' : '';
  
  // 全宽样式
  const fullWidthStyles = fullWidth ? 'w-full' : '';
  
  // 组合所有样式
  const className = `${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${disabledStyles} ${fullWidthStyles}`;
  
  return (
    <button
      className={className}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
}

export default Button;
```

## React 与服务端渲染

服务端渲染 (SSR) 允许我们在服务器上渲染 React 组件，然后将 HTML 发送到客户端。这可以提高性能和 SEO。

### 使用 Next.js 进行服务端渲染

Next.js 是一个流行的 React 框架，它内置了服务端渲染功能。

#### 基本页面组件

```jsx
// pages/index.js
import React from 'react';

export default function Home() {
  return (
    <div>
      <h1>Next.js 首页</h1>
      <p>这是一个使用 Next.js 的服务端渲染页面</p>
    </div>
  );
}
```

#### 数据获取

Next.js 提供了几种数据获取方法：

1. `getStaticProps`: 在构建时获取数据，用于静态生成
2. `getStaticPaths`: 与 `getStaticProps` 一起使用，用于动态路由的静态生成
3. `getServerSideProps`: 在每个请求时在服务器上获取数据

```jsx
// pages/products.js
import React from 'react';

export default function Products({ products }) {
  return (
    <div>
      <h1>产品列表</h1>
      <ul>
        {products.map(product => (
          <li key={product.id}>
            <h2>{product.name}</h2>
            <p>{product.description}</p>
            <p>${product.price}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}

// 在构建时获取数据
export async function getStaticProps() {
  // 模拟 API 调用
  const res = await fetch('https://api.example.com/products');
  const products = await res.json();
  
  return {
    props: {
      products
    },
    // 重新验证时间（秒）
    revalidate: 60
  };
}

// pages/products/[id].js
import React from 'react';

export default function ProductDetail({ product }) {
  if (!product) {
    return <div>产品不存在</div>;
  }
  
  return (
    <div>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      <p>${product.price}</p>
    </div>
  );
}

// 为动态路由生成静态路径
export async function getStaticPaths() {
  // 模拟 API 调用获取所有产品 ID
  const res = await fetch('https://api.example.com/products');
  const products = await res.json();
  
  // 生成路径数组
  const paths = products.map(product => ({
    params: { id: product.id.toString() }
  }));
  
  return {
    paths,
    // 对于未预生成的路径，返回 404 页面
    fallback: false
  };
}

// 为每个产品获取数据
export async function getStaticProps({ params }) {
  const res = await fetch(`https://api.example.com/products/${params.id}`);
  const product = await res.json();
  
  return {
    props: {
      product
    }
  };
}
```

#### 服务器端渲染

```jsx
// pages/user/[id].js
import React from 'react';

export default function UserProfile({ user }) {
  return (
    <div>
      <h1>{user.name}</h1>
      <p>Email: {user.email}</p>
      <p>Last updated: {user.updatedAt}</p>
    </div>
  );
}

// 在每个请求时在服务器上获取数据
export async function getServerSideProps({ params }) {
  try {
    const res = await fetch(`https://api.example.com/users/${params.id}`);
    const user = await res.json();
    
    return {
      props: {
        user
      }
    };
  } catch (error) {
    return {
      notFound: true
    };
  }
}
```

## 最佳实践与性能优化总结

### 组件设计最佳实践

1. **组件拆分**：将大型组件拆分为小型、可重用的组件
2. **单一职责**：每个组件应该只有一个职责
3. **状态提升**：将共享状态提升到最近的公共祖先组件
4. **受控组件**：优先使用受控组件处理表单
5. **避免内联函数**：对于频繁渲染的组件，避免在渲染函数中创建新的函数

### 性能优化策略

1. **使用 React.memo**：对于纯展示组件，使用 React.memo 避免不必要的重新渲染
2. **使用 useMemo 和 useCallback**：缓存计算结果和函数引用
3. **虚拟列表**：对于大量数据的列表，使用虚拟列表
4. **代码分割**：使用动态导入分割代码
5. **避免不必要的重新渲染**：
   - 避免在渲染过程中创建新对象和数组
   - 合理设置依赖项数组
   - 使用 shouldComponentUpdate (类组件) 或 React.memo (函数组件)

### 安全最佳实践

1. **XSS 防护**：避免直接将用户输入插入到 HTML 中，使用 dangerouslySetInnerHTML 时要格外小心
2. **CSRF 防护**：实现适当的 CSRF 保护
3. **输入验证**：在客户端和服务器端都进行输入验证
4. **避免暴露敏感信息**：不要在客户端存储敏感信息
5. **使用 HTTPS**：确保所有通信都通过 HTTPS 进行

### 测试最佳实践

1. **单元测试**：测试组件的各个部分
2. **集成测试**：测试组件之间的交互
3. **端到端测试**：测试整个应用的流程
4. **测试覆盖率**：尽量提高测试覆盖率，但不要为了覆盖率而牺牲测试质量
5. **模拟外部依赖**：在测试中模拟 API 调用和其他外部依赖

通过掌握这些进阶概念，你将能够构建更高效、更可维护的 React 应用。继续学习和实践，你将成为一名专业的 React 开发者！
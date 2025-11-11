# 第二章：React核心概念

## 🎯 本章学习目标

通过本章学习，你将能够：
- ✅ 理解React状态管理的核心概念
- ✅ 掌握useState和useEffect Hook的使用
- ✅ 熟练处理React事件和表单
- ✅ 实现条件渲染和列表渲染
- ✅ 创建和使用自定义Hook
- ✅ 理解React Hooks的工作原理

## 🚀 2.1 React状态管理（State）

### 🆕 什么是状态？

状态（State）是React组件中用于存储和管理组件内部数据的对象。当状态发生变化时，组件会重新渲染以反映最新的数据。

**新手理解**：状态就像组件的"记忆"，决定了组件当前是什么样子。

**高手进阶**：状态是React组件可变的私有数据，是UI的"单一数据源"。

### 💡 状态与Props的区别

| 特性 | 状态（State） | Props |
|------|---------------|-------|
| **可变性** | 可变的 | 只读的 |
| **来源** | 组件内部 | 父组件传递 |
| **作用范围** | 当前组件 | 跨组件传递 |
| **更新方式** | setState函数 | 父组件重新渲染 |

### 🔑 使用useState Hook

`useState`是React中最基础的Hook，用于在函数组件中添加状态。

```jsx
import { useState } from 'react';

function Counter() {
  // useState返回一个数组：当前状态和更新函数
  const [count, setCount] = useState(0);
  
  // 状态更新函数
  const increment = () => setCount(count + 1);
  const decrement = () => setCount(count - 1);
  const reset = () => setCount(0);

  return (
    <div>
      <h2>计数器：{count}</h2>
      <button onClick={increment}>+1</button>
      <button onClick={decrement}>-1</button>
      <button onClick={reset}>重置</button>
    </div>
  );
}
```

### 🔍 useState的工作原理

```jsx
// useState的底层实现原理（简化版）
let state; // 存储状态的变量

function useState(initialValue) {
  // 如果状态未初始化，使用初始值
  if (state === undefined) {
    state = initialValue;
  }
  
  // 返回状态和更新函数
  return [
    state, 
    (newValue) => {
      state = newValue;
      // 触发重新渲染
      renderComponent();
    }
  ];
}

// React实际实现更复杂，使用链表存储多个状态
```

**重要特性**：
- 状态更新是**异步的**，不要依赖立即获取更新后的状态
- 多次setState调用会被**批量处理**
- 状态更新会触发**组件重新渲染**

### 🎯 状态更新的最佳实践

```jsx
// ❌ 避免的写法（依赖当前状态）
setCount(count + 1);
setCount(count + 1); // 这两行只会执行一次

// ✅ 推荐的写法（使用函数式更新）
setCount(prevCount => prevCount + 1);
setCount(prevCount => prevCount + 1); // 这两行都会执行

// 🔥 对象状态更新的最佳实践
const [user, setUser] = useState({ name: '', age: 0 });

// 错误：直接修改对象
user.name = '新名字'; // ❌ 不要这样做！

// 正确：创建新对象
setUser(prevUser => ({
  ...prevUser,        // 展开旧状态
  name: '新名字',      // 覆盖需要更新的属性
  updatedAt: Date.now() // 添加新属性
}));

// 🎯 数组状态更新的最佳实践
const [items, setItems] = useState([]);

// 添加元素
setItems(prevItems => [...prevItems, newItem]);

// 删除元素
setItems(prevItems => prevItems.filter(item => item.id !== idToRemove));

// 更新元素
setItems(prevItems => prevItems.map(item => 
  item.id === idToUpdate ? { ...item, ...updates } : item
));
```

### ⚠️ 常见的状态管理错误

```jsx
// 1. 直接修改状态
const [user, setUser] = useState({ name: '张三' });
user.name = '李四'; // ❌ 错误！

// 2. 忘记使用函数式更新
const [count, setCount] = useState(0);
const increment = () => {
  setCount(count + 1);
  setCount(count + 1); // ❌ 两个setCount使用相同的count值
};

// 3. 在渲染过程中计算状态
const [data, setData] = useState([]);
const filteredData = data.filter(item => item.active); // ✅ 可以
const expensiveValue = expensiveCalculation(data); // ❌ 避免在渲染中计算
```

## 🎣 2.2 React Hooks详解

### 🆕 什么是Hooks？

Hooks是React 16.8引入的新特性，允许你在不编写class的情况下使用state以及其他React特性。

**Hooks的设计哲学**：
- **逻辑复用**：避免高阶组件和render props的嵌套地狱
- **代码组织**：按功能组织代码，而不是生命周期
- **学习曲线**：比class组件更容易理解

### 🔑 useEffect Hook详解

`useEffect`用于处理副作用，如数据获取、订阅、手动DOM操作等。

```jsx
import { useState, useEffect } from 'react';

function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // useEffect的基本结构
  useEffect(() => {
    // 副作用逻辑
    console.log('Effect执行了');
    
    // 异步数据获取
    const fetchUser = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/users/${userId}`);
        
        if (!response.ok) {
          throw new Error('用户不存在');
        }
        
        const userData = await response.json();
        setUser(userData);
        setError(null);
      } catch (err) {
        setError(err.message);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();

    // 清理函数（可选）
    return () => {
      console.log('清理函数执行了');
      // 取消请求、清除定时器等
    };
  }, [userId]); // 依赖数组

  if (loading) return <div>加载中...</div>;
  if (error) return <div>错误：{error}</div>;
  if (!user) return <div>用户不存在</div>;

  return (
    <div>
      <h2>{user.name}</h2>
      <p>邮箱：{user.email}</p>
      <p>年龄：{user.age}</p>
    </div>
  );
}
```

### 🔍 useEffect依赖数组详解

依赖数组控制effect何时重新执行：

```jsx
// 1. 无依赖数组：每次渲染后都执行
useEffect(() => {
  console.log('每次渲染后执行');
});

// 2. 空依赖数组：只在组件挂载时执行一次
useEffect(() => {
  console.log('只在挂载时执行一次');
  
  return () => {
    console.log('卸载时清理');
  };
}, []);

// 3. 有依赖数组：依赖变化时执行
useEffect(() => {
  console.log('userId变化时执行');
}, [userId]);

// 4. 多个依赖：任何一个依赖变化时执行
useEffect(() => {
  console.log('userId或page变化时执行');
}, [userId, page]);
```

**依赖数组的最佳实践**：
- 包含所有在effect中使用的props和state
- 使用ESLint规则`exhaustive-deps`自动检查
- 避免不必要的依赖（使用useCallback和useMemo优化）

### 🎯 useContext Hook

`useContext`用于访问React上下文，避免props层层传递。

```jsx
import { createContext, useContext, useState } from 'react';

// 1. 创建上下文
const ThemeContext = createContext();

// 2. 提供上下文值
function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');
  
  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

// 3. 在组件中使用上下文
function ThemedButton() {
  const { theme, toggleTheme } = useContext(ThemeContext);
  
  return (
    <button 
      onClick={toggleTheme}
      style={{
        backgroundColor: theme === 'light' ? '#fff' : '#333',
        color: theme === 'light' ? '#333' : '#fff',
        padding: '10px 20px',
        border: '1px solid #ccc'
      }}
    >
      切换主题（当前：{theme}）
    </button>
  );
}

// 4. 在应用中使用
function App() {
  return (
    <ThemeProvider>
      <div>
        <h1>我的应用</h1>
        <ThemedButton />
      </div>
    </ThemeProvider>
  );
}
```

### 🎯 useReducer Hook

`useReducer`适用于复杂的状态逻辑，类似于Redux的模式。

```jsx
import { useReducer } from 'react';

// 1. 定义action类型
const ACTION_TYPES = {
  ADD_TODO: 'ADD_TODO',
  TOGGLE_TODO: 'TOGGLE_TODO',
  DELETE_TODO: 'DELETE_TODO',
  SET_FILTER: 'SET_FILTER'
};

// 2. 定义reducer函数
function todoReducer(state, action) {
  switch (action.type) {
    case ACTION_TYPES.ADD_TODO:
      return {
        ...state,
        todos: [
          ...state.todos,
          {
            id: Date.now(),
            text: action.payload.text,
            completed: false
          }
        ]
      };
      
    case ACTION_TYPES.TOGGLE_TODO:
      return {
        ...state,
        todos: state.todos.map(todo =>
          todo.id === action.payload.id
            ? { ...todo, completed: !todo.completed }
            : todo
        )
      };
      
    case ACTION_TYPES.DELETE_TODO:
      return {
        ...state,
        todos: state.todos.filter(todo => todo.id !== action.payload.id)
      };
      
    case ACTION_TYPES.SET_FILTER:
      return {
        ...state,
        filter: action.payload.filter
      };
      
    default:
      throw new Error(`未知的action类型: ${action.type}`);
  }
}

// 3. 初始状态
const initialState = {
  todos: [],
  filter: 'all' // all, active, completed
};

// 4. 使用useReducer
function TodoApp() {
  const [state, dispatch] = useReducer(todoReducer, initialState);
  
  const addTodo = (text) => {
    dispatch({
      type: ACTION_TYPES.ADD_TODO,
      payload: { text }
    });
  };
  
  const toggleTodo = (id) => {
    dispatch({
      type: ACTION_TYPES.TOGGLE_TODO,
      payload: { id }
    });
  };
  
  const deleteTodo = (id) => {
    dispatch({
      type: ACTION_TYPES.DELETE_TODO,
      payload: { id }
    });
  };
  
  // 过滤todos
  const filteredTodos = state.todos.filter(todo => {
    if (state.filter === 'active') return !todo.completed;
    if (state.filter === 'completed') return todo.completed;
    return true; // all
  });

  return (
    <div>
      <h1>待办事项</h1>
      
      {/* 添加待办表单 */}
      <TodoForm onAdd={addTodo} />
      
      {/* 过滤选项 */}
      <FilterButtons 
        filter={state.filter}
        onFilterChange={(filter) => dispatch({
          type: ACTION_TYPES.SET_FILTER,
          payload: { filter }
        })}
      />
      
      {/* 待办列表 */}
      <TodoList 
        todos={filteredTodos}
        onToggle={toggleTodo}
        onDelete={deleteTodo}
      />
    </div>
  );
}
```

## 🎯 2.3 事件处理

### 🆕 React事件系统

React的事件处理与原生DOM事件类似，但有一些重要区别：

- React事件使用**驼峰命名**（onClick vs onclick）
- React事件是**合成事件**（SyntheticEvent），跨浏览器兼容
- 事件处理函数会自动**绑定this**（函数组件不需要）

### 💡 事件处理的基本语法

```jsx
function Button() {
  // 事件处理函数
  const handleClick = (event) => {
    event.preventDefault(); // 阻止默认行为
    event.stopPropagation(); // 阻止事件冒泡
    
    console.log('按钮被点击了', event);
    console.log('事件类型:', event.type);
    console.log('目标元素:', event.target);
  };

  return (
    <button onClick={handleClick}>
      点击我
    </button>
  );
}
```

### 🔥 事件处理最佳实践

```jsx
// 1. 使用箭头函数或bind避免this问题（类组件）
class Button extends React.Component {
  handleClick = () => {
    console.log('this指向组件实例');
  };
  
  render() {
    return <button onClick={this.handleClick}>点击</button>;
  }
}

// 2. 传递参数给事件处理函数
function TodoList({ todos, onDelete }) {
  return (
    <ul>
      {todos.map(todo => (
        <li key={todo.id}>
          {todo.text}
          {/* 方法1：箭头函数 */}
          <button onClick={() => onDelete(todo.id)}>
            删除
          </button>
          
          {/* 方法2：bind（性能更好） */}
          <button onClick={onDelete.bind(null, todo.id)}>
            删除
          </button>
          
          {/* 方法3：自定义属性 */}
          <button data-id={todo.id} onClick={handleDelete}>
            删除
          </button>
        </li>
      ))}
    </ul>
  );
  
  function handleDelete(event) {
    const id = event.target.dataset.id;
    onDelete(id);
  }
}

// 3. 事件委托（性能优化）
function List({ items, onItemClick }) {
  const handleListClick = (event) => {
    // 检查点击的是否是列表项
    if (event.target.tagName === 'LI') {
      const id = event.target.dataset.id;
      onItemClick(id);
    }
  };

  return (
    <ul onClick={handleListClick}>
      {items.map(item => (
        <li key={item.id} data-id={item.id}>
          {item.text}
        </li>
      ))}
    </ul>
  );
}
```

### 🎯 常见事件类型

```jsx
function EventExamples() {
  const [inputValue, setInputValue] = useState('');
  const [formData, setFormData] = useState({});

  return (
    <div>
      {/* 鼠标事件 */}
      <div 
        onMouseEnter={() => console.log('鼠标进入')}
        onMouseLeave={() => console.log('鼠标离开')}
        onMouseMove={(e) => console.log('鼠标移动', e.clientX, e.clientY)}
      >
        鼠标事件区域
      </div>

      {/* 键盘事件 */}
      <input 
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            console.log('按下了回车键');
          }
          if (e.ctrlKey && e.key === 's') {
            e.preventDefault(); // 阻止浏览器保存
            console.log('Ctrl+S被按下');
          }
        }}
        onKeyUp={() => console.log('按键释放')}
      />

      {/* 表单事件 */}
      <form 
        onSubmit={(e) => {
          e.preventDefault(); // 阻止表单提交
          console.log('表单提交', formData);
        }}
        onReset={() => setFormData({})}
      >
        <input 
          name="username"
          onChange={(e) => setFormData(prev => ({
            ...prev,
            username: e.target.value
          }))}
        />
        <button type="submit">提交</button>
        <button type="reset">重置</button>
      </form>

      {/* 焦点事件 */}
      <input 
        onFocus={() => console.log('获得焦点')}
        onBlur={() => console.log('失去焦点')}
      />

      {/* 剪贴板事件 */}
      <input 
        onCopy={() => console.log('内容被复制')}
        onPaste={(e) => {
          const pastedText = e.clipboardData.getData('text');
          console.log('粘贴的内容:', pastedText);
        }}
      />
    </div>
  );
}
```

## 🎯 2.4 条件渲染

### 🆕 条件渲染的概念

条件渲染是根据特定条件决定显示哪些内容的技术。

**新手理解**：就像if-else语句，但用于UI显示。

**高手进阶**：条件渲染是声明式UI的核心特性，体现了React的响应式特性。

### 💡 条件渲染的多种方式

```jsx
function UserGreeting({ user, isLoading, hasError }) {
  // 1. if-else语句（最直接）
  if (isLoading) {
    return <div>加载中...</div>;
  }
  
  if (hasError) {
    return <div>发生错误</div>;
  }
  
  if (!user) {
    return <div>请先登录</div>;
  }
  
  return <div>欢迎回来，{user.name}！</div>;
}

// 2. 条件运算符（三目运算符）
function WelcomeMessage({ isLoggedIn, userName }) {
  return (
    <div>
      {isLoggedIn ? (
        <h1>欢迎回来，{userName}！</h1>
      ) : (
        <h1>请先登录</h1>
      )}
    </div>
  );
}

// 3. 逻辑与运算符（&&）
function Notification({ message, show }) {
  return (
    <div>
      {/* 当show为true时显示通知 */}
      {show && (
        <div className="notification">
          {message}
        </div>
      )}
      
      {/* 注意：message为0时也会显示，因为0是falsy但React会渲染 */}
      {message && <div>消息：{message}</div>}
    </div>
  );
}

// 4. 立即执行函数（IIFE）
function ComplexConditional({ user, permissions }) {
  return (
    <div>
      {(() => {
        if (!user) return <div>未登录</div>;
        if (!permissions.includes('read')) return <div>无权限</div>;
        
        return (
          <div>
            <h1>欢迎，{user.name}</h1>
            <p>你有阅读权限</p>
          </div>
        );
      })()}
    </div>
  );
}

// 5. 组件提取（推荐）
function UserDashboard({ user }) {
  if (!user) {
    return <LoginPrompt />;
  }
  
  return (
    <div>
      <UserHeader user={user} />
      <UserContent user={user} />
    </div>
  );
}

function LoginPrompt() {
  return (
    <div className="login-prompt">
      <h2>请先登录</h2>
      <button>登录</button>
    </div>
  );
}
```

### 🔥 条件渲染最佳实践

```jsx
// 1. 避免嵌套过深
function BadExample({ data, isLoading, error }) {
  return (
    <div>
      {!isLoading && !error && data && (
        <div>
          {data.users && data.users.length > 0 && (
            <ul>
              {data.users.map(user => (
                <li key={user.id}>
                  {user.name}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

// 2. 使用早期返回（推荐）
function GoodExample({ data, isLoading, error }) {
  if (isLoading) return <div>加载中...</div>;
  if (error) return <div>错误：{error.message}</div>;
  if (!data || !data.users) return <div>暂无数据</div>;
  
  return (
    <ul>
      {data.users.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}

// 3. 使用枚举或配置对象
function StatusDisplay({ status }) {
  const statusConfig = {
    loading: { text: '加载中...', className: 'status-loading' },
    success: { text: '操作成功', className: 'status-success' },
    error: { text: '操作失败', className: 'status-error' },
    idle: { text: '等待操作', className: 'status-idle' }
  };
  
  const config = statusConfig[status] || statusConfig.idle;
  
  return (
    <div className={config.className}>
      {config.text}
    </div>
  );
}

// 4. 使用组件组合
function ConditionalWrapper({ condition, wrapper, children }) {
  return condition ? wrapper(children) : children;
}

function App() {
  const isAdmin = true;
  
  return (
    <ConditionalWrapper
      condition={isAdmin}
      wrapper={children => (
        <div className="admin-layout">
          <AdminSidebar />
          {children}
        </div>
      )}
    >
      <main>
        <h1>主要内容</h1>
      </main>
    </ConditionalWrapper>
  );
}
```

## 🎯 2.5 列表与键

### 🆕 列表渲染的重要性

在React应用中，列表渲染是最常见的操作之一。正确的列表渲染对性能和用户体验至关重要。

### 💡 基本列表渲染

```jsx
function TodoList({ todos }) {
  return (
    <ul>
      {todos.map(todo => (
        <li key={todo.id}>
          <span>{todo.text}</span>
          <span>状态：{todo.completed ? '已完成' : '未完成'}</span>
        </li>
      ))}
    </ul>
  );
}

// 使用示例
const sampleTodos = [
  { id: 1, text: '学习React', completed: true },
  { id: 2, text: '写项目', completed: false },
  { id: 3, text: '部署应用', completed: false }
];

function App() {
  return <TodoList todos={sampleTodos} />;
}
```

### 🔑 键（Key）的重要性

键帮助React识别哪些项已更改、添加或删除，是列表渲染性能优化的关键。

```jsx
// ❌ 错误的键使用
function BadList({ items }) {
  return (
    <ul>
      {items.map((item, index) => (
        <li key={index}> {/* 不要使用索引作为键！ */}
          {item.name}
        </li>
      ))}
    </ul>
  );
}

// ✅ 正确的键使用
function GoodList({ items }) {
  return (
    <ul>
      {items.map(item => (
        <li key={item.id}> {/* 使用唯一标识符 */}
          {item.name}
        </li>
      ))}
    </ul>
  );
}

// 🔥 复杂的键处理
function UserList({ users }) {
  // 如果没有id，可以生成稳定的键
  const usersWithKeys = users.map((user, index) => ({
    ...user,
    // 使用业务逻辑生成稳定键
    key: user.email || `user-${index}`
  }));

  return (
    <ul>
      {usersWithKeys.map(user => (
        <li key={user.key}>
          <img src={user.avatar} alt={user.name} />
          <div>
            <h3>{user.name}</h3>
            <p>{user.email}</p>
          </div>
        </li>
      ))}
    </ul>
  );
}
```

### 🎯 列表渲染最佳实践

```jsx
// 1. 提取列表项组件
function TodoList({ todos, onToggle, onDelete }) {
  return (
    <ul className="todo-list">
      {todos.map(todo => (
        <TodoItem 
          key={todo.id}
          todo={todo}
          onToggle={onToggle}
          onDelete={onDelete}
        />
      ))}
    </ul>
  );
}

// 列表项组件
function TodoItem({ todo, onToggle, onDelete }) {
  return (
    <li className={`todo-item ${todo.completed ? 'completed' : ''}`}>
      <input 
        type="checkbox"
        checked={todo.completed}
        onChange={() => onToggle(todo.id)}
      />
      <span>{todo.text}</span>
      <button onClick={() => onDelete(todo.id)}>删除</button>
    </li>
  );
}

// 2. 空状态处理
function ProductList({ products, searchTerm }) {
  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (filteredProducts.length === 0) {
    return (
      <div className="empty-state">
        <p>没有找到匹配的产品</p>
        <button>重置搜索</button>
      </div>
    );
  }

  return (
    <div className="product-grid">
      {filteredProducts.map(product => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}

// 3. 虚拟滚动（大数据量优化）
import { FixedSizeList as List } from 'react-window';

function BigList({ items }) {
  const Row = ({ index, style }) => (
    <div style={style}>
      <span>{items[index].name}</span>
    </div>
  );

  return (
    <List
      height={400}
      itemCount={items.length}
      itemSize={50}
    >
      {Row}
    </List>
  );
}
```

## 🎯 2.6 表单处理

### 🆕 受控组件 vs 非受控组件

React中有两种处理表单的方式：

| 特性 | 受控组件 | 非受控组件 |
|------|----------|------------|
| **数据流** | 单向数据流 | 直接DOM操作 |
| **值控制** | React状态控制 | DOM元素控制 |
| **推荐场景** | 大多数情况 | 简单表单、文件上传 |
| **验证时机** | 实时验证 | 提交时验证 |

### 💡 受控组件实现

```jsx
import { useState } from 'react';

function LoginForm() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    rememberMe: false
  });
  const [errors, setErrors] = useState({});

  // 统一处理输入变化
  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    // 实时验证
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  // 表单验证
  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.email) {
      newErrors.email = '邮箱不能为空';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = '邮箱格式不正确';
    }
    
    if (!formData.password) {
      newErrors.password = '密码不能为空';
    } else if (formData.password.length < 6) {
      newErrors.password = '密码至少6位';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // 表单提交
  const handleSubmit = (event) => {
    event.preventDefault();
    
    if (validateForm()) {
      console.log('表单数据:', formData);
      // 发送到服务器...
    }
  };

  return (
    <form onSubmit={handleSubmit} className="login-form">
      <div className="form-group">
        <label htmlFor="email">邮箱地址</label>
        <input
          id="email"
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          className={errors.email ? 'error' : ''}
          placeholder="请输入邮箱"
        />
        {errors.email && <span className="error-text">{errors.email}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="password">密码</label>
        <input
          id="password"
          name="password"
          type="password"
          value={formData.password}
          onChange={handleChange}
          className={errors.password ? 'error' : ''}
          placeholder="请输入密码"
        />
        {errors.password && <span className="error-text">{errors.password}</span>}
      </div>

      <div className="form-group">
        <label>
          <input
            name="rememberMe"
            type="checkbox"
            checked={formData.rememberMe}
            onChange={handleChange}
          />
          记住我
        </label>
      </div>

      <button type="submit" className="submit-btn">
        登录
      </button>
    </form>
  );
}
```

### 🔥 表单处理最佳实践

```jsx
// 1. 自定义Hook管理表单状态
function useForm(initialValues, validate) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    
    setValues(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    // 实时验证
    if (validate) {
      const newErrors = validate({ ...values, [name]: value });
      setErrors(prev => ({
        ...prev,
        [name]: newErrors[name] || ''
      }));
    }
  };

  const handleBlur = (event) => {
    const { name } = event.target;
    setTouched(prev => ({ ...prev, [name]: true }));
  };

  const handleSubmit = (onSubmit) => (event) => {
    event.preventDefault();
    
    const newErrors = validate ? validate(values) : {};
    setErrors(newErrors);
    
    if (Object.keys(newErrors).length === 0) {
      onSubmit(values);
    }
  };

  return {
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    handleSubmit
  };
}

// 2. 使用自定义Hook
function AdvancedForm() {
  const validate = (values) => {
    const errors = {};
    
    if (!values.username) {
      errors.username = '用户名不能为空';
    }
    
    if (!values.email) {
      errors.email = '邮箱不能为空';
    } else if (!/\S+@\S+\.\S+/.test(values.email)) {
      errors.email = '邮箱格式不正确';
    }
    
    return errors;
  };

  const { values, errors, touched, handleChange, handleBlur, handleSubmit } = useForm({
    username: '',
    email: ''
  }, validate);

  const onSubmit = (formData) => {
    console.log('提交的数据:', formData);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <label>用户名</label>
        <input
          name="username"
          value={values.username}
          onChange={handleChange}
          onBlur={handleBlur}
          className={touched.username && errors.username ? 'error' : ''}
        />
        {touched.username && errors.username && (
          <span className="error">{errors.username}</span>
        )}
      </div>

      <div>
        <label>邮箱</label>
        <input
          name="email"
          type="email"
          value={values.email}
          onChange={handleChange}
          onBlur={handleBlur}
          className={touched.email && errors.email ? 'error' : ''}
        />
        {touched.email && errors.email && (
          <span className="error">{errors.email}</span>
        )}
      </div>

      <button type="submit">提交</button>
    </form>
  );
}

// 3. 文件上传处理
function FileUpload() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState('');

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    
    if (selectedFile) {
      setFile(selectedFile);
      
      // 创建预览URL
      const objectUrl = URL.createObjectURL(selectedFile);
      setPreview(objectUrl);
      
      // 清理函数
      return () => URL.revokeObjectURL(objectUrl);
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    
    if (file) {
      const formData = new FormData();
      formData.append('file', file);
      
      // 上传文件...
      fetch('/api/upload', {
        method: 'POST',
        body: formData
      });
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="file"
        accept="image/*"
        onChange={handleFileChange}
      />
      
      {preview && (
        <div>
          <img src={preview} alt="预览" style={{ maxWidth: '200px' }} />
        </div>
      )}
      
      <button type="submit">上传</button>
    </form>
  );
}
```

## 🎯 2.7 副作用处理

### 🆕 什么是副作用？

副作用是指在渲染过程之外执行的操作，包括：
- 数据获取
- 订阅
- 手动DOM操作
- 定时器
- 日志记录

**React哲学**：保持渲染函数的纯净，副作用放在useEffect中处理。

### 💡 useEffect深度解析

```jsx
import { useState, useEffect } from 'react';

function DataFetcher({ url }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // 标记组件是否已挂载
    let isMounted = true;
    
    // 取消请求的控制器
    const abortController = new AbortController();

    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch(url, {
          signal: abortController.signal
        });
        
        if (!response.ok) {
          throw new Error(`HTTP错误! 状态码: ${response.status}`);
        }
        
        const result = await response.json();
        
        // 检查组件是否仍然挂载
        if (isMounted) {
          setData(result);
        }
        
      } catch (err) {
        // 忽略取消请求的错误
        if (err.name !== 'AbortError' && isMounted) {
          setError(err.message);
        }
        
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchData();

    // 清理函数
    return () => {
      isMounted = false;
      abortController.abort(); // 取消请求
    };
  }, [url]); // 依赖数组

  if (loading) return <div>加载中...</div>;
  if (error) return <div>错误：{error}</div>;
  if (!data) return <div>暂无数据</div>;

  return (
    <div>
      <h2>数据加载成功</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
```

### 🔥 useEffect使用场景

```jsx
// 1. 定时器
function Timer() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const intervalId = setInterval(() => {
      setCount(prevCount => prevCount + 1);
    }, 1000);

    // 清理定时器
    return () => clearInterval(intervalId);
  }, []); // 空依赖数组，只在挂载时执行

  return <div>计时器：{count}秒</div>;
}

// 2. 事件监听
function WindowSize() {
  const [windowSize, setWindowSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight
  });

  useEffect(() => {
    const handleResize = () => {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight
      });
    };

    window.addEventListener('resize', handleResize);
    
    // 清理事件监听
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div>
      窗口大小：{windowSize.width} x {windowSize.height}
    </div>
  );
}

// 3. 本地存储
function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`读取 ${key} 失败:`, error);
      return initialValue;
    }
  });

  const setValue = (value) => {
    try {
      setStoredValue(value);
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(`保存 ${key} 失败:`, error);
    }
  };

  return [storedValue, setValue];
}

// 4. 文档标题
function DocumentTitle({ title }) {
  useEffect(() => {
    document.title = title;
    
    // 恢复原始标题
    return () => {
      document.title = '原始标题';
    };
  }, [title]);

  return <div>当前标题：{title}</div>;
}
```

### 🎯 useEffect性能优化

```jsx
// 1. 避免不必要的effect执行
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);

  // ❌ 不好的写法：每次渲染都创建新函数
  useEffect(() => {
    fetchUser(userId).then(setUser);
  }); // 没有依赖数组

  // ✅ 好的写法：只有userId变化时执行
  useEffect(() => {
    fetchUser(userId).then(setUser);
  }, [userId]);

  // 🔥 更好的写法：使用useCallback优化函数
  const fetchUserData = useCallback(async () => {
    const userData = await fetchUser(userId);
    setUser(userData);
  }, [userId]);

  useEffect(() => {
    fetchUserData();
  }, [fetchUserData]);

  return <div>{user?.name}</div>;
}

// 2. 使用useMemo优化计算
function ExpensiveComponent({ data }) {
  // ❌ 每次渲染都重新计算
  const expensiveValue = expensiveCalculation(data);

  // ✅ 使用useMemo缓存计算结果
  const memoizedValue = useMemo(() => {
    return expensiveCalculation(data);
  }, [data]);

  return <div>{memoizedValue}</div>;
}

// 3. 批量状态更新
function BatchUpdateExample() {
  const [count, setCount] = useState(0);
  const [text, setText] = useState('');

  // ❌ 不好的写法：多个独立的状态更新
  const handleClick = () => {
    setCount(count + 1);
    setText('更新了'); // 这会触发两次渲染
  };

  // ✅ 好的写法：使用函数式更新
  const handleClickBetter = () => {
    setCount(prevCount => prevCount + 1);
    setText('更新了'); // React会自动批量处理
  };

  // 🔥 更好的写法：使用useReducer管理相关状态
  const [state, dispatch] = useReducer((prevState, action) => {
    switch (action.type) {
      case 'UPDATE':
        return {
          ...prevState,
          count: prevState.count + 1,
          text: '更新了'
        };
      default:
        return prevState;
    }
  }, { count: 0, text: '' });

  return (
    <div>
      <button onClick={handleClickBetter}>点击我</button>
      <div>计数：{count}</div>
      <div>文本：{text}</div>
    </div>
  );
}
```

## 🎯 2.8 自定义Hooks

### 🆕 什么是自定义Hook？

自定义Hook是一个函数，其名称以"use"开头，可以调用其他Hook。它是React逻辑复用的最佳方式。

**设计原则**：
- 以"use"开头
- 可以调用其他Hook
- 每个调用都有自己的状态
- 遵循Hooks的规则

### 💡 常用自定义Hook实现

```jsx
// 1. useLocalStorage Hook
function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`读取 ${key} 失败:`, error);
      return initialValue;
    }
  });

  const setValue = (value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`保存 ${key} 失败:`, error);
    }
  };

  return [storedValue, setValue];
}

// 使用示例
function ThemeToggle() {
  const [theme, setTheme] = useLocalStorage('theme', 'light');
  
  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  };

  return (
    <button onClick={toggleTheme}>
      切换主题（当前：{theme}）
    </button>
  );
}

// 2. useFetch Hook
function useFetch(url, options = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;
    const abortController = new AbortController();

    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch(url, {
          ...options,
          signal: abortController.signal
        });
        
        if (!response.ok) {
          throw new Error(`HTTP错误! 状态码: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (isMounted) {
          setData(result);
        }
        
      } catch (err) {
        if (err.name !== 'AbortError' && isMounted) {
          setError(err.message);
        }
        
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      isMounted = false;
      abortController.abort();
    };
  }, [url, JSON.stringify(options)]);

  return { data, loading, error, refetch: () => {} };
}

// 3. useDebounce Hook
function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

// 使用示例
function Search() {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 500);
  
  const { data: results, loading } = useFetch(
    `/api/search?q=${debouncedQuery}`,
    { enabled: debouncedQuery.length > 0 }
  );

  return (
    <div>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="搜索..."
      />
      {loading && <div>搜索中...</div>}
      {results && (
        <ul>
          {results.map(item => (
            <li key={item.id}>{item.name}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

// 4. useToggle Hook
function useToggle(initialValue = false) {
  const [value, setValue] = useState(initialValue);

  const toggle = useCallback(() => {
    setValue(prevValue => !prevValue);
  }, []);

  const setTrue = useCallback(() => {
    setValue(true);
  }, []);

  const setFalse = useCallback(() => {
    setValue(false);
  }, []);

  return [value, { toggle, setTrue, setFalse }];
}

// 使用示例
function Modal() {
  const [isOpen, { toggle, setTrue, setFalse }] = useToggle(false);

  return (
    <div>
      <button onClick={toggle}>切换模态框</button>
      
      {isOpen && (
        <div className="modal">
          <h2>模态框标题</h2>
          <p>这是模态框内容</p>
          <button onClick={setFalse}>关闭</button>
        </div>
      )}
    </div>
  );
}
```

### 🔥 高级自定义Hook

```jsx
// 1. useReducer + useContext 状态管理
function createStore(reducer, initialState) {
  const StateContext = createContext();
  const DispatchContext = createContext();

  function Provider({ children }) {
    const [state, dispatch] = useReducer(reducer, initialState);
    
    return (
      <StateContext.Provider value={state}>
        <DispatchContext.Provider value={dispatch}>
          {children}
        </DispatchContext.Provider>
      </StateContext.Provider>
    );
  }

  function useState() {
    const context = useContext(StateContext);
    if (!context) {
      throw new Error('必须在Provider内使用useState');
    }
    return context;
  }

  function useDispatch() {
    const context = useContext(DispatchContext);
    if (!context) {
      throw new Error('必须在Provider内使用useDispatch');
    }
    return context;
  }

  return { Provider, useState, useDispatch };
}

// 2. usePrevious Hook（获取上一次的值）
function usePrevious(value) {
  const ref = useRef();
  
  useEffect(() => {
    ref.current = value;
  }, [value]);
  
  return ref.current;
}

// 3. useInterval Hook（可控的定时器）
function useInterval(callback, delay) {
  const savedCallback = useRef();

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    function tick() {
      savedCallback.current();
    }

    if (delay !== null) {
      const id = setInterval(tick, delay);
      return () => clearInterval(id);
    }
  }, [delay]);
}

// 4. 组合多个Hook
function useUser(userId) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const { data: profile } = useFetch(`/api/users/${userId}/profile`);
  const { data: posts } = useFetch(`/api/users/${userId}/posts`);
  const [isFollowing, toggleFollow] = useToggle(false);

  useEffect(() => {
    if (profile && posts) {
      setUser({
        ...profile,
        posts,
        isFollowing
      });
      setLoading(false);
    }
  }, [profile, posts, isFollowing]);

  return {
    user,
    loading: loading || !profile || !posts,
    error,
    toggleFollow
  };
}
```

## 🎯 2.9 练习与实践

### 💪 练习1：创建完整的表单组件

**需求**：创建一个用户注册表单，包含以下功能：
- 用户名、邮箱、密码、确认密码字段
- 实时表单验证
- 密码强度显示
- 表单提交处理
- 错误状态管理

```jsx
function RegistrationForm() {
  // 在这里实现你的代码
  return (
    <form>
      {/* 实现表单字段 */}
    </form>
  );
}
```

### 💪 练习2：实现任务管理应用

**需求**：创建一个完整的任务管理应用，包含：
- 添加新任务
- 标记任务完成/未完成
- 删除任务
- 过滤任务（全部/进行中/已完成）
- 任务统计
- 本地存储持久化

```jsx
function TodoApp() {
  // 在这里实现你的代码
  return (
    <div>
      {/* 实现任务管理界面 */}
    </div>
  );
}
```

### 💪 练习3：创建自定义Hook

**需求**：创建一个`useFormValidation`自定义Hook，实现：
- 表单字段验证
- 实时错误显示
- 表单提交控制
- 字段触摸状态跟踪

```jsx
function useFormValidation(initialValues, validationRules) {
  // 在这里实现你的Hook
  return {
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    handleSubmit,
    isValid
  };
}
```

## 📚 2.10 本章小结

### 🎓 本章重点回顾

1. **状态管理**：掌握了useState和状态更新的最佳实践
2. **Hooks深入**：理解了useEffect、useContext、useReducer的工作原理
3. **事件处理**：学会了React事件系统的使用和优化
4. **条件渲染**：掌握了多种条件渲染技术和最佳实践
5. **列表渲染**：理解了键的重要性和大数据量优化
6. **表单处理**：学会了受控组件和表单验证
7. **副作用处理**：掌握了useEffect的使用场景和性能优化
8. **自定义Hooks**：学会了逻辑复用和高级Hook模式

### 🔑 关键知识点

- **状态不可变性**：永远不要直接修改状态
- **Hook规则**：只在最顶层调用Hook，不要在循环、条件或嵌套函数中调用
- **性能优化**：合理使用依赖数组，避免不必要的重新渲染
- **代码组织**：按功能组织代码，提取可复用逻辑

### 🚀 下一步学习建议

在下一章中，我们将深入学习：
- React组件设计模式
- 高阶组件和渲染属性
- 组件组合和继承
- 设计系统构建

### 💡 实战建议

1. **多练习**：本章概念较多，需要通过实际项目巩固
2. **理解原理**：不仅要会使用Hook，还要理解其工作原理
3. **代码审查**：多阅读优秀的React代码，学习最佳实践
4. **性能意识**：在开发过程中始终关注性能优化

## 🔗 延伸资源

### 📖 推荐阅读

- [React官方Hooks文档](https://react.dev/reference/react)
- [useEffect完整指南](https://overreacted.io/zh-hans/a-complete-guide-to-useeffect/)
- [React Hooks最佳实践](https://www.smashingmagazine.com/2020/04/react-hooks-best-practices/)

### 🛠️ 工具推荐

- [React DevTools](https://react.dev/learn/react-developer-tools) - React调试工具
- [ESLint插件](https://www.npmjs.com/package/eslint-plugin-react-hooks) - Hooks规则检查
- [React Hook Form](https://react-hook-form.com/) - 表单处理库

### 💬 社区支持

- [React官方论坛](https://react.dev/community)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/reactjs)
- [GitHub Discussions](https://github.com/facebook/react/discussions)

---

**恭喜你完成了第二章的学习！** 🎉

你已经掌握了React的核心概念，为构建复杂应用打下了坚实基础。继续实践和探索，你将成长为优秀的React开发者！

**下一章预告**：在第三章中，我们将学习React组件设计的最佳实践和高级模式。

# 第2章：组件与Props - 构建模块化React应用

## 章节介绍

React的核心思想是将用户界面拆分成独立、可复用的组件，然后通过组合这些组件来构建复杂的UI。组件是React应用的基本构建块，而Props则是组件之间通信的重要机制。

本章将深入探讨：
- 组件的本质与重要性
- 函数组件与类组件的区别与使用场景
- Props的基本概念与验证
- 组件组合模式与最佳实践
- 组件的生命周期（基础概念）
- 组件的设计原则与代码组织

通过本章学习，你将理解如何设计出高内聚、低耦合、可复用的React组件。

## 为什么组件化如此重要？

在传统Web开发中，我们通常会编写大量混合HTML、CSS和JavaScript的代码，随着项目规模增长，这种混合方式会导致代码难以维护、复用性差、测试困难等问题。

React的组件化思想解决了这些问题：

1. **关注点分离**：每个组件只负责自己的特定功能
2. **代码复用**：一次编写，多处使用
3. **独立开发与测试**：组件可以独立开发和测试
4. **并行开发**：不同团队成员可以同时开发不同组件
5. **便于维护**：修改某个组件不会影响其他组件

让我们从一个简单的例子开始，逐步深入理解组件的概念。

## 函数组件与类组件

React支持两种类型的组件：函数组件和类组件。理解它们的差异和适用场景对于写出高质量的React代码至关重要。

### 函数组件

函数组件是最简单、最直接的组件定义方式。它本质上就是一个JavaScript函数，接收props作为参数，返回React元素。

```jsx
function Welcome(props) {
  return <h1>Hello, {props.name}</h1>;
}
```

函数组件的优势：
- 语法简单，更直观
- 没有this绑定问题
- 更容易测试
- 性能更好（React团队正在优化函数组件）
- 推荐使用Hooks进行状态管理

### 类组件

类组件使用ES6的class语法定义，继承自React.Component。

```jsx
class Welcome extends React.Component {
  render() {
    return <h1>Hello, {this.props.name}</h1>;
  }
}
```

类组件的特点：
- 可以拥有内部状态（state）
- 可以使用生命周期方法
- 有this上下文
- 更适合复杂组件逻辑

### 如何选择？

**使用函数组件的情况：**
- 简单的展示型组件
- 无需内部状态
- 无需使用生命周期方法
- 新项目或推荐使用Hooks的现代开发

**使用类组件的情况：**
- 需要复杂的内部状态管理
- 需要使用特定的生命周期方法
- 维护旧项目代码
- 团队更熟悉面向对象编程模式

随着React Hooks的引入，函数组件现在也可以处理状态和生命周期，这使得函数组件成为大多数场景的首选。

## Props深入理解

Props（properties的缩写）是React组件之间通信的主要方式。它们是父组件向子组件传递数据的只读对象。

### Props的基本使用

```jsx
// 父组件
function App() {
  return (
    <div>
      <UserProfile name="张三" age={28} isStudent={false} />
      <UserProfile name="李四" age={22} isStudent={true} />
    </div>
  );
}

// 子组件
function UserProfile(props) {
  return (
    <div>
      <h2>用户信息</h2>
      <p>姓名: {props.name}</p>
      <p>年龄: {props.age}</p>
      <p>是否是学生: {props.isStudent ? '是' : '否'}</p>
    </div>
  );
}
```

### Props解构

我们可以使用ES6解构语法，使代码更简洁：

```jsx
function UserProfile({ name, age, isStudent }) {
  return (
    <div>
      <h2>用户信息</h2>
      <p>姓名: {name}</p>
      <p>年龄: {age}</p>
      <p>是否是学生: {isStudent ? '是' : '否'}</p>
    </div>
  );
}
```

### Props的只读性

Props是只读的，组件不能修改自己的props：

```jsx
// 错误示例 - 不能直接修改props
function UserProfile(props) {
  props.name = "新名字"; // 这会导致错误
  return <div>{props.name}</div>;
}

// 正确做法 - 通过状态管理或回调函数
function UserProfile({ name, onUpdate }) {
  const handleClick = () => {
    onUpdate("新名字"); // 通过回调通知父组件更新
  };
  
  return (
    <div>
      <div>{name}</div>
      <button onClick={handleClick}>更新名字</button>
    </div>
  );
}
```

### Props的类型检查

React提供了PropTypes库用于类型检查，帮助捕获潜在的错误：

```jsx
import PropTypes from 'prop-types';

function UserProfile({ name, age, isStudent }) {
  return (
    <div>
      <h2>用户信息</h2>
      <p>姓名: {name}</p>
      <p>年龄: {age}</p>
      <p>是否是学生: {isStudent ? '是' : '否'}</p>
    </div>
  );
}

// 定义props的类型
UserProfile.propTypes = {
  name: PropTypes.string.isRequired, // 必需的字符串
  age: PropTypes.number, // 可选的数字
  isStudent: PropTypes.bool, // 可选的布尔值
  onUpdate: PropTypes.func // 可选的函数
};

// 定义默认props值
UserProfile.defaultProps = {
  age: 18,
  isStudent: false
};
```

在TypeScript项目中，你可以使用接口来定义Props类型：

```tsx
interface UserProfileProps {
  name: string;
  age?: number;
  isStudent?: boolean;
  onUpdate?: (newName: string) => void;
}

function UserProfile({ name, age = 18, isStudent = false, onUpdate }: UserProfileProps) {
  return (
    <div>
      <h2>用户信息</h2>
      <p>姓名: {name}</p>
      <p>年龄: {age}</p>
      <p>是否是学生: {isStudent ? '是' : '否'}</p>
    </div>
  );
}
```

## 组件组合模式

React推崇组件组合而非继承。通过组合简单的组件，可以构建复杂的UI。下面介绍几种常见的组件组合模式。

### 包含关系（组合）

一个组件可以包含其他组件，形成嵌套关系：

```jsx
function Card({ children, title }) {
  return (
    <div className="card">
      <div className="card-header">
        <h3>{title}</h3>
      </div>
      <div className="card-body">
        {children}
      </div>
    </div>
  );
}

function App() {
  return (
    <div>
      <Card title="用户信息">
        <p>姓名: 张三</p>
        <p>年龄: 28</p>
        <p>职业: 前端开发</p>
      </Card>
      
      <Card title="联系方式">
        <p>邮箱: zhangsan@example.com</p>
        <p>电话: 13800138000</p>
      </Card>
    </div>
  );
}
```

### 特殊化（特殊组件）

一个组件可以是另一个组件的"特殊版本"：

```jsx
function Dialog({ title, message, children }) {
  return (
    <div className="dialog">
      <h2 className="dialog-title">{title}</h2>
      <p className="dialog-message">{message}</p>
      <div className="dialog-content">
        {children}
      </div>
    </div>
  );
}

function WelcomeDialog() {
  return (
    <Dialog 
      title="欢迎" 
      message="欢迎来到我们的应用！"
    >
      <button>开始使用</button>
    </Dialog>
  );
}
```

### 容器组件与展示组件

这是一种常见的设计模式，将逻辑组件和展示组件分离：

```jsx
// 展示组件 - 只负责UI渲染
function UserList({ users, onUserClick }) {
  return (
    <ul>
      {users.map(user => (
        <li key={user.id} onClick={() => onUserClick(user.id)}>
          {user.name}
        </li>
      ))}
    </ul>
  );
}

// 容器组件 - 负责数据获取和状态管理
class UserListContainer extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      users: [],
      loading: true
    };
  }
  
  componentDidMount() {
    // 模拟API调用
    setTimeout(() => {
      this.setState({
        users: [
          { id: 1, name: '张三' },
          { id: 2, name: '李四' },
          { id: 3, name: '王五' }
        ],
        loading: false
      });
    }, 1000);
  }
  
  handleUserClick = (userId) => {
    console.log(`用户 ${userId} 被点击`);
  }
  
  render() {
    if (this.state.loading) {
      return <div>加载中...</div>;
    }
    
    return (
      <UserList 
        users={this.state.users} 
        onUserClick={this.handleUserClick}
      />
    );
  }
}
```

### 高阶组件(HOC)模式

高阶组件是一个函数，它接收一个组件并返回一个新组件：

```jsx
// 高阶组件 - 为组件添加加载状态
function withLoading(WrappedComponent) {
  return function WithLoadingComponent({ isLoading, ...otherProps }) {
    if (isLoading) {
      return <div>加载中...</div>;
    }
    return <WrappedComponent {...otherProps} />;
  };
}

// 使用高阶组件
function UserList({ users }) {
  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}

// 添加加载功能
const UserListWithLoading = withLoading(UserList);

function App() {
  const [users, setUsers] = React.useState([]);
  const [isLoading, setIsLoading] = React.useState(true);
  
  React.useEffect(() => {
    // 模拟API调用
    setTimeout(() => {
      setUsers([
        { id: 1, name: '张三' },
        { id: 2, name: '李四' }
      ]);
      setIsLoading(false);
    }, 1000);
  }, []);
  
  return (
    <UserListWithLoading 
      isLoading={isLoading} 
      users={users} 
    />
  );
}
```

## 组件设计原则

好的组件设计应该遵循以下原则：

### 1. 单一职责原则

每个组件应该只负责一个功能：

```jsx
// 好的设计 - 职责清晰
function Avatar({ src, alt, size }) {
  return <img src={src} alt={alt} className={`avatar-${size}`} />;
}

function UserInfo({ name, email }) {
  return (
    <div>
      <h3>{name}</h3>
      <p>{email}</p>
    </div>
  );
}

function UserProfile() {
  return (
    <div className="user-profile">
      <Avatar src="avatar.jpg" alt="用户头像" size="large" />
      <UserInfo name="张三" email="zhangsan@example.com" />
    </div>
  );
}

// 不好的设计 - 职责混合
function UserProfileAndData() {
  // 既负责显示用户信息，又负责获取数据
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    // 获取用户数据的逻辑
    fetchUser().then(setUser);
  }, []);
  
  return (
    <div>
      {/* 显示用户信息的逻辑 */}
    </div>
  );
}
```

### 2. 可复用性

设计通用组件，提高复用性：

```jsx
// 好的设计 - 通用按钮组件
function Button({ 
  children, 
  variant = 'primary', 
  size = 'medium', 
  disabled = false, 
  onClick 
}) {
  const className = `btn btn-${variant} btn-${size}`;
  
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

// 使用示例
function App() {
  return (
    <div>
      <Button variant="primary" size="large">主要按钮</Button>
      <Button variant="secondary">次要按钮</Button>
      <Button disabled>禁用按钮</Button>
    </div>
  );
}
```

### 3. 封装性

隐藏组件内部实现细节，暴露最小必要的接口：

```jsx
// 好的设计 - 隐藏内部状态
function ToggleButton({ initialValue = false, onToggle }) {
  const [isToggled, setIsToggled] = useState(initialValue);
  
  const handleToggle = () => {
    const newValue = !isToggled;
    setIsToggled(newValue);
    if (onToggle) {
      onToggle(newValue);
    }
  };
  
  return (
    <button 
      onClick={handleToggle}
      className={isToggled ? 'toggled' : ''}
    >
      {isToggled ? '开启' : '关闭'}
    </button>
  );
}

// 使用者不需要知道内部状态
function App() {
  const handleToggle = (newValue) => {
    console.log(`切换到: ${newValue ? '开启' : '关闭'}`);
  };
  
  return <ToggleButton initialValue={true} onToggle={handleToggle} />;
}
```

### 4. 组合优于继承

React推崇使用组合而非继承来实现代码复用：

```jsx
// 好的设计 - 使用组合
function Card({ children, title, footer }) {
  return (
    <div className="card">
      {title && <div className="card-header">{title}</div>}
      <div className="card-body">{children}</div>
      {footer && <div className="card-footer">{footer}</div>}
    </div>
  );
}

// 不同类型的卡片，通过组合实现
function UserCard({ user }) {
  return (
    <Card title="用户信息" footer={<button>编辑</button>}>
      <p>姓名: {user.name}</p>
      <p>邮箱: {user.email}</p>
    </Card>
  );
}

// 不好的设计 - 使用继承
class UserCard extends Card {
  render() {
    return (
      <div className="card">
        <div className="card-header">用户信息</div>
        <div className="card-body">
          <p>姓名: {this.props.user.name}</p>
          <p>邮箱: {this.props.user.email}</p>
        </div>
        <div className="card-footer"><button>编辑</button></div>
      </div>
    );
  }
}
```

## 组件的生命周期（基础概念）

虽然我们将在后续章节详细讨论Hooks和生命周期方法，但在这里简单介绍组件生命周期的基本概念，以便理解组件的工作原理。

### 类组件的生命周期

类组件有一系列生命周期方法，在组件的不同阶段被调用：

```jsx
class LifecycleDemo extends React.Component {
  constructor(props) {
    super(props);
    console.log('1. 构造函数 - 初始化状态');
    this.state = { count: 0 };
  }
  
  componentDidMount() {
    console.log('3. 组件挂载后 - 可以进行DOM操作，发起API请求');
  }
  
  componentDidUpdate(prevProps, prevState) {
    console.log('4. 组件更新后 - 可以响应props或state的变化');
  }
  
  componentWillUnmount() {
    console.log('5. 组件卸载前 - 清理定时器、取消请求等');
  }
  
  render() {
    console.log('2. 渲染 - 返回JSX');
    return (
      <div>
        <p>计数: {this.state.count}</p>
        <button onClick={() => this.setState({ count: this.state.count + 1 })}>
          增加
        </button>
      </div>
    );
  }
}
```

### 函数组件的生命周期

函数组件使用Hooks来模拟生命周期：

```jsx
import { useState, useEffect } from 'react';

function LifecycleDemo() {
  const [count, setCount] = useState(0);
  
  // useEffect相当于componentDidMount和componentDidUpdate
  useEffect(() => {
    console.log('组件挂载后或更新后');
    
    // 清理函数相当于componentWillUnmount
    return () => {
      console.log('组件卸载前或更新前');
    };
  }); // 空依赖数组表示只在挂载后执行一次
  
  return (
    <div>
      <p>计数: {count}</p>
      <button onClick={() => setCount(count + 1)}>
        增加
      </button>
    </div>
  );
}
```

## 实践案例：构建一个完整的组件库

让我们通过构建一个完整的组件库来实践本章学到的知识。我们将创建一个UI组件库，包含常用的UI组件。

### 基础组件：Button

```jsx
// Button.jsx
import PropTypes from 'prop-types';

export function Button({ 
  children, 
  variant = 'primary', 
  size = 'medium',
  disabled = false,
  onClick,
  type = 'button'
}) {
  const baseClass = 'btn';
  const variantClass = `btn-${variant}`;
  const sizeClass = `btn-${size}`;
  const disabledClass = disabled ? 'btn-disabled' : '';
  
  const className = `${baseClass} ${variantClass} ${sizeClass} ${disabledClass}`;
  
  return (
    <button
      type={type}
      className={className}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
}

Button.propTypes = {
  children: PropTypes.node.isRequired,
  variant: PropTypes.oneOf(['primary', 'secondary', 'outline', 'danger']),
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  disabled: PropTypes.bool,
  onClick: PropTypes.func,
  type: PropTypes.oneOf(['button', 'submit', 'reset'])
};
```

### 复合组件：Card

```jsx
// Card.jsx
import PropTypes from 'prop-types';

export function Card({ children, className, onClick }) {
  const cardClass = `card ${className || ''}`;
  
  return (
    <div className={cardClass} onClick={onClick}>
      {children}
    </div>
  );
}

Card.propTypes = {
  children: PropTypes.node,
  className: PropTypes.string,
  onClick: PropTypes.func
};

export function CardHeader({ children }) {
  return <div className="card-header">{children}</div>;
}

export function CardBody({ children }) {
  return <div className="card-body">{children}</div>;
}

export function CardFooter({ children }) {
  return <div className="card-footer">{children}</div>;
}
```

### 表单组件：Input

```jsx
// Input.jsx
import PropTypes from 'prop-types';

export function Input({
  label,
  value,
  onChange,
  placeholder,
  type = 'text',
  error,
  disabled = false,
  required = false
}) {
  const inputId = `input-${Math.random().toString(36).substr(2, 9)}`;
  
  return (
    <div className="form-group">
      {label && (
        <label htmlFor={inputId} className="form-label">
          {label}
          {required && <span className="required">*</span>}
        </label>
      )}
      <input
        id={inputId}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        disabled={disabled}
        className={`form-input ${error ? 'input-error' : ''}`}
      />
      {error && <div className="error-message">{error}</div>}
    </div>
  );
}

Input.propTypes = {
  label: PropTypes.string,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  onChange: PropTypes.func.isRequired,
  placeholder: PropTypes.string,
  type: PropTypes.string,
  error: PropTypes.string,
  disabled: PropTypes.bool,
  required: PropTypes.bool
};
```

### 列表组件：List

```jsx
// List.jsx
import PropTypes from 'prop-types';

export function List({ items, renderItem, onItemClick, emptyMessage }) {
  if (!items || items.length === 0) {
    return <div className="list-empty">{emptyMessage || '暂无数据'}</div>;
  }
  
  return (
    <ul className="list">
      {items.map((item, index) => (
        <li 
          key={item.id || index} 
          className="list-item"
          onClick={() => onItemClick && onItemClick(item, index)}
        >
          {renderItem ? renderItem(item, index) : item}
        </li>
      ))}
    </ul>
  );
}

List.propTypes = {
  items: PropTypes.array.isRequired,
  renderItem: PropTypes.func,
  onItemClick: PropTypes.func,
  emptyMessage: PropTypes.string
};
```

### 完整示例：用户管理系统

让我们使用这些组件构建一个用户管理系统：

```jsx
// UserManagementSystem.jsx
import { useState, useEffect } from 'react';
import { Button } from './Button';
import { Card, CardHeader, CardBody, CardFooter } from './Card';
import { Input } from './Input';
import { List } from './List';

export function UserManagementSystem() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: ''
  });
  const [editingUser, setEditingUser] = useState(null);
  const [errors, setErrors] = useState({});
  
  // 模拟获取用户数据
  useEffect(() => {
    setLoading(true);
    setTimeout(() => {
      setUsers([
        { id: 1, name: '张三', email: 'zhangsan@example.com', phone: '13800138001' },
        { id: 2, name: '李四', email: 'lisi@example.com', phone: '13800138002' },
        { id: 3, name: '王五', email: 'wangwu@example.com', phone: '13800138003' }
      ]);
      setLoading(false);
    }, 1000);
  }, []);
  
  // 表单验证
  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = '姓名不能为空';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = '邮箱不能为空';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = '邮箱格式不正确';
    }
    
    if (!formData.phone.trim()) {
      newErrors.phone = '手机号不能为空';
    } else if (!/^1[3-9]\d{9}$/.test(formData.phone)) {
      newErrors.phone = '手机号格式不正确';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  // 处理表单提交
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    if (editingUser) {
      // 更新用户
      setUsers(users.map(user => 
        user.id === editingUser.id 
          ? { ...user, ...formData }
          : user
      ));
      setEditingUser(null);
    } else {
      // 添加新用户
      const newUser = {
        id: Date.now(),
        ...formData
      };
      setUsers([...users, newUser]);
    }
    
    // 重置表单
    setFormData({ name: '', email: '', phone: '' });
  };
  
  // 处理表单输入
  const handleChange = (field, value) => {
    setFormData({
      ...formData,
      [field]: value
    });
    
    // 清除该字段的错误信息
    if (errors[field]) {
      setErrors({
        ...errors,
        [field]: ''
      });
    }
  };
  
  // 编辑用户
  const handleEditUser = (user) => {
    setEditingUser(user);
    setFormData({
      name: user.name,
      email: user.email,
      phone: user.phone
    });
  };
  
  // 删除用户
  const handleDeleteUser = (userId) => {
    if (window.confirm('确定要删除这个用户吗？')) {
      setUsers(users.filter(user => user.id !== userId));
    }
  };
  
  // 渲染用户列表项
  const renderUserItem = (user) => (
    <Card className="user-card">
      <CardBody>
        <h4>{user.name}</h4>
        <p>邮箱: {user.email}</p>
        <p>电话: {user.phone}</p>
      </CardBody>
      <CardFooter>
        <Button size="small" onClick={() => handleEditUser(user)}>编辑</Button>
        <Button variant="danger" size="small" onClick={() => handleDeleteUser(user.id)}>删除</Button>
      </CardFooter>
    </Card>
  );
  
  return (
    <div className="user-management">
      <Card>
        <CardHeader>
          <h2>用户管理系统</h2>
        </CardHeader>
        <CardBody>
          <form onSubmit={handleSubmit} className="user-form">
            <Input
              label="姓名"
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              error={errors.name}
              required
            />
            <Input
              label="邮箱"
              type="email"
              value={formData.email}
              onChange={(e) => handleChange('email', e.target.value)}
              error={errors.email}
              required
            />
            <Input
              label="手机号"
              value={formData.phone}
              onChange={(e) => handleChange('phone', e.target.value)}
              error={errors.phone}
              required
            />
            <Button type="submit">
              {editingUser ? '更新用户' : '添加用户'}
            </Button>
            {editingUser && (
              <Button 
                variant="secondary" 
                onClick={() => {
                  setEditingUser(null);
                  setFormData({ name: '', email: '', phone: '' });
                }}
              >
                取消
              </Button>
            )}
          </form>
        </CardBody>
      </Card>
      
      <Card>
        <CardHeader>
          <h3>用户列表</h3>
        </CardHeader>
        <CardBody>
          {loading ? (
            <div className="loading">加载中...</div>
          ) : (
            <List 
              items={users}
              renderItem={renderUserItem}
              emptyMessage="暂无用户数据"
            />
          )}
        </CardBody>
      </Card>
    </div>
  );
}
```

## 最佳实践总结

1. **优先使用函数组件**：除非你有特殊理由使用类组件，否则优先使用函数组件配合Hooks。

2. **合理拆分组件**：保持组件单一职责，不要让组件过于复杂。

3. **使用TypeScript或PropTypes**：进行类型检查，提高代码质量。

4. **避免直接修改Props**：Props是只读的，不要尝试修改它们。

5. **组合优于继承**：使用组件组合而非继承来实现代码复用。

6. **设计可复用的组件**：通过Props使组件更加灵活和可复用。

7. **分离容器组件和展示组件**：将逻辑和UI分离，提高代码可测试性。

8. **合理使用默认Props**：为可选的Props提供合理的默认值。

9. **组件命名清晰**：使用描述性的组件名，反映组件的功能。

10. **编写组件文档**：为复杂组件编写使用说明和示例。

## 练习项目

为了巩固本章所学知识，建议完成以下练习项目：

1. **创建一个博客文章组件库**：
   - 文章卡片组件
   - 评论列表组件
   - 评论表单组件
   - 标签组件

2. **构建一个电商产品展示页面**：
   - 产品卡片组件
   - 产品图片轮播组件
   - 产品详情组件
   - 购物车按钮组件

3. **实现一个任务管理应用**：
   - 任务列表组件
   - 任务项组件
   - 任务过滤器组件
   - 任务表单组件

## 总结

本章我们深入学习了React组件与Props的核心概念，包括：

- React组件的类型与区别
- Props的使用与验证
- 组件组合模式
- 组件设计原则
- 生命周期基础概念
- 实践案例与最佳实践

组件是React的基石，掌握组件的设计与使用对于构建高质量React应用至关重要。下一章我们将学习React的状态管理与事件处理，进一步深入React的核心概念。
# 第三章：React组件设计

## 🎯 本章学习目标

通过本章学习，你将能够：
- ✅ 掌握组件设计的核心原则和最佳实践
- ✅ 设计可复用、可组合的组件系统
- ✅ 理解各种组件设计模式的应用场景
- ✅ 实现专业的组件接口和API设计
- ✅ 构建可维护的组件库和设计系统

## 🚀 3.1 组件设计原则

### 🆕 什么是好的组件设计？

**组件设计质量指标**：
- **可复用性**：在不同场景下都能正常工作
- **可维护性**：代码清晰，易于修改和扩展
- **可测试性**：组件逻辑易于测试验证
- **可组合性**：能够与其他组件灵活组合

### 💡 单一职责原则（SRP）

单一职责原则要求每个组件只负责一个特定的功能或关注点。

**新手理解**：一个组件只做一件事，并且做好。

**高手进阶**：组件应该只有一个引起变化的原因。

```jsx
// ❌ 违反单一职责原则的组件
function UserProfile({ user, onEdit, onDelete, onShare }) {
  return (
    <div className="user-profile">
      <h2>{user.name}</h2>
      <p>{user.email}</p>
      <img src={user.avatar} alt={user.name} />
      
      {/* 显示逻辑 */}
      {user.isOnline && <span className="online-indicator">在线</span>}
      
      {/* 编辑逻辑 */}
      <button onClick={() => onEdit(user.id)}>编辑</button>
      
      {/* 删除逻辑 */}
      <button onClick={() => onDelete(user.id)}>删除</button>
      
      {/* 分享逻辑 */}
      <button onClick={() => onShare(user)}>分享</button>
    </div>
  );
}

// ✅ 遵循单一职责原则的组件拆分
function UserDisplay({ user }) {
  return (
    <div className="user-display">
      <h2>{user.name}</h2>
      <p>{user.email}</p>
      <img src={user.avatar} alt={user.name} />
      {user.isOnline && <span className="online-indicator">在线</span>}
    </div>
  );
}

function UserActions({ userId, onEdit, onDelete, onShare }) {
  return (
    <div className="user-actions">
      <button onClick={() => onEdit(userId)}>编辑</button>
      <button onClick={() => onDelete(userId)}>删除</button>
      <button onClick={() => onShare(userId)}>分享</button>
    </div>
  );
}

// 组合使用
function UserProfile({ user, onEdit, onDelete, onShare }) {
  return (
    <div className="user-profile">
      <UserDisplay user={user} />
      <UserActions 
        userId={user.id} 
        onEdit={onEdit} 
        onDelete={onDelete} 
        onShare={onShare} 
      />
    </div>
  );
}
```

### 🔥 高内聚低耦合原则

**高内聚**：组件内部元素紧密相关，共同完成一个明确的功能。

**低耦合**：组件之间依赖最小化，减少相互影响。

```jsx
// 🔥 高内聚低耦合的组件设计示例

// 表单验证工具函数（高度内聚）
function useFormValidation(validationRules) {
  const [errors, setErrors] = useState({});
  
  const validateField = (name, value) => {
    const rule = validationRules[name];
    if (rule) {
      const error = rule(value);
      setErrors(prev => ({ ...prev, [name]: error }));
      return error;
    }
    return null;
  };
  
  const validateForm = (values) => {
    const newErrors = {};
    Object.keys(values).forEach(key => {
      const error = validateField(key, values[key]);
      if (error) newErrors[key] = error;
    });
    return Object.keys(newErrors).length === 0;
  };
  
  return { errors, validateField, validateForm };
}

// 输入框组件（低耦合）
function TextInput({ 
  name, 
  value, 
  onChange, 
  error, 
  placeholder, 
  type = 'text' 
}) {
  return (
    <div className="form-field">
      <input
        type={type}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className={error ? 'error' : ''}
      />
      {error && <span className="error-message">{error}</span>}
    </div>
  );
}

// 表单组件（组合使用，低耦合）
function LoginForm() {
  const [formData, setFormData] = useState({ email: '', password: '' });
  
  const validationRules = {
    email: (value) => {
      if (!value) return '邮箱不能为空';
      if (!/\S+@\S+\.\S+/.test(value)) return '邮箱格式不正确';
      return null;
    },
    password: (value) => {
      if (!value) return '密码不能为空';
      if (value.length < 6) return '密码至少6位';
      return null;
    }
  };
  
  const { errors, validateField } = useFormValidation(validationRules);
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    validateField(name, value);
  };
  
  return (
    <form>
      <TextInput
        name="email"
        value={formData.email}
        onChange={handleChange}
        error={errors.email}
        placeholder="请输入邮箱"
      />
      <TextInput
        name="password"
        type="password"
        value={formData.password}
        onChange={handleChange}
        error={errors.password}
        placeholder="请输入密码"
      />
    </form>
  );
}
```

### 🎯 关注点分离（SoC）

关注点分离是将不同功能或关注点分配到不同的组件或模块中。

```jsx
// 🔥 关注点分离的组件设计

// 数据获取关注点
function useUserData(userId) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await fetch(`/api/users/${userId}`);
        const userData = await response.json();
        setUser(userData);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchUser();
  }, [userId]);
  
  return { user, loading, error };
}

// UI显示关注点
function UserCard({ user, loading, error }) {
  if (loading) return <div>加载中...</div>;
  if (error) return <div>错误：{error}</div>;
  if (!user) return <div>用户不存在</div>;
  
  return (
    <div className="user-card">
      <img src={user.avatar} alt={user.name} />
      <h3>{user.name}</h3>
      <p>{user.email}</p>
    </div>
  );
}

// 业务逻辑关注点
function UserProfile({ userId, isEditable }) {
  const { user, loading, error } = useUserData(userId);
  
  return (
    <div className="user-profile">
      <UserCard user={user} loading={loading} error={error} />
      {isEditable && (
        <div className="user-actions">
          <button>编辑资料</button>
          <button>更改头像</button>
        </div>
      )}
    </div>
  );
}
```

## 🚀 3.2 可复用组件设计

### 🆕 组件接口设计原则

**优秀的组件接口应该具备**：
- **直观性**：属性名和类型一目了然
- **一致性**：相似的组件有相似的接口
- **灵活性**：支持多种使用场景
- **可扩展性**：易于添加新功能

### 💡 Props接口设计最佳实践

```jsx
import PropTypes from 'prop-types';

// 🎯 完整的组件接口设计示例
function Button({
  // 基础属性
  children,
  type = 'button',
  disabled = false,
  
  // 样式变体
  variant = 'primary', // 'primary' | 'secondary' | 'danger'
  size = 'medium',     // 'small' | 'medium' | 'large'
  
  // 交互行为
  onClick,
  href,
  target,
  
  // 布局控制
  fullWidth = false,
  loading = false,
  
  // 图标支持
  icon,
  iconPosition = 'left', // 'left' | 'right'
  
  // 自定义样式
  className = '',
  style = {},
  
  // 无障碍访问
  ariaLabel,
  ...rest
}) {
  // 确定组件类型（按钮或链接）
  const isLink = !!href;
  const Component = isLink ? 'a' : 'button';
  
  // 构建CSS类名
  const classNames = [
    'button',
    `button--${variant}`,
    `button--${size}`,
    fullWidth && 'button--full-width',
    loading && 'button--loading',
    disabled && 'button--disabled',
    className
  ].filter(Boolean).join(' ');
  
  // 构建Props
  const componentProps = {
    className: classNames,
    style,
    disabled: disabled || loading,
    'aria-label': ariaLabel,
    ...(isLink ? { href, target } : { type }),
    ...rest
  };
  
  // 渲染内容
  const content = (
    <>
      {icon && iconPosition === 'left' && (
        <span className="button__icon button__icon--left">{icon}</span>
      )}
      <span className="button__text">{children}</span>
      {icon && iconPosition === 'right' && (
        <span className="button__icon button__icon--right">{icon}</span>
      )}
      {loading && <span className="button__spinner">加载中...</span>}
    </>
  );
  
  return (
    <Component {...componentProps}>
      {content}
    </Component>
  );
}

// 🔥 TypeScript类型定义（推荐）
Button.propTypes = {
  children: PropTypes.node.isRequired,
  type: PropTypes.oneOf(['button', 'submit', 'reset']),
  disabled: PropTypes.bool,
  variant: PropTypes.oneOf(['primary', 'secondary', 'danger']),
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  onClick: PropTypes.func,
  href: PropTypes.string,
  target: PropTypes.string,
  fullWidth: PropTypes.bool,
  loading: PropTypes.bool,
  icon: PropTypes.node,
  iconPosition: PropTypes.oneOf(['left', 'right']),
  className: PropTypes.string,
  style: PropTypes.object,
  ariaLabel: PropTypes.string
};

Button.defaultProps = {
  type: 'button',
  disabled: false,
  variant: 'primary',
  size: 'medium',
  fullWidth: false,
  loading: false,
  iconPosition: 'left',
  className: '',
  style: {}
};

// 🎯 使用示例
function App() {
  return (
    <div>
      {/* 基础按钮 */}
      <Button onClick={() => console.log('点击了')}>
        普通按钮
      </Button>
      
      {/* 链接按钮 */}
      <Button href="/about" variant="secondary">
        关于我们
      </Button>
      
      {/* 带图标按钮 */}
      <Button 
        icon={<span>🔔</span>} 
        variant="danger" 
        size="small"
      >
        警告按钮
      </Button>
      
      {/* 加载状态 */}
      <Button loading={true} disabled={true}>
        提交中...
      </Button>
      
      {/* 全宽按钮 */}
      <Button fullWidth={true}>
        全宽按钮
      </Button>
    </div>
  );
}
```

### 🔥 条件渲染模式

```jsx
// 🔥 高级条件渲染模式

// 1. 条件包装器组件
function ConditionalWrapper({ condition, wrapper, children }) {
  return condition ? wrapper(children) : children;
}

// 2. 空状态组件
function EmptyState({ 
  isEmpty, 
  emptyMessage = "暂无数据", 
  children 
}) {
  if (isEmpty) {
    return (
      <div className="empty-state">
        <p>{emptyMessage}</p>
      </div>
    );
  }
  return children;
}

// 3. 加载状态组件
function LoadingWrapper({ isLoading, loadingText = "加载中...", children }) {
  if (isLoading) {
    return (
      <div className="loading-wrapper">
        <div className="spinner"></div>
        <span>{loadingText}</span>
      </div>
    );
  }
  return children;
}

// 4. 错误边界组件
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  
  componentDidCatch(error, errorInfo) {
    console.error('组件错误:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>出了点问题</h2>
          <details>
            {this.state.error && this.state.error.toString()}
          </details>
          <button onClick={() => this.setState({ hasError: false })}>
            重试
          </button>
        </div>
      );
    }
    
    return this.props.children;
  }
}

// 🔥 综合使用示例
function DataDisplay({ data, loading, error }) {
  return (
    <ErrorBoundary>
      <LoadingWrapper isLoading={loading}>
        <EmptyState isEmpty={!data || data.length === 0}>
          <ConditionalWrapper
            condition={data && data.length > 10}
            wrapper={children => (
              <div className="scroll-container">
                {children}
              </div>
            )}
          >
            <ul className="data-list">
              {data?.map(item => (
                <li key={item.id}>{item.name}</li>
              ))}
            </ul>
          </ConditionalWrapper>
        </EmptyState>
      </LoadingWrapper>
    </ErrorBoundary>
  );
}
```

## 🚀 3.3 组件组合模式

### 🆕 容器组件与展示组件模式

**容器组件**：负责数据获取和状态管理
**展示组件**：负责UI渲染和用户交互

```jsx
// 🔥 容器组件（逻辑处理）
function UserListContainer() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await fetch('/api/users');
        const userData = await response.json();
        setUsers(userData);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchUsers();
  }, []);
  
  // 过滤用户
  const filteredUsers = users.filter(user =>
    user.name.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  // 处理用户删除
  const handleDeleteUser = async (userId) => {
    try {
      await fetch(`/api/users/${userId}`, { method: 'DELETE' });
      setUsers(prev => prev.filter(user => user.id !== userId));
    } catch (err) {
      setError('删除失败');
    }
  };
  
  return (
    <UserList
      users={filteredUsers}
      loading={loading}
      error={error}
      searchTerm={searchTerm}
      onSearchChange={setSearchTerm}
      onDeleteUser={handleDeleteUser}
    />
  );
}

// 🔥 展示组件（UI渲染）
function UserList({
  users,
  loading,
  error,
  searchTerm,
  onSearchChange,
  onDeleteUser
}) {
  if (loading) return <div>加载中...</div>;
  if (error) return <div>错误：{error}</div>;
  
  return (
    <div className="user-list">
      <div className="search-bar">
        <input
          type="text"
          placeholder="搜索用户..."
          value={searchTerm}
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>
      
      <div className="user-grid">
        {users.map(user => (
          <UserCard
            key={user.id}
            user={user}
            onDelete={() => onDeleteUser(user.id)}
          />
        ))}
      </div>
      
      {users.length === 0 && (
        <div className="empty-state">没有找到用户</div>
      )}
    </div>
  );
}

// 用户卡片组件
function UserCard({ user, onDelete }) {
  return (
    <div className="user-card">
      <img src={user.avatar} alt={user.name} />
      <h3>{user.name}</h3>
      <p>{user.email}</p>
      <button onClick={onDelete}>删除</button>
    </div>
  );
}
```

### 🔥 高阶组件（HOC）模式

```jsx
// 🔥 高阶组件示例：withLoading
function withLoading(WrappedComponent) {
  return function WithLoadingComponent(props) {
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState(null);
    
    useEffect(() => {
      // 模拟数据加载
      const timer = setTimeout(() => {
        setData(props.initialData || '默认数据');
        setLoading(false);
      }, 1000);
      
      return () => clearTimeout(timer);
    }, []);
    
    if (loading) {
      return (
        <div className="loading-container">
          <div className="spinner"></div>
          <span>加载中...</span>
        </div>
      );
    }
    
    return <WrappedComponent {...props} data={data} />;
  };
}

// 🔥 高阶组件示例：withAuthentication
function withAuthentication(WrappedComponent) {
  return function WithAuthenticationComponent(props) {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [user, setUser] = useState(null);
    
    useEffect(() => {
      // 检查用户认证状态
      const checkAuth = async () => {
        try {
          const token = localStorage.getItem('authToken');
          if (token) {
            const response = await fetch('/api/verify-token', {
              headers: { Authorization: `Bearer ${token}` }
            });
            if (response.ok) {
              const userData = await response.json();
              setUser(userData);
              setIsAuthenticated(true);
            }
          }
        } catch (error) {
          console.error('认证检查失败:', error);
        }
      };
      
      checkAuth();
    }, []);
    
    if (!isAuthenticated) {
      return (
        <div className="auth-required">
          <h2>请先登录</h2>
          <button onClick={() => window.location.href = '/login'}>
            前往登录
          </button>
        </div>
      );
    }
    
    return <WrappedComponent {...props} user={user} />;
  };
}

// 🔥 高阶组件示例：withErrorBoundary
function withErrorBoundary(WrappedComponent, FallbackComponent) {
  return class ErrorBoundaryHOC extends React.Component {
    constructor(props) {
      super(props);
      this.state = { hasError: false, error: null };
    }
    
    static getDerivedStateFromError(error) {
      return { hasError: true, error };
    }
    
    componentDidCatch(error, errorInfo) {
      console.error('组件错误:', error, errorInfo);
    }
    
    render() {
      if (this.state.hasError) {
        return FallbackComponent ? (
          <FallbackComponent error={this.state.error} />
        ) : (
          <div>组件渲染出错</div>
        );
      }
      
      return <WrappedComponent {...this.props} />;
    }
  };
}

// 🔥 高阶组件组合使用
const EnhancedComponent = withLoading(
  withAuthentication(
    withErrorBoundary(UserProfile, ErrorFallback)
  )
);

// 使用装饰器语法（需要Babel插件）
// @withLoading
// @withAuthentication  
// @withErrorBoundary(ErrorFallback)
// class UserProfile extends React.Component {
//   // ...
// }
```

### 🔥 渲染属性（Render Props）模式

```jsx
// 🔥 渲染属性组件：DataFetcher
function DataFetcher({ url, children }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`HTTP错误! 状态码: ${response.status}`);
        }
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [url]);
  
  return children({ data, loading, error });
}

// 🔥 渲染属性组件：FormState
function FormState({ initialValues = {}, children }) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  
  const handleChange = (name, value) => {
    setValues(prev => ({ ...prev, [name]: value }));
    
    // 清除对应字段的错误
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };
  
  const handleBlur = (name) => {
    setTouched(prev => ({ ...prev, [name]: true }));
  };
  
  const setFieldValue = (name, value) => {
    setValues(prev => ({ ...prev, [name]: value }));
  };
  
  const setFieldError = (name, error) => {
    setErrors(prev => ({ ...prev, [name]: error }));
  };
  
  const resetForm = () => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
  };
  
  return children({
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    setFieldValue,
    setFieldError,
    resetForm,
    isValid: Object.keys(errors).length === 0
  });
}

// 🔥 渲染属性使用示例
function UserProfile() {
  return (
    <DataFetcher url="/api/user/123">
      {({ data: user, loading, error }) => (
        <FormState initialValues={user || {}}>
          {({ values, errors, handleChange, handleBlur, isValid }) => (
            <div>
              {loading && <div>加载中...</div>}
              {error && <div>错误：{error}</div>}
              
              {!loading && !error && (
                <form>
                  <input
                    name="name"
                    value={values.name || ''}
                    onChange={(e) => handleChange('name', e.target.value)}
                    onBlur={() => handleBlur('name')}
                    placeholder="姓名"
                  />
                  
                  <input
                    name="email"
                    value={values.email || ''}
                    onChange={(e) => handleChange('email', e.target.value)}
                    onBlur={() => handleBlur('email')}
                    placeholder="邮箱"
                  />
                  
                  <button type="submit" disabled={!isValid}>
                    保存
                  </button>
                </form>
              )}
            </div>
          )}
        </FormState>
      )}
    </DataFetcher>
  );
}
```

## 🚀 3.4 组件通信策略

### 🆕 组件通信方式对比

| 通信方式 | 适用场景 | 优点 | 缺点 |
|---------|---------|------|------|
| **Props传递** | 父子组件直接通信 | 简单直观，类型安全 | 深层嵌套时繁琐 |
| **Context API** | 跨组件层级共享数据 | 避免props层层传递 | 可能引起不必要的重渲染 |
| **事件总线** | 任意组件间通信 | 解耦组件关系 | 难以追踪数据流 |
| **状态管理库** | 复杂应用状态管理 | 可预测的状态管理 | 学习成本较高 |

### 💡 Props传递通信

```jsx
// 🔥 深层Props传递问题解决方案

// 1. 组件组合（Composition）
function App() {
  return (
    <Page>
      <Header>
        <Navigation>
          <UserMenu user={user} />
        </Navigation>
      </Header>
      <MainContent>
        <Sidebar>
          <UserProfile user={user} />
        </Sidebar>
        <Article>
          <Comments user={user} />
        </Article>
      </MainContent>
    </Page>
  );
}

// 2. 渲染属性模式
function UserProvider({ children }) {
  const [user, setUser] = useState(null);
  
  return children(user, setUser);
}

function App() {
  return (
    <UserProvider>
      {(user, setUser) => (
        <Page>
          <Header user={user} />
          <MainContent user={user} />
        </Page>
      )}
    </UserProvider>
  );
}

// 3. 使用children prop的特殊模式
function Layout({ header, sidebar, content }) {
  return (
    <div className="layout">
      <div className="header">{header}</div>
      <div className="sidebar">{sidebar}</div>
      <div className="content">{content}</div>
    </div>
  );
}

function App() {
  const user = { name: '张三', avatar: 'avatar.jpg' };
  
  return (
    <Layout
      header={<UserMenu user={user} />}
      sidebar={<UserProfile user={user} />}
      content={<Article user={user} />}
    />
  );
}
```

### 🔥 Context API高级用法

```jsx
// 🔥 性能优化的Context设计

// 1. 拆分Context避免不必要重渲染
const UserContext = React.createContext();
const UserActionsContext = React.createContext();

function UserProvider({ children }) {
  const [user, setUser] = useState(null);
  
  // 使用useMemo缓存动作函数
  const actions = useMemo(() => ({
    login: async (credentials) => {
      // 登录逻辑
      const userData = await loginUser(credentials);
      setUser(userData);
    },
    logout: () => {
      setUser(null);
    },
    updateProfile: (updates) => {
      setUser(prev => ({ ...prev, ...updates }));
    }
  }), []);
  
  return (
    <UserContext.Provider value={user}>
      <UserActionsContext.Provider value={actions}>
        {children}
      </UserActionsContext.Provider>
    </UserContext.Provider>
  );
}

// 2. 自定义Hook简化使用
function useUser() {
  const user = useContext(UserContext);
  if (user === undefined) {
    throw new Error('useUser必须在UserProvider内使用');
  }
  return user;
}

function useUserActions() {
  const actions = useContext(UserActionsContext);
  if (actions === undefined) {
    throw new Error('useUserActions必须在UserProvider内使用');
  }
  return actions;
}

// 3. 选择性订阅Context变化
function UserProfile() {
  // 只订阅user.name的变化
  const user = useUser();
  const userName = useMemo(() => user?.name, [user?.name]);
  
  return <div>{userName}</div>;
}

// 4. 使用useContextSelector（第三方库或自定义）
function useContextSelector(context, selector) {
  const value = useContext(context);
  return useMemo(() => selector(value), [value, selector]);
}

function UserAvatar() {
  // 只当user.avatar变化时重新渲染
  const avatar = useContextSelector(UserContext, user => user?.avatar);
  return <img src={avatar} alt="头像" />;
}
```

## 🚀 3.5 组件设计模式实践

### 🆕 工厂模式组件

```jsx
// 🔥 组件工厂模式
function createButtonFactory() {
  const variants = {
    primary: 'button--primary',
    secondary: 'button--secondary',
    danger: 'button--danger'
  };
  
  const sizes = {
    small: 'button--small',
    medium: 'button--medium',
    large: 'button--large'
  };
  
  return function createButton(config = {}) {
    const {
      variant = 'primary',
      size = 'medium',
      disabled = false,
      loading = false
    } = config;
    
    return function Button({ children, ...props }) {
      const classNames = [
        'button',
        variants[variant],
        sizes[size],
        disabled && 'button--disabled',
        loading && 'button--loading'
      ].filter(Boolean).join(' ');
      
      return (
        <button className={classNames} disabled={disabled} {...props}>
          {loading && <span className="button__spinner"></span>}
          {children}
        </button>
      );
    };
  };
}

// 🔥 使用工厂创建组件
const buttonFactory = createButtonFactory();

// 创建特定类型的按钮
const PrimaryButton = buttonFactory({ variant: 'primary', size: 'medium' });
const DangerButton = buttonFactory({ variant: 'danger', size: 'small' });
const LargeSecondaryButton = buttonFactory({ 
  variant: 'secondary', 
  size: 'large' 
});

// 使用示例
function App() {
  return (
    <div>
      <PrimaryButton>主要按钮</PrimaryButton>
      <DangerButton>危险按钮</DangerButton>
      <LargeSecondaryButton>大型次要按钮</LargeSecondaryButton>
    </div>
  );
}
```

### 🔥 观察者模式组件

```jsx
// 🔥 观察者模式实现事件总线
class EventBus {
  constructor() {
    this.events = {};
  }
  
  subscribe(event, callback) {
    if (!this.events[event]) {
      this.events[event] = [];
    }
    this.events[event].push(callback);
    
    // 返回取消订阅函数
    return () => {
      this.events[event] = this.events[event].filter(cb => cb !== callback);
    };
  }
  
  publish(event, data) {
    if (this.events[event]) {
      this.events[event].forEach(callback => callback(data));
    }
  }
  
  unsubscribe(event, callback) {
    if (this.events[event]) {
      this.events[event] = this.events[event].filter(cb => cb !== callback);
    }
  }
}

// 创建全局事件总线
const globalEventBus = new EventBus();

// 🔥 使用事件总线的组件
function NotificationSystem() {
  const [notifications, setNotifications] = useState([]);
  
  useEffect(() => {
    // 订阅通知事件
    const unsubscribe = globalEventBus.subscribe('NOTIFICATION', (data) => {
      setNotifications(prev => [...prev, {
        id: Date.now(),
        message: data.message,
        type: data.type || 'info'
      }]);
    });
    
    return unsubscribe;
  }, []);
  
  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(notif => notif.id !== id));
  };
  
  return (
    <div className="notification-system">
      {notifications.map(notif => (
        <div key={notif.id} className={`notification notification--${notif.type}`}>
          <span>{notif.message}</span>
          <button onClick={() => removeNotification(notif.id)}>×</button>
        </div>
      ))}
    </div>
  );
}

// 🔥 发布事件的组件
function ProductCard({ product }) {
  const handleAddToCart = () => {
    // 发布添加到购物车事件
    globalEventBus.publish('NOTIFICATION', {
      message: `已添加 ${product.name} 到购物车`,
      type: 'success'
    });
    
    // 其他业务逻辑...
  };
  
  return (
    <div className="product-card">
      <h3>{product.name}</h3>
      <p>${product.price}</p>
      <button onClick={handleAddToCart}>加入购物车</button>
    </div>
  );
}
```

### 🎯 复合模式组件

```jsx
// 🔥 复合组件模式：Accordion
const AccordionContext = React.createContext();

function Accordion({ children, defaultOpen = [] }) {
  const [openItems, setOpenItems] = useState(new Set(defaultOpen));
  
  const toggleItem = (itemId) => {
    setOpenItems(prev => {
      const newOpenItems = new Set(prev);
      if (newOpenItems.has(itemId)) {
        newOpenItems.delete(itemId);
      } else {
        newOpenItems.add(itemId);
      }
      return newOpenItems;
    });
  };
  
  const isItemOpen = (itemId) => openItems.has(itemId);
  
  const value = {
    openItems,
    toggleItem,
    isItemOpen
  };
  
  return (
    <AccordionContext.Provider value={value}>
      <div className="accordion">{children}</div>
    </AccordionContext.Provider>
  );
}

function AccordionItem({ children, id }) {
  const { isItemOpen, toggleItem } = useContext(AccordionContext);
  const isOpen = isItemOpen(id);
  
  return (
    <div className="accordion-item">
      {React.Children.map(children, child =>
        React.cloneElement(child, { isOpen, toggle: () => toggleItem(id) })
      )}
    </div>
  );
}

function AccordionHeader({ children, isOpen, toggle }) {
  return (
    <button 
      className={`accordion-header ${isOpen ? 'open' : ''}`}
      onClick={toggle}
    >
      {children}
      <span className="accordion-icon">{isOpen ? '−' : '+'}</span>
    </button>
  );
}

function AccordionContent({ children, isOpen }) {
  return (
    <div 
      className={`accordion-content ${isOpen ? 'open' : ''}`}
      style={{ 
        maxHeight: isOpen ? '1000px' : '0px',
        overflow: 'hidden',
        transition: 'max-height 0.3s ease'
      }}
    >
      {children}
    </div>
  );
}

// 🔥 使用复合组件
function FAQSection() {
  return (
    <Accordion defaultOpen={['q1']}>
      <AccordionItem id="q1">
        <AccordionHeader>
          问题1：React是什么？
        </AccordionHeader>
        <AccordionContent>
          React是一个用于构建用户界面的JavaScript库。
        </AccordionContent>
      </AccordionItem>
      
      <AccordionItem id="q2">
        <AccordionHeader>
          问题2：什么是组件？
        </AccordionHeader>
        <AccordionContent>
          组件是React应用的基本构建块。
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}

// 🔥 支持灵活的组合
Accordion.Item = AccordionItem;
Accordion.Header = AccordionHeader;
Accordion.Content = AccordionContent;

// 更简洁的使用方式
function FAQSection2() {
  return (
    <Accordion>
      <Accordion.Item id="q1">
        <Accordion.Header>问题1</Accordion.Header>
        <Accordion.Content>答案1</Accordion.Content>
      </Accordion.Item>
    </Accordion>
  );
}
```

## 🎯 3.6 练习与实践

### 💪 练习1：设计一个完整的表单组件系统

**需求**：创建一个可复用的表单组件系统，包含：
- 输入框、下拉框、单选框、复选框
- 表单验证和错误提示
- 表单提交和重置功能
- 支持自定义验证规则

```jsx
function FormSystem() {
  // 在这里实现你的代码
  return (
    <form>
      {/* 实现各种表单组件 */}
    </form>
  );
}
```

### 💪 练习2：实现一个模态框组件库

**需求**：创建一个功能完整的模态框组件库，包含：
- 基础模态框组件
- 确认对话框
- 表单模态框
- 全屏模态框
- 动画效果支持

```jsx
function ModalLibrary() {
  // 在这里实现你的代码
  return (
    <div>
      {/* 实现各种模态框组件 */}
    </div>
  );
}
```

### 💪 练习3：创建一个可配置的数据表格组件

**需求**：设计一个高度可配置的数据表格组件，包含：
- 列配置和自定义渲染
- 排序和过滤功能
- 分页和加载更多
- 行选择和批量操作

```jsx
function DataTable({ data, columns, pagination, sorting }) {
  // 在这里实现你的代码
  return (
    <table>
      {/* 实现数据表格功能 */}
    </table>
  );
}
```

## 📚 3.7 本章小结

### 🎓 本章重点回顾

1. **组件设计原则**：掌握了单一职责、高内聚低耦合、关注点分离
2. **可复用组件设计**：学会了接口设计、Props类型定义、条件渲染模式
3. **组件组合模式**：理解了容器组件、高阶组件、渲染属性模式
4. **组件通信策略**：掌握了Props传递、Context API、事件总线等通信方式
5. **组件设计模式**：实践了工厂模式、观察者模式、复合模式等设计模式

### 🔑 关键知识点

- **组件拆分原则**：按功能拆分，保持单一职责
- **接口设计**：提供直观、一致、灵活的API
- **组合优于继承**：使用组合模式构建复杂组件
- **性能优化**：合理使用Context，避免不必要的重渲染

### 🚀 下一步学习建议

在下一章中，我们将深入学习：
- React状态管理的各种方案
- Context API的高级用法
- 第三方状态管理库的使用
- 状态管理的最佳实践

### 💡 实战建议

1. **多实践**：通过实际项目练习组件设计
2. **代码审查**：学习优秀开源项目的组件设计
3. **设计系统**：尝试构建自己的组件库
4. **性能意识**：在组件设计时考虑性能影响

## 🔗 延伸资源

### 📖 推荐阅读

- [React官方设计原则](https://reactjs.org/docs/design-principles.html)
- [组件驱动开发](https://www.componentdriven.org/)
- [Storybook文档](https://storybook.js.org/docs/)
- [Atomic Design方法论](https://atomicdesign.bradfrost.com/)

### 🛠️ 工具推荐

- [Storybook](https://storybook.js.org/) - 组件开发环境
- [Chromatic](https://www.chromatic.com/) - 组件可视化测试
- [Figma](https://www.figma.com/) - 设计系统工具
- [Styleguidist](https://react-styleguidist.js.org/) - 组件文档生成

### 💬 社区支持

- [React官方社区](https://react.dev/community)
- [Design Systems社区](https://www.designsystems.com/)
- [Component Kitchen](https://component.kitchen/)

---

**恭喜你完成了第三章的学习！** 🎉

你已经掌握了React组件设计的核心原则和最佳实践，为构建可维护的组件系统打下了坚实基础。继续实践和探索，你将成长为优秀的React开发者！

**下一章预告**：在第四章中，我们将深入学习React状态管理的各种方案和最佳实践。

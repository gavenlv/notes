import { useState, useRef, useEffect, useContext, createContext, forwardRef, useImperativeHandle, lazy, Suspense } from 'react'
import './App.css'

// 1. Error Boundaries 错误边界组件
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    // 更新状态，下次渲染时显示降级UI
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // 可以在这里记录错误信息
    console.error('Error caught by ErrorBoundary:', error, errorInfo);
  }

  resetError = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      // 自定义降级UI
      return (
        <div className="error-boundary">
          <h3>出错了！</h3>
          <p>{this.state.error?.toString()}</p>
          <button onClick={this.resetError}>重试</button>
        </div>
      );
    }

    return this.props.children;
  }
}

// 会抛出错误的组件
const BuggyComponent = ({ triggerError }) => {
  if (triggerError) {
    throw new Error('这是一个测试错误！');
  }
  return <div className="buggy-component">这是一个正常工作的组件</div>;
};

// 2. 自定义 Portal 组件
const PortalComponent = ({ children }) => {
  const [portalContainer, setPortalContainer] = useState(null);

  useEffect(() => {
    // 创建一个新的DOM元素
    const div = document.createElement('div');
    div.id = 'portal-container';
    div.className = 'portal-overlay';
    document.body.appendChild(div);
    setPortalContainer(div);

    // 清理函数
    return () => {
      document.body.removeChild(div);
    };
  }, []);

  if (!portalContainer) return null;

  return ReactDOM.createPortal(
    <div className="portal-content">{children}</div>,
    portalContainer
  );
};

// 3. forwardRef 和 useImperativeHandle 示例
const FancyInput = forwardRef((props, ref) => {
  const inputRef = useRef();
  const [value, setValue] = useState('');

  // 只暴露特定的方法给父组件
  useImperativeHandle(ref, () => ({
    focus: () => {
      inputRef.current.focus();
    },
    clear: () => {
      setValue('');
      inputRef.current.focus();
    }
  }));

  return (
    <div className="fancy-input">
      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="请输入内容..."
      />
      <p>输入的内容: {value}</p>
    </div>
  );
});

// 4. Context API 高级用法
const ThemeContext = createContext();
const UserContext = createContext();

// Context Provider 组件
const ContextProvider = ({ children }) => {
  const [theme, setTheme] = useState('dark');
  const [user, setUser] = useState({ name: '张三', role: '管理员' });

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  const updateUser = (newUser) => {
    setUser(prev => ({ ...prev, ...newUser }));
  };

  const themeValue = {
    theme,
    toggleTheme,
    isDark: theme === 'dark'
  };

  const userValue = {
    user,
    updateUser
  };

  return (
    <ThemeContext.Provider value={themeValue}>
      <UserContext.Provider value={userValue}>
        {children}
      </UserContext.Provider>
    </ThemeContext.Provider>
  );
};

// 使用 Context 的组件
const ThemeAwareComponent = () => {
  const { theme, toggleTheme } = useContext(ThemeContext);
  const { user } = useContext(UserContext);

  return (
    <div className={`theme-aware theme-${theme}`}>
      <h3>当前主题: {theme}</h3>
      <p>欢迎回来, {user.name} ({user.role})</p>
      <button onClick={toggleTheme}>切换主题</button>
    </div>
  );
};

// 5. Suspense 和 lazy loading 示例
const LazyLoadedComponent = lazy(() => {
  // 模拟网络延迟
  return new Promise(resolve => {
    setTimeout(() => {
      resolve(import('./LazyLoadedComponent.jsx'));
    }, 1500);
  });
});

// 主应用组件
function App() {
  const [triggerError, setTriggerError] = useState(false);
  const [showPortal, setShowPortal] = useState(false);
  const fancyInputRef = useRef();
  const [showLazyComponent, setShowLazyComponent] = useState(false);

  // 触发 Portal 显示
  const togglePortal = () => setShowPortal(!showPortal);

  // 调用子组件暴露的方法
  const handleFocusInput = () => {
    if (fancyInputRef.current) {
      fancyInputRef.current.focus();
    }
  };

  const handleClearInput = () => {
    if (fancyInputRef.current) {
      fancyInputRef.current.clear();
    }
  };

  return (
    <ContextProvider>
      <div className="advanced-demo">
        <h1>React 高级特性示例</h1>

        {/* 1. Error Boundaries 示例 */}
        <section className="feature-section">
          <h2>1. Error Boundaries 错误边界</h2>
          <div className="feature-demo">
            <button onClick={() => setTriggerError(!triggerError)}>
              {triggerError ? '重置错误' : '触发错误'}
            </button>
            <ErrorBoundary>
              <BuggyComponent triggerError={triggerError} />
            </ErrorBoundary>
          </div>
          <div className="code-block">
            <pre>{`class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <div>出错了！</div>;
    }
    return this.props.children;
  }
}`}</pre>
          </div>
          <div className="explanation">
            Error Boundaries 用于捕获子组件树中的 JavaScript 错误，记录错误信息，并显示降级 UI。
            它不能捕获事件处理器、异步代码或服务器端渲染中的错误。
          </div>
        </section>

        {/* 2. Portals 示例 */}
        <section className="feature-section">
          <h2>2. Portals 门户</h2>
          <div className="feature-demo">
            <button onClick={togglePortal}>
              {showPortal ? '关闭 Portal' : '显示 Portal'}
            </button>
            {showPortal && (
              <PortalComponent>
                <div className="portal-modal">
                  <h3>这是一个通过 Portal 渲染的模态框</h3>
                  <p>内容被渲染到 DOM 的不同部分，但在 React 树中仍属于父组件。</p>
                  <button onClick={togglePortal}>关闭</button>
                </div>
              </PortalComponent>
            )}
          </div>
          <div className="code-block">
            <pre>{`const PortalComponent = ({ children }) => {
  return ReactDOM.createPortal(
    <div>{children}</div>,
    document.getElementById('portal-container')
  );
}`}</pre>
          </div>
          <div className="explanation">
            Portals 提供了一种将子节点渲染到父组件 DOM 层次结构之外的 DOM 节点的方法。
            常用于模态框、对话框、提示框等需要突破父组件样式限制的场景。
          </div>
        </section>

        {/* 3. Refs 和 forwardRef 示例 */}
        <section className="feature-section">
          <h2>3. Refs 和 forwardRef</h2>
          <div className="feature-demo">
            <FancyInput ref={fancyInputRef} />
            <div className="ref-controls">
              <button onClick={handleFocusInput}>聚焦输入框</button>
              <button onClick={handleClearInput}>清空输入框</button>
            </div>
          </div>
          <div className="code-block">
            <pre>{`const FancyInput = forwardRef((props, ref) => {
  const inputRef = useRef();
  
  useImperativeHandle(ref, () => ({
    focus: () => {
      inputRef.current.focus();
    },
    clear: () => {
      // 清空逻辑
    }
  }));
  
  return <input ref={inputRef} />;
});`}</pre>
          </div>
          <div className="explanation">
            forwardRef 用于将 ref 自动地通过组件传递到其一子组件上。
            useImperativeHandle 可以自定义暴露给父组件的实例值，避免暴露整个 DOM 节点。
          </div>
        </section>

        {/* 4. Context API 高级用法 */}
        <section className="feature-section">
          <h2>4. Context API 高级用法</h2>
          <div className="feature-demo">
            <ThemeAwareComponent />
          </div>
          <div className="code-block">
            <pre>{`// 创建 Context
const ThemeContext = createContext();

// Provider 组件
const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState('dark');
  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

// 消费组件
const ThemeAwareComponent = () => {
  const { theme, toggleTheme } = useContext(ThemeContext);
  return <div>当前主题: {theme}</div>;
};`}</pre>
          </div>
          <div className="explanation">
            Context API 提供了一种在组件树中共享值的方式，无需显式地通过 props 逐层传递。
            高级用法包括嵌套 Context、动态 Context 值和性能优化。
          </div>
        </section>

        {/* 5. Suspense 和 lazy loading 示例 */}
        <section className="feature-section">
          <h2>5. Suspense 和 Lazy Loading</h2>
          <div className="feature-demo">
            <button onClick={() => setShowLazyComponent(!showLazyComponent)}>
              {showLazyComponent ? '隐藏懒加载组件' : '加载组件'}
            </button>
            {showLazyComponent && (
              <Suspense fallback={<div className="loading">加载中...</div>}>
                <LazyLoadedComponent />
              </Suspense>
            )}
          </div>
          <div className="code-block">
            <pre>{`// 懒加载组件
const LazyLoadedComponent = lazy(() => import('./LazyLoadedComponent'));

// 使用 Suspense
<Suspense fallback={<div>加载中...</div>}>
  <LazyLoadedComponent />
</Suspense>`}</pre>
          </div>
          <div className="explanation">
            React.lazy 用于动态导入组件，实现代码分割。
            Suspense 用于在组件加载过程中显示加载状态。
            这两个特性结合使用可以显著减少初始加载时间。
          </div>
        </section>

        {/* 6. Fragment 和 StrictMode 示例 */}
        <section className="feature-section">
          <h2>6. Fragment 和 StrictMode</h2>
          <div className="feature-demo">
            <div className="fragment-demo">
              <h3>Fragment 示例</h3>
              <FragmentDemo />
            </div>
            <div className="strictmode-info">
              <h3>StrictMode</h3>
              <p>当前应用正在 StrictMode 中运行</p>
              <ul>
                <li>检测不安全的生命周期</li>
                <li>检测遗留的字符串 ref API</li>
                <li>检测意外的副作用</li>
                <li>检测过时的 context API</li>
              </ul>
            </div>
          </div>
          <div className="code-block">
            <pre>{`// Fragment 简写语法
const FragmentDemo = () => (
  <>
    <div>项目 1</div>
    <div>项目 2</div>
  </>
);

// StrictMode 使用
ReactDOM.createRoot(root).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);`}</pre>
          </div>
          <div className="explanation">
            Fragment 允许将子列表分组而无需向 DOM 添加额外节点。
            StrictMode 是一个开发工具，用于突出显示应用程序中的潜在问题。
          </div>
        </section>

        {/* 高级特性总结 */}
        <section className="feature-section">
          <h2>React 高级特性总结</h2>
          <div className="summary-grid">
            <div className="summary-item">
              <h3>Error Boundaries</h3>
              <p>捕获和处理组件树中的 JavaScript 错误</p>
            </div>
            <div className="summary-item">
              <h3>Portals</h3>
              <p>在 DOM 层次结构的不同部分渲染子节点</p>
            </div>
            <div className="summary-item">
              <h3>forwardRef & useImperativeHandle</h3>
              <p>高级 ref 传递和自定义暴露方法</p>
            </div>
            <div className="summary-item">
              <h3>Context API</h3>
              <p>跨组件树共享状态，避免 props drilling</p>
            </div>
            <div className="summary-item">
              <h3>Suspense & Lazy Loading</h3>
              <p>代码分割和加载状态管理</p>
            </div>
            <div className="summary-item">
              <h3>Fragment & StrictMode</h3>
              <p>无额外 DOM 节点的分组和开发模式检查</p>
            </div>
          </div>
        </section>
      </div>
    </ContextProvider>
  )
}

// Fragment 示例组件
const FragmentDemo = () => (
  <>
    <div className="fragment-item">项目 1</div>
    <div className="fragment-item">项目 2</div>
    <div className="fragment-item">项目 3</div>
  </>
);

// 导入 ReactDOM（用于 Portal）
import ReactDOM from 'react-dom';

export default App

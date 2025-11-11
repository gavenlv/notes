import React, { useState, Suspense } from 'react';

// 动态导入一个大型组件（模拟）
const LargeComponent = React.lazy(() => {
  // 模拟加载延迟
  return new Promise(resolve => {
    setTimeout(() => {
      resolve({
        default: function LargeComponent() {
          return (
            <div className="large-component">
              <h4>大型组件（懒加载）</h4>
              <p>这是一个通过 React.lazy 和 Suspense 懒加载的组件。</p>
              <p>代码分割可以减小初始加载体积，提高应用性能。</p>
            </div>
          );
        }
      });
    }, 1000);
  });
});

const CodeSplittingDemo = () => {
  const [showLargeComponent, setShowLargeComponent] = useState(false);

  const handleLoadComponent = () => {
    setShowLargeComponent(true);
  };

  return (
    <div className="demo-container">
      <div className="demo-header">
        <div className="demo-icon">CS</div>
        <div className="demo-info">
          <h3>代码分割与懒加载</h3>
          <p>减小初始加载体积，按需加载组件</p>
        </div>
      </div>

      <div className="info-box">
        <p>代码分割允许我们将代码拆分成多个小块，然后按需加载，从而减少初始加载时间，提高应用性能。</p>
      </div>

      <h4>React.lazy 和 Suspense 示例</h4>
      <div className="code-block">
        <pre>
{`// 1. 动态导入组件
const LazyComponent = React.lazy(() => import('./LazyComponent'))

// 2. 在组件中使用
function App() {
  return (
    <div>
      <Suspense fallback={\u003cdiv\u003eLoading...\u003c/div\u003e}>
        \u003cLazyComponent /\u003e
      </Suspense>
    </div>
  )
}`}</pre>
      </div>

      <h4>路由级别的代码分割</h4>
      <div className="code-block">
        <pre>
{`// 使用 React Router 进行路由级别的代码分割
import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

const Home = lazy(() => import('./pages/Home'))
const About = lazy(() => import('./pages/About'))
const Dashboard = lazy(() => import('./pages/Dashboard'))

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={\u003cdiv\u003eLoading...\u003c/div\u003e}>
        <Routes>
          \u003cRoute path="/" element={\u003cHome /\u003e} />
          \u003cRoute path="/about" element={\u003cAbout /\u003e} />
          \u003cRoute path="/dashboard" element={\u003cDashboard /\u003e} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}`}</pre>
      </div>

      <h4>代码分割演示</h4>
      <button 
        onClick={handleLoadComponent}
        className="demo-button"
        disabled={showLargeComponent}
      >
        {showLargeComponent ? '已加载' : '加载大型组件'}
      </button>

      {showLargeComponent && (
        <Suspense fallback={<div className="loading">加载中...</div>}>
          <LargeComponent />
        </Suspense>
      )}

      <h4>代码分割的好处</h4>
      <ul className="feature-list">
        <li>减小初始加载体积，提高首屏加载速度</li>
        <li>减少不必要的代码下载</li>
        <li>提高用户体验，特别是在移动设备上</li>
        <li>更好的缓存策略和资源利用</li>
      </ul>

      <div className="success-box">
        <p>✅ 查看浏览器网络面板，可以看到懒加载组件的动态加载过程</p>
      </div>
    </div>
  );
};

export default CodeSplittingDemo;
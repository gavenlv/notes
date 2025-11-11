import React, { useState, lazy, Suspense } from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import './App.css';

// 导入工程化示例组件
import LintingDemo from './components/LintingDemo';
import TestingDemo from './components/TestingDemo';
import BuildOptimizationDemo from './components/BuildOptimizationDemo';
import CodeSplittingDemo from './components/CodeSplittingDemo';
import CI_CDDemo from './components/CI_CDDemo';
import PerformanceMonitoringDemo from './components/PerformanceMonitoringDemo';

// 懒加载组件示例
const LazyLoadedComponent = lazy(() => import('./components/LazyLoadedComponent'));

function App() {

  return (
    <div className="engineering-demo">
      <h1>React 工程化最佳实践</h1>
      
      {/* 导航菜单 */}
      <nav className="engineering-nav">
        <Link to="/">概览</Link>
        <Link to="/linting">代码规范</Link>
        <Link to="/testing">单元测试</Link>
        <Link to="/build">构建优化</Link>
        <Link to="/splitting">代码分割</Link>
        <Link to="/ci-cd">CI/CD</Link>
        <Link to="/performance">性能监控</Link>
      </nav>

      {/* 路由配置 */}
      <Routes>
        <Route path="/" element={
          <div className="overview-section">
            <h2>工程化概览</h2>
            <p>工程化是现代前端开发的重要组成部分，涵盖代码规范、测试、构建优化、部署等多个方面。</p>
            
            <div className="engineering-features">
              <div className="feature-card">
                <h3>代码规范</h3>
                <p>使用 ESLint 确保代码质量和一致性，遵循最佳实践。</p>
              </div>
              
              <div className="feature-card">
                <h3>单元测试</h3>
                <p>使用 Vitest 和 Testing Library 编写可靠的测试用例。</p>
              </div>
              
              <div className="feature-card">
                <h3>构建优化</h3>
                <p>通过 Vite 实现快速开发和高效构建，包含代码分割和懒加载。</p>
              </div>
              
              <div className="feature-card">
                <h3>CI/CD</h3>
                <p>自动化持续集成和部署流程，提高开发效率。</p>
              </div>
            </div>
          </div>
        } />
        
        <Route path="/linting" element={<LintingDemo />} />
        <Route path="/testing" element={<TestingDemo />} />
        <Route path="/build" element={<BuildOptimizationDemo />} />
        <Route path="/splitting" element={<CodeSplittingDemo />} />
        <Route path="/ci-cd" element={<CI_CDDemo />} />
        <Route path="/performance" element={<PerformanceMonitoringDemo />} />
        <Route path="/lazy" element={
          <Suspense fallback={<div>加载中...</div>}>
            <LazyLoadedComponent />
          </Suspense>
        } />
      </Routes>
    </div>
  );
}

export default App;
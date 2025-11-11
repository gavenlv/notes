import React, { useState } from 'react';
import PropTypes from 'prop-types';

// 一个简单的计数器组件，用于演示测试
const Counter = ({ initialCount = 0 }) => {
  const [count, setCount] = useState(initialCount);

  const increment = () => setCount(count + 1);
  const decrement = () => setCount(count - 1);
  const reset = () => setCount(0);

  return (
    <div className="counter">
      <p className="count-display">Count: {count}</p>
      <div className="counter-controls">
        <button onClick={decrement} className="demo-button">-</button>
        <button onClick={reset} className="demo-button">Reset</button>
        <button onClick={increment} className="demo-button">+</button>
      </div>
    </div>
  );
};

Counter.propTypes = {
  initialCount: PropTypes.number
};

const TestingDemo = () => {
  return (
    <div className="demo-container">
      <div className="demo-header">
        <div className="demo-icon">VT</div>
        <div className="demo-info">
          <h3>单元测试与 Vitest</h3>
          <p>使用 Vitest 和 Testing Library 确保代码可靠性</p>
        </div>
      </div>

      <div className="info-box">
        <p>单元测试是工程化的重要组成部分，可以提高代码质量，减少回归问题，并使重构更加安全。</p>
      </div>

      <h4>测试配置示例 (Vite)</h4>
      <div className="code-block">
        <pre>{`test: {
  globals: true,
  environment: 'jsdom',
  setupFiles: './src/setupTests.js',
  css: true
}`}</pre>
      </div>

      <h4>测试示例文件</h4>
      <div className="code-block">
        <pre>{`// Counter.test.jsx
import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import Counter from './Counter'

describe('Counter Component', () => {
  it('should render with initial count', () => {
    render(<Counter />)
    const countElement = screen.getByText(/Count:/i)
    expect(countElement).toBeInTheDocument()
  })

  it('should increment count when increment button is clicked', () => {
    render(<Counter />)
    const incrementButton = screen.getByText('+')
    fireEvent.click(incrementButton)
    
    const countText = screen.getByText(/Count: 1/i)
    expect(countText).toBeInTheDocument()
  })

  it('should decrement count when decrement button is clicked', () => {
    render(<Counter initialCount={1} />)
    const decrementButton = screen.getByText('-')
    fireEvent.click(decrementButton)
    
    const countText = screen.getByText(/Count: 0/i)
    expect(countText).toBeInTheDocument()
  })

  it('should reset count when reset button is clicked', () => {
    render(<Counter initialCount={5} />)
    const resetButton = screen.getByText('Reset')
    fireEvent.click(resetButton)
    
    const countText = screen.getByText(/Count: 0/i)
    expect(countText).toBeInTheDocument()
  })
})`}</pre>
      </div>

      <h4>测试覆盖率设置</h4>
      <div className="code-block">
        <pre>{`// 可以在 package.json 中添加测试脚本
{
  "scripts": {
    "test": "vitest",
    "test:coverage": "vitest run --coverage"
  }
}`}</pre>
      </div>

      <h4>计数器组件演示（可测试的组件）</h4>
      <Counter initialCount={5} />

      <div className="success-box">
        <p>✅ 使用 npm test 运行测试，npm run test:coverage 生成覆盖率报告</p>
      </div>
    </div>
  );
};

export default TestingDemo;
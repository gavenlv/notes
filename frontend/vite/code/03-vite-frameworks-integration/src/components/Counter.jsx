import React from 'react'

/**
 * 计数器组件
 * 演示React组件的状态管理和事件处理
 */
export const Counter = ({ count, onCountChange }) => {
  // 增加计数
  const handleIncrement = () => {
    onCountChange(count + 1)
  }

  // 减少计数
  const handleDecrement = () => {
    if (count > 0) {
      onCountChange(count - 1)
    }
  }

  // 重置计数
  const handleReset = () => {
    onCountChange(0)
  }

  // 增加5
  const handleAddFive = () => {
    onCountChange(count + 5)
  }

  // 减少5
  const handleSubtractFive = () => {
    onCountChange(Math.max(0, count - 5))
  }

  // 根据计数确定颜色
  const getCountColor = () => {
    if (count === 0) return 'inherit'
    return count > 0 ? 'var(--success-color)' : 'var(--error-color)'
  }

  return (
    <div className="counter-container">
      <div className="counter-display">
        <span className="counter-label">当前计数:</span>
        <span 
          className="counter-value"
          style={{ color: getCountColor() }}
        >
          {count}
        </span>
      </div>
      
      <div className="counter-controls">
        <div className="control-group">
          <button 
            onClick={handleDecrement}
            disabled={count === 0}
            aria-label="减少"
          >
            -
          </button>
          <button onClick={handleIncrement} aria-label="增加">
            +
          </button>
        </div>
        
        <div className="control-group">
          <button 
            onClick={handleSubtractFive}
            disabled={count < 5}
            aria-label="减少5"
          >
            -5
          </button>
          <button onClick={handleAddFive} aria-label="增加5">
            +5
          </button>
        </div>
        
        <button 
          onClick={handleReset}
          className="secondary"
          disabled={count === 0}
          aria-label="重置"
        >
          重置
        </button>
      </div>
      
      <div className="counter-info">
        <p>这是一个简单的React计数器组件</p>
        <p>使用了props向下传递状态和事件处理函数</p>
        {count > 0 && (
          <p style={{ color: 'var(--success-color)' }}>
            计数为正数！
          </p>
        )}
        {count === 0 && (
          <p style={{ color: 'var(--text-secondary)' }}>
            计数为零
          </p>
        )}
      </div>
    </div>
  )
}

// 为Counter组件添加CSS样式
const style = document.createElement('style')
style.textContent = `
.counter-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  background-color: var(--background-primary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.counter-display {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  padding: 1rem;
  background-color: var(--background-secondary);
  border-radius: var(--radius-sm);
  text-align: center;
}

.counter-label {
  font-size: 1.1rem;
  color: var(--text-secondary);
}

.counter-value {
  font-size: 2.5rem;
  font-weight: 700;
  transition: color 0.3s ease;
}

.counter-controls {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.control-group {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.counter-controls button {
  min-width: 60px;
  font-size: 1.25rem;
  font-weight: 600;
}

.counter-controls button.secondary {
  min-width: auto;
  font-size: 1rem;
  padding: 0.5rem 1.5rem;
}

.counter-info {
  padding: 1rem;
  background-color: var(--background-secondary);
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--primary-color);
}

.counter-info p {
  margin: 0.25rem 0;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

@media (max-width: 480px) {
  .counter-value {
    font-size: 2rem;
  }
  
  .counter-controls {
    gap: 0.75rem;
  }
  
  .control-group {
    flex-wrap: wrap;
  }
}
`
document.head.appendChild(style)

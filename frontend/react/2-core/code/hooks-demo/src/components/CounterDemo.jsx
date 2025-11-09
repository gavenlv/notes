import { useState } from 'react'
import { useTheme } from '../context/ThemeContext.jsx'

function CounterDemo() {
  const { styles } = useTheme()
  
  // 使用useState声明状态变量
  // count: 当前计数值
  // setCount: 更新count的函数
  const [count, setCount] = useState(0)
  
  // 另一个状态，用于存储历史记录
  const [history, setHistory] = useState([])
  
  // 增加计数 - 方法1: 直接设置新值
  const handleIncrement = () => {
    setCount(count + 1)
    
    // 记录操作历史
    setHistory(prev => [...prev, `增加: ${count} -> ${count + 1}`])
  }
  
  // 减少计数 - 方法2: 基于前一个状态计算新值（推荐）
  const handleDecrement = () => {
    setCount(prevCount => {
      const newValue = prevCount - 1
      // 记录操作历史
      setHistory(prev => [...prev, `减少: ${prevCount} -> ${newValue}`])
      return newValue
    })
  }
  
  // 重置计数
  const handleReset = () => {
    setHistory(prev => [...prev, `重置: ${count} -> 0`])
    setCount(0)
  }
  
  // 增加5 - 演示异步更新的问题
  const handleIncrementBy5 = () => {
    // 这种方式在单次调用中可以正常工作
    // 但如果在一个函数中多次调用，可能会出现问题
    setCount(prevCount => prevCount + 1)
    setCount(prevCount => prevCount + 1)
    setCount(prevCount => prevCount + 1)
    setCount(prevCount => prevCount + 1)
    setCount(prevCount => prevCount + 1)
    
    // 记录最终操作
    setHistory(prev => [...prev, `增加5`])
  }
  
  // 清除历史记录
  const clearHistory = () => {
    setHistory([])
  }
  
  return (
    <div className="counter-demo">
      <h2 style={{ color: styles.primaryColor }}>useState Hook 演示</h2>
      <p className="demo-description">
        这个演示展示了如何使用useState Hook管理组件状态，包括基本操作、基于前一个状态更新、以及异步更新的特性。
      </p>
      
      <div className="counter-container" style={{ backgroundColor: styles.backgroundColor, borderColor: styles.borderColor }}>
        <div className="count-display" style={{ color: styles.primaryColor }}>
          {count}
        </div>
        
        <div className="counter-buttons">
          <button 
            className="counter-btn decrement"
            onClick={handleDecrement}
            style={{ 
              backgroundColor: styles.secondaryColor, 
              color: '#fff',
              borderColor: styles.secondaryColor
            }}
          >
            -
          </button>
          
          <button 
            className="counter-btn reset"
            onClick={handleReset}
            style={{ 
              backgroundColor: 'transparent', 
              color: styles.color,
              borderColor: styles.borderColor
            }}
          >
            重置
          </button>
          <button 
            className="counter-btn increment"
            onClick={handleIncrement}
            style={{ 
              backgroundColor: styles.primaryColor, 
              color: '#fff',
              borderColor: styles.primaryColor
            }}
          >
            +
          </button>
        </div>
        
        <button 
          className="counter-btn increment-by-5"
          onClick={handleIncrementBy5}
          style={{ 
            backgroundColor: styles.primaryColor,
            opacity: 0.8,
            color: '#fff',
            borderColor: styles.primaryColor
          }}
        >
          增加5
        </button>
      </div>
      
      <div className="history-container" style={{ borderColor: styles.borderColor }}>
        <h3 style={{ color: styles.secondaryColor }}>操作历史</h3>
        {history.length === 0 ? (
          <p className="no-history">暂无操作历史</p>
        ) : (
          <>
            <ul className="history-list">
              {history.map((item, index) => (
                <li key={index} style={{ borderColor: styles.borderColor }}>{item}</li>
              ))}
            </ul>
            <button 
              className="clear-history-btn"
              onClick={clearHistory}
              style={{ 
                backgroundColor: 'transparent', 
                color: styles.color,
                borderColor: styles.borderColor
              }}
            >
              清除历史
            </button>
          </>
        )}
      </div>
      
      <div className="code-explanation" style={{ backgroundColor: styles.backgroundColor, borderColor: styles.borderColor }}>
        <h3 style={{ color: styles.secondaryColor }}>代码解释</h3>
        <pre><code>
{`// 基本的useState使用
const [count, setCount] = useState(0);

// 方法1: 直接设置新值
setCount(count + 1);

// 方法2: 基于前一个状态计算新值（推荐）
setCount(prevCount => prevCount - 1);

// 多次更新状态
setCount(prevCount => prevCount + 1);
setCount(prevCount => prevCount + 1);`}
        </code></pre>
      </div>
    </div>
  )
}

export default CounterDemo

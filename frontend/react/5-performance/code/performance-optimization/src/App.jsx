import { useState, useMemo, useCallback, useEffect } from 'react'
import './App.css'

// 1. React.memo 示例组件
const ExpensiveComponent = React.memo(({ data }) => {
  console.log('ExpensiveComponent 渲染')
  
  // 模拟昂贵的计算
  const performExpensiveCalculation = () => {
    let result = 0;
    for (let i = 0; i < 1000000; i++) {
      result += Math.random();
    }
    return result;
  };
  
  const result = performExpensiveCalculation();
  
  return (
    <div className="optimized-item">
      <h3>React.memo 优化组件</h3>
      <p>数据: {data}</p>
      <p>计算结果: {result.toFixed(2)}</p>
      <p className="render-info">最后渲染时间: {new Date().toLocaleTimeString()}</p>
    </div>
  );
});

// 2. 普通子组件（用于对比）
const RegularChildComponent = ({ onClick }) => {
  console.log('RegularChildComponent 渲染')
  return (
    <button onClick={onClick} className="child-button">
      普通子组件按钮
    </button>
  );
};

// 3. useCallback 优化的子组件
const OptimizedChildComponent = React.memo(({ onClick }) => {
  console.log('OptimizedChildComponent 渲染')
  return (
    <button onClick={onClick} className="child-button optimized">
      useCallback 优化按钮
    </button>
  );
});

// 4. 长列表项组件
const ListItem = React.memo(({ item, index }) => {
  return (
    <div className="list-item">
      <span className="item-index">{index + 1}.</span>
      <span className="item-content">{item}</span>
    </div>
  );
});

// 5. 模拟虚拟列表组件
const VirtualizedList = ({ items, visibleCount = 10 }) => {
  const [startIndex, setStartIndex] = useState(0);
  
  // 只渲染可见的项目
  const visibleItems = useMemo(() => {
    return items.slice(startIndex, startIndex + visibleCount);
  }, [items, startIndex, visibleCount]);
  
  const handleScroll = (direction) => {
    if (direction === 'up' && startIndex > 0) {
      setStartIndex(prev => Math.max(0, prev - visibleCount));
    } else if (direction === 'down' && startIndex + visibleCount < items.length) {
      setStartIndex(prev => prev + visibleCount);
    }
  };
  
  return (
    <div className="virtualized-list">
      <div className="list-controls">
        <button onClick={() => handleScroll('up')} disabled={startIndex === 0}>
          上一页
        </button>
        <span>显示 {startIndex + 1}-{Math.min(startIndex + visibleCount, items.length)} / {items.length}</span>
        <button onClick={() => handleScroll('down')} disabled={startIndex + visibleCount >= items.length}>
          下一页
        </button>
      </div>
      <div className="list-container">
        {visibleItems.map((item, idx) => (
          <ListItem key={startIndex + idx} item={item} index={startIndex + idx} />
        ))}
      </div>
    </div>
  );
};

// 主应用组件
function App() {
  // 状态定义
  const [count, setCount] = useState(0);
  const [data, setData] = useState('初始数据');
  const [inputValue, setInputValue] = useState('');
  
  // 生成大量数据用于测试
  const largeList = useMemo(() => {
    return Array.from({ length: 1000 }, (_, i) => `项目 ${i + 1}: 这是一个用于测试虚拟化列表的数据项`);
  }, []);
  
  // 3. 使用 useCallback 优化函数引用
  const regularClickHandler = () => {
    console.log('普通点击处理函数被调用');
  };
  
  const optimizedClickHandler = useCallback(() => {
    console.log('优化的点击处理函数被调用');
  }, []);
  
  // 4. 使用 useMemo 优化计算结果
  const expensiveValue = useMemo(() => {
    console.log('执行昂贵计算...');
    let result = 0;
    for (let i = 0; i < 1000000; i++) {
      result += Math.sqrt(i * count);
    }
    return result.toFixed(2);
  }, [count]); // 只有当 count 改变时才重新计算
  
  // 5. 性能监测
  const [renderTimes, setRenderTimes] = useState([]);
  
  useEffect(() => {
    const startTime = performance.now();
    
    // 模拟一些渲染工作
    const timer = setTimeout(() => {
      const endTime = performance.now();
      const renderTime = endTime - startTime;
      setRenderTimes(prev => [...prev.slice(-9), renderTime]);
    }, 0);
    
    return () => clearTimeout(timer);
  });
  
  return (
    <div className="optimization-demo">
      <h1>React 性能优化示例</h1>
      
      {/* 性能统计 */}
      <div className="performance-stats">
        <h3>性能统计</h3>
        <p>渲染时间: {renderTimes.length > 0 ? renderTimes[renderTimes.length - 1].toFixed(2) : 0}ms</p>
        <p>最近10次渲染平均时间: {renderTimes.length > 0 ? (renderTimes.reduce((a, b) => a + b, 0) / renderTimes.length).toFixed(2) : 0}ms</p>
      </div>
      
      {/* 1. React.memo 示例 */}
      <section className="demo-section">
        <h2>1. React.memo 优化</h2>
        <div className="controls">
          <button onClick={() => setCount(count + 1)}>更新计数器: {count}</button>
          <button onClick={() => setData(`更新数据 ${Date.now()}`)}>更新数据</button>
        </div>
        <div className="memo-visual">
          <div className="memo-box">
            父组件<br/>(总是渲染)
          </div>
          <div className="memo-box">
            <ExpensiveComponent data={data} />
          </div>
        </div>
        <p className="explanation">
          点击"更新计数器"按钮，由于 ExpensiveComponent 的 props 没有改变，它不会重新渲染。<br/>
          点击"更新数据"按钮，组件会重新渲染并执行昂贵的计算。
        </p>
      </section>
      
      {/* 2. useCallback 示例 */}
      <section className="demo-section">
        <h2>2. useCallback 优化</h2>
        <input 
          type="text" 
          value={inputValue} 
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="输入内容"
        />
        <p>输入值: {inputValue}</p>
        <div className="callback-demo">
          <RegularChildComponent onClick={regularClickHandler} />
          <OptimizedChildComponent onClick={optimizedClickHandler} />
        </div>
        <p className="explanation">
          输入内容时，普通子组件会每次都重新渲染，而使用 useCallback 优化的组件不会重新渲染。
        </p>
      </section>
      
      {/* 3. useMemo 示例 */}
      <section className="demo-section">
        <h2>3. useMemo 优化</h2>
        <button onClick={() => setCount(count + 1)}>更新计数器: {count}</button>
        <button onClick={() => setInputValue(`新输入 ${Date.now()}`)}>更新输入</button>
        <p className="expensive-result">
          昂贵计算结果: {expensiveValue}
        </p>
        <p className="explanation">
          只有更新计数器时，昂贵计算才会重新执行。更新输入值不会触发重新计算。
        </p>
      </section>
      
      {/* 4. 虚拟化列表示例 */}
      <section className="demo-section">
        <h2>4. 虚拟化长列表</h2>
        <VirtualizedList items={largeList} visibleCount={10} />
        <p className="explanation">
          即使有1000个数据项，我们也只渲染可见的10个，大大提高了性能。
        </p>
      </section>
      
      {/* 性能优化最佳实践总结 */}
      <section className="demo-section">
        <h2>性能优化最佳实践总结</h2>
        <div className="best-practices">
          <div className="practice-item">
            <h3>✅ React.memo</h3>
            <p>用于优化函数组件的重新渲染，避免不必要的渲染</p>
          </div>
          <div className="practice-item">
            <h3>✅ useMemo</h3>
            <p>用于缓存计算结果，避免重复计算</p>
          </div>
          <div className="practice-item">
            <h3>✅ useCallback</h3>
            <p>用于缓存函数引用，避免子组件不必要的重新渲染</p>
          </div>
          <div className="practice-item">
            <h3>✅ 虚拟化长列表</h3>
            <p>只渲染可见区域的元素，减少DOM节点数量</p>
          </div>
          <div className="practice-item">
            <h3>✅ 避免内联对象和函数</h3>
            <p>不要在render中创建新对象或函数，除非必要</p>
          </div>
          <div className="practice-item">
            <h3>✅ 代码分割和懒加载</h3>
            <p>使用 React.lazy 和 Suspense 实现组件懒加载</p>
          </div>
        </div>
      </section>
    </div>
  )
}

export default App

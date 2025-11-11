import React, { useState } from 'react';
import './example.css';

function JSXDemo() {
  const [name, setName] = useState('React');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [items, setItems] = useState([
    { id: 1, text: '学习JSX' },
    { id: 2, text: '理解组件' },
    { id: 3, text: '掌握Props' }
  ]);

  const toggleLogin = () => {
    setIsLoggedIn(!isLoggedIn);
  };

  const addItem = () => {
    const newItem = {
      id: items.length + 1,
      text: `新任务 ${items.length + 1}`
    };
    setItems([...items, newItem]);
  };

  const removeItem = (id) => {
    setItems(items.filter(item => item.id !== id));
  };

  return (
    <div className="demo-container">
      <div className="demo-description">
        <h3>JSX语法示例</h3>
        <p>本示例展示了JSX的基本语法，包括变量插入、条件渲染、列表渲染和事件处理。</p>
      </div>

      <div className="demo-section">
        <h4 className="section-title">1. 变量插入</h4>
        <div className="code-block">
          <p>当前的name值是：<span className="highlight">{name}</span></p>
          <div className="input-group">
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="输入一个名字"
              className="input"
            />
            <span>Hello, {name}!</span>
          </div>
        </div>
      </div>

      <div className="demo-section">
        <h4 className="section-title">2. 条件渲染</h4>
        <div className="code-block">
          <div className="button-group">
            <button
              onClick={toggleLogin}
              className={`btn ${isLoggedIn ? 'btn-danger' : 'btn-primary'}`}
            >
              {isLoggedIn ? '退出登录' : '登录'}
            </button>
          </div>
          
          <div className="conditional-rendering">
            {isLoggedIn ? (
              <div className="welcome-message">
                <p>欢迎回来，{name}！</p>
                <p>您已成功登录系统。</p>
              </div>
            ) : (
              <div className="login-prompt">
                <p>请先登录系统。</p>
                <p>点击上方按钮进行登录。</p>
              </div>
            )}
            
            {isLoggedIn && (
              <p className="login-status">
                <span className="status-indicator online"></span>
                当前状态：在线
              </p>
            )}
          </div>
        </div>
      </div>

      <div className="demo-section">
        <h4 className="section-title">3. 列表渲染</h4>
        <div className="code-block">
          <div className="button-group">
            <button onClick={addItem} className="btn btn-success">
              添加任务
            </button>
          </div>
          
          <ul className="task-list">
            {items.length === 0 ? (
              <li className="empty-message">暂无任务</li>
            ) : (
              items.map(item => (
                <li key={item.id} className="task-item">
                  <span>{item.text}</span>
                  <button
                    onClick={() => removeItem(item.id)}
                    className="btn btn-small btn-danger"
                  >
                    删除
                  </button>
                </li>
              ))
            )}
          </ul>
          
          <p>当前任务数量：{items.length}</p>
        </div>
      </div>

      <div className="demo-section">
        <h4 className="section-title">4. 内联样式与CSS类</h4>
        <div className="code-block">
          <div className="style-examples">
            <div 
              className="style-box"
              style={{ backgroundColor: '#4dabf7', padding: '10px', color: 'white' }}
            >
              这是使用内联样式的元素
            </div>
            
            <div className="style-box style-class">
              这是使用CSS类的元素
            </div>
            
            <div className={`style-box ${isLoggedIn ? 'style-logged-in' : 'style-logged-out'}`}>
              这是根据状态动态切换CSS类的元素
            </div>
          </div>
        </div>
      </div>

      <div className="code-block">
        <h4>代码示例：</h4>
        <pre className="code-snippet">
{`// JSX基本语法示例
function Component() {
  const [count, setCount] = useState(0);
  const [name, setName] = useState('');
  
  // 变量插入
  return <h1>Hello, {name}!</h1>;
  
  // 条件渲染
  return (
    <div>
      {count > 0 && <p>计数大于0</p>}
      {count > 0 ? <p>计数为正数</p> : <p>计数为0或负数</p>}
    </div>
  );
  
  // 列表渲染
  return (
    <ul>
      {items.map(item => (
        <li key={item.id}>{item.text}</li>
      ))}
    </ul>
  );
}`}
        </pre>
      </div>
    </div>
  );
}

export default JSXDemo;
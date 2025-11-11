import React, { useState } from 'react';
import './example.css';

// 欢迎组件 - 基础函数组件
function Welcome({ name }) {
  return <h1>Hello, {name}!</h1>;
}

// 用户卡片组件 - 带有多个props的组件
function UserCard({ user, onFollow, isFollowing }) {
  return (
    <div className="user-card">
      <img 
        src={user.avatar} 
        alt={user.name}
        className="avatar" 
      />
      <div className="user-info">
        <h3>{user.name}</h3>
        <p>{user.bio}</p>
        <div className="user-stats">
          <span>关注者: {user.followers}</span>
          <span>帖子: {user.posts}</span>
        </div>
      </div>
      <div className="user-actions">
        <button 
          onClick={() => onFollow(user.id)}
          className={`btn ${isFollowing ? 'btn-secondary' : 'btn-primary'}`}
        >
          {isFollowing ? '已关注' : '关注'}
        </button>
      </div>
    </div>
  );
}

// 计数器组件 - 带有状态的组件
function Counter({ initialValue = 0 }) {
  const [count, setCount] = useState(initialValue);
  
  const increment = () => setCount(count + 1);
  const decrement = () => setCount(count - 1);
  const reset = () => setCount(initialValue);
  
  return (
    <div className="counter">
      <h3>计数器: {count}</h3>
      <div className="counter-controls">
        <button onClick={increment} className="btn btn-primary">+</button>
        <button onClick={decrement} className="btn btn-secondary">-</button>
        <button onClick={reset} className="btn btn-danger">重置</button>
      </div>
    </div>
  );
}

// 主题切换组件 - 使用useState和条件渲染
function ThemeToggle() {
  const [theme, setTheme] = useState('light');
  
  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };
  
  return (
    <div className={`theme-container theme-${theme}`}>
      <p>当前主题: {theme === 'light' ? '浅色' : '深色'}</p>
      <button onClick={toggleTheme} className="btn btn-primary">
        切换到{theme === 'light' ? '深色' : '浅色'}主题
      </button>
    </div>
  );
}

// 组件组合示例
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [isFollowing, setIsFollowing] = useState(false);
  
  // 模拟从API获取用户数据
  useState(() => {
    // 模拟API调用
    setTimeout(() => {
      setUser({
        id: userId,
        name: '张三',
        bio: '前端开发工程师，热爱React和JavaScript',
        avatar: 'https://picsum.photos/seed/user123/100/100.jpg',
        followers: 1234,
        posts: 56
      });
    }, 1000);
  }, [userId]);
  
  const handleFollow = (userId) => {
    setIsFollowing(!isFollowing);
    // 这里可以添加API调用逻辑
  };
  
  if (!user) {
    return <div className="loading">加载用户信息中...</div>;
  }
  
  return (
    <div className="user-profile">
      <UserCard 
        user={user} 
        onFollow={handleFollow}
        isFollowing={isFollowing} 
      />
      <Counter initialValue={user.followers} />
    </div>
  );
}

function ComponentDemo() {
  const [activeDemo, setActiveDemo] = useState('basic');
  
  return (
    <div className="demo-container">
      <div className="demo-description">
        <h3>React组件示例</h3>
        <p>本示例展示了React组件的基本用法，包括函数组件、状态管理、组件组合等概念。</p>
      </div>
      
      <div className="demo-tabs">
        <button
          className={`demo-tab ${activeDemo === 'basic' ? 'active' : ''}`}
          onClick={() => setActiveDemo('basic')}
        >
          基础组件
        </button>
        <button
          className={`demo-tab ${activeDemo === 'stateful' ? 'active' : ''}`}
          onClick={() => setActiveDemo('stateful')}
        >
          状态组件
        </button>
        <button
          className={`demo-tab ${activeDemo === 'composition' ? 'active' : ''}`}
          onClick={() => setActiveDemo('composition')}
        >
          组件组合
        </button>
      </div>
      
      <div className="demo-content">
        {activeDemo === 'basic' && (
          <div className="demo-section">
            <h4>基础函数组件</h4>
            <div className="code-block">
              <Welcome name="React学习者" />
            </div>
            
            <h4>用户卡片组件</h4>
            <div className="code-block">
              <UserCard 
                user={{
                  id: 1,
                  name: '李四',
                  bio: '全栈开发工程师',
                  avatar: 'https://picsum.photos/seed/user456/100/100.jpg',
                  followers: 567,
                  posts: 23
                }}
                onFollow={(id) => console.log(`关注用户 ${id}`)}
                isFollowing={false}
              />
            </div>
          </div>
        )}
        
        {activeDemo === 'stateful' && (
          <div className="demo-section">
            <h4>带状态的计数器组件</h4>
            <div className="code-block">
              <Counter initialValue={10} />
            </div>
            
            <h4>主题切换组件</h4>
            <div className="code-block">
              <ThemeToggle />
            </div>
          </div>
        )}
        
        {activeDemo === 'composition' && (
          <div className="demo-section">
            <h4>组件组合 - 用户资料页面</h4>
            <div className="code-block">
              <UserProfile userId={1} />
            </div>
          </div>
        )}
      </div>
      
      <div className="code-block">
        <h4>代码示例：</h4>
        <pre className="code-snippet">
{`// 基础函数组件
function Welcome({ name }) {
  return <h1>Hello, {name}!</h1>;
}

// 使用
<Welcome name="React学习者" />

// 带状态的组件
function Counter() {
  const [count, setCount] = useState(0);
  
  return (
    <div>
      <p>计数: {count}</p>
      <button onClick={() => setCount(count + 1)}>
        增加
      </button>
    </div>
  );
}

// 组件组合
function UserProfile() {
  return (
    <div>
      <UserCard user={user} />
      <Counter />
    </div>
  );
}`}
        </pre>
      </div>
    </div>
  );
}

export default ComponentDemo;
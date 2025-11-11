import React, { useState } from 'react';
import './example.css';

// 用户卡片应用组件
function UserCardApp() {
  const [users, setUsers] = useState([
    {
      id: 1,
      name: '张三',
      bio: '全栈开发工程师，擅长React和Node.js',
      skills: ['React', 'Node.js', 'JavaScript', 'TypeScript'],
      avatar: 'https://picsum.photos/seed/user1/100/100.jpg',
      followers: 1234,
      following: 567
    },
    {
      id: 2,
      name: '李四',
      bio: '前端开发工程师，专注React和Vue',
      skills: ['React', 'Vue', 'TypeScript', 'Sass'],
      avatar: 'https://picsum.photos/seed/user2/100/100.jpg',
      followers: 2345,
      following: 345
    },
    {
      id: 3,
      name: '王五',
      bio: 'UI/UX设计师，热爱创新和用户体验',
      skills: ['Figma', 'Sketch', 'Adobe XD', 'CSS'],
      avatar: 'https://picsum.photos/seed/user3/100/100.jpg',
      followers: 567,
      following: 234
    }
  ]);
  
  const [selectedUser, setSelectedUser] = useState(null);
  const [isDarkTheme, setIsDarkTheme] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  
  const filteredUsers = users.filter(user =>
    user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.skills.some(skill => skill.toLowerCase().includes(searchTerm.toLowerCase()))
  );
  
  const handleUserSelect = (user) => {
    setSelectedUser(user);
  };
  
  const handleThemeToggle = () => {
    setIsDarkTheme(!isDarkTheme);
  };
  
  const handleFollowToggle = (userId) => {
    setUsers(prevUsers =>
      prevUsers.map(user =>
        user.id === userId
          ? { ...user, followers: user.followers + 1 }
          : user
      )
    );
  };
  
  return (
    <div className={`app-container ${isDarkTheme ? 'dark-theme' : 'light-theme'}`}>
      <header className="app-header">
        <h1>React用户卡片展示应用</h1>
        <div className="header-controls">
          <div className="search-box">
            <input
              type="text"
              placeholder="搜索用户或技能..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>
          <button
            className="theme-toggle"
            onClick={handleThemeToggle}
          >
            {isDarkTheme ? '🌞 浅色' : '🌙 深色'}
          </button>
        </div>
      </header>
      
      <main className="app-main">
        {selectedUser && (
          <div className="selected-user-info">
            <div className="selected-user-card">
              <img
                src={selectedUser.avatar}
                alt={selectedUser.name}
                className="selected-avatar"
              />
              <div className="selected-details">
                <h2>{selectedUser.name}</h2>
                <p>{selectedUser.bio}</p>
                <div className="user-stats">
                  <div className="stat-item">
                    <span className="stat-value">{selectedUser.followers}</span>
                    <span className="stat-label">关注者</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-value">{selectedUser.following}</span>
                    <span className="stat-label">关注中</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div className="user-grid">
          {filteredUsers.length === 0 ? (
            <div className="no-results">
              <p>没有找到匹配的用户</p>
            </div>
          ) : (
            filteredUsers.map(user => (
              <div
                key={user.id}
                className={`user-card ${selectedUser?.id === user.id ? 'selected' : ''}`}
                onClick={() => handleUserSelect(user)}
              >
                <img
                  src={user.avatar}
                  alt={user.name}
                  className="user-avatar"
                />
                <div className="user-info">
                  <h3>{user.name}</h3>
                  <p className="user-bio">{user.bio}</p>
                  <div className="user-skills">
                    {user.skills.map(skill => (
                      <span key={skill} className="skill-tag">
                        {skill}
                      </span>
                    ))}
                  </div>
                  <div className="user-stats">
                    <span>{user.followers} 关注者</span>
                    <span>{user.following} 关注中</span>
                  </div>
                </div>
                <div className="user-actions">
                  <button
                    className="follow-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleFollowToggle(user.id);
                    }}
                  >
                    关注
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </main>
    </div>
  );
}

function FirstApp() {
  return (
    <div className="demo-container">
      <div className="demo-description">
        <h3>第一个React应用</h3>
        <p>这是一个完整的React应用示例，展示了如何使用组件、状态、事件处理等概念构建实际应用。</p>
      </div>
      
      <div className="demo-section">
        <UserCardApp />
      </div>
      
      <div className="code-block">
        <h4>代码结构：</h4>
        <pre className="code-snippet">
{`// 主应用组件
function UserCardApp() {
  const [users, setUsers] = useState([...]); // 用户列表状态
  const [selectedUser, setSelectedUser] = useState(null); // 选中用户状态
  const [isDarkTheme, setIsDarkTheme] = useState(false); // 主题状态
  
  // 事件处理函数
  const handleUserSelect = (user) => {
    setSelectedUser(user);
  };
  
  const handleThemeToggle = () => {
    setIsDarkTheme(!isDarkTheme);
  };
  
  // 渲染UI
  return (
    <div className={\`app-container \${isDarkTheme ? 'dark-theme' : 'light-theme'}\`}>
      {/* 头部 */}
      <header>
        <h1>用户卡片应用</h1>
        <button onClick={handleThemeToggle}>
          {isDarkTheme ? '浅色' : '深色'}
        </button>
      </header>
      
      {/* 主内容区 */}
      <main>
        {/* 用户卡片列表 */}
        {users.map(user => (
          <UserCard 
            key={user.id} 
            user={user} 
            onSelect={handleUserSelect} 
          />
        ))}
      </main>
    </div>
  );
}`}
        </pre>
      </div>
    </div>
  );
}

export default FirstApp;
import React, { useState } from 'react';
import './example.css';

// 按钮组件 - 展示props的基本用法
function Button({ 
  children, 
  variant = 'primary', 
  size = 'medium', 
  disabled = false, 
  onClick 
}) {
  const buttonClass = `btn btn-${variant} btn-${size} ${disabled ? 'btn-disabled' : ''}`;
  
  return (
    <button 
      className={buttonClass} 
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
}

// 卡片组件 - 展示复杂对象props
function Card({ title, content, footer, variant = 'default' }) {
  return (
    <div className={`card card-${variant}`}>
      <div className="card-header">
        <h3>{title}</h3>
      </div>
      <div className="card-body">
        {content}
      </div>
      {footer && (
        <div className="card-footer">
          {footer}
        </div>
      )}
    </div>
  );
}

// 用户列表组件 - 展示数组props和列表渲染
function UserList({ users, onSelect, selectedUser }) {
  return (
    <div className="user-list">
      <h3>用户列表</h3>
      <ul className="users">
        {users.length === 0 ? (
          <li className="empty-state">暂无用户</li>
        ) : (
          users.map(user => (
            <li 
              key={user.id} 
              className={`user-item ${selectedUser?.id === user.id ? 'selected' : ''}`}
              onClick={() => onSelect(user)}
            >
              <img 
                src={user.avatar} 
                alt={user.name}
                className="user-avatar" 
              />
              <div className="user-info">
                <h4>{user.name}</h4>
                <p>{user.email}</p>
              </div>
              <div className="user-status">
                <span className={`status ${user.active ? 'active' : 'inactive'}`}>
                  {user.active ? '活跃' : '离线'}
                </span>
              </div>
            </li>
          ))
        )}
      </ul>
    </div>
  );
}

// 表单组件 - 展示回调函数props
function Form({ onSubmit, initialValues = {} }) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setValues(prev => ({
      ...prev,
      [name]: value
    }));
    
    // 清除对应的错误
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    // 简单验证
    const newErrors = {};
    if (!values.name) newErrors.name = '姓名不能为空';
    if (!values.email) newErrors.email = '邮箱不能为空';
    if (!values.message) newErrors.message = '消息不能为空';
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    
    // 调用父组件传入的onSubmit回调
    onSubmit(values);
    
    // 重置表单
    setValues(initialValues);
    setErrors({});
  };
  
  return (
    <form className="form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="name">姓名:</label>
        <input
          type="text"
          id="name"
          name="name"
          value={values.name || ''}
          onChange={handleChange}
          className={`form-control ${errors.name ? 'error' : ''}`}
        />
        {errors.name && <span className="error-message">{errors.name}</span>}
      </div>
      
      <div className="form-group">
        <label htmlFor="email">邮箱:</label>
        <input
          type="email"
          id="email"
          name="email"
          value={values.email || ''}
          onChange={handleChange}
          className={`form-control ${errors.email ? 'error' : ''}`}
        />
        {errors.email && <span className="error-message">{errors.email}</span>}
      </div>
      
      <div className="form-group">
        <label htmlFor="message">消息:</label>
        <textarea
          id="message"
          name="message"
          value={values.message || ''}
          onChange={handleChange}
          rows="4"
          className={`form-control ${errors.message ? 'error' : ''}`}
        />
        {errors.message && <span className="error-message">{errors.message}</span>}
      </div>
      
      <Button type="submit">提交</Button>
    </form>
  );
}

// 布局组件 - 展示children prop的用法
function Layout({ header, sidebar, main, footer }) {
  return (
    <div className="layout">
      <header className="layout-header">{header}</header>
      <div className="layout-body">
        <aside className="layout-sidebar">{sidebar}</aside>
        <main className="layout-main">{main}</main>
      </div>
      <footer className="layout-footer">{footer}</footer>
    </div>
  );
}

function PropsDemo() {
  const [activeDemo, setActiveDemo] = useState('basic');
  const [selectedUser, setSelectedUser] = useState(null);
  
  const users = [
    {
      id: 1,
      name: '张三',
      email: 'zhangsan@example.com',
      avatar: 'https://picsum.photos/seed/user1/50/50.jpg',
      active: true
    },
    {
      id: 2,
      name: '李四',
      email: 'lisi@example.com',
      avatar: 'https://picsum.photos/seed/user2/50/50.jpg',
      active: false
    },
    {
      id: 3,
      name: '王五',
      email: 'wangwu@example.com',
      avatar: 'https://picsum.photos/seed/user3/50/50.jpg',
      active: true
    }
  ];
  
  const handleUserSelect = (user) => {
    setSelectedUser(user);
  };
  
  const handleFormSubmit = (values) => {
    console.log('表单提交:', values);
    alert('表单提交成功!');
  };
  
  return (
    <div className="demo-container">
      <div className="demo-description">
        <h3>Props使用示例</h3>
        <p>本示例展示了Props的各种用法，包括基本props、children、回调函数等。</p>
      </div>
      
      <div className="demo-tabs">
        <button
          className={`demo-tab ${activeDemo === 'basic' ? 'active' : ''}`}
          onClick={() => setActiveDemo('basic')}
        >
          基础Props
        </button>
        <button
          className={`demo-tab ${activeDemo === 'children' ? 'active' : ''}`}
          onClick={() => setActiveDemo('children')}
        >
          Children Props
        </button>
        <button
          className={`demo-tab ${activeDemo === 'callback' ? 'active' : ''}`}
          onClick={() => setActiveDemo('callback')}
        >
          回调函数Props
        </button>
        <button
          className={`demo-tab ${activeDemo === 'spread' ? 'active' : ''}`}
          onClick={() => setActiveDemo('spread')}
        >
          展开运算符
        </button>
      </div>
      
      <div className="demo-content">
        {activeDemo === 'basic' && (
          <div className="demo-section">
            <h4>按钮组件 - 展示不同变体的props</h4>
            <div className="code-block">
              <Button variant="primary" size="large">主要按钮</Button>
              <Button variant="secondary">次要按钮</Button>
              <Button variant="danger" size="small">危险按钮</Button>
              <Button disabled>禁用按钮</Button>
            </div>
            
            <h4>卡片组件 - 展示复杂对象props</h4>
            <div className="code-block">
              <Card 
                title="用户信息" 
                content={
                  <div>
                    <p>这是一个卡片的内容区域。</p>
                    <p>可以传入任何React元素作为内容。</p>
                  </div>
                }
                footer={<Button>了解更多</Button>}
                variant="highlight"
              />
            </div>
            
            <h4>用户列表组件 - 展示数组props</h4>
            <div className="code-block">
              <UserList 
                users={users} 
                onSelect={handleUserSelect}
                selectedUser={selectedUser}
              />
            </div>
          </div>
        )}
        
        {activeDemo === 'children' && (
          <div className="demo-section">
            <h4>布局组件 - 使用children prop</h4>
            <div className="code-block">
              <Layout
                header={<h2>应用头部</h2>}
                sidebar={
                  <div>
                    <h3>侧边栏</h3>
                    <ul>
                      <li>菜单项1</li>
                      <li>菜单项2</li>
                      <li>菜单项3</li>
                    </ul>
                  </div>
                }
                main={
                  <div>
                    <h3>主要内容</h3>
                    <p>这里是主要内容区域。</p>
                    <p>可以放置任何React元素。</p>
                  </div>
                }
                footer={<p>© 2024 React教程</p>}
              />
            </div>
          </div>
        )}
        
        {activeDemo === 'callback' && (
          <div className="demo-section">
            <h4>表单组件 - 展示回调函数props</h4>
            <div className="code-block">
              <Form 
                onSubmit={handleFormSubmit}
                initialValues={{
                  name: '默认姓名',
                  email: 'default@example.com'
                }}
              />
            </div>
          </div>
        )}
        
        {activeDemo === 'spread' && (
          <div className="demo-section">
            <h4>展开运算符 - 动态传递props</h4>
            <div className="code-block">
              <h5>原始对象:</h5>
              <pre className="code-snippet">
{`const userProps = {
  name: '张三',
  email: 'zhangsan@example.com',
  avatar: 'https://example.com/avatar.jpg'
};`}
              </pre>
              
              <h5>使用展开运算符传递:</h5>
              <pre className="code-snippet">
{`<UserCard {...userProps} />`}
              </pre>
              
              <h5>结合覆盖特定props:</h5>
              <pre className="code-snippet">
{`<UserCard 
  {...userProps} 
  name="李四"  // 覆盖原有的name属性
/>`}
              </pre>
            </div>
          </div>
        )}
      </div>
      
      <div className="code-block">
        <h4>代码示例：</h4>
        <pre className="code-snippet">
{`// 基本props传递
function Button({ children, variant, onClick }) {
  return <button onClick={onClick}>{children}</button>;
}

// 使用
<Button variant="primary" onClick={handleClick}>点击我</Button>

// children prop
function Card({ title, children }) {
  return (
    <div>
      <h2>{title}</h2>
      <div>{children}</div>
    </div>
  );
}

// 使用
<Card title="标题">
  <p>这是卡片内容</p>
</Card>

// 展开运算符
const props = { variant: 'primary', size: 'large' };
<Button {...props}>按钮</Button>

// 覆盖特定属性
<Button {...props} variant="secondary">按钮</Button>`}
        </pre>
      </div>
    </div>
  );
}

export default PropsDemo;
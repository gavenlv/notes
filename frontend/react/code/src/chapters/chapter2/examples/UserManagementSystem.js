import React, { useState, useEffect } from 'react';

// 按钮组件
function Button({ 
  children, 
  variant = 'primary', 
  size = 'medium',
  disabled = false,
  onClick,
  type = 'button'
}) {
  const baseClass = 'btn';
  const variantClass = `btn-${variant}`;
  const sizeClass = `btn-${size}`;
  const disabledClass = disabled ? 'btn-disabled' : '';
  
  const className = `${baseClass} ${variantClass} ${sizeClass} ${disabledClass}`;
  
  return (
    <button
      type={type}
      className={className}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
}

// 卡片组件
function Card({ children, className = '', onClick }) {
  const cardClass = `card ${className}`;
  
  return (
    <div className={cardClass} onClick={onClick}>
      {children}
    </div>
  );
}

function CardHeader({ children }) {
  return <div className="card-header">{children}</div>;
}

function CardBody({ children }) {
  return <div className="card-body">{children}</div>;
}

function CardFooter({ children }) {
  return <div className="card-footer">{children}</div>;
}

// 输入框组件
function Input({
  label,
  value,
  onChange,
  placeholder,
  type = 'text',
  error,
  disabled = false,
  required = false
}) {
  const inputId = `input-${Math.random().toString(36).substr(2, 9)}`;
  
  return (
    <div className="form-group">
      {label && (
        <label htmlFor={inputId} className="form-label">
          {label}
          {required && <span className="required">*</span>}
        </label>
      )}
      <input
        id={inputId}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        disabled={disabled}
        className={`form-input ${error ? 'input-error' : ''}`}
      />
      {error && <div className="error-message">{error}</div>}
    </div>
  );
}

// 列表组件
function List({ items, renderItem, onItemClick, emptyMessage }) {
  if (!items || items.length === 0) {
    return <div className="list-empty">{emptyMessage || '暂无数据'}</div>;
  }
  
  return (
    <ul className="list">
      {items.map((item, index) => (
        <li 
          key={item.id || index} 
          className="list-item"
          onClick={() => onItemClick && onItemClick(item, index)}
        >
          {renderItem ? renderItem(item, index) : item}
        </li>
      ))}
    </ul>
  );
}

// 用户管理系统主组件
export function UserManagementSystem() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: ''
  });
  const [editingUser, setEditingUser] = useState(null);
  const [errors, setErrors] = useState({});
  const [searchQuery, setSearchQuery] = useState('');
  
  // 模拟获取用户数据
  useEffect(() => {
    setLoading(true);
    setTimeout(() => {
      setUsers([
        { id: 1, name: '张三', email: 'zhangsan@example.com', phone: '13800138001' },
        { id: 2, name: '李四', email: 'lisi@example.com', phone: '13800138002' },
        { id: 3, name: '王五', email: 'wangwu@example.com', phone: '13800138003' }
      ]);
      setLoading(false);
    }, 1000);
  }, []);
  
  // 表单验证
  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = '姓名不能为空';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = '邮箱不能为空';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = '邮箱格式不正确';
    }
    
    if (!formData.phone.trim()) {
      newErrors.phone = '手机号不能为空';
    } else if (!/^1[3-9]\d{9}$/.test(formData.phone)) {
      newErrors.phone = '手机号格式不正确';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  // 处理表单提交
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    if (editingUser) {
      // 更新用户
      setUsers(users.map(user => 
        user.id === editingUser.id 
          ? { ...user, ...formData }
          : user
      ));
      setEditingUser(null);
    } else {
      // 添加新用户
      const newUser = {
        id: Date.now(),
        ...formData
      };
      setUsers([...users, newUser]);
    }
    
    // 重置表单
    setFormData({ name: '', email: '', phone: '' });
  };
  
  // 处理表单输入
  const handleChange = (field, value) => {
    setFormData({
      ...formData,
      [field]: value
    });
    
    // 清除该字段的错误信息
    if (errors[field]) {
      setErrors({
        ...errors,
        [field]: ''
      });
    }
  };
  
  // 编辑用户
  const handleEditUser = (user) => {
    setEditingUser(user);
    setFormData({
      name: user.name,
      email: user.email,
      phone: user.phone
    });
  };
  
  // 删除用户
  const handleDeleteUser = (userId) => {
    if (window.confirm('确定要删除这个用户吗？')) {
      setUsers(users.filter(user => user.id !== userId));
    }
  };
  
  // 渲染用户列表项
  const renderUserItem = (user) => (
    <Card className="user-card">
      <CardBody>
        <h4>{user.name}</h4>
        <p>邮箱: {user.email}</p>
        <p>电话: {user.phone}</p>
      </CardBody>
      <CardFooter>
        <Button size="small" onClick={() => handleEditUser(user)}>编辑</Button>
        <Button variant="danger" size="small" onClick={() => handleDeleteUser(user.id)}>删除</Button>
      </CardFooter>
    </Card>
  );
  
  // 过滤用户
  const filteredUsers = users.filter(user => 
    user.name.includes(searchQuery) || 
    user.email.includes(searchQuery) ||
    user.phone.includes(searchQuery)
  );
  
  return (
    <div className="user-management">
      <Card>
        <CardHeader>
          <h2>用户管理系统</h2>
        </CardHeader>
        <CardBody>
          <form onSubmit={handleSubmit} className="user-form">
            <Input
              label="姓名"
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              error={errors.name}
              required
            />
            <Input
              label="邮箱"
              type="email"
              value={formData.email}
              onChange={(e) => handleChange('email', e.target.value)}
              error={errors.email}
              required
            />
            <Input
              label="手机号"
              value={formData.phone}
              onChange={(e) => handleChange('phone', e.target.value)}
              error={errors.phone}
              required
            />
            <div className="button-group">
              <Button type="submit">
                {editingUser ? '更新用户' : '添加用户'}
              </Button>
              {editingUser && (
                <Button 
                  variant="secondary" 
                  onClick={() => {
                    setEditingUser(null);
                    setFormData({ name: '', email: '', phone: '' });
                  }}
                >
                  取消
                </Button>
              )}
            </div>
          </form>
        </CardBody>
      </Card>
      
      <Card>
        <CardHeader>
          <div className="list-header">
            <h3>用户列表</h3>
            <Input
              label="搜索"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="输入关键词搜索"
            />
          </div>
        </CardHeader>
        <CardBody>
          {loading ? (
            <div className="loading">加载中...</div>
          ) : (
            <List 
              items={filteredUsers}
              renderItem={renderUserItem}
              emptyMessage="暂无用户数据"
            />
          )}
        </CardBody>
      </Card>
    </div>
  );
}
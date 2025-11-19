// React + TypeScript 应用主组件

import React, { useState, useEffect } from 'react';
import { useCrudApi, usePaginatedApi } from './hooks/useApi';
import { UserCard, UserList } from './components/UserCard';

// 用户接口
interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
  avatar?: string;
  createdAt: string;
  updatedAt: string;
}

// 创建用户表单数据接口
interface CreateUserData {
  name: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
}

// 应用组件
const App: React.FC = () => {
  // 用户管理状态
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingUserId, setEditingUserId] = useState<string | null>(null);
  
  // 使用自定义Hook管理用户
  const { items: users, loading, error, createItem, updateItem, deleteItem } = useCrudApi<User>('/api/users');
  
  // 用户表单状态
  const [formData, setFormData] = useState<CreateUserData>({
    name: '',
    email: '',
    role: 'user'
  });
  
  // 重置表单
  const resetForm = () => {
    setFormData({
      name: '',
      email: '',
      role: 'user'
    });
    setEditingUserId(null);
    setShowCreateForm(false);
  };
  
  // 处理表单输入变化
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  // 提交表单
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      if (editingUserId) {
        await updateItem(editingUserId, formData);
      } else {
        await createItem(formData);
      }
      resetForm();
    } catch (error) {
      console.error('保存用户失败:', error);
    }
  };
  
  // 编辑用户
  const handleEditUser = (userId: string) => {
    const user = users.find(u => u.id === userId);
    if (user) {
      setFormData({
        name: user.name,
        email: user.email,
        role: user.role
      });
      setEditingUserId(userId);
      setShowCreateForm(true);
    }
  };
  
  // 删除用户
  const handleDeleteUser = async (userId: string) => {
    try {
      await deleteItem(userId);
    } catch (error) {
      console.error('删除用户失败:', error);
    }
  };
  
  // 获取用户数量
  const userStats = {
    total: users.length,
    admin: users.filter(u => u.role === 'admin').length,
    user: users.filter(u => u.role === 'user').length,
    guest: users.filter(u => u.role === 'guest').length
  };
  
  return (
    <div className="app">
      <header className="app-header">
        <h1>用户管理系统</h1>
        <button 
          className="create-button"
          onClick={() => setShowCreateForm(true)}
        >
          添加用户
        </button>
      </header>
      
      <main className="app-main">
        {/* 用户统计 */}
        <section className="stats-section">
          <h2>用户统计</h2>
          <div className="stats-cards">
            <div className="stat-card">
              <h3>总用户数</h3>
              <span className="stat-value">{userStats.total}</span>
            </div>
            <div className="stat-card admin">
              <h3>管理员</h3>
              <span className="stat-value">{userStats.admin}</span>
            </div>
            <div className="stat-card user">
              <h3>普通用户</h3>
              <span className="stat-value">{userStats.user}</span>
            </div>
            <div className="stat-card guest">
              <h3>访客</h3>
              <span className="stat-value">{userStats.guest}</span>
            </div>
          </div>
        </section>
        
        {/* 创建/编辑用户表单 */}
        {showCreateForm && (
          <section className="form-section">
            <h2>{editingUserId ? '编辑用户' : '创建用户'}</h2>
            <form onSubmit={handleSubmit} className="user-form">
              <div className="form-group">
                <label htmlFor="name">姓名</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="email">邮箱</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="role">角色</label>
                <select
                  id="role"
                  name="role"
                  value={formData.role}
                  onChange={handleInputChange}
                  required
                >
                  <option value="admin">管理员</option>
                  <option value="user">普通用户</option>
                  <option value="guest">访客</option>
                </select>
              </div>
              
              <div className="form-actions">
                <button type="submit" className="submit-button">
                  {editingUserId ? '更新' : '创建'}
                </button>
                <button type="button" className="cancel-button" onClick={resetForm}>
                  取消
                </button>
              </div>
            </form>
          </section>
        )}
        
        {/* 用户列表 */}
        <section className="users-section">
          <h2>用户列表</h2>
          {error ? (
            <div className="error-message">{error}</div>
          ) : (
            <UserList
              users={users}
              loading={loading}
              onEdit={handleEditUser}
              onDelete={handleDeleteUser}
            />
          )}
        </section>
      </main>
      
      <footer className="app-footer">
        <p>&copy; 2023 用户管理系统 - TypeScript + React</p>
      </footer>
    </div>
  );
};

export default App;
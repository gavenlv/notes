// React + TypeScript 用户卡片组件示例

import React, { useState } from 'react';

// 用户接口定义
interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
  avatar?: string;
  createdAt: string;
  updatedAt: string;
}

// 组件属性接口
interface UserCardProps {
  user: User;
  onEdit?: (userId: string) => void;
  onDelete?: (userId: string) => void;
  showActions?: boolean;
}

// 角色颜色映射
const roleColors = {
  admin: '#e74c3c',
  user: '#3498db',
  guest: '#95a5a6'
};

// 用户卡片组件
export const UserCard: React.FC<UserCardProps> = ({
  user,
  onEdit,
  onDelete,
  showActions = true
}) => {
  const [isLoading, setIsLoading] = useState(false);
  
  const handleEdit = () => {
    if (onEdit) {
      onEdit(user.id);
    }
  };
  
  const handleDelete = async () => {
    if (onDelete && window.confirm(`确定要删除用户 ${user.name} 吗？`)) {
      setIsLoading(true);
      try {
        await onDelete(user.id);
      } finally {
        setIsLoading(false);
      }
    }
  };
  
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };
  
  return (
    <div className="user-card">
      <div className="user-avatar">
        {user.avatar ? (
          <img src={user.avatar} alt={user.name} />
        ) : (
          <div className="avatar-placeholder">
            {user.name.charAt(0).toUpperCase()}
          </div>
        )}
      </div>
      
      <div className="user-info">
        <h3 className="user-name">{user.name}</h3>
        <p className="user-email">{user.email}</p>
        <div 
          className="user-role"
          style={{ backgroundColor: roleColors[user.role] }}
        >
          {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
        </div>
        
        <div className="user-dates">
          <span>创建于: {formatDate(user.createdAt)}</span>
          {user.updatedAt !== user.createdAt && (
            <span>更新于: {formatDate(user.updatedAt)}</span>
          )}
        </div>
      </div>
      
      {showActions && (
        <div className="user-actions">
          <button 
            className="edit-button" 
            onClick={handleEdit}
            disabled={isLoading}
          >
            编辑
          </button>
          <button 
            className="delete-button" 
            onClick={handleDelete}
            disabled={isLoading}
          >
            {isLoading ? '删除中...' : '删除'}
          </button>
        </div>
      )}
    </div>
  );
};

// 用户列表组件
interface UserListProps {
  users: User[];
  loading?: boolean;
  onEdit?: (userId: string) => void;
  onDelete?: (userId: string) => void;
}

export const UserList: React.FC<UserListProps> = ({
  users,
  loading = false,
  onEdit,
  onDelete
}) => {
  if (loading) {
    return <div className="loading">加载用户列表中...</div>;
  }
  
  if (users.length === 0) {
    return <div className="empty-state">没有找到用户</div>;
  }
  
  return (
    <div className="user-list">
      {users.map(user => (
        <UserCard
          key={user.id}
          user={user}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
};

// 可重用列表组件（泛型）
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
  keyExtractor: (item: T) => string;
  loading?: boolean;
  emptyMessage?: string;
  className?: string;
}

export function List<T>({
  items,
  renderItem,
  keyExtractor,
  loading = false,
  emptyMessage = '没有找到项目',
  className = ''
}: ListProps<T>) {
  if (loading) {
    return <div className="loading">加载中...</div>;
  }
  
  if (items.length === 0) {
    return <div className="empty-state">{emptyMessage}</div>;
  }
  
  return (
    <div className={`generic-list ${className}`}>
      {items.map(item => (
        <div key={keyExtractor(item)} className="list-item">
          {renderItem(item)}
        </div>
      ))}
    </div>
  );
}
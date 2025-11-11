import React, { useState } from 'react';

// 通用按钮组件
function Button({ 
  children, 
  variant = 'primary', 
  size = 'medium', 
  disabled = false, 
  onClick 
}) {
  const baseClass = 'btn';
  const variantClass = `btn-${variant}`;
  const sizeClass = `btn-${size}`;
  const disabledClass = disabled ? 'btn-disabled' : '';
  
  const className = `${baseClass} ${variantClass} ${sizeClass} ${disabledClass}`;
  
  return (
    <button
      className={className}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
}

// 卡片组件 - 包含关系
function Card({ children, title, footer }) {
  return (
    <div className="card">
      {title && (
        <div className="card-header">
          <h3>{title}</h3>
        </div>
      )}
      <div className="card-body">
        {children}
      </div>
      {footer && (
        <div className="card-footer">
          {footer}
        </div>
      )}
    </div>
  );
}

// 特殊化组合 - 继承自卡片
function Dialog({ message, onConfirm, onCancel }) {
  return (
    <Card 
      title="确认对话框" 
      footer={
        <div className="dialog-footer">
          <Button variant="secondary" onClick={onCancel}>取消</Button>
          <Button onClick={onConfirm}>确认</Button>
        </div>
      }
    >
      <p>{message}</p>
    </Card>
  );
}

// 容器组件与展示组件模式
// 展示组件 - 只负责UI渲染
function UserList({ users, onUserClick }) {
  return (
    <div className="user-list">
      {users.map(user => (
        <div 
          key={user.id} 
          className="user-item"
          onClick={() => onUserClick(user.id)}
        >
          <div className="user-avatar">
            {user.name.charAt(0).toUpperCase()}
          </div>
          <div className="user-info">
            <div className="user-name">{user.name}</div>
            <div className="user-email">{user.email}</div>
          </div>
        </div>
      ))}
    </div>
  );
}

// 容器组件 - 负责数据获取和状态管理
function UserListContainer() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedUserId, setSelectedUserId] = useState(null);
  
  React.useEffect(() => {
    // 模拟API调用
    setTimeout(() => {
      setUsers([
        { id: 1, name: '张三', email: 'zhangsan@example.com' },
        { id: 2, name: '李四', email: 'lisi@example.com' },
        { id: 3, name: '王五', email: 'wangwu@example.com' }
      ]);
      setLoading(false);
    }, 1000);
  }, []);
  
  const handleUserClick = (userId) => {
    setSelectedUserId(userId);
  };
  
  if (loading) {
    return <div className="loading">加载中...</div>;
  }
  
  return (
    <div className="user-container">
      <UserList 
        users={users} 
        onUserClick={handleUserClick}
      />
      {selectedUserId && (
        <div className="selected-user">
          选中的用户ID: {selectedUserId}
        </div>
      )}
    </div>
  );
}

// 高阶组件(HOC)模式
function withLoading(WrappedComponent) {
  return function WithLoadingComponent({ isLoading, ...otherProps }) {
    if (isLoading) {
      return <div className="loading-overlay">加载中...</div>;
    }
    return <WrappedComponent {...otherProps} />;
  };
}

// 待包装的数据组件
function DataTable({ data }) {
  return (
    <div className="data-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>名称</th>
            <th>值</th>
          </tr>
        </thead>
        <tbody>
          {data.map(item => (
            <tr key={item.id}>
              <td>{item.id}</td>
              <td>{item.name}</td>
              <td>{item.value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// 使用HOC增强组件
const DataTableWithLoading = withLoading(DataTable);

// 复合组件模式 - 表单组件
function FormField({ label, error, children }) {
  return (
    <div className={`form-field ${error ? 'has-error' : ''}`}>
      {label && <label className="form-label">{label}</label>}
      {children}
      {error && <div className="form-error">{error}</div>}
    </div>
  );
}

function TextInput({ value, onChange, placeholder, ...props }) {
  return (
    <input
      type="text"
      value={value}
      onChange={e => onChange(e.target.value)}
      placeholder={placeholder}
      className="form-input"
      {...props}
    />
  );
}

function Form({ children, onSubmit }) {
  return (
    <form onSubmit={onSubmit} className="form">
      {children}
    </form>
  );
}

// 使用复合组件构建表单
function UserForm({ initialData, onSubmit }) {
  const [formData, setFormData] = useState(initialData || {
    name: '',
    email: '',
    phone: ''
  });
  
  const [errors, setErrors] = useState({});
  
  const handleChange = (field, value) => {
    setFormData({
      ...formData,
      [field]: value
    });
    
    // 清除该字段的错误
    if (errors[field]) {
      setErrors({
        ...errors,
        [field]: null
      });
    }
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    // 简单验证
    const newErrors = {};
    if (!formData.name.trim()) {
      newErrors.name = '姓名不能为空';
    }
    if (!formData.email.trim()) {
      newErrors.email = '邮箱不能为空';
    }
    
    if (Object.keys(newErrors).length === 0) {
      if (onSubmit) {
        onSubmit(formData);
      }
    } else {
      setErrors(newErrors);
    }
  };
  
  return (
    <Form onSubmit={handleSubmit}>
      <FormField label="姓名" error={errors.name}>
        <TextInput
          value={formData.name}
          onChange={value => handleChange('name', value)}
          placeholder="请输入姓名"
        />
      </FormField>
      
      <FormField label="邮箱" error={errors.email}>
        <TextInput
          value={formData.email}
          onChange={value => handleChange('email', value)}
          placeholder="请输入邮箱"
        />
      </FormField>
      
      <FormField label="电话">
        <TextInput
          value={formData.phone}
          onChange={value => handleChange('phone', value)}
          placeholder="请输入电话"
        />
      </FormField>
      
      <Button type="submit">提交</Button>
    </Form>
  );
}

export const CompositionDemo = () => {
  const [showDialog, setShowDialog] = useState(false);
  const [loading, setLoading] = useState(false);
  const [tableData, setTableData] = useState([]);
  const [formSubmittedData, setFormSubmittedData] = useState(null);
  
  const handleDialogConfirm = () => {
    setShowDialog(false);
    alert('操作已确认');
  };
  
  const handleDialogCancel = () => {
    setShowDialog(false);
  };
  
  // 模拟加载数据
  const loadData = () => {
    setLoading(true);
    setTimeout(() => {
      setTableData([
        { id: 1, name: '产品A', value: 100 },
        { id: 2, name: '产品B', value: 200 },
        { id: 3, name: '产品C', value: 300 }
      ]);
      setLoading(false);
    }, 1500);
  };
  
  const handleFormSubmit = (data) => {
    setFormSubmittedData(data);
    alert(`表单提交成功: ${JSON.stringify(data)}`);
  };
  
  return (
    <div className="demo-container">
      <div className="demo-description">
        <h2>组件组合模式示例</h2>
        <p>React推崇组件组合而非继承，通过组合简单的组件来构建复杂的UI。</p>
      </div>

      <div className="examples-grid">
        {/* 基本组合示例 */}
        <Card title="基本组合模式" footer={
          <Button onClick={() => setShowDialog(true)}>打开对话框</Button>
        }>
          <p>这个卡片展示了基本的组合模式。</p>
          <p>卡片组件包含头部、内容和底部。</p>
          <div className="button-group">
            <Button variant="primary">主要按钮</Button>
            <Button variant="secondary">次要按钮</Button>
          </div>
        </Card>
        
        {/* 容器组件与展示组件 */}
        <Card title="容器与展示组件分离">
          <UserListContainer />
        </Card>
        
        {/* 高阶组件 */}
        <Card title="高阶组件(HOC)模式">
          <p>HOC是一个函数，它接收组件并返回一个新组件。</p>
          <Button onClick={loadData}>加载数据</Button>
          <DataTableWithLoading 
            isLoading={loading} 
            data={tableData}
          />
        </Card>
        
        {/* 复合组件 */}
        <Card title="复合组件模式">
          <p>复合组件允许构建更加灵活的组件API。</p>
          <UserForm onSubmit={handleFormSubmit} />
          {formSubmittedData && (
            <div className="submitted-data">
              提交的数据: {JSON.stringify(formSubmittedData)}
            </div>
          )}
        </Card>
      </div>
      
      {/* 对话框 */}
      {showDialog && (
        <div className="dialog-overlay">
          <Dialog 
            message="这是一个特殊化的组合组件示例。"
            onConfirm={handleDialogConfirm}
            onCancel={handleDialogCancel}
          />
        </div>
      )}
      
      <div className="demo-info">
        <h3>组件组合模式要点</h3>
        <ul>
          <li>包含关系：组件可以包含其他组件，形成嵌套关系</li>
          <li>特殊化：一个组件可以是另一个组件的"特殊版本"</li>
          <li>容器/展示组件分离：分离关注点，提高可测试性</li>
          <li>高阶组件：通过函数包装来增强组件功能</li>
          <li>复合组件：构建更加灵活的组件API</li>
        </ul>
      </div>
    </div>
  );
};
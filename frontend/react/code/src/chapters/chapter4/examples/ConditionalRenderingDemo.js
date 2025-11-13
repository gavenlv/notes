import React, { useState } from 'react';

// 基本条件渲染示例
function BasicConditionalExample() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [hasError, setHasError] = useState(false);
  
  const handleLogin = () => {
    setIsLoading(true);
    
    // 模拟登录过程
    setTimeout(() => {
      setIsLoading(false);
      
      // 随机模拟成功或失败
      const success = Math.random() > 0.3;
      if (success) {
        setIsLoggedIn(true);
        setHasError(false);
      } else {
        setHasError(true);
      }
    }, 1500);
  };
  
  const handleLogout = () => {
    setIsLoggedIn(false);
  };
  
  return (
    <div className="example-section">
      <h3>基本条件渲染</h3>
      
      <div className="demo-container">
        {/* 方式1: 使用三元运算符 */}
        <div className="conditional-block">
          <h4>三元运算符</h4>
          {isLoggedIn ? <p>欢迎回来，用户!</p> : <p>请先登录</p>}
        </div>
        
        {/* 方式2: 使用逻辑与运算符 */}
        <div className="conditional-block">
          <h4>逻辑与(&&)运算符</h4>
          {isLoggedIn && <p>这是登录后才能看到的内容</p>}
        </div>
        
        {/* 方式3: 复杂条件 */}
        <div className="conditional-block">
          <h4>复杂条件渲染</h4>
          {isLoading ? (
            <p>正在登录中...</p>
          ) : hasError ? (
            <p>登录失败，请重试</p>
          ) : isLoggedIn ? (
            <p>登录成功!</p>
          ) : (
            <p>请点击登录按钮</p>
          )}
        </div>
        
        {/* 控制按钮 */}
        <div className="button-group">
          {!isLoggedIn ? (
            <button onClick={handleLogin} disabled={isLoading}>
              {isLoading ? '登录中...' : '登录'}
            </button>
          ) : (
            <button onClick={handleLogout}>退出登录</button>
          )}
          
          {hasError && (
            <button onClick={() => setHasError(false)}>
              清除错误
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// 多条件渲染示例
function MultiConditionalExample() {
  const [userRole, setUserRole] = useState('guest');
  const [subscription, setSubscription] = useState('none');
  
  // 使用映射表实现多条件渲染
  const getRoleDisplay = () => {
    const roleConfig = {
      guest: { text: '访客', color: '#6c757d', permissions: '只读权限' },
      user: { text: '普通用户', color: '#007bff', permissions: '基本功能' },
      premium: { text: '高级用户', color: '#28a745', permissions: '所有功能' },
      admin: { text: '管理员', color: '#dc3545', permissions: '系统管理' }
    };
    
    return roleConfig[userRole] || roleConfig.guest;
  };
  
  const getSubscriptionDisplay = () => {
    const subConfig = {
      none: { text: '未订阅', features: '无额外功能' },
      basic: { text: '基础版', features: '基础功能' },
      professional: { text: '专业版', features: '专业功能' },
      enterprise: { text: '企业版', features: '所有功能' }
    };
    
    return subConfig[subscription] || subConfig.none;
  };
  
  const roleInfo = getRoleDisplay();
  const subInfo = getSubscriptionDisplay();
  
  // 计算可用功能
  const getAvailableFeatures = () => {
    const features = [];
    
    // 基于角色的功能
    if (userRole !== 'guest') {
      features.push('创建内容');
    }
    
    if (userRole === 'premium' || userRole === 'admin') {
      features.push('高级搜索');
    }
    
    if (userRole === 'admin') {
      features.push('用户管理');
    }
    
    // 基于订阅的功能
    if (subscription !== 'none') {
      features.push('下载资源');
    }
    
    if (subscription === 'professional' || subscription === 'enterprise') {
      features.push('API访问');
    }
    
    if (subscription === 'enterprise') {
      features.push('专属支持');
    }
    
    return features;
  };
  
  const availableFeatures = getAvailableFeatures();
  
  return (
    <div className="example-section">
      <h3>多条件渲染</h3>
      
      <div className="demo-container">
        <div className="status-display">
          <div className="status-item">
            <h4>用户角色</h4>
            <div className="role-badge" style={{ backgroundColor: roleInfo.color }}>
              {roleInfo.text}
            </div>
            <p>{roleInfo.permissions}</p>
          </div>
          
          <div className="status-item">
            <h4>订阅状态</h4>
            <div className="subscription-badge">
              {subInfo.text}
            </div>
            <p>{subInfo.features}</p>
          </div>
        </div>
        
        <div className="features-section">
          <h4>可用功能</h4>
          {availableFeatures.length > 0 ? (
            <ul className="features-list">
              {availableFeatures.map((feature, index) => (
                <li key={index}>{feature}</li>
              ))}
            </ul>
          ) : (
            <p className="no-features">暂无可用功能</p>
          )}
        </div>
        
        <div className="controls-section">
          <h4>控制面板</h4>
          <div className="control-group">
            <label>用户角色:</label>
            <select 
              value={userRole} 
              onChange={(e) => setUserRole(e.target.value)}
            >
              <option value="guest">访客</option>
              <option value="user">普通用户</option>
              <option value="premium">高级用户</option>
              <option value="admin">管理员</option>
            </select>
          </div>
          
          <div className="control-group">
            <label>订阅状态:</label>
            <select 
              value={subscription} 
              onChange={(e) => setSubscription(e.target.value)}
            >
              <option value="none">未订阅</option>
              <option value="basic">基础版</option>
              <option value="professional">专业版</option>
              <option value="enterprise">企业版</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
}

// 提取条件渲染逻辑
function ExtractedLogicExample() {
  const [view, setView] = useState('home');
  const [isAdmin, setIsAdmin] = useState(false);
  
  // 提取条件渲染逻辑为函数
  const renderViewContent = () => {
    const commonViews = {
      home: <HomeView />,
      profile: <ProfileView />,
      settings: <SettingsView />
    };
    
    const adminViews = {
      dashboard: <DashboardView />,
      users: <UsersView />
    };
    
    // 如果是管理员且有对应视图，返回管理员视图
    if (isAdmin && adminViews[view]) {
      return adminViews[view];
    }
    
    // 返回通用视图，如果不存在则返回404
    return commonViews[view] || <NotFoundView />;
  };
  
  // 提取导航逻辑
  const renderNavigation = () => {
    const commonNavItems = [
      { id: 'home', label: '首页' },
      { id: 'profile', label: '个人资料' },
      { id: 'settings', label: '设置' }
    ];
    
    const adminNavItems = [
      { id: 'dashboard', label: '仪表盘' },
      { id: 'users', label: '用户管理' }
    ];
    
    return (
      <nav className="navigation">
        {commonNavItems.map(item => (
          <button 
            key={item.id}
            className={view === item.id ? 'active' : ''}
            onClick={() => setView(item.id)}
          >
            {item.label}
          </button>
        ))}
        
        {isAdmin && adminNavItems.map(item => (
          <button 
            key={item.id}
            className={view === item.id ? 'active' : ''}
            onClick={() => setView(item.id)}
          >
            {item.label}
          </button>
        ))}
      </nav>
    );
  };
  
  return (
    <div className="example-section">
      <h3>提取条件渲染逻辑</h3>
      
      <div className="demo-container">
        <div className="app-container">
          <div className="app-header">
            <h4>应用示例</h4>
            <div className="admin-toggle">
              <label>
                <input
                  type="checkbox"
                  checked={isAdmin}
                  onChange={(e) => setIsAdmin(e.target.checked)}
                />
                管理员模式
              </label>
            </div>
          </div>
          
          {renderNavigation()}
          
          <div className="app-content">
            {renderViewContent()}
          </div>
        </div>
      </div>
    </div>
  );
}

// 防止组件卸载的渲染
function PreventUnmountExample() {
  const [activeTab, setActiveTab] = useState('profile');
  const [formValues, setFormValues] = useState({
    profile: { name: '张三', email: 'zhangsan@example.com' },
    settings: { theme: 'light', notifications: true }
  });
  
  // 条件渲染方式 - 组件会卸载/挂载，状态会丢失
  const ConditionalTabs = () => (
    <div className="tab-container">
      <div className="tab-headers">
        <button 
          className={activeTab === 'profile' ? 'active' : ''}
          onClick={() => setActiveTab('profile')}
        >
          个人资料
        </button>
        <button 
          className={activeTab === 'settings' ? 'active' : ''}
          onClick={() => setActiveTab('settings')}
        >
          设置
        </button>
      </div>
      
      <div className="tab-content">
        {activeTab === 'profile' && (
          <div className="tab-panel">
            <h4>个人资料 (条件渲染)</h4>
            <input
              type="text"
              value={formValues.profile.name}
              onChange={(e) => setFormValues(prev => ({
                ...prev,
                profile: { ...prev.profile, name: e.target.value }
              }))}
              placeholder="姓名"
            />
            <input
              type="email"
              value={formValues.profile.email}
              onChange={(e) => setFormValues(prev => ({
                ...prev,
                profile: { ...prev.profile, email: e.target.value }
              }))}
              placeholder="邮箱"
            />
          </div>
        )}
        
        {activeTab === 'settings' && (
          <div className="tab-panel">
            <h4>设置 (条件渲染)</h4>
            <select
              value={formValues.settings.theme}
              onChange={(e) => setFormValues(prev => ({
                ...prev,
                settings: { ...prev.settings, theme: e.target.value }
              }))}
            >
              <option value="light">浅色主题</option>
              <option value="dark">深色主题</option>
            </select>
            <label>
              <input
                type="checkbox"
                checked={formValues.settings.notifications}
                onChange={(e) => setFormValues(prev => ({
                  ...prev,
                  settings: { ...prev.settings, notifications: e.target.checked }
                }))}
              />
              启用通知
            </label>
          </div>
        )}
      </div>
    </div>
  );
  
  // CSS隐藏方式 - 组件保持挂载，状态保留
  const CSSTabs = () => (
    <div className="tab-container">
      <div className="tab-headers">
        <button 
          className={activeTab === 'profile' ? 'active' : ''}
          onClick={() => setActiveTab('profile')}
        >
          个人资料
        </button>
        <button 
          className={activeTab === 'settings' ? 'active' : ''}
          onClick={() => setActiveTab('settings')}
        >
          设置
        </button>
      </div>
      
      <div className="tab-content">
        <div 
          className="tab-panel"
          style={{ display: activeTab === 'profile' ? 'block' : 'none' }}
        >
          <h4>个人资料 (CSS隐藏)</h4>
          <input
            type="text"
            value={formValues.profile.name}
            onChange={(e) => setFormValues(prev => ({
              ...prev,
              profile: { ...prev.profile, name: e.target.value }
            }))}
            placeholder="姓名"
          />
          <input
            type="email"
            value={formValues.profile.email}
            onChange={(e) => setFormValues(prev => ({
              ...prev,
              profile: { ...prev.profile, email: e.target.value }
            }))}
            placeholder="邮箱"
          />
        </div>
        
        <div 
          className="tab-panel"
          style={{ display: activeTab === 'settings' ? 'block' : 'none' }}
        >
          <h4>设置 (CSS隐藏)</h4>
          <select
            value={formValues.settings.theme}
            onChange={(e) => setFormValues(prev => ({
              ...prev,
              settings: { ...prev.settings, theme: e.target.value }
            }))}
          >
            <option value="light">浅色主题</option>
            <option value="dark">深色主题</option>
          </select>
          <label>
            <input
              type="checkbox"
              checked={formValues.settings.notifications}
              onChange={(e) => setFormValues(prev => ({
                ...prev,
              settings: { ...prev.settings, notifications: e.target.checked }
              }))}
            />
            启用通知
          </label>
        </div>
      </div>
    </div>
  );
  
  return (
    <div className="example-section">
      <h3>防止组件卸载的渲染</h3>
      
      <div className="demo-container">
        <div className="rendering-comparison">
          <div className="rendering-method">
            <h4>条件渲染 (组件卸载/挂载)</h4>
            <p>切换标签时，组件会卸载并重新挂载，状态可能丢失</p>
            <ConditionalTabs />
          </div>
          
          <div className="rendering-method">
            <h4>CSS隐藏 (组件保持挂载)</h4>
            <p>切换标签时，组件保持挂载，状态保留</p>
            <CSSTabs />
          </div>
        </div>
      </div>
    </div>
  );
}

// 视图组件（用于提取逻辑示例）
function HomeView() {
  return <div className="view-content">欢迎来到首页</div>;
}

function ProfileView() {
  return <div className="view-content">这是个人资料页面</div>;
}

function SettingsView() {
  return <div className="view-content">这是设置页面</div>;
}

function DashboardView() {
  return <div className="view-content admin-view">这是管理员仪表盘</div>;
}

function UsersView() {
  return <div className="view-content admin-view">这是用户管理页面</div>;
}

function NotFoundView() {
  return <div className="view-content error">页面未找到</div>;
}

export const ConditionalRenderingDemo = () => {
  return (
    <div className="demo-container">
      <div className="demo-description">
        <h2>条件渲染示例</h2>
        <p>本示例演示了React中各种条件渲染的实现方式，包括基本条件渲染、多条件渲染、提取条件逻辑以及防止组件卸载的渲染技巧。</p>
      </div>

      <div className="examples-grid">
        <BasicConditionalExample />
        <MultiConditionalExample />
        <ExtractedLogicExample />
        <PreventUnmountExample />
      </div>
      
      <div className="demo-info">
        <h3>条件渲染要点</h3>
        <ul>
          <li>简单条件使用逻辑与(&&)运算符或三元运算符</li>
          <li>复杂条件使用if语句或提取为函数</li>
          <li>多条件渲染可以使用映射表提高可维护性</li>
          <li>考虑使用CSS隐藏而非条件渲染来保持组件状态</li>
          <li>提取条件逻辑为函数可以使组件更清晰</li>
          <li>使用高阶组件封装常见的条件渲染模式</li>
        </ul>
      </div>
    </div>
  );
};
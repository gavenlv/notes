import React, { useState, useMemo, useCallback } from 'react';

// 动态组件渲染
function DynamicComponentExample() {
  const [activeComponent, setActiveComponent] = useState('welcome');
  const [userName, setUserName] = useState('');
  
  // 组件映射表
  const componentMap = {
    welcome: (
      <div className="dynamic-component">
        <h2>欢迎页面</h2>
        <p>这是欢迎页面组件</p>
      </div>
    ),
    profile: (
      <div className="dynamic-component">
        <h2>个人资料</h2>
        <input
          type="text"
          value={userName}
          onChange={(e) => setUserName(e.target.value)}
          placeholder="输入你的名字"
        />
      </div>
    ),
    settings: (
      <div className="dynamic-component">
        <h2>设置页面</h2>
        <p>这是设置页面组件</p>
      </div>
    ),
    analytics: (
      <div className="dynamic-component">
        <h2>分析页面</h2>
        <p>这是分析页面组件</p>
      </div>
    )
  };
  
  return (
    <div className="example-section">
      <h3>动态组件渲染</h3>
      
      <div className="demo-container">
        <div className="component-navigation">
          {Object.keys(componentMap).map(key => (
            <button
              key={key}
              onClick={() => setActiveComponent(key)}
              className={activeComponent === key ? 'active' : ''}
            >
              {key === 'welcome' ? '欢迎' :
               key === 'profile' ? '个人资料' :
               key === 'settings' ? '设置' : '分析'}
            </button>
          ))}
        </div>
        
        <div className="component-container">
          {componentMap[activeComponent]}
        </div>
      </div>
    </div>
  );
}

// 高阶条件渲染模式
function HOCConditionalExample() {
  const [userRole, setUserRole] = useState('guest');
  
  // 创建条件渲染的高阶组件
  const withAuth = (Component, requiredRole) => {
    return function AuthenticatedComponent(props) {
      if (userRole === requiredRole) {
        return <Component {...props} />;
      }
      
      return (
        <div className="auth-denied">
          <p>需要 {requiredRole} 权限</p>
        </div>
      );
    };
  };
  
  // 基础组件
  const UserContent = () => <div className="content-box">这是普通用户内容</div>;
  const AdminContent = () => <div className="content-box">这是管理员内容</div>;
  const SuperAdminContent = () => <div className="content-box">这是超级管理员内容</div>;
  
  // 使用HOC创建有条件访问的组件
  const ProtectedUserContent = withAuth(UserContent, 'user');
  const ProtectedAdminContent = withAuth(AdminContent, 'admin');
  const ProtectedSuperAdminContent = withAuth(SuperAdminContent, 'superadmin');
  
  return (
    <div className="example-section">
      <h3>高阶条件渲染模式</h3>
      
      <div className="demo-container">
        <div className="role-selector">
          <label>当前角色:</label>
          <select value={userRole} onChange={(e) => setUserRole(e.target.value)}>
            <option value="guest">访客</option>
            <option value="user">普通用户</option>
            <option value="admin">管理员</option>
            <option value="superadmin">超级管理员</option>
          </select>
        </div>
        
        <div className="protected-content">
          <h4>内容区域</h4>
          <ProtectedUserContent />
          <ProtectedAdminContent />
          <ProtectedSuperAdminContent />
        </div>
      </div>
    </div>
  );
}

// 自定义渲染逻辑Hook
function CustomRenderHookExample() {
  const [items, setItems] = useState([
    { id: 1, name: '苹果', price: 2.5, category: '水果' },
    { id: 2, name: '牛奶', price: 5.0, category: '饮料' },
    { id: 3, name: '面包', price: 3.5, category: '主食' },
    { id: 4, name: '橙子', price: 3.0, category: '水果' },
    { id: 5, name: '咖啡', price: 8.0, category: '饮料' }
  ]);
  
  const [activeFilter, setActiveFilter] = useState('all');
  
  // 自定义Hook用于分组渲染
  const useGroupByCategory = (items) => {
    const groupedItems = useMemo(() => {
      return items.reduce((acc, item) => {
        const { category } = item;
        if (!acc[category]) {
          acc[category] = [];
        }
        acc[category].push(item);
        return acc;
      }, {});
    }, [items]);
    
    return groupedItems;
  };
  
  // 自定义Hook用于条件渲染
  const useFilterRender = (items, filterType) => {
    const filteredItems = useMemo(() => {
      switch (filterType) {
        case 'fruit':
          return items.filter(item => item.category === '水果');
        case 'drink':
          return items.filter(item => item.category === '饮料');
        case 'staple':
          return items.filter(item => item.category === '主食');
        case 'expensive':
          return items.filter(item => item.price > 4);
        case 'cheap':
          return items.filter(item => item.price <= 4);
        default:
          return items;
      }
    }, [items, filterType]);
    
    return filteredItems;
  };
  
  const groupedItems = useGroupByCategory(items);
  const filteredItems = useFilterRender(items, activeFilter);
  
  const renderGroupedItems = () => {
    return (
      <div className="grouped-items">
        {Object.entries(groupedItems).map(([category, categoryItems]) => (
          <div key={category} className="category-group">
            <h4>{category}</h4>
            <ul>
              {categoryItems.map(item => (
                <li key={item.id}>
                  {item.name} - ¥{item.price}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    );
  };
  
  const renderFilteredItems = () => {
    return (
      <div className="filtered-items">
        <ul>
          {filteredItems.map(item => (
            <li key={item.id} className="item-card">
              <div className="item-name">{item.name}</div>
              <div className="item-details">
                <span className="item-category">{item.category}</span>
                <span className="item-price">¥{item.price}</span>
              </div>
            </li>
          ))}
        </ul>
      </div>
    );
  };
  
  return (
    <div className="example-section">
      <h3>自定义渲染逻辑Hook</h3>
      
      <div className="demo-container">
        <div className="filter-tabs">
          <button 
            className={activeFilter === 'all' ? 'active' : ''}
            onClick={() => setActiveFilter('all')}
          >
            全部
          </button>
          <button 
            className={activeFilter === 'fruit' ? 'active' : ''}
            onClick={() => setActiveFilter('fruit')}
          >
            水果
          </button>
          <button 
            className={activeFilter === 'drink' ? 'active' : ''}
            onClick={() => setActiveFilter('drink')}
          >
            饮料
          </button>
          <button 
            className={activeFilter === 'staple' ? 'active' : ''}
            onClick={() => setActiveFilter('staple')}
          >
            主食
          </button>
          <button 
            className={activeFilter === 'expensive' ? 'active' : ''}
            onClick={() => setActiveFilter('expensive')}
          >
            昂贵 (>¥4)
          </button>
          <button 
            className={activeFilter === 'cheap' ? 'active' : ''}
            onClick={() => setActiveFilter('cheap')}
          >
            便宜 (≤¥4)
          </button>
        </div>
        
        <div className="render-mode-toggle">
          <button 
            className={activeFilter === 'all' ? 'active' : ''}
            onClick={() => setActiveFilter('all')}
          >
            分组视图
          </button>
          <button 
            className={activeFilter !== 'all' ? 'active' : ''}
            onClick={() => setActiveFilter('fruit')}
          >
            过滤视图
          </button>
        </div>
        
        <div className="render-output">
          {activeFilter === 'all' ? renderGroupedItems() : renderFilteredItems()}
        </div>
      </div>
    </div>
  );
}

// 条件渲染性能优化
function PerformanceOptimizationExample() {
  const [activeTab, setActiveTab] = useState('tab1');
  const [counter, setCounter] = useState(0);
  const [isHeavyComponentVisible, setIsHeavyComponentVisible] = useState(false);
  
  // 模拟昂贵的组件
  const HeavyComponent = React.memo(() => {
    console.log('HeavyComponent 渲染');
    
    // 模拟繁重计算
    const now = Date.now();
    while (Date.now() < now + 300) {} // 模拟300ms的阻塞
    
    return (
      <div className="heavy-component">
        <h3>昂贵的组件</h3>
        <p>这个组件需要300ms来渲染</p>
      </div>
    );
  });
  
  // 普通组件（未优化）
  const NormalComponent = () => {
    console.log('NormalComponent 渲染');
    return (
      <div className="normal-component">
        <h3>普通组件</h3>
        <p>这个组件渲染很快</p>
      </div>
    );
  };
  
  // 使用React.memo和缓存的优化组件
  const OptimizedComponent = React.memo(() => {
    console.log('OptimizedComponent 渲染');
    return (
      <div className="optimized-component">
        <h3>优化组件</h3>
        <p>这个组件使用React.memo优化</p>
      </div>
    );
  });
  
  // 使用useMemo缓存昂贵的组件
  const memoizedHeavyComponent = useMemo(() => {
    console.log('创建缓存的重型组件');
    return <HeavyComponent />;
  }, []);
  
  // 使用useCallback缓存事件处理函数
  const handleToggleHeavyComponent = useCallback(() => {
    setIsHeavyComponentVisible(prev => !prev);
  }, []);
  
  return (
    <div className="example-section">
      <h3>条件渲染性能优化</h3>
      
      <div className="demo-container">
        <div className="performance-demo">
          <h4>触发重新渲染的计数器</h4>
          <div className="counter">
            <button onClick={() => setCounter(prev => prev + 1)}>
              增加计数: {counter}
            </button>
          </div>
        </div>
        
        <div className="tab-navigation">
          <button 
            onClick={() => setActiveTab('tab1')}
            className={activeTab === 'tab1' ? 'active' : ''}
          >
            标准条件渲染
          </button>
          <button 
            onClick={() => setActiveTab('tab2')}
            className={activeTab === 'tab2' ? 'active' : ''}
          >
            优化版本
          </button>
          <button 
            onClick={() => setActiveTab('tab3')}
            className={activeTab === 'tab3' ? 'active' : ''}
          >
            缓存版本
          </button>
        </div>
        
        <div className="tab-content">
          {activeTab === 'tab1' && (
            <div>
              <p>每次渲染都会重新创建组件</p>
              <NormalComponent />
              {isHeavyComponentVisible && <HeavyComponent />}
              <button onClick={handleToggleHeavyComponent}>
                {isHeavyComponentVisible ? '隐藏' : '显示'}昂贵组件
              </button>
            </div>
          )}
          
          {activeTab === 'tab2' && (
            <div>
              <p>使用React.memo优化，但仍然会重新创建</p>
              <OptimizedComponent />
              {isHeavyComponentVisible && <HeavyComponent />}
              <button onClick={handleToggleHeavyComponent}>
                {isHeavyComponentVisible ? '隐藏' : '显示'}昂贵组件
              </button>
            </div>
          )}
          
          {activeTab === 'tab3' && (
            <div>
              <p>使用useMemo缓存组件，避免重新创建</p>
              <OptimizedComponent />
              {isHeavyComponentVisible && memoizedHeavyComponent}
              <button onClick={handleToggleHeavyComponent}>
                {isHeavyComponentVisible ? '隐藏' : '显示'}昂贵组件
              </button>
            </div>
          )}
        </div>
        
        <div className="performance-note">
          <p>打开浏览器开发者工具查看控制台日志，观察不同优化方式的渲染行为</p>
        </div>
      </div>
    </div>
  );
}

// 复杂条件渲染场景
function ComplexConditionalExample() {
  const [user, setUser] = useState({
    name: '',
    isVerified: false,
    subscriptionType: 'none', // none, basic, premium
    preferences: {
      theme: 'light', // light, dark
      notifications: true
    }
  });
  
  // 复杂的条件渲染逻辑
  const renderDashboard = () => {
    const { name, isVerified, subscriptionType, preferences } = user;
    
    // 基础验证
    if (!name.trim()) {
      return <WelcomeForm onSetName={(name) => setUser(prev => ({ ...prev, name }))} />;
    }
    
    // 未验证用户
    if (!isVerified) {
      return <VerificationPrompt onVerify={() => setUser(prev => ({ ...prev, isVerified: true }))} />;
    }
    
    // 根据订阅类型渲染不同的仪表盘
    const dashboardProps = {
      userName: name,
      theme: preferences.theme
    };
    
    switch (subscriptionType) {
      case 'premium':
        return <PremiumDashboard {...dashboardProps} />;
      case 'basic':
        return <BasicDashboard {...dashboardProps} />;
      default:
        return <FreeDashboard {...dashboardProps} />;
    }
  };
  
  return (
    <div className="example-section">
      <h3>复杂条件渲染场景</h3>
      
      <div className="demo-container">
        <div className="user-config">
          <h4>用户配置</h4>
          
          <div className="config-field">
            <label>用户名:</label>
            <input 
              type="text"
              value={user.name}
              onChange={(e) => setUser(prev => ({ ...prev, name: e.target.value }))}
              placeholder="输入用户名"
            />
          </div>
          
          <div className="config-field">
            <label>
              <input 
                type="checkbox"
                checked={user.isVerified}
                onChange={(e) => setUser(prev => ({ ...prev, isVerified: e.target.checked }))}
              />
              已验证
            </label>
          </div>
          
          <div className="config-field">
            <label>订阅类型:</label>
            <select 
              value={user.subscriptionType}
              onChange={(e) => setUser(prev => ({ ...prev, subscriptionType: e.target.value }))}
            >
              <option value="none">免费版</option>
              <option value="basic">基础版</option>
              <option value="premium">高级版</option>
            </select>
          </div>
          
          <div className="config-field">
            <label>主题:</label>
            <select 
              value={user.preferences.theme}
              onChange={(e) => setUser(prev => ({ 
                ...prev, 
                preferences: { ...prev.preferences, theme: e.target.value } 
              }))}
            >
              <option value="light">浅色</option>
              <option value="dark">深色</option>
            </select>
          </div>
          
          <div className="config-field">
            <label>
              <input 
                type="checkbox"
                checked={user.preferences.notifications}
                onChange={(e) => setUser(prev => ({ 
                  ...prev, 
                  preferences: { ...prev.preferences, notifications: e.target.checked } 
                }))}
              />
              启用通知
            </label>
          </div>
        </div>
        
        <div className="dashboard-container">
          {renderDashboard()}
        </div>
      </div>
    </div>
  );
}

// 子组件（用于复杂条件渲染）
function WelcomeForm({ onSetName }) {
  const [tempName, setTempName] = useState('');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (tempName.trim()) {
      onSetName(tempName);
    }
  };
  
  return (
    <div className="welcome-form">
      <h3>欢迎来到我们的平台</h3>
      <p>请输入您的名字继续</p>
      <form onSubmit={handleSubmit}>
        <input 
          type="text" 
          value={tempName}
          onChange={(e) => setTempName(e.target.value)}
          placeholder="输入您的名字"
          required
        />
        <button type="submit">继续</button>
      </form>
    </div>
  );
}

function VerificationPrompt({ onVerify }) {
  return (
    <div className="verification-prompt">
      <h3>验证您的账户</h3>
      <p>请验证您的账户以解锁更多功能</p>
      <button onClick={onVerify}>验证账户</button>
    </div>
  );
}

function FreeDashboard({ userName, theme }) {
  return (
    <div className={`dashboard free-dashboard ${theme}`}>
      <h3>免费版仪表盘 - {userName}</h3>
      <p>您正在使用免费版，功能有限</p>
      <ul>
        <li>基础功能</li>
        <li>有限的存储空间</li>
        <li>基础支持</li>
      </ul>
    </div>
  );
}

function BasicDashboard({ userName, theme }) {
  return (
    <div className={`dashboard basic-dashboard ${theme}`}>
      <h3>基础版仪表盘 - {userName}</h3>
      <p>您正在使用基础版，功能有所提升</p>
      <ul>
        <li>所有免费功能</li>
        <li>更多存储空间</li>
        <li>优先支持</li>
        <li>高级分析</li>
      </ul>
    </div>
  );
}

function PremiumDashboard({ userName, theme }) {
  return (
    <div className={`dashboard premium-dashboard ${theme}`}>
      <h3>高级版仪表盘 - {userName}</h3>
      <p>您正在使用高级版，享受所有功能</p>
      <ul>
        <li>所有基础功能</li>
        <li>无限存储空间</li>
        <li>专属支持</li>
        <li>高级分析</li>
        <li>API访问</li>
        <li>自定义功能</li>
      </ul>
    </div>
  );
}

export const AdvancedRenderingDemo = () => {
  return (
    <div className="demo-container">
      <div className="demo-description">
        <h2>高级渲染技术示例</h2>
        <p>本示例演示了React中的高级渲染技术，包括动态组件渲染、高阶条件渲染模式、自定义渲染逻辑Hook、条件渲染性能优化以及复杂条件渲染场景。</p>
      </div>

      <div className="examples-grid">
        <DynamicComponentExample />
        <HOCConditionalExample />
        <CustomRenderHookExample />
        <PerformanceOptimizationExample />
        <ComplexConditionalExample />
      </div>
      
      <div className="demo-info">
        <h3>高级渲染要点</h3>
        <ul>
          <li>使用组件映射表实现动态组件渲染</li>
          <li>高阶组件可以封装常见的条件渲染模式</li>
          <li>自定义Hook可以提取和复用复杂的渲染逻辑</li>
          <li>使用React.memo和useMemo优化条件渲染性能</li>
          <li>复杂条件渲染应该分解为多个简单条件</li>
          <li>考虑使用状态机模式管理复杂的状态转换</li>
        </ul>
      </div>
    </div>
  );
};
import React, { useState, useMemo } from 'react';

// 基本列表渲染
function BasicListExample() {
  const [items] = useState([
    { id: 1, name: '苹果', color: 'red' },
    { id: 2, name: '香蕉', color: 'yellow' },
    { id: 3, name: '橙子', color: 'orange' },
    { id: 4, name: '葡萄', color: 'purple' }
  ]);
  
  // 正确的使用方式：使用稳定的ID作为key
  const renderCorrectList = () => (
    <ul className="fruit-list">
      {items.map(item => (
        <li key={item.id} style={{ color: item.color }}>
          {item.name}
        </li>
      ))}
    </ul>
  );
  
  // 错误的使用方式：使用索引作为key
  const renderIncorrectList = () => (
    <ul className="fruit-list">
      {items.map((item, index) => (
        <li key={index} style={{ color: item.color }}>
          {item.name}
        </li>
      ))}
    </ul>
  );
  
  return (
    <div className="example-section">
      <h3>基本列表渲染</h3>
      
      <div className="demo-container">
        <div className="list-example">
          <h4>正确使用ID作为Key</h4>
          <p>每个列表项都有唯一的、稳定的key</p>
          {renderCorrectList()}
        </div>
        
        <div className="list-example">
          <h4>错误使用索引作为Key</h4>
          <p>当列表项顺序变化时，可能导致状态问题</p>
          {renderIncorrectList()}
        </div>
      </div>
    </div>
  );
}

// 动态列表操作
function DynamicListExample() {
  const [items, setItems] = useState([
    { id: 1, text: '学习React基础' },
    { id: 2, text: '理解组件与Props' },
    { id: 3, text: '掌握状态管理' }
  ]);
  
  const [newItemText, setNewItemText] = useState('');
  const [nextId, setNextId] = useState(4);
  
  // 添加新项
  const addItem = () => {
    if (newItemText.trim()) {
      setItems([...items, { id: nextId, text: newItemText }]);
      setNextId(nextId + 1);
      setNewItemText('');
    }
  };
  
  // 删除项
  const deleteItem = (id) => {
    setItems(items.filter(item => item.id !== id));
  };
  
  // 更新项
  const updateItem = (id, newText) => {
    setItems(items.map(item =>
      item.id === id ? { ...item, text: newText } : item
    ));
  };
  
  // 重新排序
  const moveItem = (id, direction) => {
    const index = items.findIndex(item => item.id === id);
    if (index === -1) return;
    
    const newItems = [...items];
    const newIndex = direction === 'up' ? index - 1 : index + 1;
    
    // 检查边界
    if (newIndex < 0 || newIndex >= items.length) return;
    
    // 交换位置
    [newItems[index], newItems[newIndex]] = [newItems[newIndex], newItems[index]];
    setItems(newItems);
  };
  
  return (
    <div className="example-section">
      <h3>动态列表操作</h3>
      
      <div className="demo-container">
        <div className="add-item">
          <input
            type="text"
            value={newItemText}
            onChange={(e) => setNewItemText(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && addItem()}
            placeholder="添加新项目"
          />
          <button onClick={addItem}>添加</button>
        </div>
        
        <ul className="dynamic-list">
          {items.map((item, index) => (
            <li key={item.id} className="list-item">
              <span className="item-index">{index + 1}</span>
              <span 
                className="item-text"
                contentEditable
                suppressContentEditableWarning
                onBlur={(e) => updateItem(item.id, e.target.textContent)}
              >
                {item.text}
              </span>
              <div className="item-actions">
                <button 
                  onClick={() => moveItem(item.id, 'up')}
                  disabled={index === 0}
                >
                  ↑
                </button>
                <button 
                  onClick={() => moveItem(item.id, 'down')}
                  disabled={index === items.length - 1}
                >
                  ↓
                </button>
                <button onClick={() => deleteItem(item.id)}>
                  ×
                </button>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

// 条件列表渲染
function ConditionalListExample() {
  const [users] = useState([
    { id: 1, name: '张三', age: 28, department: '技术部', active: true },
    { id: 2, name: '李四', age: 32, department: '市场部', active: true },
    { id: 3, name: '王五', age: 24, department: '技术部', active: false },
    { id: 4, name: '赵六', age: 35, department: '人事部', active: true },
    { id: 5, name: '钱七', age: 29, department: '财务部', active: false },
    { id: 6, name: '孙八', age: 26, department: '技术部', active: true }
  ]);
  
  const [filter, setFilter] = useState('all');
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');
  
  // 过滤逻辑
  const filteredUsers = useMemo(() => {
    switch(filter) {
      case 'active':
        return users.filter(user => user.active);
      case 'inactive':
        return users.filter(user => !user.active);
      case 'tech':
        return users.filter(user => user.department === '技术部');
      case 'non-tech':
        return users.filter(user => user.department !== '技术部');
      default:
        return users;
    }
  }, [users, filter]);
  
  // 排序逻辑
  const sortedUsers = useMemo(() => {
    const sorted = [...filteredUsers];
    
    sorted.sort((a, b) => {
      let aVal = a[sortBy];
      let bVal = b[sortBy];
      
      // 对于字符串，使用本地化比较
      if (typeof aVal === 'string') {
        aVal = aVal.toLowerCase();
        bVal = bVal.toLowerCase();
      }
      
      let result = 0;
      if (aVal > bVal) result = 1;
      else if (aVal < bVal) result = -1;
      
      return sortOrder === 'asc' ? result : -result;
    });
    
    return sorted;
  }, [filteredUsers, sortBy, sortOrder]);
  
  return (
    <div className="example-section">
      <h3>条件列表渲染</h3>
      
      <div className="demo-container">
        <div className="controls">
          <div className="filter-controls">
            <h4>过滤器</h4>
            <select value={filter} onChange={(e) => setFilter(e.target.value)}>
              <option value="all">全部用户</option>
              <option value="active">活跃用户</option>
              <option value="inactive">非活跃用户</option>
              <option value="tech">技术部</option>
              <option value="non-tech">非技术部</option>
            </select>
          </div>
          
          <div className="sort-controls">
            <h4>排序</h4>
            <div className="sort-options">
              <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                <option value="name">按姓名</option>
                <option value="age">按年龄</option>
                <option value="department">按部门</option>
              </select>
              <button 
                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
              >
                {sortOrder === 'asc' ? '升序' : '降序'}
              </button>
            </div>
          </div>
        </div>
        
        <div className="result-summary">
          显示 {sortedUsers.length} / {users.length} 用户
        </div>
        
        <div className="user-list">
          {sortedUsers.length === 0 ? (
            <div className="empty-state">没有符合条件的用户</div>
          ) : (
            sortedUsers.map(user => (
              <div 
                key={user.id} 
                className={`user-card ${user.active ? 'active' : 'inactive'}`}
              >
                <div className="user-avatar">
                  {user.name.charAt(0)}
                </div>
                <div className="user-info">
                  <div className="user-name">{user.name}</div>
                  <div className="user-details">
                    {user.age}岁 · {user.department}
                  </div>
                </div>
                <div className="user-status">
                  {user.active ? '活跃' : '非活跃'}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

// 分页列表
function PaginatedListExample() {
  const [items] = useState(Array.from({ length: 57 }, (_, i) => ({
    id: i + 1,
    name: `项目 ${i + 1}`,
    description: `这是项目 ${i + 1} 的描述信息`
  })));
  
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;
  
  // 计算分页数据
  const totalPages = Math.ceil(items.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentItems = items.slice(startIndex, endIndex);
  
  // 页码数组
  const pageNumbers = Array.from({ length: totalPages }, (_, i) => i + 1);
  
  // 限制显示的页码数量
  const getVisiblePageNumbers = () => {
    const maxVisible = 5;
    const half = Math.floor(maxVisible / 2);
    
    if (totalPages <= maxVisible) {
      return pageNumbers;
    }
    
    let start = Math.max(1, currentPage - half);
    let end = Math.min(totalPages, start + maxVisible - 1);
    
    // 调整开始位置，确保显示足够数量的页码
    if (end - start < maxVisible - 1) {
      start = Math.max(1, end - maxVisible + 1);
    }
    
    // 添加省略号
    const visiblePages = pageNumbers.slice(start - 1, end);
    
    if (start > 1) {
      visiblePages.unshift(1, '...');
    }
    
    if (end < totalPages) {
      visiblePages.push('...', totalPages);
    }
    
    return visiblePages;
  };
  
  const visiblePageNumbers = getVisiblePageNumbers();
  
  return (
    <div className="example-section">
      <h3>分页列表渲染</h3>
      
      <div className="demo-container">
        <div className="pagination-summary">
          显示第 {startIndex + 1}-{Math.min(endIndex, items.length)} 项，共 {items.length} 项
        </div>
        
        <div className="paginated-list">
          {currentItems.map(item => (
            <div key={item.id} className="list-item">
              <div className="item-number">{item.id}</div>
              <div className="item-content">
                <div className="item-name">{item.name}</div>
                <div className="item-description">{item.description}</div>
              </div>
            </div>
          ))}
        </div>
        
        <div className="pagination-controls">
          <button 
            onClick={() => setCurrentPage(1)}
            disabled={currentPage === 1}
          >
            首页
          </button>
          
          <button 
            onClick={() => setCurrentPage(currentPage - 1)}
            disabled={currentPage === 1}
          >
            上一页
          </button>
          
          {visiblePageNumbers.map((page, index) => (
            page === '...' ? (
              <span key={`ellipsis-${index}`} className="ellipsis">...</span>
            ) : (
              <button 
                key={page}
                onClick={() => setCurrentPage(page)}
                className={currentPage === page ? 'active' : ''}
              >
                {page}
              </button>
            )
          ))}
          
          <button 
            onClick={() => setCurrentPage(currentPage + 1)}
            disabled={currentPage === totalPages}
          >
            下一页
          </button>
          
          <button 
            onClick={() => setCurrentPage(totalPages)}
            disabled={currentPage === totalPages}
          >
            末页
          </button>
        </div>
      </div>
    </div>
  );
}

// 虚拟列表（简化版）
function VirtualListExample() {
  const [items] = useState(Array.from({ length: 10000 }, (_, i) => ({
    id: i + 1,
    text: `虚拟列表项目 ${i + 1}`
  })));
  
  const [scrollTop, setScrollTop] = useState(0);
  const containerHeight = 300;
  const itemHeight = 30;
  
  // 计算可见范围
  const startIndex = Math.floor(scrollTop / itemHeight);
  const endIndex = Math.min(
    startIndex + Math.ceil(containerHeight / itemHeight) + 5, // 添加5个缓冲项
    items.length - 1
  );
  
  // 获取可见项目
  const visibleItems = items.slice(startIndex, endIndex + 1);
  
  const handleScroll = (e) => {
    setScrollTop(e.target.scrollTop);
  };
  
  return (
    <div className="example-section">
      <h3>虚拟列表渲染</h3>
      
      <div className="demo-container">
        <div className="virtual-list-info">
          渲染 {visibleItems.length} / {items.length} 项
        </div>
        
        <div 
          className="virtual-list-container"
          style={{ height: containerHeight }}
          onScroll={handleScroll}
        >
          <div 
            className="virtual-list-spacer"
            style={{ height: items.length * itemHeight }}
          >
            {visibleItems.map((item, index) => (
              <div
                key={item.id}
                className="virtual-list-item"
                style={{
                  position: 'absolute',
                  top: (startIndex + index) * itemHeight,
                  height: itemHeight,
                  width: '100%'
                }}
              >
                {item.text}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// 性能优化示例
function PerformanceOptimizedList() {
  const [items] = useState(Array.from({ length: 1000 }, (_, i) => ({
    id: i + 1,
    name: `用户 ${i + 1}`,
    email: `user${i + 1}@example.com`,
    selected: false
  })));
  
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCount, setSelectedCount] = useState(0);
  
  // 使用useMemo缓存过滤结果，避免每次渲染都重新计算
  const filteredItems = useMemo(() => {
    console.log('重新计算过滤列表');
    return items.filter(item =>
      item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.email.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [items, searchTerm]);
  
  // 使用React.memo优化的列表项组件
  const OptimizedListItem = React.memo(({ item, onSelect, index }) => {
    return (
      <div className="optimized-list-item">
        <span className="item-index">{index}</span>
        <input
          type="checkbox"
          checked={item.selected}
          onChange={() => onSelect(item.id)}
        />
        <span className="item-name">{item.name}</span>
        <span className="item-email">{item.email}</span>
      </div>
    );
  });
  
  const handleSelectItem = (id) => {
    // 这里应该更新状态，但为了简化示例，我们只计算选中的数量
    const selected = filteredItems.filter(item => item.selected).length;
    setSelectedCount(id ? selected + 1 : selected - 1);
  };
  
  return (
    <div className="example-section">
      <h3>性能优化示例</h3>
      
      <div className="demo-container">
        <div className="search-box">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="搜索用户..."
          />
          <div className="selected-count">
            已选择: {selectedCount} 项
          </div>
        </div>
        
        <div className="performance-info">
          总共 {items.length} 项，过滤后 {filteredItems.length} 项
        </div>
        
        <div className="optimized-list">
          {filteredItems.map((item, index) => (
            <OptimizedListItem
              key={item.id}
              item={item}
              index={index}
              onSelect={handleSelectItem}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export const ListRenderingDemo = () => {
  return (
    <div className="demo-container">
      <div className="demo-description">
        <h2>列表渲染示例</h2>
        <p>本示例演示了React中各种列表渲染技术，包括基本列表渲染、动态列表操作、条件渲染、分页、虚拟列表以及性能优化技巧。</p>
      </div>

      <div className="examples-grid">
        <BasicListExample />
        <DynamicListExample />
        <ConditionalListExample />
        <PaginatedListExample />
        <VirtualListExample />
        <PerformanceOptimizedList />
      </div>
      
      <div className="demo-info">
        <h3>列表渲染要点</h3>
        <ul>
          <li>始终为列表项提供稳定、唯一的key</li>
          <li>使用map方法渲染列表，而不是for循环</li>
          <li>对于大型列表，考虑使用分页或虚拟滚动技术</li>
          <li>使用React.memo优化列表项组件，减少不必要的渲染</li>
          <li>使用useMemo缓存派生数据，避免重复计算</li>
          <li>考虑使用CSS隐藏而非条件渲染来保持列表项状态</li>
        </ul>
      </div>
    </div>
  );
};
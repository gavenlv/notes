# 第4章：条件渲染与列表渲染 - 动态构建React UI

## 章节介绍

条件渲染和列表渲染是React中构建动态UI的核心技术。条件渲染允许我们根据应用状态显示或隐藏组件，而列表渲染使我们能够高效地渲染数据集合。这两种渲染方式构成了现代Web应用的基础。

本章将深入探讨：
- 条件渲染的多种实现方式
- 列表渲染与Keys的重要性
- 高阶条件渲染模式
- 动态组件渲染
- 性能优化技巧
- 常见陷阱与最佳实践

通过本章学习，你将掌握如何根据状态动态构建UI，并了解如何高效处理列表数据。

## 条件渲染基础

### 什么是条件渲染？

条件渲染是指根据某些条件（通常是应用状态）来决定是否渲染某些元素或组件。这是React中实现动态UI的基本机制。

条件渲染的常见场景：
- 根据用户权限显示不同UI
- 根据数据加载状态显示加载指示器或错误信息
- 根据用户选择显示不同的内容面板
- 根据设备类型或屏幕尺寸调整UI

### 基本条件渲染方式

#### 1. 使用if语句（在render外）

```jsx
function UserGreeting(props) {
  const { isLoggedIn } = props;
  
  if (isLoggedIn) {
    return <h1>欢迎回来!</h1>;
  }
  
  return <h1>请先登录</h1>;
}
```

#### 2. 使用三元运算符

```jsx
function UserGreeting(props) {
  const { isLoggedIn } = props;
  
  return (
    <div>
      <h1>{isLoggedIn ? '欢迎回来!' : '请先登录'}</h1>
      {isLoggedIn && <UserDashboard />}
    </div>
  );
}
```

#### 3. 使用逻辑与(&&)运算符

```jsx
function Notification(props) {
  const { message } = props;
  
  return (
    <div>
      <h1>通知中心</h1>
      {message && (
        <div className="notification">
          {message}
        </div>
      )}
    </div>
  );
}
```

### 选择合适的条件渲染方式

不同的条件渲染方式适用于不同的场景：

| 场景 | 推荐方式 | 原因 |
|------|----------|------|
| 两个互斥的渲染选项 | 三元运算符 | 语法简洁，表达性强 |
| 简单的条件显示/隐藏 | 逻辑与(&&) | 语法最简洁，直观 |
| 复杂的条件逻辑 | if语句或提取为函数 | 代码更清晰，易于维护 |
| 多个条件分支 | if/else链或switch语句 | 结构清晰，易于扩展 |

## 高级条件渲染模式

### 多条件渲染

#### 1. 多元条件渲染

```jsx
function Alert({ type, message }) {
  let alertClass = 'alert';
  let icon = null;
  
  switch(type) {
    case 'success':
      alertClass += ' alert-success';
      icon = <SuccessIcon />;
      break;
    case 'warning':
      alertClass += ' alert-warning';
      icon = <WarningIcon />;
      break;
    case 'error':
      alertClass += ' alert-error';
      icon = <ErrorIcon />;
      break;
    default:
      alertClass += ' alert-info';
      icon = <InfoIcon />;
  }
  
  return (
    <div className={alertClass}>
      {icon}
      <span>{message}</span>
    </div>
  );
}
```

#### 2. 条件渲染映射表

```jsx
function StatusBadge({ status }) {
  const statusConfig = {
    pending: { text: '待处理', color: 'orange' },
    approved: { text: '已批准', color: 'green' },
    rejected: { text: '已拒绝', color: 'red' }
  };
  
  const config = statusConfig[status] || { text: '未知', color: 'gray' };
  
  return (
    <span style={{ color: config.color }}>
      {config.text}
    </span>
  );
}
```

### 防止组件卸载的渲染

有时我们希望在条件改变时不卸载组件，可以使用CSS隐藏而非条件渲染：

```jsx
// 方式1：条件渲染（组件会卸载/挂载）
function TabContent({ activeTab }) {
  if (activeTab === 'profile') {
    return <ProfileTab />;
  }
  
  if (activeTab === 'settings') {
    return <SettingsTab />;
  }
  
  return null;
}

// 方式2：CSS隐藏（组件保持挂载）
function TabContent({ activeTab }) {
  return (
    <div>
      <div style={{ display: activeTab === 'profile' ? 'block' : 'none' }}>
        <ProfileTab />
      </div>
      <div style={{ display: activeTab === 'settings' ? 'block' : 'none' }}>
        <SettingsTab />
      </div>
    </div>
  );
}
```

### 高阶组件模式

```jsx
// 创建一个条件渲染的高阶组件
function withCondition(WrappedComponent, condition) {
  return function ConditionalComponent(props) {
    if (condition(props)) {
      return <WrappedComponent {...props} />;
    }
    return null;
  };
}

// 使用高阶组件
const AdminOnlyPanel = withCondition(AdminPanel, props => props.isAdmin);
const LoggedInUserMenu = withCondition(UserMenu, props => props.isLoggedIn);
```

## 列表渲染基础

### 使用map渲染列表

在React中，我们使用数组的`map`方法来渲染列表：

```jsx
function TodoList({ todos }) {
  return (
    <ul>
      {todos.map(todo => (
        <li key={todo.id}>
          {todo.text}
        </li>
      ))}
    </ul>
  );
}

// 使用示例
const todos = [
  { id: 1, text: '学习React' },
  { id: 2, text: '构建应用' },
  { id: 3, text: '部署上线' }
];

function App() {
  return <TodoList todos={todos} />;
}
```

### Keys的重要性

Keys帮助React识别哪些元素发生了变化、添加或删除。Keys应该是稳定的、唯一的、可预测的。

```jsx
// 正确：使用唯一且稳定的ID作为key
function TodoList({ todos }) {
  return (
    <ul>
      {todos.map(todo => (
        <li key={todo.id}>  {/* 使用唯一的ID */}
          {todo.text}
        </li>
      ))}
    </ul>
  );
}

// 错误：使用数组索引作为key（当列表项顺序可能变化时）
function TodoList({ todos }) {
  return (
    <ul>
      {todos.map((todo, index) => (
        <li key={index}>  {/* 避免使用索引，特别是当列表可能重新排序时 */}
          {todo.text}
        </li>
      ))}
    </ul>
  );
}
```

#### 选择Keys的原则

1. **唯一性**：在兄弟元素中，key应该是唯一的
2. **稳定性**：key不应该随时间变化
3. **可预测性**：相同的元素应该始终有相同的key

#### 何时可以使用索引作为Key

以下情况可以安全地使用数组索引作为key：
- 列表是静态的（不会重新排序）
- 列表项没有ID
- 列表不会进行过滤或重新排序

```jsx
// 安全的情况：静态列表，不会重新排序
function StaticList() {
  const items = ['苹果', '香蕉', '橙子'];
  
  return (
    <ul>
      {items.map((item, index) => (
        <li key={index}>{item}</li>
      ))}
    </ul>
  );
}
```

## 高级列表渲染技术

### 条件列表渲染

```jsx
function FilteredList({ items, filter }) {
  const filteredItems = items.filter(item => {
    switch(filter) {
      case 'active':
        return !item.completed;
      case 'completed':
        return item.completed;
      default:
        return true;
    }
  });
  
  return (
    <ul>
      {filteredItems.map(item => (
        <li 
          key={item.id}
          className={item.completed ? 'completed' : ''}
        >
          {item.text}
        </li>
      ))}
    </ul>
  );
}
```

### 分页列表渲染

```jsx
function PaginatedList({ items, itemsPerPage = 10 }) {
  const [currentPage, setCurrentPage] = useState(1);
  
  // 计算当前页的数据
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = items.slice(indexOfFirstItem, indexOfLastItem);
  
  // 计算总页数
  const totalPages = Math.ceil(items.length / itemsPerPage);
  
  return (
    <div>
      <ul>
        {currentItems.map(item => (
          <li key={item.id}>
            {item.text}
          </li>
        ))}
      </ul>
      
      {/* 分页控件 */}
      <div className="pagination">
        <button 
          disabled={currentPage === 1}
          onClick={() => setCurrentPage(currentPage - 1)}
        >
          上一页
        </button>
        
        <span>第 {currentPage} 页 / 共 {totalPages} 页</span>
        
        <button 
          disabled={currentPage === totalPages}
          onClick={() => setCurrentPage(currentPage + 1)}
        >
          下一页
        </button>
      </div>
    </div>
  );
}
```

### 虚拟滚动列表

对于大量数据的列表，虚拟滚动只渲染可见区域的项目，大大提高性能：

```jsx
function VirtualizedList({ items, itemHeight = 50, containerHeight = 300 }) {
  const [scrollTop, setScrollTop] = useState(0);
  
  // 计算可见范围
  const startIndex = Math.floor(scrollTop / itemHeight);
  const endIndex = Math.min(
    startIndex + Math.ceil(containerHeight / itemHeight) + 1, // 添加缓冲项
    items.length - 1
  );
  
  // 计算可见项目
  const visibleItems = items.slice(startIndex, endIndex + 1);
  
  const handleScroll = (e) => {
    setScrollTop(e.target.scrollTop);
  };
  
  return (
    <div 
      style={{ height: containerHeight, overflow: 'auto' }}
      onScroll={handleScroll}
    >
      <div style={{ height: items.length * itemHeight, position: 'relative' }}>
        {visibleItems.map((item, index) => (
          <div
            key={startIndex + index}
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
  );
}
```

## 动态组件渲染

### 基于状态渲染不同组件

```jsx
function Dashboard({ userRole, activeView }) {
  const renderView = () => {
    // 根据用户角色决定可以访问的视图
    const accessibleViews = {
      admin: ['overview', 'users', 'settings', 'analytics'],
      editor: ['overview', 'content', 'analytics'],
      viewer: ['overview']
    };
    
    const allowedViews = accessibleViews[userRole] || [];
    
    if (!allowedViews.includes(activeView)) {
      return <div>访问被拒绝</div>;
    }
    
    // 根据视图类型渲染相应组件
    const viewComponents = {
      overview: <OverviewView />,
      users: <UsersView />,
      settings: <SettingsView />,
      analytics: <AnalyticsView />,
      content: <ContentView />
    };
    
    return viewComponents[activeView] || <div>视图未找到</div>;
  };
  
  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>管理面板</h1>
        <p>当前角色: {userRole}</p>
      </div>
      
      <div className="dashboard-content">
        {renderView()}
      </div>
    </div>
  );
}
```

### 动态导入与渲染组件

```jsx
import React, { useState, Suspense } from 'react';

// 动态导入组件
const AdminPanel = React.lazy(() => import('./AdminPanel'));
const UserPanel = React.lazy(() => import('./UserPanel'));

function DynamicComponentExample({ userRole }) {
  return (
    <div>
      <h1>动态组件加载示例</h1>
      
      <Suspense fallback={<div>加载中...</div>}>
        {userRole === 'admin' ? (
          <AdminPanel />
        ) : (
          <UserPanel />
        )}
      </Suspense>
    </div>
  );
}
```

## 性能优化技巧

### 使用React.memo优化列表项

```jsx
// 使用React.memo防止不必要的重新渲染
const TodoItem = React.memo(({ todo, onToggle, onDelete }) => {
  console.log(`渲染TodoItem: ${todo.id}`);
  
  return (
    <li className={todo.completed ? 'completed' : ''}>
      <span onClick={() => onToggle(todo.id)}>
        {todo.text}
      </span>
      <button onClick={() => onDelete(todo.id)}>
        删除
      </button>
    </li>
  );
});

function TodoList({ todos, onToggle, onDelete }) {
  return (
    <ul>
      {todos.map(todo => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={onToggle}
          onDelete={onDelete}
        />
      ))}
    </ul>
  );
}
```

### 使用useMemo优化派生数据

```jsx
function FilterableList({ items, filter }) {
  // 使用useMemo缓存过滤结果，避免每次渲染都重新计算
  const filteredItems = useMemo(() => {
    console.log('重新计算过滤列表');
    return items.filter(item => {
      switch(filter) {
        case 'active':
          return !item.completed;
        case 'completed':
          return item.completed;
        default:
          return true;
      }
    });
  }, [items, filter]);
  
  return (
    <ul>
      {filteredItems.map(item => (
        <li key={item.id}>
          {item.text}
        </li>
      ))}
    </ul>
  );
}
```

### 虚拟化长列表

对于大量数据的列表，使用专门的虚拟化库：

```jsx
import { FixedSizeList as List } from 'react-window';

function VirtualizedTodoList({ todos }) {
  const Row = ({ index, style }) => (
    <div style={style}>
      {todos[index].text}
    </div>
  );
  
  return (
    <List
      height={500}
      itemCount={todos.length}
      itemSize={35}
      width="100%"
    >
      {Row}
    </List>
  );
}
```

## 常见陷阱与解决方案

###陷阱1：不正确的Key使用

```jsx
// 问题：使用不稳定的key
function ProblematicList({ users }) {
  return (
    <ul>
      {users.map((user, index) => (
        <li key={index + Math.random()}>  {/* 错误：随机key */}
          <input />
          <span>{user.name}</span>
        </li>
      ))}
    </ul>
  );
}

// 解决方案：使用稳定的唯一ID
function CorrectList({ users }) {
  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>  {/* 正确：使用稳定的ID */}
          <input />
          <span>{user.name}</span>
        </li>
      ))}
    </ul>
  );
}
```

### 陷阱2：条件渲染导致的性能问题

```jsx
// 问题：每次渲染都创建新组件
function ProblematicComponent({ condition, data }) {
  return (
    <div>
      {condition ? (
        <ExpensiveComponent data={data} />  {/* 每次渲染都会创建新组件 */}
      ) : (
        <AnotherComponent data={data} />  {/* 每次渲染都会创建新组件 */}
      )}
    </div>
  );
}

// 解决方案：提前渲染并缓存
function OptimizedComponent({ condition, data }) {
  const expensiveComponent = useMemo(
    () => <ExpensiveComponent data={data} />,
    [data]
  );
  
  const anotherComponent = useMemo(
    () => <AnotherComponent data={data} />,
    [data]
  );
  
  return (
    <div>
      {condition ? expensiveComponent : anotherComponent}
    </div>
  );
}
```

### 陷阱3：列表项状态丢失

```jsx
// 问题：条件渲染导致组件卸载/重新挂载，状态丢失
function ProblematicList({ items, showDetails }) {
  return (
    <ul>
      {items.map(item => (
        <li key={item.id}>
          <span>{item.name}</span>
          {showDetails && (
            <ItemDetails details={item.details} />  {/* 每次条件变化都会卸载/重新挂载 */}
          )}
        </li>
      ))}
    </ul>
  );
}

// 解决方案：使用CSS隐藏而非条件渲染
function OptimizedList({ items, showDetails }) {
  return (
    <ul>
      {items.map(item => (
        <li key={item.id}>
          <span>{item.name}</span>
          <div style={{ display: showDetails ? 'block' : 'none' }}>
            <ItemDetails details={item.details} />  {/* 组件保持挂载，只是显示/隐藏 */}
          </div>
        </li>
      ))}
    </ul>
  );
}
```

## 实践案例：构建动态数据表格

让我们构建一个功能完整的数据表格，综合运用条件渲染和列表渲染：

```jsx
import React, { useState, useMemo } from 'react';

// 自定义Hook用于排序
function useSort(initialData, initialSortKey) {
  const [sortConfig, setSortConfig] = useState({
    key: initialSortKey,
    direction: 'ascending'
  });
  
  const sortedData = useMemo(() => {
    if (!initialData) return [];
    
    const sortableData = [...initialData];
    
    if (sortConfig.key !== null) {
      sortableData.sort((a, b) => {
        const aVal = a[sortConfig.key];
        const bVal = b[sortConfig.key];
        
        if (aVal < bVal) {
          return sortConfig.direction === 'ascending' ? -1 : 1;
        }
        if (aVal > bVal) {
          return sortConfig.direction === 'ascending' ? 1 : -1;
        }
        return 0;
      });
    }
    
    return sortableData;
  }, [initialData, sortConfig]);
  
  const requestSort = (key) => {
    let direction = 'ascending';
    if (
      sortConfig.key === key &&
      sortConfig.direction === 'ascending'
    ) {
      direction = 'descending';
    }
    setSortConfig({ key, direction });
  };
  
  return { sortedData, requestSort, sortConfig };
}

// 自定义Hook用于分页
function usePagination(items, itemsPerPage) {
  const [currentPage, setCurrentPage] = useState(1);
  
  const paginatedItems = useMemo(() => {
    if (!items) return [];
    
    const startIndex = (currentPage - 1) * itemsPerPage;
    return items.slice(startIndex, startIndex + itemsPerPage);
  }, [items, currentPage, itemsPerPage]);
  
  const totalPages = Math.ceil((items?.length || 0) / itemsPerPage);
  
  const goToPage = (page) => setCurrentPage(page);
  const nextPage = () => setCurrentPage(prev => Math.min(prev + 1, totalPages));
  const prevPage = () => setCurrentPage(prev => Math.max(prev - 1, 1));
  
  return {
    paginatedItems,
    currentPage,
    totalPages,
    goToPage,
    nextPage,
    prevPage
  };
}

// 主表格组件
function DataTable({ data, columns }) {
  const [filter, setFilter] = useState('');
  const [selectedRows, setSelectedRows] = useState(new Set());
  
  // 过滤数据
  const filteredData = useMemo(() => {
    if (!data) return [];
    
    if (!filter) return data;
    
    return data.filter(item =>
      columns.some(column => 
        String(item[column.accessor])
          .toLowerCase()
          .includes(filter.toLowerCase())
      )
    );
  }, [data, columns, filter]);
  
  // 排序
  const { sortedData, requestSort, sortConfig } = useSort(filteredData, columns[0]?.accessor);
  
  // 分页
  const {
    paginatedItems,
    currentPage,
    totalPages,
    goToPage,
    nextPage,
    prevPage
  } = usePagination(sortedData, 10);
  
  // 选择行
  const toggleRowSelection = (id) => {
    const newSelectedRows = new Set(selectedRows);
    if (newSelectedRows.has(id)) {
      newSelectedRows.delete(id);
    } else {
      newSelectedRows.add(id);
    }
    setSelectedRows(newSelectedRows);
  };
  
  const toggleAllRowsSelection = () => {
    if (selectedRows.size === paginatedItems.length) {
      setSelectedRows(new Set());
    } else {
      setSelectedRows(new Set(paginatedItems.map(item => item.id)));
    }
  };
  
  return (
    <div className="data-table-container">
      {/* 搜索和操作栏 */}
      <div className="table-actions">
        <input
          type="text"
          placeholder="搜索..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="search-input"
        />
        
        <div className="bulk-actions">
          {selectedRows.size > 0 && (
            <button 
              className="bulk-action-btn"
              onClick={() => alert(`删除 ${selectedRows.size} 条记录`)}
            >
              删除选中 ({selectedRows.size})
            </button>
          )}
        </div>
      </div>
      
      {/* 表格 */}
      <div className="data-table">
        <table>
          <thead>
            <tr>
              <th>
                <input
                  type="checkbox"
                  checked={selectedRows.size === paginatedItems.length && paginatedItems.length > 0}
                  onChange={toggleAllRowsSelection}
                />
              </th>
              {columns.map(column => (
                <th
                  key={column.accessor}
                  onClick={() => requestSort(column.accessor)}
                  className="sortable-header"
                >
                  {column.Header}
                  {sortConfig.key === column.accessor && (
                    <span>
                      {sortConfig.direction === 'ascending' ? ' ↑' : ' ↓'}
                    </span>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginatedItems.length === 0 ? (
              <tr>
                <td colSpan={columns.length + 1} className="no-data">
                  {data?.length === 0 ? '暂无数据' : '没有匹配的结果'}
                </td>
              </tr>
            ) : (
              paginatedItems.map(item => (
                <tr 
                  key={item.id}
                  className={selectedRows.has(item.id) ? 'selected' : ''}
                >
                  <td>
                    <input
                      type="checkbox"
                      checked={selectedRows.has(item.id)}
                      onChange={() => toggleRowSelection(item.id)}
                    />
                  </td>
                  {columns.map(column => (
                    <td key={column.accessor}>
                      {column.Cell ? column.Cell(item) : item[column.accessor]}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      
      {/* 分页控件 */}
      <div className="pagination">
        <button 
          onClick={prevPage} 
          disabled={currentPage === 1}
        >
          上一页
        </button>
        
        <span>
          第 {currentPage} 页，共 {totalPages} 页 (
          {sortedData.length} 条记录)
        </span>
        
        <button 
          onClick={nextPage} 
          disabled={currentPage === totalPages || totalPages === 0}
        >
          下一页
        </button>
      </div>
    </div>
  );
}

// 使用示例
function UserTable() {
  const [users] = useState([
    { id: 1, name: '张三', email: 'zhangsan@example.com', age: 28, active: true },
    { id: 2, name: '李四', email: 'lisi@example.com', age: 32, active: false },
    { id: 3, name: '王五', email: 'wangwu@example.com', age: 24, active: true },
    { id: 4, name: '赵六', email: 'zhaoliu@example.com', age: 36, active: true },
    { id: 5, name: '钱七', email: 'qianqi@example.com', age: 29, active: false },
    { id: 6, name: '孙八', email: 'sunba@example.com', age: 31, active: true },
    { id: 7, name: '周九', email: 'zhoujiu@example.com', age: 26, active: false },
    { id: 8, name: '吴十', email: 'wushi@example.com', age: 33, active: true }
  ]);
  
  const columns = [
    {
      Header: '姓名',
      accessor: 'name'
    },
    {
      Header: '邮箱',
      accessor: 'email'
    },
    {
      Header: '年龄',
      accessor: 'age'
    },
    {
      Header: '状态',
      accessor: 'active',
      Cell: ({ value }) => (
        <span className={value ? 'status-active' : 'status-inactive'}>
          {value ? '活跃' : '非活跃'}
        </span>
      )
    }
  ];
  
  return (
    <div className="user-table-container">
      <h1>用户管理</h1>
      <DataTable data={users} columns={columns} />
    </div>
  );
}
```

## 最佳实践总结

1. **条件渲染最佳实践**：
   - 为简单条件使用逻辑与(&&)或三元运算符
   - 为复杂逻辑提取函数或使用映射表
   - 考虑使用CSS隐藏而非条件渲染来保持状态
   - 谨慎使用条件渲染，避免不必要的组件卸载/挂载

2. **列表渲染最佳实践**：
   - 始终为列表项提供稳定、唯一的key
   - 避免在渲染过程中创建新组件
   - 使用React.memo优化列表项组件
   - 对大型列表考虑虚拟化技术

3. **性能优化技巧**：
   - 使用useMemo缓存派生数据
   - 对大型列表实现分页或虚拟滚动
   - 避免在render中创建新对象或函数
   - 合理使用条件渲染，减少不必要的DOM操作

4. **代码组织技巧**：
   - 将复杂渲染逻辑提取为函数
   - 使用自定义Hook封装列表逻辑
   - 保持组件单一职责
   - 使用TypeScript提高类型安全

## 练习项目

1. **动态表单生成器**：根据JSON配置动态渲染表单字段和验证规则。

2. **可配置的仪表板**：允许用户自定义显示的组件和布局。

3. **高级数据表格**：实现排序、过滤、分页、列选择等功能。

4. **图片画廊**：支持多种布局模式（网格、列表、瀑布流）和筛选功能。

5. **动态导航菜单**：根据用户权限和配置动态渲染导航结构。

## 总结

本章我们深入学习了React中的条件渲染和列表渲染，包括：

- 条件渲染的多种实现方式和适用场景
- 列表渲染的正确方式和Keys的重要性
- 高级渲染技术和性能优化方法
- 常见陷阱与解决方案
- 实践案例：构建功能完整的数据表格

条件渲染和列表渲染是React应用的核心技术，掌握它们将使你能够构建灵活、高效、动态的用户界面。下一章我们将学习表单处理与受控组件，进一步丰富我们的React开发技能。
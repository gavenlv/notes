import React, { useState, useMemo, useCallback } from 'react';

// 自定义排序Hook
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

// 自定义分页Hook
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

// 主数据表格组件
function DataTable({ data, columns, enableSelection = false, enableSearch = true }) {
  const [filter, setFilter] = useState('');
  const [selectedRows, setSelectedRows] = useState(new Set());
  
  // 过滤数据
  const filteredData = useMemo(() => {
    if (!data) return [];
    
    if (!filter) return data;
    
    return data.filter(item =>
      columns.some(column => {
        const value = String(item[column.accessor] || '');
        return value.toLowerCase().includes(filter.toLowerCase());
      })
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
  const toggleRowSelection = useCallback((id) => {
    const newSelectedRows = new Set(selectedRows);
    if (newSelectedRows.has(id)) {
      newSelectedRows.delete(id);
    } else {
      newSelectedRows.add(id);
    }
    setSelectedRows(newSelectedRows);
  }, [selectedRows]);
  
  const toggleAllRowsSelection = useCallback(() => {
    if (selectedRows.size === paginatedItems.length) {
      setSelectedRows(new Set());
    } else {
      setSelectedRows(new Set(paginatedItems.map(item => item.id)));
    }
  }, [selectedRows, paginatedItems]);
  
  const clearSelection = useCallback(() => {
    setSelectedRows(new Set());
  }, []);
  
  const bulkDelete = useCallback(() => {
    if (selectedRows.size === 0) return;
    
    if (window.confirm(`确定要删除选中的 ${selectedRows.size} 条记录吗？`)) {
      // 这里应该调用删除回调函数，但为了示例简化，我们只显示警告
      alert(`已删除 ${selectedRows.size} 条记录`);
      clearSelection();
    }
  }, [selectedRows, clearSelection]);
  
  return (
    <div className="data-table-container">
      {/* 搜索和操作栏 */}
      {enableSearch && (
        <div className="table-actions">
          <input
            type="text"
            placeholder="搜索..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="search-input"
          />
          
          {enableSelection && (
            <div className="bulk-actions">
              {selectedRows.size > 0 && (
                <div className="selected-info">
                  <span>已选择 {selectedRows.size} 条</span>
                  <button 
                    className="bulk-action-btn delete"
                    onClick={bulkDelete}
                  >
                    删除
                  </button>
                  <button 
                    className="bulk-action-btn secondary"
                    onClick={clearSelection}
                  >
                    清除选择
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      )}
      
      {/* 表格 */}
      <div className="data-table">
        <table>
          <thead>
            <tr>
              {enableSelection && (
                <th>
                  <input
                    type="checkbox"
                    checked={selectedRows.size === paginatedItems.length && paginatedItems.length > 0}
                    onChange={toggleAllRowsSelection}
                    disabled={paginatedItems.length === 0}
                  />
                </th>
              )}
              {columns.map(column => (
                <th
                  key={column.accessor}
                  onClick={() => column.sortable !== false && requestSort(column.accessor)}
                  className={column.sortable !== false ? "sortable-header" : ""}
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
                <td colSpan={columns.length + (enableSelection ? 1 : 0)} className="no-data">
                  {data?.length === 0 ? '暂无数据' : '没有匹配的结果'}
                </td>
              </tr>
            ) : (
              paginatedItems.map(item => (
                <tr 
                  key={item.id}
                  className={selectedRows.has(item.id) ? 'selected' : ''}
                >
                  {enableSelection && (
                    <td>
                      <input
                        type="checkbox"
                        checked={selectedRows.has(item.id)}
                        onChange={() => toggleRowSelection(item.id)}
                      />
                    </td>
                  )}
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
        <div className="pagination-info">
          显示第 {(currentPage - 1) * 10 + 1}-{Math.min(currentPage * 10, sortedData.length)} 项，共 {sortedData.length} 项
        </div>
        
        <div className="pagination-controls">
          <button 
            onClick={prevPage} 
            disabled={currentPage === 1}
          >
            上一页
          </button>
          
          {/* 页码按钮 */}
          <div className="page-numbers">
            {(() => {
              const maxVisiblePages = 5;
              const totalPagesCount = totalPages;
              const currentPageNum = currentPage;
              
              if (totalPagesCount <= maxVisiblePages) {
                return Array.from({ length: totalPagesCount }, (_, i) => i + 1).map(page => (
                  <button
                    key={page}
                    onClick={() => goToPage(page)}
                    className={page === currentPageNum ? 'active' : ''}
                  >
                    {page}
                  </button>
                ));
              }
              
              // 复杂分页逻辑
              const pages = [];
              const half = Math.floor(maxVisiblePages / 2);
              
              // 显示第一页
              if (currentPageNum > half + 1) {
                pages.push(1);
                if (currentPageNum > half + 2) {
                  pages.push('...');
                }
              }
              
              // 显示中间页码
              const start = Math.max(1, currentPageNum - half);
              const end = Math.min(totalPagesCount, start + maxVisiblePages - 1);
              
              for (let i = start; i <= end; i++) {
                pages.push(i);
              }
              
              // 显示最后一页
              if (end < totalPagesCount) {
                if (end < totalPagesCount - 1) {
                  pages.push('...');
                }
                pages.push(totalPagesCount);
              }
              
              return pages.map((page, index) => 
                page === '...' ? (
                  <span key={`ellipsis-${index}`} className="ellipsis">...</span>
                ) : (
                  <button
                    key={page}
                    onClick={() => goToPage(page)}
                    className={page === currentPageNum ? 'active' : ''}
                  >
                    {page}
                  </button>
                )
              );
            })()}
          </div>
          
          <button 
            onClick={nextPage} 
            disabled={currentPage === totalPages || totalPages === 0}
          >
            下一页
          </button>
        </div>
      </div>
    </div>
  );
}

// 用户表示例
function UserTableExample() {
  const [users] = useState([
    { id: 1, name: '张三', email: 'zhangsan@example.com', age: 28, department: '技术部', status: 'active' },
    { id: 2, name: '李四', email: 'lisi@example.com', age: 32, department: '市场部', status: 'inactive' },
    { id: 3, name: '王五', email: 'wangwu@example.com', age: 24, department: '技术部', status: 'active' },
    { id: 4, name: '赵六', email: 'zhaoliu@example.com', age: 36, department: '人事部', status: 'active' },
    { id: 5, name: '钱七', email: 'qianqi@example.com', age: 29, department: '财务部', status: 'inactive' },
    { id: 6, name: '孙八', email: 'sunba@example.com', age: 31, department: '技术部', status: 'active' },
    { id: 7, name: '周九', email: 'zhoujiu@example.com', age: 26, department: '市场部', status: 'active' },
    { id: 8, name: '吴十', email: 'wushi@example.com', age: 33, department: '技术部', status: 'inactive' },
    { id: 9, name: '郑十一', email: 'zheng11@example.com', age: 27, department: '人事部', status: 'active' },
    { id: 10, name: '王十二', email: 'wang12@example.com', age: 30, department: '财务部', status: 'active' },
    { id: 11, name: '刘十三', email: 'liu13@example.com', age: 35, department: '市场部', status: 'inactive' },
    { id: 12, name: '陈十四', email: 'chen14@example.com', age: 25, department: '技术部', status: 'active' }
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
      Header: '部门',
      accessor: 'department'
    },
    {
      Header: '状态',
      accessor: 'status',
      Cell: ({ value }) => (
        <span className={`status-badge ${value}`}>
          {value === 'active' ? '活跃' : '非活跃'}
        </span>
      )
    }
  ];
  
  return (
    <div className="table-example">
      <h3>用户管理表格</h3>
      <DataTable 
        data={users} 
        columns={columns} 
        enableSelection={true}
        enableSearch={true}
      />
    </div>
  );
}

// 产品表示例
function ProductTableExample() {
  const [products] = useState([
    { id: 1, name: 'React 入门教程', category: '书籍', price: 59.99, stock: 120, rating: 4.5 },
    { id: 2, name: 'JavaScript 高级编程', category: '书籍', price: 79.99, stock: 85, rating: 4.8 },
    { id: 3, name: 'React 开发工具', category: '软件', price: 99.00, stock: 50, rating: 4.2 },
    { id: 4, name: 'React Native 实战', category: '视频课程', price: 129.99, stock: 200, rating: 4.7 },
    { id: 5, name: 'Vue.js 从入门到精通', category: '书籍', price: 69.99, stock: 95, rating: 4.6 },
    { id: 6, name: 'Node.js 实战教程', category: '视频课程', price: 149.99, stock: 150, rating: 4.4 },
    { id: 7, name: 'CSS 动画设计', category: '软件', price: 89.00, stock: 70, rating: 4.3 },
    { id: 8, name: '前端工程化实践', category: '书籍', price: 89.99, stock: 60, rating: 4.9 },
    { id: 9, name: 'React Hooks 深入解析', category: '视频课程', price: 109.99, stock: 180, rating: 4.7 },
    { id: 10, name: 'TypeScript 全面指南', category: '书籍', price: 79.99, stock: 110, rating: 4.6 },
    { id: 11, name: 'Webpack 配置详解', category: '视频课程', price: 119.99, stock: 90, rating: 4.1 },
    { id: 12, name: '前端性能优化', category: '书籍', price: 75.99, stock: 130, rating: 4.8 }
  ]);
  
  const columns = [
    {
      Header: '产品名称',
      accessor: 'name'
    },
    {
      Header: '类别',
      accessor: 'category',
      Cell: ({ value }) => (
        <span className={`category-badge ${value.toLowerCase().replace(/\s+/g, '-')}`}>
          {value}
        </span>
      )
    },
    {
      Header: '价格',
      accessor: 'price',
      Cell: ({ value }) => (
        <span className="price">¥{value.toFixed(2)}</span>
      )
    },
    {
      Header: '库存',
      accessor: 'stock',
      Cell: ({ value }) => (
        <div className="stock-indicator">
          <span>{value}</span>
          <div 
            className={`stock-bar ${value < 100 ? 'low' : value < 200 ? 'medium' : 'high'}`}
            style={{ width: `${Math.min(100, value / 5)}%` }}
          ></div>
        </div>
      )
    },
    {
      Header: '评分',
      accessor: 'rating',
      Cell: ({ value }) => (
        <div className="rating">
          <span>{value}</span>
          <div className="stars">
            {Array.from({ length: 5 }, (_, i) => (
              <span 
                key={i} 
                className={`star ${i < Math.floor(value) ? 'filled' : 'empty'}`}
              >
                ★
              </span>
            ))}
          </div>
        </div>
      )
    }
  ];
  
  return (
    <div className="table-example">
      <h3>产品管理表格</h3>
      <DataTable 
        data={products} 
        columns={columns}
        enableSelection={true}
        enableSearch={true}
      />
    </div>
  );
}

// 自定义表格配置示例
function CustomTableExample() {
  const [data] = useState([
    { id: 1, name: 'React', stars: 178000, license: 'MIT', language: 'JavaScript' },
    { id: 2, name: 'Vue', stars: 199000, license: 'MIT', language: 'JavaScript' },
    { id: 3, name: 'Angular', stars: 83000, license: 'MIT', language: 'TypeScript' },
    { id: 4, name: 'Svelte', stars: 64000, license: 'MIT', language: 'JavaScript' },
    { id: 5, name: 'Next.js', stars: 98000, license: 'MIT', language: 'JavaScript' },
    { id: 6, name: 'Nuxt', stars: 43000, license: 'MIT', language: 'TypeScript' },
    { id: 7, name: 'Gatsby', stars: 53000, license: 'MIT', language: 'JavaScript' },
    { id: 8, name: 'Remix', stars: 21000, license: 'MIT', language: 'TypeScript' }
  ]);
  
  const [tableConfig, setTableConfig] = useState({
    enableSelection: false,
    enableSearch: true,
    itemsPerPage: 5
  });
  
  const columns = [
    {
      Header: '框架',
      accessor: 'name',
      Cell: ({ value }) => (
        <div className="framework-name">
          <span>{value}</span>
        </div>
      )
    },
    {
      Header: 'Stars',
      accessor: 'stars',
      Cell: ({ value }) => (
        <div className="stars-count">
          <span>{value.toLocaleString()}</span>
          <div className="stars-bar" style={{ width: `${Math.min(100, value / 2000)}%` }}></div>
        </div>
      ),
      sortable: false
    },
    {
      Header: '许可证',
      accessor: 'license',
      Cell: ({ value }) => (
        <span className={`license ${value.toLowerCase().replace(/\s+/g, '-')}`}>
          {value}
        </span>
      )
    },
    {
      Header: '主要语言',
      accessor: 'language',
      Cell: ({ value }) => (
        <span className={`language ${value.toLowerCase().replace(/\s+/g, '-')}`}>
          {value}
        </span>
      )
    }
  ];
  
  return (
    <div className="table-example">
      <h3>自定义表格配置</h3>
      
      <div className="table-config">
        <h4>表格设置</h4>
        <div className="config-options">
          <label>
            <input
              type="checkbox"
              checked={tableConfig.enableSelection}
              onChange={(e) => setTableConfig(prev => ({ 
                ...prev, 
                enableSelection: e.target.checked 
              }))}
            />
            启用多选
          </label>
          
          <label>
            <input
              type="checkbox"
              checked={tableConfig.enableSearch}
              onChange={(e) => setTableConfig(prev => ({ 
                ...prev, 
                enableSearch: e.target.checked 
              }))}
            />
            启用搜索
          </label>
          
          <div className="items-per-page">
            <label>每页显示:</label>
            <select
              value={tableConfig.itemsPerPage}
              onChange={(e) => setTableConfig(prev => ({ 
                ...prev, 
                itemsPerPage: parseInt(e.target.value) 
              }))}
            >
              <option value={5}>5</option>
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
            </select>
          </div>
        </div>
      </div>
      
      <DataTable 
        data={data} 
        columns={columns}
        enableSelection={tableConfig.enableSelection}
        enableSearch={tableConfig.enableSearch}
        itemsPerPage={tableConfig.itemsPerPage}
      />
    </div>
  );
}

export const DataTableDemo = () => {
  const [activeTable, setActiveTable] = useState('users');
  
  return (
    <div className="demo-container">
      <div className="demo-description">
        <h2>数据表格示例</h2>
        <p>这是一个功能完整的数据表格组件，支持排序、分页、搜索、多选等功能。表格组件采用高度可配置的设计，可以适应各种数据展示场景。</p>
      </div>

      <div className="table-tabs">
        <button 
          className={activeTable === 'users' ? 'active' : ''}
          onClick={() => setActiveTable('users')}
        >
          用户表格
        </button>
        <button 
          className={activeTable === 'products' ? 'active' : ''}
          onClick={() => setActiveTable('products')}
        >
          产品表格
        </button>
        <button 
          className={activeTable === 'custom' ? 'active' : ''}
          onClick={() => setActiveTable('custom')}
        >
          自定义配置
        </button>
      </div>
      
      <div className="table-content">
        {activeTable === 'users' && <UserTableExample />}
        {activeTable === 'products' && <ProductTableExample />}
        {activeTable === 'custom' && <CustomTableExample />}
      </div>
      
      <div className="demo-info">
        <h3>数据表格技术要点</h3>
        <ul>
          <li>使用自定义Hook封装排序和分页逻辑，提高代码复用性</li>
          <li>列配置对象使表格高度可配置，支持自定义单元格渲染</li>
          <li>使用useMemo缓存派生数据，避免不必要的重新计算</li>
          <li>使用useCallback优化事件处理函数，减少子组件重新渲染</li>
          <li>实现高效的多选功能，支持全选、批量操作等</li>
          <li>分页组件支持智能页码显示，处理大量页码的情况</li>
          <li>灵活的单元格渲染机制，支持各种数据类型的展示</li>
        </ul>
      </div>
    </div>
  );
};
import React, { useState, useEffect } from 'react';

// 任务管理器主组件
export function TaskManagerDemo() {
  const [tasks, setTasks] = useState([
    { id: 1, text: '学习React基础', completed: true, priority: 'high' },
    { id: 2, text: '理解组件与Props', completed: true, priority: 'medium' },
    { id: 3, text: '掌握状态管理', completed: false, priority: 'high' },
    { id: 4, text: '学习事件处理', completed: false, priority: 'low' }
  ]);
  
  const [inputValue, setInputValue] = useState('');
  const [filter, setFilter] = useState('all'); // all, active, completed
  const [priority, setPriority] = useState('medium'); // high, medium, low
  const [editingId, setEditingId] = useState(null);
  const [editValue, setEditValue] = useState('');
  const [sortBy, setSortBy] = useState('date'); // date, priority, text
  
  // 添加任务
  const addTask = () => {
    if (inputValue.trim()) {
      const newTask = {
        id: Date.now(),
        text: inputValue,
        completed: false,
        priority: priority
      };
      
      setTasks(prevTasks => [...prevTasks, newTask]);
      setInputValue('');
    }
  };
  
  // 删除任务
  const deleteTask = (id) => {
    setTasks(prevTasks => prevTasks.filter(task => task.id !== id));
  };
  
  // 切换任务完成状态
  const toggleTask = (id) => {
    setTasks(prevTasks =>
      prevTasks.map(task =>
        task.id === id ? { ...task, completed: !task.completed } : task
      )
    );
  };
  
  // 开始编辑任务
  const startEditTask = (id, text) => {
    setEditingId(id);
    setEditValue(text);
  };
  
  // 保存编辑的任务
  const saveEditTask = () => {
    if (editValue.trim()) {
      setTasks(prevTasks =>
        prevTasks.map(task =>
          task.id === editingId ? { ...task, text: editValue } : task
        )
      );
      setEditingId(null);
      setEditValue('');
    }
  };
  
  // 取消编辑
  const cancelEdit = () => {
    setEditingId(null);
    setEditValue('');
  };
  
  // 更新任务优先级
  const updateTaskPriority = (id, newPriority) => {
    setTasks(prevTasks =>
      prevTasks.map(task =>
        task.id === id ? { ...task, priority: newPriority } : task
      )
    );
  };
  
  // 切换所有任务完成状态
  const toggleAllTasks = () => {
    const allCompleted = tasks.every(task => task.completed);
    setTasks(prevTasks =>
      prevTasks.map(task => ({ ...task, completed: !allCompleted }))
    );
  };
  
  // 清除已完成的任务
  const clearCompleted = () => {
    setTasks(prevTasks => prevTasks.filter(task => !task.completed));
  };
  
  // 获取过滤后的任务
  const getFilteredTasks = () => {
    let filtered = tasks;
    
    switch (filter) {
      case 'active':
        filtered = tasks.filter(task => !task.completed);
        break;
      case 'completed':
        filtered = tasks.filter(task => task.completed);
        break;
      default:
        filtered = tasks;
    }
    
    // 排序
    filtered = [...filtered].sort((a, b) => {
      switch (sortBy) {
        case 'priority':
          const priorityOrder = { high: 0, medium: 1, low: 2 };
          return priorityOrder[a.priority] - priorityOrder[b.priority];
        case 'text':
          return a.text.localeCompare(b.text);
        case 'date':
        default:
          return b.id - a.id; // 按ID降序（最新的在前）
      }
    });
    
    return filtered;
  };
  
  // 获取任务统计
  const getTaskStats = () => {
    const total = tasks.length;
    const completed = tasks.filter(task => task.completed).length;
    const active = total - completed;
    
    return { total, completed, active };
  };
  
  const stats = getTaskStats();
  const filteredTasks = getFilteredTasks();
  const allCompleted = tasks.length > 0 && tasks.every(task => task.completed);
  
  return (
    <div className="task-manager-container">
      <div className="task-manager-header">
        <h1>任务管理器</h1>
        <div className="stats">
          <span>总计: {stats.total}</span>
          <span>已完成: {stats.completed}</span>
          <span>未完成: {stats.active}</span>
        </div>
      </div>
      
      {/* 添加任务区域 */}
      <div className="add-task-section">
        <div className="input-group">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && addTask()}
            placeholder="添加新任务..."
          />
          <select
            value={priority}
            onChange={(e) => setPriority(e.target.value)}
            className="priority-select"
          >
            <option value="high">高优先级</option>
            <option value="medium">中优先级</option>
            <option value="low">低优先级</option>
          </select>
          <button onClick={addTask} className="add-btn">添加</button>
        </div>
      </div>
      
      {/* 过滤和排序控制 */}
      <div className="controls-section">
        <div className="filter-controls">
          <span>过滤:</span>
          <button
            onClick={() => setFilter('all')}
            className={filter === 'all' ? 'active' : ''}
          >
            全部
          </button>
          <button
            onClick={() => setFilter('active')}
            className={filter === 'active' ? 'active' : ''}
          >
            未完成
          </button>
          <button
            onClick={() => setFilter('completed')}
            className={filter === 'completed' ? 'active' : ''}
          >
            已完成
          </button>
        </div>
        
        <div className="sort-controls">
          <span>排序:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="date">按日期</option>
            <option value="priority">按优先级</option>
            <option value="text">按文本</option>
          </select>
        </div>
        
        <div className="bulk-actions">
          <button onClick={toggleAllTasks}>
            {allCompleted ? '全部未完成' : '全部完成'}
          </button>
          <button onClick={clearCompleted}>清除已完成</button>
        </div>
      </div>
      
      {/* 任务列表 */}
      <div className="tasks-section">
        {filteredTasks.length === 0 ? (
          <div className="empty-state">
            {filter === 'all' ? '暂无任务，添加一个任务开始吧！' : 
             filter === 'active' ? '太棒了！没有未完成的任务。' : 
             '暂无已完成的任务。'}
          </div>
        ) : (
          <ul className="task-list">
            {filteredTasks.map(task => (
              <li key={task.id} className={`task-item ${task.completed ? 'completed' : ''}`}>
                {editingId === task.id ? (
                  // 编辑模式
                  <div className="edit-mode">
                    <input
                      type="text"
                      value={editValue}
                      onChange={(e) => setEditValue(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && saveEditTask()}
                      autoFocus
                    />
                    <div className="edit-actions">
                      <button onClick={saveEditTask} className="save-btn">保存</button>
                      <button onClick={cancelEdit} className="cancel-btn">取消</button>
                    </div>
                  </div>
                ) : (
                  // 查看模式
                  <>
                    <input
                      type="checkbox"
                      checked={task.completed}
                      onChange={() => toggleTask(task.id)}
                      className="task-checkbox"
                    />
                    <span className="task-text">{task.text}</span>
                    <span className={`task-priority ${task.priority}`}>
                      {task.priority === 'high' ? '高' : task.priority === 'medium' ? '中' : '低'}
                    </span>
                    <div className="task-actions">
                      <select
                        value={task.priority}
                        onChange={(e) => updateTaskPriority(task.id, e.target.value)}
                        className="priority-dropdown"
                      >
                        <option value="high">高</option>
                        <option value="medium">中</option>
                        <option value="low">低</option>
                      </select>
                      <button 
                        onClick={() => startEditTask(task.id, task.text)}
                        className="edit-btn"
                      >
                        编辑
                      </button>
                      <button 
                        onClick={() => deleteTask(task.id)}
                        className="delete-btn"
                      >
                        删除
                      </button>
                    </div>
                  </>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
      
      {/* 进度条 */}
      {stats.total > 0 && (
        <div className="progress-section">
          <div className="progress-bar-container">
            <div 
              className="progress-bar" 
              style={{ width: `${(stats.completed / stats.total) * 100}%` }}
            ></div>
          </div>
          <p>完成进度: {stats.completed}/{stats.total} ({Math.round((stats.completed / stats.total) * 100)}%)</p>
        </div>
      )}
    </div>
  );
}

// 简化版任务管理器 - 演示核心功能
export function SimpleTaskManagerDemo() {
  const [tasks, setTasks] = useState([
    { id: 1, text: '学习React Hooks', completed: false },
    { id: 2, text: '理解组件生命周期', completed: true },
    { id: 3, text: '掌握状态管理', completed: false }
  ]);
  
  const [inputValue, setInputValue] = useState('');
  const [filter, setFilter] = useState('all');
  
  // 添加任务
  const addTask = () => {
    if (inputValue.trim()) {
      const newTask = {
        id: Date.now(),
        text: inputValue,
        completed: false
      };
      setTasks(prevTasks => [...prevTasks, newTask]);
      setInputValue('');
    }
  };
  
  // 删除任务
  const deleteTask = (id) => {
    setTasks(prevTasks => prevTasks.filter(task => task.id !== id));
  };
  
  // 切换任务状态
  const toggleTask = (id) => {
    setTasks(prevTasks =>
      prevTasks.map(task =>
        task.id === id ? { ...task, completed: !task.completed } : task
      )
    );
  };
  
  // 获取过滤后的任务
  const getFilteredTasks = () => {
    switch (filter) {
      case 'active':
        return tasks.filter(task => !task.completed);
      case 'completed':
        return tasks.filter(task => task.completed);
      default:
        return tasks;
    }
  };
  
  const filteredTasks = getFilteredTasks();
  const activeCount = tasks.filter(task => !task.completed).length;
  
  return (
    <div className="simple-task-manager">
      <h2>简化任务管理器</h2>
      
      <div className="add-task">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && addTask()}
          placeholder="添加新任务..."
        />
        <button onClick={addTask}>添加</button>
      </div>
      
      <div className="filters">
        <button 
          onClick={() => setFilter('all')}
          className={filter === 'all' ? 'active' : ''}
        >
          全部 ({tasks.length})
        </button>
        <button 
          onClick={() => setFilter('active')}
          className={filter === 'active' ? 'active' : ''}
        >
          未完成 ({activeCount})
        </button>
        <button 
          onClick={() => setFilter('completed')}
          className={filter === 'completed' ? 'active' : ''}
        >
          已完成 ({tasks.length - activeCount})
        </button>
      </div>
      
      <ul className="task-list">
        {filteredTasks.length === 0 ? (
          <li className="empty-message">
            {filter === 'all' ? '暂无任务，添加一个任务开始吧！' : 
             filter === 'active' ? '太棒了！没有未完成的任务。' : 
             '暂无已完成的任务。'}
          </li>
        ) : (
          filteredTasks.map(task => (
            <li key={task.id} className={`task-item ${task.completed ? 'completed' : ''}`}>
              <input
                type="checkbox"
                checked={task.completed}
                onChange={() => toggleTask(task.id)}
              />
              <span className="task-text">{task.text}</span>
              <button onClick={() => deleteTask(task.id)}>删除</button>
            </li>
          ))
        )}
      </ul>
    </div>
  );
}

// 任务管理器使用说明
export function TaskManagerInfo() {
  return (
    <div className="task-manager-info">
      <h2>任务管理器 - 状态与事件处理综合示例</h2>
      
      <div className="info-section">
        <h3>功能特点</h3>
        <ul>
          <li>添加、删除、编辑任务</li>
          <li>标记任务完成状态</li>
          <li>任务优先级管理</li>
          <li>过滤和排序功能</li>
          <li>批量操作</li>
          <li>进度可视化</li>
        </ul>
      </div>
      
      <div className="info-section">
        <h3>React技术点</h3>
        <ul>
          <li><strong>useState:</strong> 管理任务列表、输入值、过滤条件等状态</li>
          <li><strong>事件处理:</strong> 处理用户输入、点击、选择等交互</li>
          <li><strong>条件渲染:</strong> 根据状态显示不同的UI</li>
          <li><strong>列表渲染:</strong> 动态渲染任务列表</li>
          <li><strong>表单处理:</strong> 受控组件处理用户输入</li>
          <li><strong>状态更新模式:</strong> 函数式更新和不可变性原则</li>
        </ul>
      </div>
      
      <div className="info-section">
        <h3>关键概念演示</h3>
        <ul>
          <li><strong>状态管理:</strong> 使用useState管理复杂的状态结构</li>
          <li><strong>事件处理:</strong> 多种事件类型的处理方式</li>
          <li><strong>受控组件:</strong> 表单输入与状态同步</li>
          <li><strong>列表操作:</strong> 添加、删除、更新列表项</li>
          <li><strong>条件渲染:</strong> 根据过滤条件渲染不同的任务</li>
          <li><strong>表单验证:</strong> 输入验证和错误处理</li>
        </ul>
      </div>
    </div>
  );
}

// 主组件 - 包含所有示例
export const TaskManagerDemo = () => {
  const [activeView, setActiveView] = useState('simple');
  
  return (
    <div className="demo-container">
      <div className="demo-description">
        <h2>任务管理器应用</h2>
        <p>这是一个综合性的任务管理应用，展示了React状态管理和事件处理的实际应用。它包含了完整的任务管理功能，如添加、删除、编辑、排序和过滤等。</p>
      </div>

      <div className="view-toggle">
        <button 
          className={activeView === 'info' ? 'active' : ''}
          onClick={() => setActiveView('info')}
        >
          项目说明
        </button>
        <button 
          className={activeView === 'simple' ? 'active' : ''}
          onClick={() => setActiveView('simple')}
        >
          简化版
        </button>
        <button 
          className={activeView === 'full' ? 'active' : ''}
          onClick={() => setActiveView('full')}
        >
          完整版
        </button>
      </div>
      
      <div className="demo-content">
        {activeView === 'info' && <TaskManagerInfo />}
        {activeView === 'simple' && <SimpleTaskManagerDemo />}
        {activeView === 'full' && <TaskManagerDemo />}
      </div>
      
      <div className="demo-info">
        <h3>学习要点</h3>
        <ul>
          <li>React的状态管理是构建交互式应用的核心</li>
          <li>事件处理是响应用户操作的关键机制</li>
          <li>受控组件确保表单数据与状态同步</li>
          <li>函数式更新可以避免状态更新中的竞态条件</li>
          <li>保持状态不可变性是React的重要原则</li>
          <li>通过状态组织可以简化复杂的UI逻辑</li>
        </ul>
      </div>
    </div>
  );
};
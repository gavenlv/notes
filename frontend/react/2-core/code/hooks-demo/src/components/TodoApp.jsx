import { useReducer, useState } from 'react'
import { useTheme } from '../context/ThemeContext.jsx'

// 定义初始状态
const initialState = {
  todos: [],
  nextId: 1,
  filter: 'all' // 'all', 'active', 'completed'
}

// 定义action类型
const ACTIONS = {
  ADD_TODO: 'ADD_TODO',
  TOGGLE_TODO: 'TOGGLE_TODO',
  DELETE_TODO: 'DELETE_TODO',
  SET_FILTER: 'SET_FILTER',
  EDIT_TODO: 'EDIT_TODO',
  CLEAR_COMPLETED: 'CLEAR_COMPLETED'
}

// Reducer函数 - 处理状态更新逻辑
function todoReducer(state, action) {
  switch (action.type) {
    case ACTIONS.ADD_TODO:
      if (!action.payload.text.trim()) return state
      return {
        ...state,
        todos: [...state.todos, {
          id: state.nextId,
          text: action.payload.text,
          completed: false
        }],
        nextId: state.nextId + 1
      }
    
    case ACTIONS.TOGGLE_TODO:
      return {
        ...state,
        todos: state.todos.map(todo => 
          todo.id === action.payload.id
            ? { ...todo, completed: !todo.completed }
            : todo
        )
      }
    
    case ACTIONS.DELETE_TODO:
      return {
        ...state,
        todos: state.todos.filter(todo => todo.id !== action.payload.id)
      }
    
    case ACTIONS.SET_FILTER:
      return {
        ...state,
        filter: action.payload.filter
      }
    
    case ACTIONS.EDIT_TODO:
      if (!action.payload.text.trim()) return state
      return {
        ...state,
        todos: state.todos.map(todo =>
          todo.id === action.payload.id
            ? { ...todo, text: action.payload.text }
            : todo
        )
      }
    
    case ACTIONS.CLEAR_COMPLETED:
      return {
        ...state,
        todos: state.todos.filter(todo => !todo.completed)
      }
    
    default:
      return state
  }
}

function TodoApp() {
  const { styles } = useTheme()
  const [state, dispatch] = useReducer(todoReducer, initialState)
  const [newTodoText, setNewTodoText] = useState('')
  const [editingId, setEditingId] = useState(null)
  const [editText, setEditText] = useState('')

  // 根据筛选条件过滤待办事项
  const filteredTodos = state.todos.filter(todo => {
    if (state.filter === 'active') return !todo.completed
    if (state.filter === 'completed') return todo.completed
    return true // 'all'
  })

  // 计算未完成的待办事项数量
  const activeTodosCount = state.todos.filter(todo => !todo.completed).length

  // 添加待办事项
  const handleAddTodo = (e) => {
    e.preventDefault()
    if (newTodoText.trim()) {
      dispatch({
        type: ACTIONS.ADD_TODO,
        payload: { text: newTodoText }
      })
      setNewTodoText('')
    }
  }

  // 切换待办事项完成状态
  const handleToggleTodo = (id) => {
    dispatch({
      type: ACTIONS.TOGGLE_TODO,
      payload: { id }
    })
  }

  // 删除待办事项
  const handleDeleteTodo = (id) => {
    dispatch({
      type: ACTIONS.DELETE_TODO,
      payload: { id }
    })
  }

  // 设置筛选条件
  const handleSetFilter = (filter) => {
    dispatch({
      type: ACTIONS.SET_FILTER,
      payload: { filter }
    })
  }

  // 开始编辑待办事项
  const handleStartEdit = (todo) => {
    setEditingId(todo.id)
    setEditText(todo.text)
  }

  // 保存编辑
  const handleSaveEdit = (id) => {
    if (editText.trim()) {
      dispatch({
        type: ACTIONS.EDIT_TODO,
        payload: { id, text: editText }
      })
    }
    setEditingId(null)
    setEditText('')
  }

  // 取消编辑
  const handleCancelEdit = () => {
    setEditingId(null)
    setEditText('')
  }

  // 清除已完成的待办事项
  const handleClearCompleted = () => {
    dispatch({
      type: ACTIONS.CLEAR_COMPLETED
    })
  }

  return (
    <div className="todo-app">
      <h2 style={{ color: styles.primaryColor }}>useReducer Hook 待办事项应用</h2>
      <p className="demo-description">
        这个演示展示了如何使用useReducer Hook管理复杂状态，包括添加、编辑、删除和筛选待办事项。
      </p>

      {/* 添加待办事项表单 */}
      <form onSubmit={handleAddTodo} className="add-todo-form" style={{ borderColor: styles.borderColor }}>
        <input
          type="text"
          value={newTodoText}
          onChange={(e) => setNewTodoText(e.target.value)}
          placeholder="添加新的待办事项..."
          className="todo-input"
          style={{
            backgroundColor: styles.backgroundColor,
            color: styles.color,
            borderColor: styles.borderColor
          }}
        />
        <button 
          type="submit" 
          style={{
            backgroundColor: styles.primaryColor,
            color: '#fff',
            borderColor: styles.primaryColor
          }}
        >
          添加
        </button>
      </form>

      {/* 待办事项列表 */}
      <div className="todo-list-container" style={{ borderColor: styles.borderColor }}>
        {filteredTodos.length === 0 ? (
          <p className="no-todos">暂无待办事项</p>
        ) : (
          <ul className="todo-list">
            {filteredTodos.map(todo => (
              <li 
                key={todo.id} 
                className={`todo-item ${todo.completed ? 'completed' : ''} ${editingId === todo.id ? 'editing' : ''}`}
                style={{ borderColor: styles.borderColor }}
              >
                {editingId === todo.id ? (
                  <div className="todo-edit">
                    <input
                      type="text"
                      value={editText}
                      onChange={(e) => setEditText(e.target.value)}
                      autoFocus
                      className="todo-edit-input"
                      style={{
                        backgroundColor: styles.backgroundColor,
                        color: styles.color,
                        borderColor: styles.borderColor
                      }}
                    />
                    <div className="edit-actions">
                      <button 
                        onClick={() => handleSaveEdit(todo.id)}
                        style={{
                          backgroundColor: styles.primaryColor,
                          color: '#fff',
                          borderColor: styles.primaryColor
                        }}
                      >
                        保存
                      </button>
                      <button 
                        onClick={handleCancelEdit}
                        style={{
                          backgroundColor: 'transparent',
                          color: styles.color,
                          borderColor: styles.borderColor
                        }}
                      >
                        取消
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <input
                      type="checkbox"
                      checked={todo.completed}
                      onChange={() => handleToggleTodo(todo.id)}
                      className="todo-checkbox"
                    />
                    <span 
                      className="todo-text" 
                      onClick={() => handleToggleTodo(todo.id)}
                      style={{ textDecoration: todo.completed ? 'line-through' : 'none' }}
                    >
                      {todo.text}
                    </span>
                    <div className="todo-actions">
                      <button 
                        onClick={() => handleStartEdit(todo)}
                        className="edit-btn"
                        style={{
                          backgroundColor: styles.secondaryColor,
                          color: '#fff',
                          borderColor: styles.secondaryColor
                        }}
                      >
                        编辑
                      </button>
                      <button 
                        onClick={() => handleDeleteTodo(todo.id)}
                        className="delete-btn"
                        style={{
                          backgroundColor: 'transparent',
                          color: '#e53e3e',
                          borderColor: '#e53e3e'
                        }}
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

      {/* 筛选和统计信息 */}
      <div className="todo-footer" style={{ borderColor: styles.borderColor }}>
        <div className="todo-stats">
          <span>还有 {activeTodosCount} 项待完成</span>
        </div>
        <div className="todo-filters">
          <button 
            className={`filter-btn ${state.filter === 'all' ? 'active' : ''}`}
            onClick={() => handleSetFilter('all')}
            style={{
              backgroundColor: state.filter === 'all' ? styles.primaryColor : 'transparent',
              color: state.filter === 'all' ? '#fff' : styles.color,
              borderColor: styles.borderColor
            }}
          >
            全部
          </button>
          <button 
            className={`filter-btn ${state.filter === 'active' ? 'active' : ''}`}
            onClick={() => handleSetFilter('active')}
            style={{
              backgroundColor: state.filter === 'active' ? styles.primaryColor : 'transparent',
              color: state.filter === 'active' ? '#fff' : styles.color,
              borderColor: styles.borderColor
            }}
          >
            未完成
          </button>
          <button 
            className={`filter-btn ${state.filter === 'completed' ? 'active' : ''}`}
            onClick={() => handleSetFilter('completed')}
            style={{
              backgroundColor: state.filter === 'completed' ? styles.primaryColor : 'transparent',
              color: state.filter === 'completed' ? '#fff' : styles.color,
              borderColor: styles.borderColor
            }}
          >
            已完成
          </button>
        </div>
        <div className="todo-actions">
          <button 
            onClick={handleClearCompleted}
            disabled={state.todos.filter(todo => todo.completed).length === 0}
            style={{
              backgroundColor: 'transparent',
              color: styles.color,
              borderColor: styles.borderColor,
              opacity: state.todos.filter(todo => todo.completed).length === 0 ? 0.5 : 1
            }}
          >
            清除已完成
          </button>
        </div>
      </div>

      {/* Reducer代码解释 */}
      <div className="code-explanation" style={{ backgroundColor: styles.backgroundColor, borderColor: styles.borderColor }}>
        <h3 style={{ color: styles.secondaryColor }}>useReducer 代码示例</h3>
        <pre><code>
{`// 定义初始状态
const initialState = {
  todos: [],
  nextId: 1,
  filter: 'all'
};

// 定义action类型
const ACTIONS = {
  ADD_TODO: 'ADD_TODO',
  TOGGLE_TODO: 'TOGGLE_TODO',
  DELETE_TODO: 'DELETE_TODO',
  // 其他action类型...
};

// Reducer函数
function todoReducer(state, action) {
  switch (action.type) {
    case ACTIONS.ADD_TODO:
      // 添加待办事项逻辑
      return {
        ...state,
        todos: [...state.todos, {
          id: state.nextId,
          text: action.payload.text,
          completed: false
        }],
        nextId: state.nextId + 1
      };
    // 其他case...
    default:
      return state;
  }
}

// 在组件中使用
const [state, dispatch] = useReducer(todoReducer, initialState);

// 派发action
dispatch({
  type: ACTIONS.ADD_TODO,
  payload: { text: '学习React' }
});`}
        </code></pre>
      </div>
    </div>
  )
}

export default TodoApp

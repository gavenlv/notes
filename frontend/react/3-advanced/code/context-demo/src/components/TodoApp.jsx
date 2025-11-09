import { useState } from 'react';
import { useAppContext } from '../context/AppContext';

function TodoApp() {
  const [inputText, setInputText] = useState('');
  const { todos, dispatchTodos, isDarkMode } = useAppContext();
  
  // 添加待办事项
  const handleAddTodo = () => {
    if (inputText.trim()) {
      dispatchTodos({ type: 'ADD_TODO', payload: inputText });
      setInputText('');
    }
  };
  
  // 切换待办事项状态
  const handleToggleTodo = (id) => {
    dispatchTodos({ type: 'TOGGLE_TODO', payload: id });
  };
  
  // 删除待办事项
  const handleDeleteTodo = (id) => {
    dispatchTodos({ type: 'DELETE_TODO', payload: id });
  };
  
  // 处理回车添加
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleAddTodo();
    }
  };
  
  return (
    <div style={{ 
      backgroundColor: isDarkMode ? '#333' : '#f5f5f5',
      padding: '20px',
      borderRadius: '8px',
      minHeight: '300px'
    }}>
      <h2 style={{ marginBottom: '20px' }}>待办事项管理</h2>
      <div style={{ marginBottom: '20px', display: 'flex', justifyContent: 'center' }}>
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="添加新待办..."
          style={{
            padding: '10px 15px',
            fontSize: '16px',
            borderRadius: '4px 0 0 4px',
            border: 'none',
            outline: 'none',
            flexGrow: 1,
            maxWidth: '400px'
          }}
        />
        <button
          onClick={handleAddTodo}
          style={{
            padding: '10px 20px',
            fontSize: '16px',
            borderRadius: '0 4px 4px 0',
            border: 'none',
            backgroundColor: '#646cff',
            color: 'white',
            cursor: 'pointer'
          }}
        >
          添加
        </button>
      </div>
      <div style={{ marginTop: '20px' }}>
        {todos.length === 0 ? (
          <p style={{ opacity: 0.7 }}>暂无待办事项，添加一个吧！</p>
        ) : (
          <ul style={{ padding: 0 }}>
            {todos.map((todo) => (
              <li 
                key={todo.id} 
                style={{
                  backgroundColor: isDarkMode ? '#444' : 'white',
                  padding: '15px',
                  marginBottom: '10px',
                  borderRadius: '4px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                }}
              >
                <span
                  onClick={() => handleToggleTodo(todo.id)}
                  style={{
                    cursor: 'pointer',
                    textDecoration: todo.completed ? 'line-through' : 'none',
                    opacity: todo.completed ? 0.6 : 1,
                    flexGrow: 1,
                    marginRight: '10px'
                  }}
                >
                  {todo.text}
                </span>
                <button
                  onClick={() => handleDeleteTodo(todo.id)}
                  style={{
                    padding: '5px 10px',
                    backgroundColor: '#ff4d4f',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '14px'
                  }}
                >
                  删除
                </button>
              </li>
            ))}
          </ul>
        )}
        {todos.length > 0 && (
          <p style={{ 
            marginTop: '20px', 
            opacity: 0.7, 
            fontSize: '14px' 
          }}>
            共 {todos.length} 个待办事项，
            已完成 {todos.filter(todo => todo.completed).length} 个
          </p>
        )}
      </div>
    </div>
  );
}

export default TodoApp
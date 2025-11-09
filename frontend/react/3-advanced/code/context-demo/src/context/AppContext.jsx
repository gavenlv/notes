import React, { createContext, useContext, useState, useReducer } from 'react';

// 创建 Context
const AppContext = createContext();

// 定义待办事项的reducer函数
function todoReducer(state, action) {
  switch (action.type) {
    case 'ADD_TODO':
      return [...state, {
        id: Date.now(),
        text: action.payload,
        completed: false
      }];
    case 'TOGGLE_TODO':
      return state.map(todo => 
        todo.id === action.payload 
          ? { ...todo, completed: !todo.completed }
          : todo
      );
    case 'DELETE_TODO':
      return state.filter(todo => todo.id !== action.payload);
    default:
      return state;
  }
}

// 创建 Provider 组件
export function AppProvider({ children }) {
  // 用户状态
  const [user, setUser] = useState({
    name: '用户',
    isLoggedIn: true
  });
  
  // 主题状态
  const [isDarkMode, setIsDarkMode] = useState(true);
  
  // 待办事项状态（使用useReducer）
  const [todos, dispatchTodos] = useReducer(todoReducer, []);
  
  // 切换主题模式
  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };
  
  // 模拟用户登录
  const login = (username) => {
    setUser({
      name: username,
      isLoggedIn: true
    });
  };
  
  // 模拟用户登出
  const logout = () => {
    setUser({
      name: '',
      isLoggedIn: false
    });
  };
  
  // 提供给子组件的值
  const value = {
    // 用户相关
    user,
    login,
    logout,
    
    // 主题相关
    isDarkMode,
    toggleTheme,
    
    // 待办事项相关
    todos,
    dispatchTodos
  };
  
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

// 创建自定义 Hook 便于使用 Context
export function useAppContext() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
}
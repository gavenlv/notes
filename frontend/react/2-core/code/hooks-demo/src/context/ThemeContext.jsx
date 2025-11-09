import React, { createContext, useState, useContext } from 'react'

// 创建主题上下文
const ThemeContext = createContext()

/**
 * 主题提供者组件
 * 用于为整个应用提供主题相关的状态和函数
 */
export function ThemeProvider({ children }) {
  // 使用useState管理当前主题
  const [theme, setTheme] = useState('light')

  // 主题样式定义
  const themeStyles = {
    light: {
      backgroundColor: '#ffffff',
      color: '#333333',
      primaryColor: '#667eea',
      secondaryColor: '#764ba2',
      borderColor: '#e2e8f0',
      cardBackground: '#f7fafc'
    },
    dark: {
      backgroundColor: '#1a202c',
      color: '#e2e8f0',
      primaryColor: '#818cf8',
      secondaryColor: '#b794f4',
      borderColor: '#4a5568',
      cardBackground: '#2d3748'
    }
  }

  // 切换主题的函数
  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light')
  }

  // 提供给子组件的值
  const contextValue = {
    theme,
    styles: themeStyles[theme],
    toggleTheme
  }

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  )
}

/**
 * 自定义Hook，用于在组件中获取主题上下文
 */
export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/main.css'
import App from './App.jsx'
import { ThemeProvider } from './context/ThemeContext.jsx'

// 获取根DOM元素
const rootElement = document.getElementById('root')

// 创建React根并渲染应用
createRoot(rootElement).render(
  <StrictMode>
    // 使用ThemeProvider包裹整个应用，提供主题上下文
    <ThemeProvider>
      <App />
    </ThemeProvider>
  </StrictMode>
)

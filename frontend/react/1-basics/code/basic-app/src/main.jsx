import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/main.css'
import App from './App.jsx'

// 获取根DOM元素
const rootElement = document.getElementById('root')

// 创建React根并渲染App组件
createRoot(rootElement).render(
  <StrictMode>
    <App />
  </StrictMode>
)

// 说明：
// 1. StrictMode 是一个开发工具，用于帮助识别潜在问题
// 2. createRoot 是React 18中的新API，用于创建根节点
// 3. 渲染App组件到id为'root'的DOM元素中

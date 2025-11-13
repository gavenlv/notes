import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './styles/main.css'

// 创建根节点并渲染App组件
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)

// 支持热模块替换(HMR)
if (import.meta.hot) {
  import.meta.hot.accept('./App.jsx', () => {
    // App组件更新时重新渲染
    console.log('App component hot updated')
  })
}

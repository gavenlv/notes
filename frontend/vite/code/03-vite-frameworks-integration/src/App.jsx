import React, { useState, useEffect } from 'react'
import { Counter } from './components/Counter.jsx'
import { MessageList } from './components/MessageList.jsx'
import { ThemeToggle } from './components/ThemeToggle.jsx'
import { useLocalStorage } from './hooks/useLocalStorage.js'
import { formatTime } from './utils/formatTime.js'

function App() {
  // 状态管理
  const [count, setCount] = useState(0)
  const [messages, setMessages] = useState([
    { id: 1, text: '欢迎使用 Vite + React 集成示例', timestamp: new Date() },
    { id: 2, text: '这是一个演示组件状态和HMR的示例', timestamp: new Date() }
  ])
  const [newMessage, setNewMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  
  // 使用自定义Hook管理主题
  const [theme, setTheme] = useLocalStorage('app-theme', 'light')
  
  // 模拟数据加载
  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true)
      try {
        // 模拟API请求延迟
        await new Promise(resolve => setTimeout(resolve, 1000))
        setCount(42) // 设置初始计数值
        console.log('数据加载完成')
      } catch (error) {
        console.error('数据加载失败:', error)
      } finally {
        setIsLoading(false)
      }
    }
    
    loadData()
  }, [])
  
  // 监听主题变化并应用到文档
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])
  
  // 处理添加消息
  const handleAddMessage = () => {
    if (newMessage.trim()) {
      const message = {
        id: Date.now(),
        text: newMessage.trim(),
        timestamp: new Date()
      }
      setMessages(prevMessages => [...prevMessages, message])
      setNewMessage('')
    }
  }
  
  // 处理按键事件
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleAddMessage()
    }
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1 className="app-title">Vite + React 框架集成示例</h1>
        <ThemeToggle theme={theme} onToggleTheme={setTheme} />
      </header>
      
      <main className="app-main">
        <section className="feature-section">
          <h2 className="section-title">1. 计数器组件示例</h2>
          <Counter count={count} onCountChange={setCount} />
          <p className="section-description">
            演示React组件状态管理和事件处理
          </p>
        </section>
        <section className="feature-section">
          <h2 className="section-title">2. 消息列表组件</h2>
          <div className="message-input-container">
            <textarea
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="输入新消息..."
              className="message-input"
            />
            <button 
              onClick={handleAddMessage}
              className="send-button"
              disabled={!newMessage.trim()}
            >
              发送消息
            </button>
          </div>
          <MessageList messages={messages} />
          <p className="section-description">
            演示列表渲染和表单处理
          </p>
        </section>
        <section className="feature-section">
          <h2 className="section-title">3. 自定义Hook示例</h2>
          <div className="hook-example">
            <p>当前主题: <strong>{theme === 'light' ? '浅色' : '深色'}</strong></p>
            <p>使用自定义Hook保存主题偏好到本地存储</p>
          </div>
        </section>
        <section className="feature-section">
          <h2 className="section-title">4. 工具函数集成</h2>
          <div className="utils-example">
            <p>当前时间: <strong>{formatTime(new Date())}</strong></p>
            <p>演示Vite中ES模块的导入和使用</p>
          </div>
        </section>
          <section className="feature-section">
          <h2 className="section-title">5. Vite 特性演示</h2>
          <ul className="vite-features">
            <li>✅ 快速的开发服务器启动速度</li>
            <li>✅ 即时热模块替换 (HMR)</li>
            <li>✅ 路径别名支持 (@/components)</li>
            <li>✅ CSS 模块支持</li>
            <li>✅ 环境变量处理</li>
            <li>✅ 智能的依赖预构建</li>
          </ul>
        </section>
      </main>
      <footer className="app-footer">
        <p>© 2023 Vite + React 集成示例 | 构建时间: {new Date().toLocaleString()}</p>
      </footer>
    </div>
  )
}

export default App

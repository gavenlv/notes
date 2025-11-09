import { useState } from 'react'
import { useTheme } from './context/ThemeContext.jsx'
import CounterDemo from './components/CounterDemo.jsx'
import TodoApp from './components/TodoApp.jsx'
import DataFetchingDemo from './components/DataFetchingDemo.jsx'
import FormDemo from './components/FormDemo.jsx'
import ThemeToggle from './components/ThemeToggle.jsx'

function App() {
  const { styles } = useTheme()
  const [activeTab, setActiveTab] = useState('counter')

  // 渲染当前选中的演示组件
  const renderActiveDemo = () => {
    switch (activeTab) {
      case 'counter':
        return <CounterDemo />
      case 'todo':
        return <TodoApp />
      case 'fetch':
        return <DataFetchingDemo />
      case 'form':
        return <FormDemo />
      default:
        return <CounterDemo />
    }
  }

  return (
    <div className="app-container" style={{ backgroundColor: styles.backgroundColor, color: styles.color, minHeight: '100vh' }}>
      <header className="app-header" style={{ backgroundColor: styles.cardBackground, borderBottomColor: styles.borderColor }}>
        <h1>React Hooks 演示应用</h1>
        <p>学习和探索React核心Hooks的使用方法</p>
      </header>

      <div className="main-content">
        <nav className="demo-nav" style={{ backgroundColor: styles.cardBackground, borderColor: styles.borderColor }}>
          <button 
            className={`nav-btn ${activeTab === 'counter' ? 'active' : ''}`}
            onClick={() => setActiveTab('counter')}
            style={{ 
              backgroundColor: activeTab === 'counter' ? styles.primaryColor : 'transparent',
              color: activeTab === 'counter' ? '#fff' : styles.color,
              borderColor: styles.borderColor
            }}
          >
            useState 计数器
          </button>
          <button 
            className={`nav-btn ${activeTab === 'todo' ? 'active' : ''}`}
            onClick={() => setActiveTab('todo')}
            style={{ 
              backgroundColor: activeTab === 'todo' ? styles.primaryColor : 'transparent',
              color: activeTab === 'todo' ? '#fff' : styles.color,
              borderColor: styles.borderColor
            }}
          >
            useReducer 待办事项
          </button>
          <button 
            className={`nav-btn ${activeTab === 'fetch' ? 'active' : ''}`}
            onClick={() => setActiveTab('fetch')}
            style={{ 
              backgroundColor: activeTab === 'fetch' ? styles.primaryColor : 'transparent',
              color: activeTab === 'fetch' ? '#fff' : styles.color,
              borderColor: styles.borderColor
            }}
          >
            useFetch 数据获取
          </button>
          <button 
            className={`nav-btn ${activeTab === 'form' ? 'active' : ''}`}
            onClick={() => setActiveTab('form')}
            style={{ 
              backgroundColor: activeTab === 'form' ? styles.primaryColor : 'transparent',
              color: activeTab === 'form' ? '#fff' : styles.color,
              borderColor: styles.borderColor
            }}
          >
            useForm 表单处理
          </button>
        </nav>

        <div className="demo-container" style={{ backgroundColor: styles.cardBackground, borderColor: styles.borderColor }}>
          {renderActiveDemo()}
        </div>
      </div>

      <ThemeToggle />

      <footer className="app-footer" style={{ backgroundColor: styles.cardBackground, borderTopColor: styles.borderColor }}>
        <p>React 从0入门到专家 | 核心概念演示应用</p>
      </footer>
    </div>
  )
}

export default App

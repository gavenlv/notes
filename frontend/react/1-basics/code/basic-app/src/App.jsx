import { useState } from 'react'
import Greeting from './components/Greeting.jsx'
import UserProfile from './components/UserProfile.jsx'
import ProductList from './components/ProductList.jsx'

function App() {
  // 使用useState Hook管理状态
  const [count, setCount] = useState(0)

  // 产品数据示例
  const products = [
    {
      id: 1,
      name: 'React 基础教程',
      price: 99.99,
      description: '从零开始学习React开发'
    },
    {
      id: 2,
      name: 'React 高级实战',
      price: 199.99,
      description: '深入学习React高级特性和最佳实践'
    },
    {
      id: 3,
      name: 'React 项目实战',
      price: 159.99,
      description: '通过项目学习React开发全过程'
    }
  ]

  // 增加计数的处理函数
  const handleIncrement = () => {
    setCount(count + 1)
  }

  // 重置计数的处理函数
  const handleReset = () => {
    setCount(0)
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>React 基础应用示例</h1>
        <p>这是一个展示React基础功能的示例应用</p>
      </header>

      <main className="app-main">
        <section className="counter-section">
          <h2>计数器示例</h2>
          <p className="count-display">当前计数: {count}</p>
          <div className="button-group">
            <button onClick={handleIncrement} className="btn increment-btn">
              增加
            </button>
            <button onClick={handleReset} className="btn reset-btn">
              重置
            </button>
          </div>
        </section>

        <section className="greeting-section">
          <h2>问候组件示例</h2>
          <Greeting name="React学习者" />
          <Greeting /> {/* 使用默认props */}
        </section>

        <section className="profile-section">
          <h2>用户资料组件示例</h2>
          <UserProfile
            name="张三"
            age={28}
            email="zhangsan@example.com"
          />
        </section>

        <section className="products-section">
          <h2>产品列表组件示例</h2>
          <ProductList products={products} />
        </section>
      </main>

      <footer className="app-footer">
        <p>© 2023 React学习教程 | 从0入门到专家</p>
      </footer>
    </div>
  )
}

export default App

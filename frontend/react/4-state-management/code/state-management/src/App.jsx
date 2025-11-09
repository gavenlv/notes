import React, { useState } from 'react'
import './App.css'

// Redux imports
import { useSelector, useDispatch } from 'react-redux'
import { selectTodos, addTodo, toggleTodo, removeTodo } from './store/reduxStore.js'

// Zustand imports
import { useCounterStore, useUserStore, useProductStore } from './store/zustandStore.js'

// Jotai imports
import { useTheme, useCart } from './store/jotaiStore.js'

// 1. Redux Todo App组件
const ReduxTodoApp = () => {
  const [inputText, setInputText] = useState('')
  const todos = useSelector(selectTodos)
  const dispatch = useDispatch()

  const handleAddTodo = () => {
    if (inputText.trim()) {
      dispatch(addTodo(inputText))
      setInputText('')
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleAddTodo()
    }
  }

  return (
    <div className="todo-app">
      <h3>Redux Todo List</h3>
      <div className="todo-input-container">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Add a new todo..."
        />
        <button onClick={handleAddTodo}>Add Todo</button>
      </div>
      <ul className="todo-list">
        {todos.map((todo) => (
          <li key={todo.id} className="todo-item">
            <button
              className={`toggle-btn ${todo.completed ? 'active' : ''}`}
              onClick={() => dispatch(toggleTodo(todo.id))}
            />
            <span className={`todo-text ${todo.completed ? 'todo-done' : ''}`}>
              {todo.text}
            </span>
            <button
              className="remove-btn"
              onClick={() => dispatch(removeTodo(todo.id))}
            >Remove</button>
          </li>
        ))}
      </ul>
    </div>
  )
}

// 2. Zustand Demo组件
const ZustandDemo = () => {
  const { count, increment, decrement, reset } = useCounterStore()
  const { user, login, logout } = useUserStore()
  const { products, toggleStock } = useProductStore()
  const [username, setUsername] = useState('')

  const handleLogin = () => {
    if (username.trim()) {
      login({
        name: username,
        email: `${username.toLowerCase()}@example.com`,
        loggedInAt: new Date().toISOString()
      })
      setUsername('')
    }
  }

  return (
    <div className="zustand-demo">
      <h3>Zustand Counter</h3>
      <div className="counter">
        <button className="counter-btn" onClick={decrement}>-</button>
        <span className="counter-value">{count}</span>
        <button className="counter-btn" onClick={increment}>+</button>
        <button onClick={reset}>Reset</button>
      </div>

      <h3>User Authentication</h3>
      {user ? (
        <div className="user-info">
          <p>Welcome, {user.name}!</p>
          <p>Email: {user.email}</p>
          <button onClick={logout}>Logout</button>
        </div>
      ) : (
        <div className="login-form">
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter your name"
          />
          <button onClick={handleLogin}>Login</button>
        </div>
      )}

      <h3>Product List</h3>
      <ul className="product-list">
        {products.map(product => (
          <li key={product.id} className="product-item">
            <span>
              {product.name} - ${product.price.toFixed(2)}
              <span style={{
                marginLeft: '0.5rem',
                padding: '0.2rem 0.5rem',
                backgroundColor: product.inStock ? '#4CAF50' : '#FF9800',
                borderRadius: '4px',
                fontSize: '0.8rem'
              }}>
                {product.inStock ? 'In Stock' : 'Out of Stock'}
              </span>
            </span>
            <button onClick={() => toggleStock(product.id)}>
              Toggle Stock
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}

// 3. Jotai Demo组件
const JotaiDemo = () => {
  const { theme, toggleTheme } = useTheme()
  const { items, total, addToCart, removeFromCart, clearCart } = useCart()
  const [productName, setProductName] = useState('')
  const [productPrice, setProductPrice] = useState('')

  const handleAddProduct = () => {
    if (productName.trim() && productPrice) {
      addToCart({
        name: productName,
        price: parseFloat(productPrice)
      })
      setProductName('')
      setProductPrice('')
    }
  }

  return (
    <div className="jotai-demo">
      <h3>Theme Switcher (Persisted)</h3>
      <p>Current theme: {theme}</p>
      <button onClick={toggleTheme}>Toggle Theme</button>

      <h3>Shopping Cart</h3>
      <div className="cart-form">
        <input
          type="text"
          value={productName}
          onChange={(e) => setProductName(e.target.value)}
          placeholder="Product name"
        />
        <input
          type="number"
          value={productPrice}
          onChange={(e) => setProductPrice(e.target.value)}
          placeholder="Price"
          min="0"
          step="0.01"
        />
        <button onClick={handleAddProduct}>Add to Cart</button>
      </div>

      {items.length === 0 ? (
        <p>Your cart is empty.</p>
      ) : (
        <>
          <ul className="cart-items">
            {items.map((item, index) => (
              <li key={index} className="cart-item">
                <span>
                  {item.name} - ${item.price.toFixed(2)} x {item.quantity}
                </span>
                <button className="remove-btn"
                  onClick={() => removeFromCart(index)}>
                  Remove
                </button>
              </li>
            ))}
          </ul>
          <div className="cart-summary">
            <p style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>
              Total: ${total.toFixed(2)}
            </p>
            <button onClick={clearCart}>Clear Cart</button>
          </div>
        </>
      )}
    </div>
  )
}

// 主应用组件
function App() {
  const [activeTab, setActiveTab] = useState('redux')

  return (
    <div className="App">
      <h1>React State Management Demo</h1>
      <h2>不同状态管理方案对比</h2>

      <div className="demo-tabs">
        <button
          className={`demo-tab ${activeTab === 'redux' ? 'active' : ''}`}
          onClick={() => setActiveTab('redux')}
        >Redux</button>
        <button
          className={`demo-tab ${activeTab === 'zustand' ? 'active' : ''}`}
          onClick={() => setActiveTab('zustand')}
        >Zustand</button>
        <button
          className={`demo-tab ${activeTab === 'jotai' ? 'active' : ''}`}
          onClick={() => setActiveTab('jotai')}
        >Jotai</button>
      </div>

      <div className="demo-section">
        {activeTab === 'redux' && <ReduxTodoApp />}
        {activeTab === 'zustand' && <ZustandDemo />}
        {activeTab === 'jotai' && <JotaiDemo />}
      </div>

      <div className="comparison-section">
        <h3>状态管理方案对比总结</h3>
        <ul className="comparison-list">
          <li>
            <strong>Redux:</strong> 功能强大，生态成熟，适合大型复杂应用，但样板代码较多
          </li>
          <li>
            <strong>Zustand:</strong> 轻量级，API简洁，无需Provider，适合中小型应用
          </li>
          <li>
            <strong>Jotai:</strong> 原子化设计，按需更新，适合精细状态管理和性能优化
          </li>
        </ul>
      </div>
    </div>
  )
}

export default App
import { useState } from 'react'
import './App.css'
import { AppProvider } from './context/AppContext'
import Navbar from './components/Navbar'
import TodoApp from './components/TodoApp'

function App() {
  return (
    <AppProvider>
      <div className="App">
        <h1>React Context 示例应用</h1>
        <Navbar />
        <TodoApp />
      </div>
    </AppProvider>
  )
}

export default App
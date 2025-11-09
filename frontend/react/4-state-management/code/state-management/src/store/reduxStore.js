import { configureStore, createSlice } from '@reduxjs/toolkit'

// 定义Todo slice
const todosSlice = createSlice({
  name: 'todos',
  initialState: [
    { id: 1, text: 'Learn React', completed: false },
    { id: 2, text: 'Master Redux', completed: false },
    { id: 3, text: 'Build amazing apps', completed: true }
  ],
  reducers: {
    addTodo: (state, action) => {
      const newTodo = {
        id: Date.now(),
        text: action.payload,
        completed: false
      }
      state.push(newTodo)
    },
    toggleTodo: (state, action) => {
      const todo = state.find(todo => todo.id === action.payload)
      if (todo) {
        todo.completed = !todo.completed
      }
    },
    removeTodo: (state, action) => {
      return state.filter(todo => todo.id !== action.payload)
    }
  }
})

// 导出actions
export const { addTodo, toggleTodo, removeTodo } = todosSlice.actions

// 配置store
export const store = configureStore({
  reducer: {
    todos: todosSlice.reducer
  }
})

// 导出selectors
export const selectTodos = state => state.todos
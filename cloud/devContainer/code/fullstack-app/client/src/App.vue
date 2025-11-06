<template>
  <div id="app">
    <header class="header">
      <h1>🚀 全栈应用演示</h1>
      <p>使用DevContainer开发的全栈应用</p>
    </header>

    <main class="main">
      <div class="todo-section">
        <h2>待办事项管理</h2>
        
        <div class="add-todo">
          <input 
            v-model="newTodo" 
            @keyup.enter="addTodo" 
            placeholder="输入新的待办事项..."
            class="todo-input"
          >
          <button @click="addTodo" class="add-btn">添加</button>
        </div>

        <div class="todo-list">
          <div 
            v-for="todo in todos" 
            :key="todo.id" 
            class="todo-item"
            :class="{ completed: todo.completed }"
          >
            <input 
              type="checkbox" 
              v-model="todo.completed" 
              @change="updateTodo(todo)"
              class="todo-checkbox"
            >
            <span class="todo-title">{{ todo.title }}</span>
            <button @click="deleteTodo(todo.id)" class="delete-btn">删除</button>
          </div>
        </div>

        <div v-if="todos.length === 0" class="empty-state">
          📝 暂无待办事项，添加一个开始吧！
        </div>
      </div>

      <div class="system-info">
        <h2>系统信息</h2>
        <div class="info-grid">
          <div class="info-item">
            <span class="label">前端:</span>
            <span class="value">Vue 3 + Vite</span>
          </div>
          <div class="info-item">
            <span class="label">后端:</span>
            <span class="value">Node.js + Express</span>
          </div>
          <div class="info-item">
            <span class="label">数据库:</span>
            <span class="value">PostgreSQL</span>
          </div>
          <div class="info-item">
            <span class="label">容器:</span>
            <span class="value">Docker Compose</span>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const API_URL = 'http://localhost:5000/api'

export default {
  name: 'App',
  setup() {
    const todos = ref([])
    const newTodo = ref('')

    const fetchTodos = async () => {
      try {
        const response = await axios.get(`${API_URL}/todos`)
        todos.value = response.data
      } catch (error) {
        console.error('获取待办事项失败:', error)
      }
    }

    const addTodo = async () => {
      if (!newTodo.value.trim()) return
      
      try {
        await axios.post(`${API_URL}/todos`, {
          title: newTodo.value.trim()
        })
        newTodo.value = ''
        await fetchTodos()
      } catch (error) {
        console.error('添加待办事项失败:', error)
      }
    }

    const updateTodo = async (todo) => {
      try {
        await axios.put(`${API_URL}/todos/${todo.id}`, {
          completed: todo.completed
        })
      } catch (error) {
        console.error('更新待办事项失败:', error)
      }
    }

    const deleteTodo = async (id) => {
      try {
        await axios.delete(`${API_URL}/todos/${id}`)
        await fetchTodos()
      } catch (error) {
        console.error('删除待办事项失败:', error)
      }
    }

    onMounted(() => {
      fetchTodos()
    })

    return {
      todos,
      newTodo,
      addTodo,
      updateTodo,
      deleteTodo
    }
  }
}
</script>

<style scoped>
/* 样式代码省略，实际文件中需要完整样式 */
</style>
import { defineStore } from 'pinia'
import { taskService } from '../services/taskService'

export const useTaskStore = defineStore('tasks', {
  state: () => ({
    tasks: [],
    loading: false,
    error: null
  }),

  getters: {
    completedTasks: (state) => state.tasks.filter(task => task.completed),
    pendingTasks: (state) => state.tasks.filter(task => !task.completed)
  },

  actions: {
    async fetchTasks() {
      this.loading = true
      try {
        const tasks = await taskService.getTasks()
        this.tasks = tasks
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    async addTask(taskData) {
      try {
        const newTask = await taskService.createTask(taskData)
        this.tasks.push(newTask)
        return newTask
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    async updateTask(id, taskData) {
      try {
        const updatedTask = await taskService.updateTask(id, taskData)
        const index = this.tasks.findIndex(task => task.id === id)
        if (index !== -1) {
          this.tasks[index] = updatedTask
        }
        return updatedTask
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    async deleteTask(id) {
      try {
        await taskService.deleteTask(id)
        this.tasks = this.tasks.filter(task => task.id !== id)
      } catch (error) {
        this.error = error.message
        throw error
      }
    }
  }
})
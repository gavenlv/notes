// 模拟API服务
class TaskService {
  constructor() {
    this.tasks = [
      { id: 1, title: '学习Vue.js', description: '掌握Vue.js核心概念', completed: true },
      { id: 2, title: '完成项目实战', description: '开发一个完整的Vue项目', completed: false },
      { id: 3, title: '学习状态管理', description: '掌握Pinia的使用', completed: false }
    ]
    this.nextId = 4
  }

  async getTasks() {
    return new Promise(resolve => {
      setTimeout(() => {
        resolve(this.tasks)
      }, 500)
    })
  }

  async createTask(taskData) {
    return new Promise(resolve => {
      setTimeout(() => {
        const newTask = {
          id: this.nextId++,
          ...taskData,
          completed: false
        }
        this.tasks.push(newTask)
        resolve(newTask)
      }, 300)
    })
  }

  async updateTask(id, taskData) {
    return new Promise(resolve => {
      setTimeout(() => {
        const index = this.tasks.findIndex(task => task.id === id)
        if (index !== -1) {
          this.tasks[index] = { ...this.tasks[index], ...taskData }
          resolve(this.tasks[index])
        } else {
          reject(new Error('Task not found'))
        }
      }, 300)
    })
  }

  async deleteTask(id) {
    return new Promise(resolve => {
      setTimeout(() => {
        this.tasks = this.tasks.filter(task => task.id !== id)
        resolve()
      }, 300)
    })
  }
}

export const taskService = new TaskService()
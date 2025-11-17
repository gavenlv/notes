<template>
  <div class="users-management">
    <div class="page-header">
      <h2>用户管理</h2>
      <button @click="showAddUserModal" class="btn btn-primary">添加用户</button>
    </div>
    
    <div class="filters">
      <input 
        v-model="searchQuery" 
        placeholder="搜索用户..." 
        class="search-input"
      >
      <select v-model="roleFilter" class="filter-select">
        <option value="">所有角色</option>
        <option value="admin">管理员</option>
        <option value="user">普通用户</option>
      </select>
    </div>
    
    <div class="users-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>姓名</th>
            <th>邮箱</th>
            <th>角色</th>
            <th>注册日期</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.name }}</td>
            <td>{{ user.email }}</td>
            <td>
              <span :class="['role-badge', user.role]">{{ user.role }}</span>
            </td>
            <td>{{ user.joinDate }}</td>
            <td>
              <button @click="editUser(user)" class="btn btn-small btn-edit">编辑</button>
              <button @click="deleteUser(user.id)" class="btn btn-small btn-delete">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- 添加/编辑用户模态框 -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h3>{{ isEditing ? '编辑用户' : '添加用户' }}</h3>
        <form @submit.prevent="saveUser">
          <div class="form-group">
            <label for="userName">姓名:</label>
            <input type="text" id="userName" v-model="currentUser.name" required>
          </div>
          <div class="form-group">
            <label for="userEmail">邮箱:</label>
            <input type="email" id="userEmail" v-model="currentUser.email" required>
          </div>
          <div class="form-group">
            <label for="userRole">角色:</label>
            <select id="userRole" v-model="currentUser.role" required>
              <option value="user">普通用户</option>
              <option value="admin">管理员</option>
            </select>
          </div>
          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">取消</button>
            <button type="submit" class="btn btn-primary">保存</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UsersManagement',
  data() {
    return {
      searchQuery: '',
      roleFilter: '',
      showModal: false,
      isEditing: false,
      currentUser: {
        id: null,
        name: '',
        email: '',
        role: 'user',
        joinDate: ''
      },
      users: [
        { id: 1, name: '张三', email: 'zhangsan@example.com', role: 'admin', joinDate: '2023-01-15' },
        { id: 2, name: '李四', email: 'lisi@example.com', role: 'user', joinDate: '2023-02-20' },
        { id: 3, name: '王五', email: 'wangwu@example.com', role: 'user', joinDate: '2023-03-10' },
        { id: 4, name: '赵六', email: 'zhaoliu@example.com', role: 'user', joinDate: '2023-04-05' }
      ]
    }
  },
  computed: {
    filteredUsers() {
      return this.users.filter(user => {
        const matchesSearch = user.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                             user.email.toLowerCase().includes(this.searchQuery.toLowerCase())
        const matchesRole = !this.roleFilter || user.role === this.roleFilter
        return matchesSearch && matchesRole
      })
    }
  },
  methods: {
    showAddUserModal() {
      this.isEditing = false
      this.currentUser = {
        id: null,
        name: '',
        email: '',
        role: 'user',
        joinDate: new Date().toISOString().split('T')[0]
      }
      this.showModal = true
    },
    editUser(user) {
      this.isEditing = true
      this.currentUser = { ...user }
      this.showModal = true
    },
    closeModal() {
      this.showModal = false
    },
    saveUser() {
      if (this.isEditing) {
        // 编辑用户
        const index = this.users.findIndex(u => u.id === this.currentUser.id)
        if (index !== -1) {
          this.users.splice(index, 1, { ...this.currentUser })
        }
      } else {
        // 添加用户
        const newUser = {
          ...this.currentUser,
          id: Math.max(...this.users.map(u => u.id)) + 1
        }
        this.users.push(newUser)
      }
      this.closeModal()
    },
    deleteUser(userId) {
      if (confirm('确定要删除这个用户吗？')) {
        this.users = this.users.filter(u => u.id !== userId)
      }
    }
  }
}
</script>

<style scoped>
.users-management {
  padding: 1rem 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-header h2 {
  margin: 0;
}

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.search-input,
.filter-select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.users-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background: #f8f9fa;
  font-weight: bold;
  color: #2c3e50;
}

.role-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
}

.role-badge.admin {
  background: #dc3545;
  color: white;
}

.role-badge.user {
  background: #6c757d;
  color: white;
}

.btn-small {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
  margin-right: 0.5rem;
}

.btn-edit {
  background: #ffc107;
  color: #212529;
}

.btn-delete {
  background: #dc3545;
  color: white;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #2c3e50;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #2c3e50;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}
</style>
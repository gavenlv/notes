<template>
  <div class="user-card">
    <img :src="user.avatar" :alt="user.name" class="avatar" />
    <div class="user-info">
      <h3>{{ user.name }}</h3>
      <p>{{ user.email }}</p>
      <button @click="editUser">编辑信息</button>
    </div>
    
    <!-- 编辑表单 -->
    <div v-if="isEditing" class="edit-form">
      <input v-model="editableUser.name" placeholder="姓名" />
      <input v-model="editableUser.email" placeholder="邮箱" />
      <input v-model="editableUser.avatar" placeholder="头像URL" />
      <button @click="saveUser">保存</button>
      <button @click="cancelEdit">取消</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserCard',
  props: {
    user: {
      type: Object,
      required: true,
      validator(value) {
        return typeof value.name === 'string' && 
               typeof value.email === 'string' && 
               typeof value.avatar === 'string'
      }
    }
  },
  emits: ['user-updated'],
  data() {
    return {
      isEditing: false,
      editableUser: { ...this.user }
    }
  },
  watch: {
    user: {
      handler(newUser) {
        this.editableUser = { ...newUser }
      },
      deep: true
    }
  },
  methods: {
    editUser() {
      this.isEditing = true
      this.editableUser = { ...this.user }
    },
    saveUser() {
      this.$emit('user-updated', { ...this.editableUser })
      this.isEditing = false
    },
    cancelEdit() {
      this.isEditing = false
      this.editableUser = { ...this.user }
    }
  }
}
</script>

<style scoped>
.user-card {
  max-width: 300px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
}

.user-info h3 {
  margin: 10px 0 5px;
}

.user-info p {
  margin: 5px 0;
  color: #666;
}

.edit-form {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.edit-form input {
  display: block;
  width: 100%;
  margin-bottom: 10px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.edit-form button {
  margin-right: 5px;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.edit-form button:first-of-type {
  background-color: #42b983;
  color: white;
}

.edit-form button:last-of-type {
  background-color: #ccc;
}
</style>
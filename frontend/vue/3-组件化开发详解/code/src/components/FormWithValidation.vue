<template>
  <div class="form-container">
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="username">用户名:</label>
        <input 
          id="username" 
          v-model="formData.username" 
          type="text" 
          :class="{ error: errors.username }"
        />
        <span v-if="errors.username" class="error-message">{{ errors.username }}</span>
      </div>

      <div class="form-group">
        <label for="email">邮箱:</label>
        <input 
          id="email" 
          v-model="formData.email" 
          type="email" 
          :class="{ error: errors.email }"
        />
        <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
      </div>

      <div class="form-group">
        <label for="password">密码:</label>
        <input 
          id="password" 
          v-model="formData.password" 
          type="password" 
          :class="{ error: errors.password }"
        />
        <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
      </div>

      <div class="form-group">
        <label for="confirmPassword">确认密码:</label>
        <input 
          id="confirmPassword" 
          v-model="formData.confirmPassword" 
          type="password" 
          :class="{ error: errors.confirmPassword }"
        />
        <span v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword }}</span>
      </div>

      <button type="submit" :disabled="isSubmitting">
        {{ isSubmitting ? '提交中...' : '提交' }}
      </button>
    </form>
  </div>
</template>

<script>
export default {
  name: 'FormWithValidation',
  emits: ['form-submitted'],
  data() {
    return {
      formData: {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      },
      errors: {},
      isSubmitting: false
    }
  },
  methods: {
    validate() {
      this.errors = {}
      
      // 用户名验证
      if (!this.formData.username) {
        this.errors.username = '用户名不能为空'
      } else if (this.formData.username.length < 3) {
        this.errors.username = '用户名至少3个字符'
      }
      
      // 邮箱验证
      if (!this.formData.email) {
        this.errors.email = '邮箱不能为空'
      } else if (!/\S+@\S+\.\S+/.test(this.formData.email)) {
        this.errors.email = '邮箱格式不正确'
      }
      
      // 密码验证
      if (!this.formData.password) {
        this.errors.password = '密码不能为空'
      } else if (this.formData.password.length < 6) {
        this.errors.password = '密码至少6个字符'
      }
      
      // 确认密码验证
      if (!this.formData.confirmPassword) {
        this.errors.confirmPassword = '请确认密码'
      } else if (this.formData.confirmPassword !== this.formData.password) {
        this.errors.confirmPassword = '两次输入的密码不一致'
      }
      
      return Object.keys(this.errors).length === 0
    },
    
    handleSubmit() {
      if (this.validate()) {
        this.isSubmitting = true
        
        // 模拟异步提交
        setTimeout(() => {
          this.$emit('form-submitted', { ...this.formData })
          this.resetForm()
          this.isSubmitting = false
        }, 1000)
      }
    },
    
    resetForm() {
      this.formData = {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      }
      this.errors = {}
    }
  }
}
</script>

<style scoped>
.form-container {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.form-group {
  margin-bottom: 15px;
  text-align: left;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.form-group input.error {
  border-color: #e74c3c;
}

.error-message {
  display: block;
  color: #e74c3c;
  font-size: 14px;
  margin-top: 5px;
}

button {
  width: 100%;
  padding: 12px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>
<template>
  <div class="user-auth">
    <div v-if="!isAuthenticated" class="login-form">
      <h2>用户登录</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">用户名:</label>
          <input 
            type="text" 
            id="username" 
            v-model="loginForm.username" 
            required 
          />
        </div>
        
        <div class="form-group">
          <label for="password">密码:</label>
          <input 
            type="password" 
            id="password" 
            v-model="loginForm.password" 
            required 
          />
        </div>
        
        <button type="submit" :disabled="isLoading">登录</button>
      </form>
    </div>
    
    <div v-else class="user-profile">
      <h2>用户信息</h2>
      <div class="profile-info">
        <img :src="userProfile.avatar" :alt="userProfile.username" class="avatar" />
        <div class="details">
          <p><strong>用户名:</strong> {{ userProfile.username }}</p>
          <p><strong>邮箱:</strong> {{ userProfile.email }}</p>
        </div>
      </div>
      
      <button @click="handleLogout" :disabled="isLoading">登出</button>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex'

export default {
  name: 'UserAuthComponent',
  data() {
    return {
      loginForm: {
        username: 'admin',
        password: 'password'
      }
    }
  },
  computed: {
    ...mapState(['isLoading']),
    ...mapGetters('user', ['userProfile', 'isAuthenticated'])
  },
  methods: {
    async handleLogin() {
      this.$store.dispatch('setLoading', true)
      try {
        const result = await this.$store.dispatch('user/login', this.loginForm)
        if (!result.success) {
          this.$store.dispatch('setError', result.error)
        }
      } finally {
        this.$store.dispatch('setLoading', false)
      }
    },
    
    async handleLogout() {
      this.$store.dispatch('setLoading', true)
      try {
        const result = await this.$store.dispatch('user/logout')
        if (!result.success) {
          this.$store.dispatch('setError', result.error)
        }
      } finally {
        this.$store.dispatch('setLoading', false)
      }
    }
  }
}
</script>

<style scoped>
.user-auth {
  background-color: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
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
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

button {
  background-color: #42b983;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.profile-info {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  margin-right: 20px;
}

.details {
  text-align: left;
}

.details p {
  margin: 5px 0;
}
</style>
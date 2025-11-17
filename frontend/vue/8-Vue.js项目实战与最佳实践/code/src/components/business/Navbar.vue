<template>
  <div class="navbar">
    <div class="logo">任务管理系统</div>
    <div class="user-info" v-if="isLoggedIn">
      <el-dropdown @command="handleCommand">
        <span class="el-dropdown-link">
          用户中心<i class="el-icon-arrow-down el-icon--right"></i>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'Navbar',
  setup() {
    const router = useRouter()
    
    const isLoggedIn = computed(() => {
      return !!localStorage.getItem('token')
    })
    
    const handleCommand = (command) => {
      if (command === 'logout') {
        localStorage.removeItem('token')
        router.push('/login')
      }
    }
    
    return {
      isLoggedIn,
      handleCommand
    }
  }
}
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.logo {
  font-size: 20px;
  font-weight: bold;
}

.user-info {
  cursor: pointer;
}
</style>
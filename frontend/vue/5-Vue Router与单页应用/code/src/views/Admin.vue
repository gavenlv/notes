<template>
  <div class="admin-dashboard">
    <div class="dashboard-header">
      <h1>管理后台</h1>
      <div class="user-info">
        <span>管理员</span>
        <button @click="logout" class="btn btn-outline">退出</button>
      </div>
    </div>
    
    <div class="dashboard-layout">
      <aside class="sidebar">
        <nav class="nav-menu">
          <ul>
            <li v-for="item in menuItems" :key="item.id">
              <router-link 
                :to="item.path" 
                :class="{ active: $route.path === item.path }"
                @click="activeMenu = item.id"
              >
                {{ item.name }}
              </router-link>
            </li>
          </ul>
        </nav>
      </aside>
      
      <main class="main-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminPanel',
  data() {
    return {
      activeMenu: 'dashboard',
      menuItems: [
        { id: 'dashboard', name: '仪表盘', path: '/admin' },
        { id: 'users', name: '用户管理', path: '/admin/users' },
        { id: 'products', name: '产品管理', path: '/admin/products' },
        { id: 'orders', name: '订单管理', path: '/admin/orders' },
        { id: 'settings', name: '系统设置', path: '/admin/settings' }
      ]
    }
  },
  methods: {
    logout() {
      // 模拟退出登录
      alert('已退出管理后台')
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  height: 100%;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: #2c3e50;
  color: white;
}

.dashboard-header h1 {
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-outline {
  background: transparent;
  color: white;
  border: 1px solid white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-outline:hover {
  background: white;
  color: #2c3e50;
}

.dashboard-layout {
  display: flex;
  height: calc(100vh - 70px);
}

.sidebar {
  width: 250px;
  background: #f8f9fa;
  border-right: 1px solid #dee2e6;
}

.nav-menu ul {
  list-style: none;
  padding: 1rem 0;
}

.nav-menu a {
  display: block;
  padding: 1rem 2rem;
  text-decoration: none;
  color: #2c3e50;
  transition: all 0.3s;
  border-left: 3px solid transparent;
}

.nav-menu a:hover,
.nav-menu a.active {
  background: #e9ecef;
  border-left: 3px solid #42b983;
}

.main-content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}
</style>
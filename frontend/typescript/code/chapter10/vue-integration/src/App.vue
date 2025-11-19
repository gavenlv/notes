<!-- Vue 3 + TypeScript 应用主组件 -->
<template>
  <div class="app">
    <header class="app-header">
      <h1>用户管理系统</h1>
      <button 
        class="create-button"
        @click="showCreateForm = true"
      >
        添加用户
      </button>
    </header>
    
    <main class="app-main">
      <!-- 用户统计 -->
      <section class="stats-section">
        <h2>用户统计</h2>
        <div class="stats-cards">
          <div class="stat-card">
            <h3>总用户数</h3>
            <span class="stat-value">{{ userStore.userStats.total }}</span>
          </div>
          <div class="stat-card admin">
            <h3>管理员</h3>
            <span class="stat-value">{{ userStore.userStats.admin }}</span>
          </div>
          <div class="stat-card user">
            <h3>普通用户</h3>
            <span class="stat-value">{{ userStore.userStats.user }}</span>
          </div>
          <div class="stat-card guest">
            <h3>访客</h3>
            <span class="stat-value">{{ userStore.userStats.guest }}</span>
          </div>
        </div>
      </section>
      
      <!-- 用户过滤器 -->
      <section class="filter-section">
        <div class="filter-controls">
          <div class="filter-group">
            <label for="role-filter">角色</label>
            <select id="role-filter" v-model="filters.role" @change="applyFilters">
              <option value="">全部</option>
              <option value="admin">管理员</option>
              <option value="user">普通用户</option>
              <option value="guest">访客</option>
            </select>
          </div>
          
          <div class="filter-group">
            <label for="search-filter">搜索</label>
            <input
              id="search-filter"
              type="text"
              v-model="filters.search"
              placeholder="姓名或邮箱"
              @keyup.enter="applyFilters"
            />
          </div>
          
          <button class="filter-button" @click="applyFilters">
            应用筛选
          </button>
          
          <button class="clear-button" @click="clearFilters">
            清除筛选
          </button>
        </div>
      </section>
      
      <!-- 创建/编辑用户表单 -->
      <section v-if="showCreateForm" class="form-section">
        <h2>{{ editingUserId ? '编辑用户' : '创建用户' }}</h2>
        <form @submit.prevent="handleSubmit" class="user-form">
          <div class="form-group">
            <label for="name">姓名</label>
            <input
              type="text"
              id="name"
              v-model="formData.name"
              required
            />
          </div>
          
          <div class="form-group">
            <label for="email">邮箱</label>
            <input
              type="email"
              id="email"
              v-model="formData.email"
              required
            />
          </div>
          
          <div class="form-group">
            <label for="role">角色</label>
            <select
              id="role"
              v-model="formData.role"
              required
            >
              <option value="admin">管理员</option>
              <option value="user">普通用户</option>
              <option value="guest">访客</option>
            </select>
          </div>
          
          <div v-if="!editingUserId" class="form-group">
            <label for="password">密码</label>
            <input
              type="password"
              id="password"
              v-model="formData.password"
              required
            />
          </div>
          
          <div class="form-actions">
            <button type="submit" class="submit-button" :disabled="userStore.isLoading">
              {{ editingUserId ? '更新' : '创建' }}
            </button>
            <button type="button" class="cancel-button" @click="resetForm">
              取消
            </button>
          </div>
        </form>
      </section>
      
      <!-- 用户列表 -->
      <section class="users-section">
        <div class="section-header">
          <h2>用户列表</h2>
          
          <!-- 分页信息 -->
          <div class="pagination-info">
            显示 {{ paginationInfo.startItem }}-{{ paginationInfo.endItem }} 
            共 {{ paginationInfo.totalItems }} 条
          </div>
        </div>
        
        <div v-if="userStore.isLoading" class="loading">
          加载用户列表中...
        </div>
        
        <div v-else-if="userStore.error" class="error-message">
          {{ userStore.error }}
        </div>
        
        <div v-else-if="userStore.filteredUsers.length === 0" class="empty-state">
          没有找到用户
        </div>
        
        <div v-else class="user-list">
          <UserCard
            v-for="user in paginatedUsers"
            :key="user.id"
            :user="user"
            @edit="handleEditUser"
            @delete="handleDeleteUser"
          />
        </div>
        
        <!-- 分页控件 -->
        <div v-if="paginationInfo.totalPages > 1" class="pagination">
          <button 
            class="pagination-button" 
            @click="goToPage(1)"
            :disabled="currentPage === 1"
          >
            首页
          </button>
          
          <button 
            class="pagination-button" 
            @click="prevPage"
            :disabled="!hasPrevPage"
          >
            上一页
          </button>
          
          <div class="page-numbers">
            <button
              v-for="page in visiblePages"
              :key="page"
              class="pagination-button page-number"
              :class="{ active: page === currentPage }"
              @click="goToPage(page)"
            >
              {{ page }}
            </button>
          </div>
          
          <button 
            class="pagination-button" 
            @click="nextPage"
            :disabled="!hasNextPage"
          >
            下一页
          </button>
          
          <button 
            class="pagination-button" 
            @click="goToPage(totalPages)"
            :disabled="currentPage === totalPages"
          >
            末页
          </button>
          
          <div class="page-size-selector">
            <label for="page-size">每页显示:</label>
            <select id="page-size" v-model="pageSize" @change="changePageSize">
              <option value="5">5</option>
              <option value="10">10</option>
              <option value="20">20</option>
              <option value="50">50</option>
            </select>
          </div>
        </div>
      </section>
    </main>
    
    <footer class="app-footer">
      <p>&copy; 2023 用户管理系统 - TypeScript + Vue 3</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useUserStore, User, CreateUserRequest } from './stores/userStore';
import { usePagination } from './composables/usePagination';
import UserCard from './components/UserCard.vue';

// 用户store
const userStore = useUserStore();

// 表单状态
const showCreateForm = ref(false);
const editingUserId = ref<string | null>(null);

const formData = reactive<CreateUserData & { password: string }>({
  name: '',
  email: '',
  role: 'user',
  password: ''
});

// 过滤器状态
const filters = reactive({
  role: '',
  search: ''
});

// 分页
const {
  currentPage,
  pageSize,
  totalItems,
  totalPages,
  hasNextPage,
  hasPrevPage,
  paginationInfo,
  goToPage,
  nextPage,
  prevPage,
  setPageSize
} = usePagination({ initialPage: 1, initialPageSize: 10 });

// 计算属性
const paginatedUsers = computed(() => {
  const filtered = userStore.filteredUsers;
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filtered.slice(start, end);
});

// 可见页码
const visiblePages = computed(() => {
  const total = totalPages.value;
  const current = currentPage.value;
  const delta = 2; // 当前页前后显示的页数
  
  const range = [];
  const rangeWithDots = [];
  let l;

  for (let i = 1; i <= total; i++) {
    if (i === 1 || i === total || (i >= current - delta && i <= current + delta)) {
      range.push(i);
    }
  }

  range.forEach((i) => {
    if (l) {
      if (i - l === 2) {
        rangeWithDots.push(l + 1);
      } else if (i - l !== 1) {
        rangeWithDots.push('...');
      }
    }
    rangeWithDots.push(i);
    l = i;
  });

  return rangeWithDots.filter(page => page !== '...');
});

// 方法
const resetForm = () => {
  formData.name = '';
  formData.email = '';
  formData.role = 'user';
  formData.password = '';
  editingUserId.value = null;
  showCreateForm.value = false;
};

const handleSubmit = async () => {
  try {
    if (editingUserId.value) {
      await userStore.updateUser(editingUserId.value, {
        name: formData.name,
        email: formData.email,
        role: formData.role
      });
    } else {
      await userStore.createUser({
        name: formData.name,
        email: formData.email,
        role: formData.role,
        password: formData.password
      });
    }
    resetForm();
  } catch (error) {
    console.error('保存用户失败:', error);
  }
};

const handleEditUser = (userId: string) => {
  const user = userStore.users.find(u => u.id === userId);
  if (user) {
    formData.name = user.name;
    formData.email = user.email;
    formData.role = user.role;
    formData.password = '';
    editingUserId.value = userId;
    showCreateForm.value = true;
  }
};

const handleDeleteUser = async (userId: string) => {
  try {
    await userStore.deleteUser(userId);
  } catch (error) {
    console.error('删除用户失败:', error);
  }
};

const applyFilters = () => {
  userStore.setFilters({ ...filters });
  goToPage(1); // 重置到第一页
};

const clearFilters = () => {
  filters.role = '';
  filters.search = '';
  userStore.clearFilters();
  goToPage(1); // 重置到第一页
};

const changePageSize = () => {
  setPageSize(pageSize.value);
  goToPage(1); // 重置到第一页
};

// 生命周期
onMounted(() => {
  userStore.fetchUsers();
});

// 监听总项目数变化
watch(() => userStore.filteredUsers.length, (newCount) => {
  totalItems.value = newCount;
  // 如果当前页超出范围，调整到有效页面
  if (currentPage.value > totalPages.value) {
    goToPage(Math.max(1, totalPages.value));
  }
});
</script>

<style>
/* 全局样式 */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: #f5f5f5;
}

.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* 头部样式 */
.app-header {
  background-color: #2c3e50;
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.app-header h1 {
  font-size: 1.8rem;
  font-weight: 600;
}

.create-button {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: background-color 0.2s;
}

.create-button:hover {
  background-color: #2980b9;
}

/* 主内容区域 */
.app-main {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  width: 100%;
}

/* 统计部分 */
.stats-section {
  margin-bottom: 2rem;
}

.stats-section h2 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.stat-card {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-card h3 {
  font-size: 0.9rem;
  color: #7f8c8d;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
}

.stat-card.admin .stat-value {
  color: #e74c3c;
}

.stat-card.user .stat-value {
  color: #3498db;
}

.stat-card.guest .stat-value {
  color: #95a5a6;
}

/* 过滤器部分 */
.filter-section {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.filter-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  min-width: 150px;
}

.filter-group label {
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.filter-group input,
.filter-group select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.filter-button,
.clear-button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.filter-button {
  background-color: #27ae60;
  color: white;
}

.filter-button:hover {
  background-color: #219a52;
}

.clear-button {
  background-color: #95a5a6;
  color: white;
}

.clear-button:hover {
  background-color: #7f8c8d;
}

/* 表单样式 */
.form-section {
  background-color: white;
  border-radius: 8px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-section h2 {
  margin-bottom: 1.5rem;
  color: #2c3e50;
}

.user-form {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group input,
.form-group select {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.form-actions {
  grid-column: 1 / -1;
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.submit-button,
.cancel-button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.submit-button {
  background-color: #27ae60;
  color: white;
}

.submit-button:hover {
  background-color: #219a52;
}

.cancel-button {
  background-color: #95a5a6;
  color: white;
}

.cancel-button:hover {
  background-color: #7f8c8d;
}

.submit-button:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

/* 用户列表部分 */
.users-section h2 {
  margin-bottom: 1.5rem;
  color: #2c3e50;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.pagination-info {
  font-size: 0.9rem;
  color: #7f8c8d;
}

.loading,
.error-message,
.empty-state {
  background-color: white;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  margin-bottom: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.error-message {
  color: #e74c3c;
}

.user-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

/* 分页样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 2rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.pagination-button {
  padding: 0.5rem 0.75rem;
  border: 1px solid #ddd;
  background-color: white;
  color: #333;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-button:hover:not(:disabled) {
  background-color: #f1f1f1;
}

.pagination-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-button.page-number.active {
  background-color: #3498db;
  color: white;
  border-color: #3498db;
}

.page-numbers {
  display: flex;
  gap: 0.25rem;
}

.page-size-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-left: 1rem;
}

.page-size-selector label {
  font-size: 0.9rem;
}

.page-size-selector select {
  padding: 0.25rem 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

/* 底部样式 */
.app-footer {
  background-color: #34495e;
  color: white;
  text-align: center;
  padding: 1.5rem;
  margin-top: 2rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .app-main {
    padding: 1rem;
  }
  
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .filter-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    min-width: auto;
  }
  
  .user-list {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .pagination {
    flex-direction: column;
    gap: 1rem;
  }
  
  .page-size-selector {
    margin-left: 0;
    align-self: center;
  }
}
</style>
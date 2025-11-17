<template>
  <div class="user-profile" v-if="user">
    <div class="profile-header">
      <img :src="user.avatar" :alt="user.name" class="avatar">
      <div class="user-info">
        <h1>{{ user.name }}</h1>
        <p class="email">{{ user.email }}</p>
        <p class="role">{{ user.role }}</p>
      </div>
    </div>
    
    <div class="profile-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
        class="tab-button"
      >
        {{ tab.name }}
      </button>
    </div>
    
    <div class="tab-content">
      <div v-if="activeTab === 'profile'" class="tab-pane">
        <h3>个人信息</h3>
        <div class="profile-details">
          <div class="detail-item">
            <label>姓名:</label>
            <span>{{ user.name }}</span>
          </div>
          <div class="detail-item">
            <label>邮箱:</label>
            <span>{{ user.email }}</span>
          </div>
          <div class="detail-item">
            <label>角色:</label>
            <span>{{ user.role }}</span>
          </div>
          <div class="detail-item">
            <label>注册日期:</label>
            <span>{{ user.joinDate }}</span>
          </div>
        </div>
      </div>
      
      <div v-if="activeTab === 'orders'" class="tab-pane">
        <h3>订单历史</h3>
        <div v-if="user.orders.length > 0" class="orders-list">
          <div v-for="order in user.orders" :key="order.id" class="order-item">
            <div class="order-header">
              <span class="order-id">订单号: {{ order.id }}</span>
              <span class="order-date">{{ order.date }}</span>
              <span class="order-status" :class="order.status">{{ order.status }}</span>
            </div>
            <div class="order-products">
              <div v-for="item in order.items" :key="item.id" class="order-product">
                <img :src="item.image" :alt="item.name" class="product-thumb">
                <div class="product-info">
                  <h4>{{ item.name }}</h4>
                  <p>数量: {{ item.quantity }} | 单价: ${{ item.price }}</p>
                </div>
              </div>
            </div>
            <div class="order-total">
              总计: ${{ order.total }}
            </div>
          </div>
        </div>
        <div v-else class="no-orders">
          <p>暂无订单记录</p>
        </div>
      </div>
      
      <div v-if="activeTab === 'settings'" class="tab-pane">
        <h3>账户设置</h3>
        <form @submit.prevent="saveSettings" class="settings-form">
          <div class="form-group">
            <label for="name">姓名:</label>
            <input type="text" id="name" v-model="editableUser.name" required>
          </div>
          <div class="form-group">
            <label for="email">邮箱:</label>
            <input type="email" id="email" v-model="editableUser.email" required>
          </div>
          <div class="form-group">
            <label for="password">新密码:</label>
            <input type="password" id="password" v-model="editableUser.password">
          </div>
          <button type="submit" class="btn btn-primary">保存设置</button>
        </form>
      </div>
    </div>
  </div>
  <div v-else class="loading">
    加载中...
  </div>
</template>

<script>
export default {
  name: 'UserProfile',
  props: {
    id: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      activeTab: 'profile',
      tabs: [
        { id: 'profile', name: '个人资料' },
        { id: 'orders', name: '订单历史' },
        { id: 'settings', name: '账户设置' }
      ],
      editableUser: {
        name: '',
        email: '',
        password: ''
      },
      // 模拟用户数据
      user: {
        id: 1,
        name: '张三',
        email: 'zhangsan@example.com',
        role: '普通用户',
        avatar: 'https://via.placeholder.com/150',
        joinDate: '2023-01-15',
        orders: [
          {
            id: 'ORD001',
            date: '2023-05-20',
            status: '已发货',
            total: 1200,
            items: [
              {
                id: 1,
                name: '笔记本电脑',
                quantity: 1,
                price: 1200,
                image: 'https://via.placeholder.com/50x50?text=Laptop'
              }
            ]
          },
          {
            id: 'ORD002',
            date: '2023-04-10',
            status: '已完成',
            total: 450,
            items: [
              {
                id: 2,
                name: '智能手机',
                quantity: 1,
                price: 300,
                image: 'https://via.placeholder.com/50x50?text=Phone'
              },
              {
                id: 3,
                name: '无线耳机',
                quantity: 1,
                price: 150,
                image: 'https://via.placeholder.com/50x50?text=Earbuds'
              }
            ]
          }
        ]
      }
    }
  },
  mounted() {
    // 初始化可编辑用户数据
    this.editableUser.name = this.user.name
    this.editableUser.email = this.user.email
  },
  methods: {
    saveSettings() {
      // 模拟保存设置
      this.user.name = this.editableUser.name
      this.user.email = this.editableUser.email
      alert('设置已保存!')
    }
  }
}
</script>

<style scoped>
.user-profile {
  max-width: 1000px;
  margin: 0 auto;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 2rem;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
}

.user-info h1 {
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.email {
  color: #6c757d;
  margin-bottom: 0.5rem;
}

.role {
  background: #42b983;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
}

.profile-tabs {
  display: flex;
  border-bottom: 1px solid #ddd;
  margin-bottom: 2rem;
}

.tab-button {
  padding: 1rem 2rem;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  color: #6c757d;
}

.tab-button.active {
  color: #42b983;
  border-bottom: 3px solid #42b983;
}

.tab-content {
  min-height: 300px;
}

.tab-pane h3 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.profile-details {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #eee;
}

.detail-item label {
  font-weight: bold;
  color: #2c3e50;
}

.orders-list {
  display: grid;
  gap: 1.5rem;
}

.order-item {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 1.5rem;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.order-id {
  font-weight: bold;
}

.order-date {
  color: #6c757d;
}

.order-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
}

.order-status.已发货 {
  background: #ffc107;
  color: #212529;
}

.order-status.已完成 {
  background: #28a745;
  color: white;
}

.order-products {
  margin-bottom: 1rem;
}

.order-product {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.product-thumb {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 4px;
}

.product-info h4 {
  margin-bottom: 0.25rem;
}

.order-total {
  font-weight: bold;
  text-align: right;
  font-size: 1.1rem;
}

.no-orders {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}

.settings-form {
  max-width: 500px;
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

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.btn-primary {
  background-color: #42b983;
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s;
}

.btn-primary:hover {
  background-color: #359c6d;
}

.loading {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
}
</style>
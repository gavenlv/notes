<template>
  <div class="orders-management">
    <div class="page-header">
      <h2>订单管理</h2>
    </div>
    
    <div class="filters">
      <input 
        v-model="searchQuery" 
        placeholder="搜索订单..." 
        class="search-input"
      >
      <select v-model="statusFilter" class="filter-select">
        <option value="">所有状态</option>
        <option value="pending">待处理</option>
        <option value="processing">处理中</option>
        <option value="shipped">已发货</option>
        <option value="delivered">已完成</option>
        <option value="cancelled">已取消</option>
      </select>
    </div>
    
    <div class="orders-table">
      <table>
        <thead>
          <tr>
            <th>订单号</th>
            <th>客户</th>
            <th>日期</th>
            <th>金额</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in filteredOrders" :key="order.id">
            <td>{{ order.id }}</td>
            <td>{{ order.customer }}</td>
            <td>{{ order.date }}</td>
            <td>${{ order.amount }}</td>
            <td>
              <span :class="['status-badge', order.status]">{{ order.status }}</span>
            </td>
            <td>
              <button @click="viewOrder(order)" class="btn btn-small btn-view">查看</button>
              <button @click="updateOrderStatus(order)" class="btn btn-small btn-edit">更新状态</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- 订单详情模态框 -->
    <div v-if="showOrderModal" class="modal-overlay" @click="closeOrderModal">
      <div class="modal-content order-modal" @click.stop>
        <h3>订单详情 - {{ selectedOrder.id }}</h3>
        <div class="order-details">
          <div class="order-info">
            <p><strong>客户:</strong> {{ selectedOrder.customer }}</p>
            <p><strong>日期:</strong> {{ selectedOrder.date }}</p>
            <p><strong>状态:</strong> 
              <span :class="['status-badge', selectedOrder.status]">{{ selectedOrder.status }}</span>
            </p>
            <p><strong>总金额:</strong> ${{ selectedOrder.amount }}</p>
          </div>
          
          <h4>订单项目</h4>
          <div class="order-items">
            <div v-for="item in selectedOrder.items" :key="item.id" class="order-item">
              <img :src="item.image" :alt="item.name" class="item-image">
              <div class="item-details">
                <h5>{{ item.name }}</h5>
                <p>数量: {{ item.quantity }} | 单价: ${{ item.price }}</p>
              </div>
            </div>
          </div>
          
          <div class="modal-actions">
            <button @click="closeOrderModal" class="btn btn-secondary">关闭</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'OrdersManagement',
  data() {
    return {
      searchQuery: '',
      statusFilter: '',
      showOrderModal: false,
      selectedOrder: {},
      orders: [
        {
          id: 'ORD001',
          customer: '张三',
          date: '2023-05-20',
          amount: 1200,
          status: 'shipped',
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
          customer: '李四',
          date: '2023-05-18',
          amount: 450,
          status: 'delivered',
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
        },
        {
          id: 'ORD003',
          customer: '王五',
          date: '2023-05-15',
          amount: 800,
          status: 'processing',
          items: [
            {
              id: 2,
              name: '智能手机',
              quantity: 1,
              price: 800,
              image: 'https://via.placeholder.com/50x50?text=Phone'
            }
          ]
        },
        {
          id: 'ORD004',
          customer: '赵六',
          date: '2023-05-10',
          amount: 250,
          status: 'pending',
          items: [
            {
              id: 4,
              name: 'T恤衫',
              quantity: 2,
              price: 125,
              image: 'https://via.placeholder.com/50x50?text=T-Shirt'
            }
          ]
        }
      ]
    }
  },
  computed: {
    filteredOrders() {
      return this.orders.filter(order => {
        const matchesSearch = order.id.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                             order.customer.toLowerCase().includes(this.searchQuery.toLowerCase())
        const matchesStatus = !this.statusFilter || order.status === this.statusFilter
        return matchesSearch && matchesStatus
      })
    }
  },
  methods: {
    viewOrder(order) {
      this.selectedOrder = { ...order }
      this.showOrderModal = true
    },
    closeOrderModal() {
      this.showOrderModal = false
    },
    updateOrderStatus(order) {
      const statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
      const currentIndex = statuses.indexOf(order.status)
      const nextIndex = (currentIndex + 1) % statuses.length
      const nextStatus = statuses[nextIndex]
      
      // 更新订单状态
      const orderToUpdate = this.orders.find(o => o.id === order.id)
      if (orderToUpdate) {
        orderToUpdate.status = nextStatus
      }
      
      // 如果是查看的订单，也更新查看的订单状态
      if (this.selectedOrder.id === order.id) {
        this.selectedOrder.status = nextStatus
      }
    }
  }
}
</script>

<style scoped>
.orders-management {
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

.orders-table {
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

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
  text-transform: capitalize;
}

.status-badge.pending {
  background: #ffc107;
  color: #212529;
}

.status-badge.processing {
  background: #17a2b8;
  color: white;
}

.status-badge.shipped {
  background: #007bff;
  color: white;
}

.status-badge.delivered {
  background: #28a745;
  color: white;
}

.status-badge.cancelled {
  background: #dc3545;
  color: white;
}

.btn-small {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
  margin-right: 0.5rem;
}

.btn-view {
  background: #6c757d;
  color: white;
}

.btn-edit {
  background: #ffc107;
  color: #212529;
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
  max-width: 600px;
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #2c3e50;
}

.order-info {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1.5rem;
}

.order-info p {
  margin: 0.5rem 0;
}

.order-items {
  margin-bottom: 1.5rem;
}

.order-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid #eee;
}

.item-image {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 4px;
}

.item-details h5 {
  margin: 0 0 0.25rem 0;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
}

.order-modal {
  max-height: 80vh;
  overflow-y: auto;
}
</style>
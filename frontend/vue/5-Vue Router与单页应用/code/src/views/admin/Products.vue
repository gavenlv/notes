<template>
  <div class="products-management">
    <div class="page-header">
      <h2>产品管理</h2>
      <button @click="showAddProductModal" class="btn btn-primary">添加产品</button>
    </div>
    
    <div class="filters">
      <input 
        v-model="searchQuery" 
        placeholder="搜索产品..." 
        class="search-input"
      >
      <select v-model="categoryFilter" class="filter-select">
        <option value="">所有分类</option>
        <option value="electronics">电子产品</option>
        <option value="clothing">服装</option>
        <option value="books">图书</option>
      </select>
    </div>
    
    <div class="products-grid">
      <div 
        v-for="product in filteredProducts" 
        :key="product.id" 
        class="product-card"
      >
        <img :src="product.image" :alt="product.name" class="product-image">
        <div class="product-info">
          <h3>{{ product.name }}</h3>
          <p class="product-category">{{ product.category }}</p>
          <p class="product-price">${{ product.price }}</p>
          <div class="product-actions">
            <button @click="editProduct(product)" class="btn btn-small btn-edit">编辑</button>
            <button @click="deleteProduct(product.id)" class="btn btn-small btn-delete">删除</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 添加/编辑产品模态框 -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h3>{{ isEditing ? '编辑产品' : '添加产品' }}</h3>
        <form @submit.prevent="saveProduct">
          <div class="form-group">
            <label for="productName">产品名称:</label>
            <input type="text" id="productName" v-model="currentProduct.name" required>
          </div>
          <div class="form-group">
            <label for="productCategory">分类:</label>
            <select id="productCategory" v-model="currentProduct.category" required>
              <option value="electronics">电子产品</option>
              <option value="clothing">服装</option>
              <option value="books">图书</option>
            </select>
          </div>
          <div class="form-group">
            <label for="productPrice">价格:</label>
            <input type="number" id="productPrice" v-model.number="currentProduct.price" step="0.01" required>
          </div>
          <div class="form-group">
            <label for="productImage">图片URL:</label>
            <input type="text" id="productImage" v-model="currentProduct.image" required>
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
  name: 'ProductsManagement',
  data() {
    return {
      searchQuery: '',
      categoryFilter: '',
      showModal: false,
      isEditing: false,
      currentProduct: {
        id: null,
        name: '',
        category: 'electronics',
        price: 0,
        image: ''
      },
      products: [
        {
          id: 1,
          name: '笔记本电脑',
          category: 'electronics',
          price: 1200,
          image: 'https://via.placeholder.com/300x200?text=Laptop'
        },
        {
          id: 2,
          name: '智能手机',
          category: 'electronics',
          price: 800,
          image: 'https://via.placeholder.com/300x200?text=Smartphone'
        },
        {
          id: 3,
          name: 'T恤衫',
          category: 'clothing',
          price: 25,
          image: 'https://via.placeholder.com/300x200?text=T-Shirt'
        },
        {
          id: 4,
          name: 'JavaScript权威指南',
          category: 'books',
          price: 65,
          image: 'https://via.placeholder.com/300x200?text=JavaScript+Guide'
        }
      ]
    }
  },
  computed: {
    filteredProducts() {
      return this.products.filter(product => {
        const matchesSearch = product.name.toLowerCase().includes(this.searchQuery.toLowerCase())
        const matchesCategory = !this.categoryFilter || product.category === this.categoryFilter
        return matchesSearch && matchesCategory
      })
    }
  },
  methods: {
    showAddProductModal() {
      this.isEditing = false
      this.currentProduct = {
        id: null,
        name: '',
        category: 'electronics',
        price: 0,
        image: ''
      }
      this.showModal = true
    },
    editProduct(product) {
      this.isEditing = true
      this.currentProduct = { ...product }
      this.showModal = true
    },
    closeModal() {
      this.showModal = false
    },
    saveProduct() {
      if (this.isEditing) {
        // 编辑产品
        const index = this.products.findIndex(p => p.id === this.currentProduct.id)
        if (index !== -1) {
          this.products.splice(index, 1, { ...this.currentProduct })
        }
      } else {
        // 添加产品
        const newProduct = {
          ...this.currentProduct,
          id: Math.max(...this.products.map(p => p.id)) + 1
        }
        this.products.push(newProduct)
      }
      this.closeModal()
    },
    deleteProduct(productId) {
      if (confirm('确定要删除这个产品吗？')) {
        this.products = this.products.filter(p => p.id !== productId)
      }
    }
  }
}
</script>

<style scoped>
.products-management {
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

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 2rem;
}

.product-card {
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.3s;
}

.product-card:hover {
  transform: translateY(-5px);
}

.product-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.product-info {
  padding: 1rem;
}

.product-info h3 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
}

.product-category {
  color: #6c757d;
  font-size: 0.875rem;
  margin: 0 0 0.5rem 0;
}

.product-price {
  font-size: 1.25rem;
  font-weight: bold;
  color: #42b983;
  margin: 0 0 1rem 0;
}

.product-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-small {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
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
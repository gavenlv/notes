<template>
  <div class="product-list">
    <h2>产品列表</h2>
    
    <!-- 分类筛选 -->
    <div class="category-filter">
      <button 
        v-for="category in categories" 
        :key="category"
        :class="{ active: selectedCategory === category }"
        @click="selectCategory(category)"
      >
        {{ category }}
      </button>
    </div>
    
    <!-- 产品列表 -->
    <div class="products-grid">
      <div 
        v-for="product in filteredProducts" 
        :key="product.id" 
        class="product-card"
      >
        <img :src="product.image" :alt="product.name" class="product-image" />
        <div class="product-info">
          <h3>{{ product.name }}</h3>
          <p class="price">¥{{ product.price }}</p>
          <button @click="addToCart(product)">加入购物车</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex'

export default {
  name: 'ProductListComponent',
  computed: {
    ...mapState('products', ['categories']),
    ...mapGetters('products', ['filteredProducts', 'selectedCategory'])
  },
  methods: {
    ...mapActions('products', ['selectCategory', 'addToCart'])
  }
}
</script>

<style scoped>
.product-list {
  margin-bottom: 30px;
}

.category-filter {
  margin-bottom: 20px;
}

.category-filter button {
  background-color: #eee;
  border: none;
  padding: 8px 16px;
  margin-right: 10px;
  border-radius: 4px;
  cursor: pointer;
}

.category-filter button.active {
  background-color: #42b983;
  color: white;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.product-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.2s;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.product-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.product-info {
  padding: 15px;
}

.product-info h3 {
  margin: 0 0 10px 0;
}

.price {
  font-size: 18px;
  font-weight: bold;
  color: #42b983;
  margin: 10px 0;
}

.product-info button {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}
</style>
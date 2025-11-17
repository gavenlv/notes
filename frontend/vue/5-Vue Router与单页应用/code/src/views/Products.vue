<template>
  <div class="products">
    <h1>产品列表</h1>
    
    <div class="filters">
      <input 
        v-model="searchQuery" 
        placeholder="搜索产品..." 
        class="search-input"
      >
    </div>
    
    <div class="product-grid">
      <div 
        v-for="product in filteredProducts" 
        :key="product.id" 
        class="product-card"
      >
        <img :src="product.image" :alt="product.name" class="product-image">
        <div class="product-info">
          <h3>{{ product.name }}</h3>
          <p class="product-price">${{ product.price }}</p>
          <p class="product-description">{{ product.description }}</p>
          <router-link 
            :to="{ name: 'ProductDetail', params: { id: product.id } }" 
            class="details-link"
          >
            查看详情
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProductsPage',
  data() {
    return {
      searchQuery: '',
      products: [
        {
          id: 1,
          name: '智能手机',
          price: 699,
          description: '最新款智能手机，配备先进的摄像头和长续航电池。',
          image: 'https://via.placeholder.com/300x200?text=Smartphone'
        },
        {
          id: 2,
          name: '笔记本电脑',
          price: 1299,
          description: '轻薄便携的笔记本电脑，适合办公和娱乐。',
          image: 'https://via.placeholder.com/300x200?text=Laptop'
        },
        {
          id: 3,
          name: '无线耳机',
          price: 199,
          description: '高品质无线耳机，提供沉浸式音频体验。',
          image: 'https://via.placeholder.com/300x200?text=Headphones'
        },
        {
          id: 4,
          name: '智能手表',
          price: 299,
          description: '功能丰富的智能手表，支持健康监测和消息提醒。',
          image: 'https://via.placeholder.com/300x200?text=Smartwatch'
        }
      ]
    }
  },
  computed: {
    filteredProducts() {
      return this.products.filter(product => 
        product.name.toLowerCase().includes(this.searchQuery.toLowerCase())
      )
    }
  }
}
</script>

<style scoped>
.products {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.filters {
  margin-bottom: 2rem;
}

.search-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
}

.product-card {
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;
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
  padding: 1.5rem;
}

.product-info h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.product-price {
  font-size: 1.25rem;
  font-weight: bold;
  color: #42b983;
  margin: 0.5rem 0;
}

.product-description {
  color: #666;
  margin: 0.5rem 0;
}

.details-link {
  display: inline-block;
  background-color: #42b983;
  color: white;
  padding: 0.5rem 1rem;
  text-decoration: none;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.details-link:hover {
  background-color: #359c6d;
}

@media (max-width: 768px) {
  .products {
    padding: 1rem;
  }
  
  .product-grid {
    grid-template-columns: 1fr;
  }
}
</style>
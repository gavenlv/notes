<template>
  <div class="product-detail" v-if="product">
    <div class="product-header">
      <img :src="product.image" :alt="product.name" class="product-image">
      <div class="product-info">
        <h1>{{ product.name }}</h1>
        <p class="price">${{ product.price }}</p>
        <p class="description">{{ product.description }}</p>
        <button @click="addToCart" class="btn btn-primary">加入购物车</button>
      </div>
    </div>
    
    <div class="product-tabs">
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
      <div v-if="activeTab === 'description'" class="tab-pane">
        <h3>产品描述</h3>
        <p>{{ product.fullDescription }}</p>
      </div>
      <div v-if="activeTab === 'specs'" class="tab-pane">
        <h3>技术规格</h3>
        <ul>
          <li v-for="(spec, key) in product.specs" :key="key">
            <strong>{{ key }}:</strong> {{ spec }}
          </li>
        </ul>
      </div>
      <div v-if="activeTab === 'reviews'" class="tab-pane">
        <h3>用户评价</h3>
        <div v-for="review in product.reviews" :key="review.id" class="review">
          <div class="review-header">
            <span class="reviewer">{{ review.user }}</span>
            <span class="rating">{{ '★'.repeat(review.rating) }}</span>
          </div>
          <p class="review-content">{{ review.comment }}</p>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="not-found">
    <h2>产品未找到</h2>
    <p>抱歉，您查找的产品不存在。</p>
    <router-link to="/products" class="btn">返回产品列表</router-link>
  </div>
</template>

<script>
export default {
  name: 'ProductDetail',
  props: {
    id: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      activeTab: 'description',
      tabs: [
        { id: 'description', name: '描述' },
        { id: 'specs', name: '规格' },
        { id: 'reviews', name: '评价' }
      ],
      products: [
        {
          id: 1,
          name: '笔记本电脑',
          price: 1200,
          image: 'https://via.placeholder.com/400x300?text=Laptop',
          description: '高性能笔记本电脑，适合办公和娱乐',
          fullDescription: '这款笔记本电脑配备了最新的处理器和大容量内存，能够轻松应对各种工作任务。高清显示屏带来出色的视觉体验，长续航电池确保您在外出时也能持续工作。',
          specs: {
            处理器: 'Intel Core i7',
            内存: '16GB RAM',
            存储: '512GB SSD',
            显示屏: '15.6英寸 Full HD',
            重量: '1.8kg'
          },
          reviews: [
            { id: 1, user: '张三', rating: 5, comment: '性能出色，非常满意！' },
            { id: 2, user: '李四', rating: 4, comment: '性价比很高，推荐购买。' }
          ]
        },
        {
          id: 2,
          name: '智能手机',
          price: 800,
          image: 'https://via.placeholder.com/400x300?text=Smartphone',
          description: '功能强大的智能手机，拍照效果出色',
          fullDescription: '这款智能手机拥有高分辨率摄像头和先进的图像处理技术，让您随时随地捕捉精彩瞬间。流畅的操作系统和大容量电池为您提供全天候的使用体验。',
          specs: {
            屏幕: '6.1英寸 OLED',
            处理器: 'Snapdragon 888',
            内存: '8GB RAM',
            存储: '128GB',
            摄像头: '48MP 主摄'
          },
          reviews: [
            { id: 1, user: '王五', rating: 5, comment: '拍照效果太棒了！' },
            { id: 2, user: '赵六', rating: 4, comment: '运行流畅，电池续航不错。' }
          ]
        }
      ]
    }
  },
  computed: {
    product() {
      return this.products.find(p => p.id == this.id)
    }
  },
  methods: {
    addToCart() {
      alert(`${this.product.name} 已加入购物车！`)
    }
  },
  watch: {
    id: {
      handler() {
        // 当路由参数变化时重置活动标签
        this.activeTab = 'description'
      },
      immediate: true
    }
  }
}
</script>

<style scoped>
.product-detail {
  max-width: 1000px;
  margin: 0 auto;
}

.product-header {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
}

.product-image {
  flex: 1;
  max-width: 400px;
  height: 300px;
  object-fit: cover;
  border-radius: 8px;
}

.product-info {
  flex: 1;
}

.product-info h1 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.price {
  font-size: 2rem;
  font-weight: bold;
  color: #42b983;
  margin-bottom: 1rem;
}

.description {
  margin-bottom: 2rem;
  line-height: 1.6;
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

.product-tabs {
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
  min-height: 200px;
}

.tab-pane h3 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.review {
  border-bottom: 1px solid #eee;
  padding: 1rem 0;
}

.review-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.reviewer {
  font-weight: bold;
}

.rating {
  color: #ffc107;
}

.not-found {
  text-align: center;
  padding: 2rem;
}

.not-found h2 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.not-found p {
  margin-bottom: 2rem;
  color: #6c757d;
}
</style>
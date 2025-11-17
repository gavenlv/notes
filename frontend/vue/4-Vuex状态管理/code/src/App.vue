<template>
  <div id="app">
    <header>
      <h1>Vue.js Vuex 状态管理示例</h1>
    </header>
    
    <main>
      <!-- 用户认证组件 -->
      <UserAuth />
      
      <!-- 产品列表组件 -->
      <ProductList />
      
      <!-- 购物车组件 -->
      <ShoppingCart />
    </main>
  </div>
</template>

<script>
import UserAuth from './components/UserAuth.vue'
import ProductList from './components/ProductList.vue'
import ShoppingCart from './components/ShoppingCart.vue'

export default {
  name: 'App',
  components: {
    UserAuth,
    ProductList,
    ShoppingCart
  },
  mounted() {
    // 初始化数据
    this.$store.dispatch('products/fetchProducts')
    this.$store.dispatch('products/fetchCategories')
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

header {
  margin-bottom: 40px;
}

main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}
</style>
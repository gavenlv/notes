<template>
  <div class="async-component-demo">
    <h2>Async Component Demo</h2>
    <p>Click the button below to load an async component:</p>
    <button @click="loadComponent" :disabled="loading">
      {{ loading ? 'Loading...' : 'Load Async Component' }}
    </button>
    
    <!-- 异步组件占位符 -->
    <div v-if="error" class="error">
      Error loading component: {{ error.message }}
    </div>
    
    <!-- 使用Suspense包装异步组件 -->
    <Suspense v-else>
      <template #default>
        <AsyncComponent v-if="showAsyncComponent" />
      </template>
      <template #fallback>
        <div>Loading async component...</div>
      </template>
    </Suspense>
  </div>
</template>

<script>
import { defineAsyncComponent } from 'vue'

export default {
  name: 'AsyncComponentDemo',
  data() {
    return {
      showAsyncComponent: false,
      loading: false,
      error: null
    }
  },
  methods: {
    async loadComponent() {
      this.loading = true
      this.error = null
      
      try {
        // 动态导入组件
        const { default: AsyncComponent } = await import('./HeavyComponent.vue')
        
        // 注册异步组件
        this.$options.components.AsyncComponent = AsyncComponent
        
        // 显示组件
        this.showAsyncComponent = true
      } catch (err) {
        this.error = err
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.async-component-demo {
  margin: 20px 0;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  padding: 10px 20px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.error {
  color: red;
  margin-top: 10px;
}
</style>
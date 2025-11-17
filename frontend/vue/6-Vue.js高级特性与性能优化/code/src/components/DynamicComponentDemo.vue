<template>
  <div class="dynamic-component-demo">
    <h2>Dynamic Component Demo</h2>
    <div class="component-selector">
      <button 
        v-for="tab in tabs" 
        :key="tab.name"
        :class="{ active: currentTab === tab.name }"
        @click="currentTab = tab.name"
      >
        {{ tab.name }}
      </button>
    </div>
    
    <!-- 使用keep-alive缓存动态组件 -->
    <keep-alive>
      <component :is="currentTabComponent" class="tab"></component>
    </keep-alive>
  </div>
</template>

<script>
import TabHome from './TabHome.vue'
import TabPosts from './TabPosts.vue'
import TabArchive from './TabArchive.vue'

export default {
  name: 'DynamicComponentDemo',
  components: {
    TabHome,
    TabPosts,
    TabArchive
  },
  data() {
    return {
      currentTab: 'TabHome',
      tabs: [
        { name: 'TabHome', component: TabHome },
        { name: 'TabPosts', component: TabPosts },
        { name: 'TabArchive', component: TabArchive }
      ]
    }
  },
  computed: {
    currentTabComponent() {
      return this.currentTab
    }
  }
}
</script>

<style scoped>
.component-selector {
  margin-bottom: 20px;
}

button {
  padding: 10px 20px;
  margin-right: 10px;
  background-color: #f0f0f0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button.active {
  background-color: #42b983;
  color: white;
}

.tab {
  border: 1px solid #ddd;
  padding: 20px;
  border-radius: 4px;
}
</style>
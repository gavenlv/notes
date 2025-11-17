<template>
  <div class="sidebar">
    <el-menu
      :default-active="activeIndex"
      class="el-menu-vertical"
      @select="handleSelect"
    >
      <el-menu-item index="1">
        <i class="el-icon-house"></i>
        <span>首页</span>
      </el-menu-item>
      <el-menu-item index="2">
        <i class="el-icon-document"></i>
        <span>任务管理</span>
      </el-menu-item>
    </el-menu>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'

export default {
  name: 'Sidebar',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const activeIndex = ref('1')
    
    // 根据当前路由设置激活菜单项
    const setActiveMenu = () => {
      if (route.path === '/') {
        activeIndex.value = '1'
      } else if (route.path === '/tasks') {
        activeIndex.value = '2'
      }
    }
    
    setActiveMenu()
    
    const handleSelect = (index) => {
      switch (index) {
        case '1':
          router.push('/')
          break
        case '2':
          router.push('/tasks')
          break
      }
    }
    
    return {
      activeIndex,
      handleSelect
    }
  }
}
</script>

<style scoped>
.sidebar {
  height: 100%;
}

.el-menu-vertical {
  height: 100%;
  border-right: none;
}
</style>
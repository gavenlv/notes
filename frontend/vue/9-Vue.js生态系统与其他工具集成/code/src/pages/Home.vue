<template>
  <div class="home-page">
    <h1>Vue.js生态系统与其他工具集成示例</h1>
    <p>本项目展示了Vue.js生态系统与其他工具的集成方式，包括开发工具、构建工具、测试工具等。</p>
    
    <div class="section">
      <h2>核心特性</h2>
      <div class="features">
        <div class="feature-card" v-for="feature in features" :key="feature.title">
          <h3>{{ feature.title }}</h3>
          <p>{{ feature.description }}</p>
        </div>
      </div>
    </div>
    
    <div class="section">
      <h2>组件示例</h2>
      <div class="component-examples">
        <div class="example-card">
          <h3>用户资料组件</h3>
          <p>展示了Vue DevTools调试、异步数据获取和组合式函数的使用。</p>
          <UserProfile />
        </div>
        
        <div class="example-card">
          <h3>移动端卡片组件</h3>
          <p>展示了响应式设计和移动端优化的组件实现。</p>
          <MobileCard title="移动端示例" description="这是一个移动端优化的卡片组件示例">
            <template #actions>
              <button class="btn btn-primary">操作按钮</button>
            </template>
          </MobileCard>
        </div>
        
        <div class="example-card">
          <h3>数据表格组件</h3>
          <p>展示了Element Plus组件库和数据管理的集成。</p>
          <div class="table-container">
            <DataTable />
          </div>
        </div>
        
        <div class="example-card">
          <h3>图表展示组件</h3>
          <p>展示了ECharts图表库的集成和使用。</p>
          <ChartViewer />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import UserProfile from '@/components/UserProfile.vue';
import MobileCard from '@/components/MobileCard.vue';
import DataTable from '@/components/DataTable.vue';
import ChartViewer from '@/components/ChartViewer.vue';

// 定义特性列表
const features = ref([
  {
    title: 'Vue DevTools',
    description: '使用官方DevTools扩展调试Vue应用程序，实时查看组件状态和性能分析'
  },
  {
    title: '服务端渲染(SSR)',
    description: '通过Nuxt.js等框架实现服务端渲染，提升SEO和首屏加载速度'
  },
  {
    title: '移动端开发',
    description: '集成Vant等移动端UI库，构建响应式移动应用'
  },
  {
    title: 'TypeScript集成',
    description: '使用TypeScript增强代码质量和开发体验，提供静态类型检查'
  },
  {
    title: '构建工具与部署',
    description: '使用Vite等现代构建工具优化项目性能并高效部署'
  },
  {
    title: '测试体系',
    description: '建立完整的单元测试和端到端测试体系，确保代码质量'
  },
  {
    title: '社区生态',
    description: '集成Element Plus、ECharts等丰富的第三方库和工具'
  }
]);
</script>

<style scoped>
.home-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.section {
  margin-bottom: 40px;
}

.section h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #42b983;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.feature-card {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  background: white;
}

.feature-card h3 {
  margin-top: 0;
  color: #333;
}

.feature-card p {
  color: #666;
}

.component-examples {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
  gap: 30px;
}

.example-card {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  background: white;
}

.example-card h3 {
  margin-top: 0;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.example-card p {
  color: #666;
  margin-bottom: 15px;
}

.table-container {
  max-height: 300px;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .component-examples {
    grid-template-columns: 1fr;
  }
  
  .features {
    grid-template-columns: 1fr;
  }
}
</style>
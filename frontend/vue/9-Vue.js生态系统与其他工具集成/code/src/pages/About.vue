<template>
  <div class="about-page">
    <h1>关于本项目</h1>
    <p>这是一个展示Vue.js生态系统与其他工具集成的示例项目。</p>
    
    <div class="features">
      <h2>项目特性</h2>
      <ul>
        <li>Vue DevTools调试工具集成</li>
        <li>服务端渲染(SSR)与Nuxt.js概念演示</li>
        <li>移动端开发与Vant组件库集成</li>
        <li>TypeScript类型安全支持</li>
        <li>Vite构建工具配置</li>
        <li>单元测试与端到端测试示例</li>
        <li>第三方库集成（Element Plus、ECharts等）</li>
      </ul>
    </div>
    
    <div class="tech-stack">
      <h2>技术栈</h2>
      <div class="tech-items">
        <div class="tech-item">
          <h3>核心框架</h3>
          <ul>
            <li>Vue 3</li>
            <li>Vue Router</li>
            <li>Pinia</li>
          </ul>
        </div>
        
        <div class="tech-item">
          <h3>UI组件库</h3>
          <ul>
            <li>Element Plus</li>
            <li>Vant</li>
          </ul>
        </div>
        
        <div class="tech-item">
          <h3>构建工具</h3>
          <ul>
            <li>Vite</li>
            <li>TypeScript</li>
          </ul>
        </div>
        
        <div class="tech-item">
          <h3>测试工具</h3>
          <ul>
            <li>Vitest</li>
            <li>Playwright</li>
          </ul>
        </div>
        
        <div class="tech-item">
          <h3>其他工具</h3>
          <ul>
            <li>ECharts</li>
            <li>Axios</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AboutPage'
}
</script>

<style scoped>
.about-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.features ul,
.tech-items {
  text-align: left;
  margin: 1rem 0;
}

.tech-items {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.tech-item {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
}

.tech-item h3 {
  margin-top: 0;
  color: #42b983;
}

footer {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}
</style>
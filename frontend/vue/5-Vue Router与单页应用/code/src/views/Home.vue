<template>
  <div class="home">
    <section class="hero">
      <div class="container">
        <h1>欢迎来到 Vue Router SPA 示例</h1>
        <p>这是一个展示 Vue Router 各种特性的单页应用程序示例</p>
        <button class="cta-button">开始探索</button>
      </div>
    </section>

    <section class="features">
      <div class="container">
        <div class="feature-grid">
          <div class="feature-card">
            <h3>嵌套路由</h3>
            <p>演示如何在 Vue Router 中实现嵌套路由</p>
          </div>
          <div class="feature-card">
            <h3>动态路由</h3>
            <p>展示如何使用动态路由参数传递数据</p>
          </div>
          <div class="feature-card">
            <h3>路由守卫</h3>
            <p>演示如何使用路由守卫保护路由</p>
          </div>
          <div class="feature-card">
            <h3>编程式导航</h3>
            <p>展示如何通过代码进行页面导航</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'HomePage'
}
</script>

<style scoped>
.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4rem 0;
  text-align: center;
}

.hero h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.hero p {
  font-size: 1.2rem;
  margin-bottom: 2rem;
}

.cta-button {
  background: #fff;
  color: #667eea;
  border: none;
  padding: 1rem 2rem;
  font-size: 1.1rem;
  border-radius: 5px;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.cta-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.features {
  padding: 4rem 0;
  background: #f8f9fa;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  text-align: center;
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-card h3 {
  color: #667eea;
  margin-bottom: 1rem;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

@media (max-width: 768px) {
  .hero h1 {
    font-size: 2rem;
  }
  
  .hero p {
    font-size: 1rem;
  }
  
  .features {
    padding: 2rem 0;
  }
}
</style>
<template>
  <div class="about">
    <h1>关于我们</h1>
    
    <section class="team">
      <h2>我们的团队</h2>
      <div class="team-grid">
        <div class="team-member">
          <img src="https://via.placeholder.com/150" alt="张三">
          <h3>张三</h3>
          <p>首席执行官</p>
        </div>
        <div class="team-member">
          <img src="https://via.placeholder.com/150" alt="李四">
          <h3>李四</h3>
          <p>技术总监</p>
        </div>
        <div class="team-member">
          <img src="https://via.placeholder.com/150" alt="王五">
          <h3>王五</h3>
          <p>产品经理</p>
        </div>
      </div>
    </section>
    
    <section class="history">
      <h2>公司历史</h2>
      <p>我们是一家专注于前端技术解决方案的公司，致力于为客户提供高质量的Vue.js开发服务。</p>
    </section>
  </div>
</template>

<script>
export default {
  name: 'AboutPage'
}
</script>

<style scoped>
.about {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.team-member {
  text-align: center;
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.team-member img {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 1rem;
}

.history {
  margin-top: 3rem;
}

@media (max-width: 768px) {
  .about {
    padding: 1rem;
  }
}
</style>
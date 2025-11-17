<template>
  <div class="admin-dashboard-content">
    <h2>仪表盘</h2>
    
    <div class="stats-grid">
      <div class="stat-card">
        <h3>总销售额</h3>
        <p class="stat-value">$24,560</p>
        <p class="stat-change positive">+12% 本月</p>
      </div>
      
      <div class="stat-card">
        <h3>订单数</h3>
        <p class="stat-value">142</p>
        <p class="stat-change positive">+8% 本月</p>
      </div>
      
      <div class="stat-card">
        <h3>用户数</h3>
        <p class="stat-value">1,248</p>
        <p class="stat-change negative">-2% 本月</p>
      </div>
      
      <div class="stat-card">
        <h3>产品数</h3>
        <p class="stat-value">86</p>
        <p class="stat-change">0% 本月</p>
      </div>
    </div>
    
    <div class="charts">
      <div class="chart-container">
        <h3>销售趋势</h3>
        <div class="chart-placeholder">
          <p>销售趋势图表</p>
        </div>
      </div>
      
      <div class="chart-container">
        <h3>热门产品</h3>
        <div class="chart-placeholder">
          <p>热门产品图表</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminDashboard'
}
</script>

<style scoped>
.admin-dashboard-content {
  padding: 1rem 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stat-card h3 {
  color: #6c757d;
  font-size: 1rem;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 0.5rem 0;
}

.stat-change {
  font-size: 0.875rem;
}

.stat-change.positive {
  color: #28a745;
}

.stat-change.negative {
  color: #dc3545;
}

.charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.chart-container {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.chart-container h3 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.chart-placeholder {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-radius: 4px;
}

.chart-placeholder p {
  color: #6c757d;
  font-size: 1.2rem;
}
</style>
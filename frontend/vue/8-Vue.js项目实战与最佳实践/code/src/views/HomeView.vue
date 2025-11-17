<template>
  <div class="home">
    <h1>欢迎使用任务管理系统</h1>
    <p>这是一个基于Vue.js开发的完整项目示例，展示了Vue.js项目开发的最佳实践。</p>
    
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>项目特点</span>
            </div>
          </template>
          <div class="card-content">
            <ul>
              <li>组件化设计</li>
              <li>状态管理（Pinia）</li>
              <li>路由管理（Vue Router）</li>
              <li>API接口封装</li>
              <li>代码规范</li>
            </ul>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>技术栈</span>
            </div>
          </template>
          <div class="card-content">
            <ul>
              <li>Vue 3</li>
              <li>Vue Router</li>
              <li>Pinia</li>
              <li>Element Plus</li>
              <li>Axios</li>
            </ul>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>开始使用</span>
            </div>
          </template>
          <div class="card-content">
            <p>点击下方按钮开始管理您的任务</p>
            <el-button type="primary" @click="$router.push('/tasks')">查看任务列表</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: 'HomeView'
}
</script>

<style scoped>
.home {
  padding: 20px;
}

.card-header {
  font-weight: bold;
}

.card-content ul {
  padding-left: 20px;
}

.card-content li {
  margin: 10px 0;
}
</style>